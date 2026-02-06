"""Lint suppression configuration: CLI ignore codes and .ignition-lintignore file."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pathspec


@dataclass
class SuppressionConfig:
    """Holds all suppression rules: CLI ignore codes + ignore-file patterns."""

    ignore_codes: set[str] = field(default_factory=set)
    blanket_path_spec: pathspec.PathSpec | None = None
    rule_path_specs: list[tuple[pathspec.PathSpec, set[str]]] = field(
        default_factory=list
    )
    project_root: Path | None = None

    def should_suppress(self, code: str, file_path: str) -> bool:
        """Return True if this issue should be suppressed."""
        if code in self.ignore_codes:
            return True

        if self.project_root is None:
            return False

        try:
            rel_path = (
                Path(file_path).resolve().relative_to(self.project_root).as_posix()
            )
        except ValueError:
            return False

        if self.blanket_path_spec and self.blanket_path_spec.match_file(rel_path):
            return True

        for spec, codes in self.rule_path_specs:
            if code in codes and spec.match_file(rel_path):
                return True

        return False


def load_ignition_lintignore(
    ignore_file: Path,
) -> tuple[pathspec.PathSpec | None, list[tuple[pathspec.PathSpec, set[str]]]]:
    """Parse an .ignition-lintignore file.

    Lines without a colon are blanket patterns (suppress all rules).
    Lines with ``pattern:CODE1,CODE2`` suppress only those codes.
    Lines starting with ``#`` or blank lines are skipped.
    """
    if not ignore_file.is_file():
        return None, []

    blanket_lines: list[str] = []
    rule_specs: list[tuple[pathspec.PathSpec, set[str]]] = []

    for raw_line in ignore_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if ":" in line:
            pattern_part, codes_part = line.rsplit(":", 1)
            codes = {c.strip() for c in codes_part.split(",") if c.strip()}
            if codes and pattern_part.strip():
                spec = pathspec.PathSpec.from_lines(
                    "gitwildmatch", [pattern_part.strip()]
                )
                rule_specs.append((spec, codes))
            else:
                blanket_lines.append(line)
        else:
            blanket_lines.append(line)

    blanket_spec = (
        pathspec.PathSpec.from_lines("gitwildmatch", blanket_lines)
        if blanket_lines
        else None
    )
    return blanket_spec, rule_specs


def build_suppression_config(
    ignore_codes: str | None = None,
    project_root: Path | None = None,
    ignore_file: Path | None = None,
) -> SuppressionConfig:
    """Factory that combines CLI ignore codes with an ignore file."""
    codes: set[str] = set()
    if ignore_codes:
        codes = {c.strip() for c in ignore_codes.split(",") if c.strip()}

    blanket_spec = None
    rule_specs: list[tuple[pathspec.PathSpec, set[str]]] = []

    if project_root or ignore_file:
        path = ignore_file or (project_root / ".ignition-lintignore")
        blanket_spec, rule_specs = load_ignition_lintignore(path)

    resolved_root = (
        project_root.resolve()
        if project_root
        else (ignore_file.parent.resolve() if ignore_file else None)
    )

    return SuppressionConfig(
        ignore_codes=codes,
        blanket_path_spec=blanket_spec,
        rule_path_specs=rule_specs,
        project_root=resolved_root,
    )
