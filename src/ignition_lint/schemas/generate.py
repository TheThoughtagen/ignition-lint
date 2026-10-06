"""Regenerate the Perspective component list from Ignition's own module files.

Each Perspective component ships its definition (id and props schema) as a
``*.components.json`` resource inside a module jar. This reads those
definitions and updates two schema files in place:

- ``core-ia-components-schema-robust.json``: the ``type`` enum and pattern
- ``component-props.json``: each component's top-level props

Types and props already listed are kept, so views from older Ignition
versions still pass; ``--prune`` drops anything the given Ignition lacks.

Usage::

    python -m ignition_lint.schemas.generate --image inductiveautomation/ignition:8.3.9
    python -m ignition_lint.schemas.generate --source /usr/local/bin/ignition/user-lib/modules --ignition-version 8.3.9
"""

from __future__ import annotations

import argparse
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

from . import schema_path_for

COMPONENT_PROPS_FILE = schema_path_for("robust").parent / "component-props.json"
IMAGE_MODULES_DIR = "/usr/local/bin/ignition/user-lib/modules"


class GenerateError(Exception):
    """Raised when the component list cannot be generated."""


@dataclass
class Extracted:
    """Components found in a set of Ignition modules."""

    components: dict[str, set[str]] = field(default_factory=dict)
    modules: dict[str, str] = field(default_factory=dict)


def _top_level_props(schema: dict) -> set[str]:
    """Collect a component schema's top-level prop names, including branches."""
    props: set[str] = set()
    if not isinstance(schema, dict):
        return props
    if isinstance(schema.get("properties"), dict):
        props.update(schema["properties"])
    for key in ("allOf", "anyOf", "oneOf"):
        for branch in schema.get(key) or []:
            props |= _top_level_props(branch)
    return props


def _iter_jars(archive: zipfile.ZipFile) -> Iterator[zipfile.ZipFile]:
    for name in archive.namelist():
        if not name.endswith(".jar"):
            continue
        try:
            yield zipfile.ZipFile(io.BytesIO(archive.read(name)))
        except zipfile.BadZipFile:
            continue


def _component_definitions(jar: zipfile.ZipFile, source: Path) -> Iterator[dict]:
    for name in jar.namelist():
        if not name.endswith(".components.json"):
            continue
        where = f"{name} in {source}"
        try:
            data = json.loads(jar.read(name))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise GenerateError(f"Cannot read {where}: {e}") from e
        components = data.get("components", []) if isinstance(data, dict) else None
        if not isinstance(components, list) or not all(
            isinstance(c, dict) for c in components
        ):
            raise GenerateError(
                f"Unexpected {where}: expected an object whose 'components' "
                "is a list of objects"
            )
        yield from components


def _module_name_version(modl: zipfile.ZipFile) -> tuple[str, str] | None:
    try:
        root = ET.fromstring(modl.read("module.xml"))
    except (KeyError, ET.ParseError):
        return None
    module = root.find("module")
    if module is None:
        return None
    return module.findtext("name", ""), module.findtext("version", "")


def _archive_files(sources: Iterable[Path]) -> Iterator[Path]:
    for source in sources:
        if not source.exists():
            raise GenerateError(f"Source not found: {source}")
        if source.is_dir():
            for pattern in ("*.modl", "*.jar"):
                yield from sorted(source.rglob(pattern))
        else:
            yield source


def extract_components(sources: Iterable[Path]) -> Extracted:
    """Read every component definition from .modl or .jar files (or folders)."""
    found = Extracted()
    for path in _archive_files(Path(s) for s in sources):
        try:
            archive = zipfile.ZipFile(path)
        except zipfile.BadZipFile:
            continue
        with archive:
            jars = list(_iter_jars(archive)) if path.suffix == ".modl" else [archive]
            count = 0
            for jar in jars:
                for definition in _component_definitions(jar, path):
                    comp_id = definition.get("id")
                    if not comp_id:
                        continue
                    props = _top_level_props(definition.get("schema", {}))
                    found.components.setdefault(comp_id, set()).update(props)
                    count += 1
            if count and path.suffix == ".modl":
                name_version = _module_name_version(archive)
                if name_version:
                    found.modules[name_version[0]] = name_version[1]
    if not found.components:
        raise GenerateError(
            "No Perspective component definitions (*.components.json) found in "
            "the given source"
        )
    return found


def source_label(ignition_version: str | None, modules: dict[str, str]) -> str:
    """Describe where a component list came from, e.g. for the schema comment."""
    parts = [
        f"{name} {'.'.join(version.split('.')[:3])}"
        for name, version in sorted(modules.items())
    ]
    label = f"Ignition {ignition_version}" if ignition_version else "Ignition"
    return f"{label} ({', '.join(parts)})" if parts else label


def update_type_schema(
    schema: dict, component_ids: Iterable[str], label: str, prune: bool = False
) -> dict:
    """Set the schema's component ``type`` enum and pattern from component ids."""
    type_schema = schema.setdefault("properties", {}).setdefault("type", {})
    types = set(component_ids)
    if not prune:
        types.update(type_schema.get("enum", []))
    enum = sorted(types)
    categories = sorted({t.split(".")[1] for t in enum if t.count(".") >= 2})
    type_schema["$comment"] = (
        f"Generated from {label} by `python -m ignition_lint.schemas.generate`"
        + ("." if prune else ", keeping types listed before.")
        + " Regenerate rather than editing by hand."
    )
    type_schema["pattern"] = f"^ia\\.({'|'.join(categories)})\\."
    type_schema["enum"] = enum
    return schema


def update_component_props(
    existing: dict[str, list[str]],
    components: dict[str, set[str]],
    prune: bool = False,
) -> dict[str, list[str]]:
    """Merge generated top-level props into the per-component props map."""
    merged: dict[str, set[str]] = {}
    if not prune:
        merged = {comp: set(props) for comp, props in existing.items()}
    for comp, props in components.items():
        merged.setdefault(comp, set()).update(props)
    return {comp: sorted(merged[comp]) for comp in sorted(merged)}


def copy_modules_from_image(image: str, dest: Path) -> Path:
    """Copy the bundled modules out of an Ignition Docker image."""
    if not shutil.which("docker"):
        raise GenerateError("--image needs the docker CLI on PATH")
    try:
        container = subprocess.run(
            ["docker", "create", image],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        try:
            subprocess.run(
                ["docker", "cp", f"{container}:{IMAGE_MODULES_DIR}", str(dest)],
                check=True,
                capture_output=True,
                text=True,
            )
        finally:
            subprocess.run(["docker", "rm", container], capture_output=True)
    except subprocess.CalledProcessError as e:
        raise GenerateError(f"docker failed: {e.stderr.strip()}") from e
    return dest


def _image_version(image: str) -> str | None:
    match = re.search(r":(\d+\.\d+\.\d+)", image)
    return match.group(1) if match else None


def _read_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m ignition_lint.schemas.generate",
        description="Regenerate the Perspective component list from Ignition.",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--image",
        help="Ignition Docker image to read modules from, "
        "e.g. inductiveautomation/ignition:8.3.9",
    )
    source.add_argument(
        "--source",
        nargs="+",
        type=Path,
        help="Module files (.modl/.jar) or folders, e.g. an install's "
        "user-lib/modules",
    )
    parser.add_argument(
        "--ignition-version",
        help="Ignition version to record (default: taken from the --image tag)",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="Drop types and props the given Ignition does not ship",
    )
    parser.add_argument("--schema", type=Path, default=schema_path_for("robust"))
    parser.add_argument("--component-props", type=Path, default=COMPONENT_PROPS_FILE)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            if args.image:
                sources = [copy_modules_from_image(args.image, Path(tmp) / "modules")]
                version = args.ignition_version or _image_version(args.image)
            else:
                sources = args.source
                version = args.ignition_version
            found = extract_components(sources)
    except GenerateError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    label = source_label(version, found.modules)
    schema = update_type_schema(
        _read_json(args.schema), found.components, label, prune=args.prune
    )
    _write_json(args.schema, schema)
    props = update_component_props(
        _read_json(args.component_props), found.components, prune=args.prune
    )
    _write_json(args.component_props, props)
    print(
        f"{len(found.components)} components from {label}; "
        f"{len(schema['properties']['type']['enum'])} types listed"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
