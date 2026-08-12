from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

try:
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import SchemaError
except ModuleNotFoundError:
    print(
        "ERROR: missing dependency 'jsonschema'; "
        "run: python -m pip install -r tools/docs/requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(1)


def _format_json_path(parts: Sequence[object]) -> str:
    return ".".join(str(part) for part in parts) or "<root>"


def _read_json(path: Path, label: str) -> tuple[Any | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return None, [f"{label} not found: {path}"]
    except OSError as exc:
        return None, [f"cannot read {label} {path}: {exc}"]
    except json.JSONDecodeError as exc:
        return None, [f"invalid JSON in {label} {path}: line {exc.lineno}, column {exc.colno}"]


def validate_repository(repo_root: Path) -> list[str]:
    root = repo_root.resolve()
    registry, errors = _read_json(root / "docs" / "registry.json", "registry")
    schema, schema_read_errors = _read_json(
        root / "docs" / "registry.schema.json", "registry schema"
    )
    errors.extend(schema_read_errors)
    if errors:
        return sorted(errors)

    try:
        validator = Draft202012Validator(schema)
        validator.check_schema(schema)
    except SchemaError as exc:
        return [f"invalid registry schema: {exc.message}"]

    for error in sorted(
        validator.iter_errors(registry),
        key=lambda item: tuple(str(part) for part in item.absolute_path),
    ):
        location = _format_json_path(list(error.absolute_path))
        errors.append(f"schema error at {location}: {error.message}")

    return sorted(errors)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate the Eidos documentation registry.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="repository root; defaults to the root containing tools/docs/validate.py",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        errors = validate_repository(args.repo_root)
    except Exception as exc:  # defensive CLI boundary; unit-tested helpers stay explicit
        print(f"ERROR: validator execution failed: {exc}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Documentation validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
