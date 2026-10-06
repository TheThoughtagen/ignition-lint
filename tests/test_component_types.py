"""Tests for component type checking against the generated component list."""

import json
import os
import re
import tempfile

import pytest

from ignition_lint.perspective.linter import IgnitionPerspectiveLinter
from ignition_lint.reporting import LintSeverity
from ignition_lint.schemas import schema_path_for

COMPONENT_PROPS = schema_path_for("robust").parent / "component-props.json"


def _lint_root(root, target_component_type=None):
    """Lint a view whose root component is ``root``; return (linter, issues)."""
    linter = IgnitionPerspectiveLinter()
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, "view.json")
    with open(path, "w") as f:
        json.dump({"custom": {}, "params": {}, "props": {}, "root": root}, f)
    try:
        linter.lint_file(path, target_component_type)
    finally:
        os.unlink(path)
        os.rmdir(tmpdir)
    return linter, linter.issues


def _with_code(issues, code):
    return [i for i in issues if i.code == code]


# Components that Ignition 8.3 ships but the hand-written list did not have.
IGNITION_83_TYPES = [
    "ia.display.cylindrical-tank",
    "ia.display.map",
    "ia.display.pdf-viewer",
    "ia.display.sparkline",
    "ia.container.split",
    "ia.input.slider",
    "ia.navigation.link",
    "ia.shapes.circle",
    "ia.symbol.valve",
    "ia.symbol.motor",
    "ia.reporting.report-viewer",
]


class TestKnownComponentTypes:
    @pytest.mark.parametrize("comp_type", IGNITION_83_TYPES)
    def test_ignition_83_component_passes(self, comp_type):
        linter, issues = _lint_root(
            {"type": comp_type, "meta": {"name": "Thing"}, "props": {}}
        )
        assert _with_code(issues, "SCHEMA_VALIDATION") == []
        assert _with_code(issues, "UNKNOWN_COMPONENT_TYPE") == []
        assert linter.component_stats["invalid_components"] == 0

    def test_known_component_with_bad_structure_is_still_an_error(self):
        _, issues = _lint_root(
            {
                "type": "ia.display.label",
                "meta": {"name": "StatusLabel"},
                "props": {"text": "ok"},
                "position": {"grow": -1},
            }
        )
        errors = _with_code(issues, "SCHEMA_VALIDATION")
        assert len(errors) == 1
        assert errors[0].severity == LintSeverity.ERROR
        assert _with_code(issues, "UNKNOWN_COMPONENT_TYPE") == []

    def test_ignition_83_props_are_known(self):
        _, issues = _lint_root(
            {
                "type": "ia.symbol.valve",
                "meta": {"name": "InletValve"},
                "props": {"state": "open", "appearance": "auto"},
            }
        )
        assert _with_code(issues, "UNKNOWN_PROP") == []


class TestUnknownComponentType:
    def test_unknown_type_is_a_warning_not_an_error(self):
        linter, issues = _lint_root(
            {"type": "ia.display.lable", "meta": {"name": "StatusLabel"}}
        )
        warnings = _with_code(issues, "UNKNOWN_COMPONENT_TYPE")
        assert len(warnings) == 1
        assert warnings[0].severity == LintSeverity.WARNING
        assert "ia.display.lable" in warnings[0].message
        assert _with_code(issues, "SCHEMA_VALIDATION") == []
        assert linter.component_stats["invalid_components"] == 0

    def test_unknown_category_is_a_warning(self):
        _, issues = _lint_root({"type": "ia.newcategory.widget", "meta": {"name": "W"}})
        assert len(_with_code(issues, "UNKNOWN_COMPONENT_TYPE")) == 1
        assert _with_code(issues, "SCHEMA_VALIDATION") == []

    def test_rest_of_unknown_component_is_still_checked(self):
        _, issues = _lint_root(
            {
                "type": "ia.display.brand-new",
                "meta": {"name": "BrandNew"},
                "position": {"grow": -1},
            }
        )
        assert len(_with_code(issues, "UNKNOWN_COMPONENT_TYPE")) == 1
        errors = _with_code(issues, "SCHEMA_VALIDATION")
        assert len(errors) == 1
        assert "type" not in errors[0].message

    def test_unknown_child_is_reported_once_on_the_child(self):
        _, issues = _lint_root(
            {
                "type": "ia.container.flex",
                "meta": {"name": "Root"},
                "props": {"direction": "column"},
                "children": [
                    {
                        "type": "ia.display.brand-new",
                        "meta": {"name": "BrandNew"},
                        "position": {"basis": "50px"},
                    },
                    {
                        "type": "ia.display.label",
                        "meta": {"name": "StatusLabel"},
                        "position": {"basis": "50px"},
                        "props": {"text": "ok"},
                    },
                ],
            }
        )
        warnings = _with_code(issues, "UNKNOWN_COMPONENT_TYPE")
        assert [w.component_path for w in warnings] == ["root.root.children[0]"]
        assert _with_code(issues, "SCHEMA_VALIDATION") == []

    def test_unknown_type_does_not_fail_default_threshold(self):
        _, issues = _lint_root({"type": "ia.display.brand-new", "meta": {"name": "B"}})
        assert not any(i.severity == LintSeverity.ERROR for i in issues)


def _flex(name, *children):
    return {
        "type": "ia.container.flex",
        "meta": {"name": name},
        "props": {"direction": "column"},
        "position": {"basis": "50px"},
        "children": list(children),
    }


def _leaf(comp_type, name="Thing"):
    return {"type": comp_type, "meta": {"name": name}, "position": {"basis": "50px"}}


class TestUnknownChildNotLintedOnItsOwn:
    """A child is linted on its own only if its type starts with ``ia.`` (and
    matches --component). Otherwise its unknown type is reported by the nearest
    ancestor that is linted, exactly once."""

    def test_child_without_ia_prefix_is_reported(self):
        _, issues = _lint_root(_flex("Root", _leaf("ai.display.label")))
        warnings = _with_code(issues, "UNKNOWN_COMPONENT_TYPE")
        assert [(w.component_path, w.component_type) for w in warnings] == [
            ("root.root.children[0]", "ai.display.label")
        ]
        assert _with_code(issues, "SCHEMA_VALIDATION") == []

    def test_grandchild_is_reported_once_by_nearest_linted_ancestor(self):
        _, issues = _lint_root(_flex("Root", _flex("Inner", _leaf("ai.display.label"))))
        warnings = _with_code(issues, "UNKNOWN_COMPONENT_TYPE")
        assert [w.component_path for w in warnings] == [
            "root.root.children[0].children[0]"
        ]

    def test_grandchild_under_unlinted_parent_is_reported_by_grandparent(self):
        _, issues = _lint_root(
            _flex("Root", {**_flex("Inner", _leaf("ai.x")), "type": "ai.flex"})
        )
        warnings = _with_code(issues, "UNKNOWN_COMPONENT_TYPE")
        assert sorted(w.component_path for w in warnings) == [
            "root.root.children[0]",
            "root.root.children[0].children[0]",
        ]

    def test_child_excluded_by_component_filter_is_reported(self):
        _, issues = _lint_root(
            _flex("Root", _leaf("ia.input.buton"), _leaf("ia.container.typo")),
            target_component_type="ia.container",
        )
        warnings = _with_code(issues, "UNKNOWN_COMPONENT_TYPE")
        assert sorted(w.component_path for w in warnings) == [
            "root.root.children[0]",
            "root.root.children[1]",
        ]

    def test_ia_child_is_still_reported_only_on_itself(self):
        _, issues = _lint_root(_flex("Root", _leaf("ia.display.brand-new")))
        warnings = _with_code(issues, "UNKNOWN_COMPONENT_TYPE")
        assert [w.component_path for w in warnings] == ["root.root.children[0]"]


@pytest.fixture(scope="module")
def type_schema():
    with open(schema_path_for("robust"), encoding="utf-8") as f:
        return json.load(f)["properties"]["type"]


class TestSchemaConsistency:
    def test_every_listed_type_matches_the_pattern(self, type_schema):
        pattern = re.compile(type_schema["pattern"])
        mismatched = [t for t in type_schema["enum"] if not pattern.match(t)]
        assert mismatched == []

    def test_type_list_is_sorted_and_unique(self, type_schema):
        assert type_schema["enum"] == sorted(set(type_schema["enum"]))

    def test_every_listed_type_has_a_props_entry(self, type_schema):
        with open(COMPONENT_PROPS, encoding="utf-8") as f:
            props = json.load(f)
        missing = [t for t in type_schema["enum"] if t not in props]
        # ia.display.barcode was listed by hand and is not in Ignition 8.3.
        assert missing == ["ia.display.barcode"]
