"""Tests for regenerating the component list from Ignition module files."""

import io
import json
import re
import shutil
import subprocess
import zipfile

import pytest

from ignition_lint.schemas import generate

MODULE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<modules><module><name>{name}</name><version>{version}</version></module></modules>
"""


def _components_json(*components):
    return json.dumps(
        {"groupId": "test", "libraryName": "test", "components": list(components)}
    )


def _component(comp_id, props=(), **schema_extra):
    schema = {"type": "object", "properties": {p: {} for p in props}}
    schema.update(schema_extra)
    return {"id": comp_id, "name": comp_id, "schema": schema}


def _jar(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as jar:
        for name, data in files.items():
            jar.writestr(name, data)
    return buf.getvalue()


def _write_modl(path, name, version, jars):
    with zipfile.ZipFile(path, "w") as modl:
        modl.writestr("module.xml", MODULE_XML.format(name=name, version=version))
        for jar_name, files in jars.items():
            modl.writestr(jar_name, _jar(files))
    return path


@pytest.fixture
def modules_dir(tmp_path):
    _write_modl(
        tmp_path / "Perspective-module.modl",
        "Perspective",
        "3.3.9.2026082511",
        {
            "perspective-common.jar": {
                "ia.components.json": _components_json(
                    _component("ia.display.label", ["text", "style"]),
                    _component(
                        "ia.symbol.valve",
                        ["state"],
                        allOf=[{"properties": {"appearance": {}}}],
                    ),
                ),
                "map.components.json": _components_json(
                    _component("ia.display.map", ["init", "layers"])
                ),
                "schemas/style.json": "{}",
                "Other.class": b"\xca\xfe",
            },
            "not-a-zip.jar": {},
        },
    )
    _write_modl(
        tmp_path / "Reporting-module.modl",
        "Reporting",
        "7.3.9.2026082511",
        {
            "reporting-common.jar": {
                "reporting.components.json": _components_json(
                    _component("ia.reporting.report-viewer", ["source"])
                )
            }
        },
    )
    _write_modl(tmp_path / "Driver.modl", "Some Driver", "1.0.0", {"d.jar": {}})
    return tmp_path


class TestExtract:
    def test_reads_every_component_from_every_module(self, modules_dir):
        found = generate.extract_components([modules_dir])
        assert sorted(found.components) == [
            "ia.display.label",
            "ia.display.map",
            "ia.reporting.report-viewer",
            "ia.symbol.valve",
        ]

    def test_collects_top_level_props_including_branches(self, modules_dir):
        found = generate.extract_components([modules_dir])
        assert found.components["ia.display.label"] == {"style", "text"}
        assert found.components["ia.symbol.valve"] == {"appearance", "state"}

    def test_records_versions_of_modules_that_define_components(self, modules_dir):
        found = generate.extract_components([modules_dir])
        assert found.modules == {
            "Perspective": "3.3.9.2026082511",
            "Reporting": "7.3.9.2026082511",
        }

    def test_accepts_a_single_modl_file(self, modules_dir):
        found = generate.extract_components([modules_dir / "Reporting-module.modl"])
        assert list(found.components) == ["ia.reporting.report-viewer"]

    def test_no_components_is_an_error(self, tmp_path):
        with pytest.raises(generate.GenerateError, match="No Perspective component"):
            generate.extract_components([tmp_path])


class TestUpdateTypeSchema:
    @pytest.fixture
    def schema(self):
        return {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "pattern": "^ia\\.(display)\\.",
                    "description": "Component type",
                    "enum": ["ia.display.label", "ia.display.old-thing"],
                },
                "meta": {"type": "object"},
            },
        }

    def test_adds_new_types_and_keeps_old_ones(self, schema):
        generate.update_type_schema(
            schema, ["ia.symbol.valve", "ia.display.label"], "Ignition 8.3.9"
        )
        assert schema["properties"]["type"]["enum"] == [
            "ia.display.label",
            "ia.display.old-thing",
            "ia.symbol.valve",
        ]

    def test_prune_drops_types_the_source_lacks(self, schema):
        generate.update_type_schema(
            schema, ["ia.display.label"], "Ignition 8.3.9", prune=True
        )
        assert schema["properties"]["type"]["enum"] == ["ia.display.label"]

    def test_pattern_covers_every_category(self, schema):
        generate.update_type_schema(
            schema, ["ia.symbol.valve", "ia.shapes.circle"], "Ignition 8.3.9"
        )
        type_schema = schema["properties"]["type"]
        assert type_schema["pattern"] == "^ia\\.(display|shapes|symbol)\\."
        assert all(re.match(type_schema["pattern"], t) for t in type_schema["enum"])

    def test_records_where_the_list_came_from(self, schema):
        generate.update_type_schema(schema, ["ia.display.label"], "Ignition 8.3.9")
        comment = schema["properties"]["type"]["$comment"]
        assert "Ignition 8.3.9" in comment
        assert "ignition_lint.schemas.generate" in comment

    def test_keeps_the_rest_of_the_schema(self, schema):
        generate.update_type_schema(schema, ["ia.display.label"], "Ignition 8.3.9")
        assert schema["properties"]["meta"] == {"type": "object"}
        assert schema["properties"]["type"]["description"] == "Component type"


class TestUpdateComponentProps:
    def test_merges_props_and_adds_new_components(self):
        existing = {"ia.display.label": ["text", "visible"]}
        result = generate.update_component_props(
            existing,
            {"ia.display.label": {"text", "style"}, "ia.symbol.valve": {"state"}},
        )
        assert result == {
            "ia.display.label": ["style", "text", "visible"],
            "ia.symbol.valve": ["state"],
        }
        assert list(result) == sorted(result)

    def test_prune_replaces_hand_written_entries(self):
        existing = {"ia.display.label": ["visible"], "ia.display.gone": ["x"]}
        result = generate.update_component_props(
            existing, {"ia.display.label": {"text"}}, prune=True
        )
        assert result == {"ia.display.label": ["text"]}


class TestMain:
    def test_writes_both_files(self, modules_dir, tmp_path):
        out = tmp_path / "out"
        out.mkdir()
        schema_file = out / "schema.json"
        props_file = out / "props.json"
        schema_file.write_text(
            json.dumps({"properties": {"type": {"type": "string", "enum": []}}})
        )
        props_file.write_text("{}")

        code = generate.main(
            [
                "--source",
                str(modules_dir),
                "--ignition-version",
                "8.3.9",
                "--schema",
                str(schema_file),
                "--component-props",
                str(props_file),
            ]
        )

        assert code == 0
        schema = json.loads(schema_file.read_text())
        assert "ia.reporting.report-viewer" in schema["properties"]["type"]["enum"]
        assert "Ignition 8.3.9" in schema["properties"]["type"]["$comment"]
        assert "Perspective 3.3.9" in schema["properties"]["type"]["$comment"]
        props = json.loads(props_file.read_text())
        assert props["ia.display.map"] == ["init", "layers"]
        assert schema_file.read_bytes().endswith(b"}\n")

    def test_needs_a_source(self, capsys):
        with pytest.raises(SystemExit):
            generate.main([])

    def test_reports_a_missing_source(self, tmp_path, capsys):
        code = generate.main(["--source", str(tmp_path / "missing")])
        assert code == 1
        assert "missing" in capsys.readouterr().err


def _schema_files(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    schema_file = out / "schema.json"
    props_file = out / "props.json"
    schema_file.write_text(
        json.dumps({"properties": {"type": {"type": "string", "enum": []}}})
    )
    props_file.write_text("{}")
    return ["--schema", str(schema_file), "--component-props", str(props_file)]


class TestMalformedResources:
    @pytest.mark.parametrize(
        "content",
        [
            b"{not json",
            b"\x80\x81 not utf-8",
            b"[]",
            b'{"components": {"id": "ia.display.label"}}',
            b'{"components": ["ia.display.label"]}',
        ],
        ids=["bad-json", "bad-encoding", "not-object", "not-list", "not-objects"],
    )
    def test_is_reported_with_archive_and_resource(self, tmp_path, capsys, content):
        source = tmp_path / "modules"
        source.mkdir()
        _write_modl(
            source / "Broken-module.modl",
            "Broken",
            "1.0.0",
            {"broken.jar": {"broken.components.json": content}},
        )

        code = generate.main(["--source", str(source)] + _schema_files(tmp_path))

        assert code == 1
        err = capsys.readouterr().err
        assert "broken.components.json" in err
        assert "Broken-module.modl" in err
        assert "Traceback" not in err


class FakeDocker:
    """Stands in for subprocess.run; fails the docker step named by ``fail``."""

    def __init__(self, modules_dir=None, fail=None):
        self.modules_dir = modules_dir
        self.fail = fail
        self.calls = []

    def __call__(self, cmd, check=False, capture_output=False, text=False):
        self.calls.append(cmd)
        step = cmd[1]
        if step == self.fail:
            raise subprocess.CalledProcessError(1, cmd, stderr=f"{step} broke\n")
        if step == "cp":
            shutil.copytree(self.modules_dir, cmd[3])
        return subprocess.CompletedProcess(cmd, 0, stdout="abc123\n", stderr="")


class TestImage:
    @pytest.fixture
    def docker_on_path(self, monkeypatch):
        monkeypatch.setattr(generate.shutil, "which", lambda name: "/bin/docker")

    def _run(self, monkeypatch, fake, tmp_path):
        monkeypatch.setattr(generate.subprocess, "run", fake)
        return generate.main(
            ["--image", "inductiveautomation/ignition:8.3.9"] + _schema_files(tmp_path)
        )

    def test_reads_modules_from_the_image(
        self, monkeypatch, tmp_path, modules_dir, docker_on_path
    ):
        fake = FakeDocker(modules_dir)
        assert self._run(monkeypatch, fake, tmp_path) == 0
        assert [c[1] for c in fake.calls] == ["create", "cp", "rm"]
        assert fake.calls[1][2] == f"abc123:{generate.IMAGE_MODULES_DIR}"
        assert fake.calls[2] == ["docker", "rm", "abc123"]
        schema = json.loads((tmp_path / "out" / "schema.json").read_text())
        assert "Ignition 8.3.9" in schema["properties"]["type"]["$comment"]

    def test_missing_docker_is_reported(self, monkeypatch, tmp_path, capsys):
        monkeypatch.setattr(generate.shutil, "which", lambda name: None)
        fake = FakeDocker()
        assert self._run(monkeypatch, fake, tmp_path) == 1
        assert fake.calls == []
        assert "docker" in capsys.readouterr().err

    def test_failed_create_reports_docker_stderr(
        self, monkeypatch, tmp_path, capsys, docker_on_path
    ):
        fake = FakeDocker(fail="create")
        assert self._run(monkeypatch, fake, tmp_path) == 1
        assert [c[1] for c in fake.calls] == ["create"]
        assert "create broke" in capsys.readouterr().err

    def test_container_is_removed_when_copy_fails(
        self, monkeypatch, tmp_path, capsys, docker_on_path
    ):
        fake = FakeDocker(fail="cp")
        assert self._run(monkeypatch, fake, tmp_path) == 1
        assert fake.calls[-1] == ["docker", "rm", "abc123"]
        assert "cp broke" in capsys.readouterr().err
