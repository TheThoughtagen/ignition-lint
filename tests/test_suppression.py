"""Tests for lint suppression mechanisms."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from ignition_lint.reporting import LintIssue, LintReport, LintSeverity
from ignition_lint.suppression import SuppressionConfig, build_suppression_config, load_ignition_lintignore
from ignition_lint.scripts.linter import IgnitionScriptLinter


# ---------------------------------------------------------------------------
# Mechanism 1: --ignore-codes
# ---------------------------------------------------------------------------

class TestIgnoreCodes:
    def test_matching_code_suppressed(self):
        config = SuppressionConfig(ignore_codes={"NAMING_PARAMETER", "LONG_LINE"})
        assert config.should_suppress("NAMING_PARAMETER", "/any/file.json") is True
        assert config.should_suppress("LONG_LINE", "/any/file.py") is True

    def test_non_matching_code_passes(self):
        config = SuppressionConfig(ignore_codes={"NAMING_PARAMETER"})
        assert config.should_suppress("SYNTAX_ERROR", "/any/file.py") is False

    def test_empty_ignore_codes(self):
        config = SuppressionConfig()
        assert config.should_suppress("ANYTHING", "/any/file.py") is False

    def test_report_add_issue_filters(self):
        config = SuppressionConfig(ignore_codes={"LONG_LINE"})
        report = LintReport(suppression=config)

        report.add_issue(LintIssue(
            severity=LintSeverity.STYLE,
            code="LONG_LINE",
            message="too long",
            file_path="/a.py",
        ))
        report.add_issue(LintIssue(
            severity=LintSeverity.ERROR,
            code="SYNTAX_ERROR",
            message="bad syntax",
            file_path="/a.py",
        ))

        assert len(report.issues) == 1
        assert report.issues[0].code == "SYNTAX_ERROR"
        assert report.suppressed_count == 1

    def test_build_suppression_config_from_string(self):
        config = build_suppression_config(ignore_codes="NAMING_PARAMETER,LONG_LINE")
        assert config.ignore_codes == {"NAMING_PARAMETER", "LONG_LINE"}

    def test_build_suppression_config_none(self):
        config = build_suppression_config(ignore_codes=None)
        assert config.ignore_codes == set()


# ---------------------------------------------------------------------------
# Mechanism 2: .ignition-lintignore file
# ---------------------------------------------------------------------------

class TestLintIgnoreFile:
    def test_blanket_pattern(self, tmp_path):
        ignore = tmp_path / ".ignition-lintignore"
        ignore.write_text("scripts/generated/**\n")
        blanket, rules = load_ignition_lintignore(ignore)
        assert blanket is not None
        assert blanket.match_file("scripts/generated/foo.py") is True
        assert blanket.match_file("scripts/other/bar.py") is False
        assert rules == []

    def test_rule_specific_pattern(self, tmp_path):
        ignore = tmp_path / ".ignition-lintignore"
        ignore.write_text("views/_REFERENCE/**:NAMING_COMPONENT,GENERIC_COMPONENT_NAME\n")
        blanket, rules = load_ignition_lintignore(ignore)
        assert blanket is None
        assert len(rules) == 1
        spec, codes = rules[0]
        assert codes == {"NAMING_COMPONENT", "GENERIC_COMPONENT_NAME"}
        assert spec.match_file("views/_REFERENCE/test/view.json") is True
        assert spec.match_file("views/Main/view.json") is False

    def test_comments_skipped(self, tmp_path):
        ignore = tmp_path / ".ignition-lintignore"
        ignore.write_text("# This is a comment\n\n# Another\ngenerated/**\n")
        blanket, rules = load_ignition_lintignore(ignore)
        assert blanket is not None
        assert blanket.match_file("generated/foo.py") is True

    def test_missing_file(self, tmp_path):
        blanket, rules = load_ignition_lintignore(tmp_path / "nonexistent")
        assert blanket is None
        assert rules == []

    def test_should_suppress_blanket(self, tmp_path):
        ignore = tmp_path / ".ignition-lintignore"
        ignore.write_text("sub/**\n")

        config = build_suppression_config(project_root=tmp_path, ignore_file=ignore)

        # Create a fake file path inside the project
        target = tmp_path / "sub" / "test.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch()

        assert config.should_suppress("ANY_CODE", str(target)) is True
        assert config.should_suppress("ANY_CODE", str(tmp_path / "other.py")) is False

    def test_should_suppress_rule_specific(self, tmp_path):
        ignore = tmp_path / ".ignition-lintignore"
        ignore.write_text("views/_REF/**:NAMING_COMPONENT\n")

        config = build_suppression_config(project_root=tmp_path, ignore_file=ignore)

        target = tmp_path / "views" / "_REF" / "view.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch()

        assert config.should_suppress("NAMING_COMPONENT", str(target)) is True
        assert config.should_suppress("SYNTAX_ERROR", str(target)) is False

    def test_mixed_blanket_and_rules(self, tmp_path):
        ignore = tmp_path / ".ignition-lintignore"
        ignore.write_text("generated/**\nviews/_REF/**:NAMING_COMPONENT\n")

        config = build_suppression_config(project_root=tmp_path, ignore_file=ignore)

        gen = tmp_path / "generated" / "a.py"
        gen.parent.mkdir(parents=True, exist_ok=True)
        gen.touch()

        ref = tmp_path / "views" / "_REF" / "v.json"
        ref.parent.mkdir(parents=True, exist_ok=True)
        ref.touch()

        assert config.should_suppress("ANYTHING", str(gen)) is True
        assert config.should_suppress("NAMING_COMPONENT", str(ref)) is True
        assert config.should_suppress("OTHER", str(ref)) is False


# ---------------------------------------------------------------------------
# Mechanism 3: Inline suppression (scripts only)
# ---------------------------------------------------------------------------

class TestInlineSuppression:
    def _make_linter_with_file(self, tmp_path, content: str) -> IgnitionScriptLinter:
        """Write content to a .py file and lint it."""
        f = tmp_path / "test_script.py"
        f.write_text(textwrap.dedent(content))
        linter = IgnitionScriptLinter()
        linter._lint_file(f)
        return linter

    def test_disable_file(self, tmp_path):
        content = """\
        # ignition-lint: disable-file=MISSING_DOCSTRING
        def hello():
            pass
        def world():
            pass
        """
        linter = self._make_linter_with_file(tmp_path, content)
        docstring_issues = [i for i in linter.issues if i.code == "MISSING_DOCSTRING"]
        assert len(docstring_issues) == 0

    def test_disable_line_shorthand(self, tmp_path):
        # The `disable=` shorthand suppresses the current line
        long = "a" * 130
        f = tmp_path / "test_script.py"
        f.write_text(
            f'x = "{long}"  # ignition-lint: disable=LONG_LINE\n'
            f'y = "{long}"\n'
        )
        linter = IgnitionScriptLinter()
        linter._lint_file(f)
        long_issues = [i for i in linter.issues if i.code == "LONG_LINE"]
        # Line 1 should be suppressed, line 2 should remain
        assert all(i.line_number != 1 for i in long_issues)
        assert any(i.line_number == 2 for i in long_issues)

    def test_disable_next(self, tmp_path):
        long = "a" * 130
        f = tmp_path / "test_script.py"
        f.write_text(
            f'# ignition-lint: disable-next=LONG_LINE\n'
            f'x = "{long}"\n'
            f'y = "{long}"\n'
        )
        linter = IgnitionScriptLinter()
        linter._lint_file(f)
        long_issues = [i for i in linter.issues if i.code == "LONG_LINE"]
        # Line 2 suppressed, line 3 remains
        assert all(i.line_number != 2 for i in long_issues)
        assert any(i.line_number == 3 for i in long_issues)

    def test_disable_line_explicit(self, tmp_path):
        long = "a" * 130
        f = tmp_path / "test_script.py"
        f.write_text(f'x = "{long}"  # ignition-lint: disable-line=LONG_LINE\n')
        linter = IgnitionScriptLinter()
        linter._lint_file(f)
        long_issues = [i for i in linter.issues if i.code == "LONG_LINE"]
        assert len(long_issues) == 0

    def test_multiple_codes(self, tmp_path):
        content = """\
        # ignition-lint: disable-file=MISSING_DOCSTRING,LONG_LINE
        def hello():
            x = "a" * 200
        """
        linter = self._make_linter_with_file(tmp_path, content)
        suppressed = [i for i in linter.issues if i.code in ("MISSING_DOCSTRING", "LONG_LINE")]
        assert len(suppressed) == 0

    def test_non_matching_code_passes_through(self, tmp_path):
        # disable-file for one code shouldn't suppress others
        content = """\
        # ignition-lint: disable-file=LONG_LINE
        def hello():
            pass
        """
        linter = self._make_linter_with_file(tmp_path, content)
        docstring_issues = [i for i in linter.issues if i.code == "MISSING_DOCSTRING"]
        assert len(docstring_issues) >= 1

    def test_disable_file_only_first_10_lines(self, tmp_path):
        # A disable-file comment on line 12 should be ignored
        lines = [""] * 11 + ["# ignition-lint: disable-file=MISSING_DOCSTRING", "def hello():", "    pass"]
        content = "\n".join(lines)
        f = tmp_path / "script.py"
        f.write_text(content)
        linter = IgnitionScriptLinter()
        linter._lint_file(f)
        docstring_issues = [i for i in linter.issues if i.code == "MISSING_DOCSTRING"]
        assert len(docstring_issues) >= 1
