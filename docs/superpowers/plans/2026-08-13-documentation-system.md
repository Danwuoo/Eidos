# Agent-First Documentation System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish an English, agent-first documentation governance system with a central JSON registry, JSON Schema, local validator, tested document lifecycles, reusable templates, and a clearly non-normative archive of the original concept note.

**Architecture:** `AGENTS.md` is the operational entry point, while `docs/registry.json` is the sole metadata authority for governed documents. A Python validator combines JSON Schema Draft 2020-12 validation with filesystem, relationship, graph, and supersession checks; Markdown governance and templates explain the human-readable policy without duplicating registry metadata.

**Tech Stack:** Markdown, JSON, JSON Schema Draft 2020-12, Python 3, `jsonschema` 4.x, standard-library `unittest` and `tempfile`.

## Global Constraints

- The system is agent-first: agents MUST discover authority through `AGENTS.md`, `docs/README.md`, and `docs/registry.json`.
- All formal documents MUST be English; the archived concept note MUST preserve its original Traditional Chinese substantive content.
- `docs/registry.json` is the sole authority for governed-document metadata; governed Markdown MUST NOT duplicate metadata in front matter.
- The initial registry contains only `GOV-0001` and `NOTE-0001`.
- The repository MUST state that no research architecture, roadmap, or technology choice has been formally approved.
- The concept note is historical input only and MUST NOT be converted into a formal vision, architecture, roadmap, specification, or decision.
- The validator MUST report errors without rewriting files and MUST return nonzero on failure.
- `jsonschema` is the validator's only third-party runtime dependency.
- Tests MUST use standard-library `unittest` with temporary repository fixtures.
- No CI, research code, dataset, experiment implementation, or formal research specification is added in this plan.
- Planning files under `docs/superpowers/` are non-normative and excluded from the registry.

---

## File Map

| Path | Responsibility |
| --- | --- |
| `AGENTS.md` | Concise mandatory workflow for agents operating in Eidos. |
| `README.md` | Project status, navigation, and explicit absence of an approved research architecture. |
| `docs/README.md` | Documentation authority model, type/lifecycle index, registry instructions, and local commands. |
| `docs/registry.json` | Sole machine-readable metadata authority for governed documents. |
| `docs/registry.schema.json` | Draft 2020-12 structural and conditional validation contract. |
| `docs/governance/GOV-0001-documentation-system.md` | Binding documentation lifecycle, authority, synchronization, and conflict policy. |
| `docs/notes/README.md` | Non-normative notes policy. |
| `docs/notes/early-arc-specialized-reasoning-concept.zh-TW.md` | Original concept note with an English archival warning. |
| `docs/templates/rfc.md` | RFC authoring structure and non-normative notice. |
| `docs/templates/adr.md` | ADR authoring structure. |
| `docs/templates/specification.md` | Normative specification authoring structure. |
| `docs/templates/experiment.md` | Experiment-evidence authoring structure. |
| `tools/docs/requirements.txt` | Compatible `jsonschema` dependency constraint. |
| `tools/docs/validate.py` | CLI and reusable validation functions. |
| `tests/docs/test_validate.py` | Temporary-repository unit tests for schema, filesystem, relationship, and graph checks. |
| `tests/docs/test_repository_contract.py` | Tests for the live documentation corpus, required notices, headings, and agent entry point. |

---

### Task 1: Bootstrap the Registry Schema and Validator CLI

**Files:**

- Create: `tools/docs/requirements.txt`
- Create: `docs/registry.schema.json`
- Create: `tools/docs/validate.py`
- Create: `tests/docs/test_validate.py`

**Interfaces:**

- Consumes: a repository root containing `docs/registry.json` and `docs/registry.schema.json`.
- Produces: `validate_repository(repo_root: pathlib.Path) -> list[str]` and `main(argv: Sequence[str] | None = None) -> int`.
- CLI contract: `python tools/docs/validate.py [--repo-root PATH]` prints `Documentation validation passed.` on success, otherwise prints one `ERROR: ...` line per violation and exits `1`.

- [ ] **Step 1: Write the initial failing tests**

Create `tests/docs/test_validate.py` with fixture helpers and the first schema-level cases:

```python
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.docs.validate import validate_repository


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_SOURCE = PROJECT_ROOT / "docs" / "registry.schema.json"


VALID_ENTRY = {
    "id": "GOV-0001",
    "title": "Documentation system",
    "type": "governance",
    "status": "active",
    "path": "docs/governance/GOV-0001-documentation-system.md",
    "language": "en",
    "summary": "Defines the documentation system.",
    "depends_on": [],
    "supersedes": [],
    "informed_by": [],
}


class ValidatorTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name)
        (self.repo / "docs" / "governance").mkdir(parents=True)
        shutil.copyfile(SCHEMA_SOURCE, self.repo / "docs" / "registry.schema.json")

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_registry(self, documents):
        payload = {"schema_version": 1, "documents": documents}
        (self.repo / "docs" / "registry.json").write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )

    def write_document(self, relative_path):
        path = self.repo / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Test document\n", encoding="utf-8")

    def test_valid_registry_has_no_errors(self):
        self.write_registry([VALID_ENTRY])
        self.write_document(VALID_ENTRY["path"])
        self.assertEqual([], validate_repository(self.repo))

    def test_schema_error_is_actionable(self):
        invalid = dict(VALID_ENTRY, status="draft")
        self.write_registry([invalid])
        self.write_document(invalid["path"])
        errors = validate_repository(self.repo)
        self.assertTrue(any("schema" in error and "status" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and verify the validator is missing**

Run:

```powershell
python -m unittest tests.docs.test_validate -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'tools.docs.validate'`.

- [ ] **Step 3: Declare the validator dependency**

Create `tools/docs/requirements.txt`:

```text
jsonschema>=4.23,<5
```

Install it:

```powershell
python -m pip install -r tools/docs/requirements.txt
```

Expected: installation succeeds and `python -c "import jsonschema; print(jsonschema.__version__)"` prints a 4.x version. A deprecation warning about `__version__` is acceptable for this one check.

- [ ] **Step 4: Add the complete Draft 2020-12 registry schema**

Create `docs/registry.schema.json` with:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://eidos.local/schemas/document-registry-v1.json",
  "title": "Eidos document registry",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version", "documents"],
  "properties": {
    "schema_version": {"const": 1},
    "documents": {
      "type": "array",
      "items": {"$ref": "#/$defs/document"}
    }
  },
  "$defs": {
    "relation_list": {
      "type": "array",
      "uniqueItems": true,
      "items": {"type": "string", "pattern": "^(GOV|RFC|ADR|SPEC|EXP|NOTE)-[0-9]{4}$"}
    },
    "document": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "id", "title", "type", "status", "path", "language", "summary",
        "depends_on", "supersedes", "informed_by"
      ],
      "properties": {
        "id": {"type": "string"},
        "title": {"type": "string", "minLength": 1},
        "type": {
          "enum": ["governance", "rfc", "adr", "specification", "experiment", "note"]
        },
        "status": {"type": "string"},
        "path": {
          "type": "string",
          "pattern": "^docs/[A-Za-z0-9._/-]+\\.md$"
        },
        "language": {
          "type": "string",
          "pattern": "^[a-z]{2}(?:-[A-Z]{2})?$"
        },
        "summary": {"type": "string", "minLength": 1},
        "depends_on": {"$ref": "#/$defs/relation_list"},
        "supersedes": {"$ref": "#/$defs/relation_list"},
        "informed_by": {"$ref": "#/$defs/relation_list"}
      },
      "allOf": [
        {
          "if": {"properties": {"type": {"const": "governance"}}, "required": ["type"]},
          "then": {
            "properties": {
              "id": {"pattern": "^GOV-[0-9]{4}$"},
              "status": {"enum": ["active", "superseded", "archived"]},
              "path": {"pattern": "^docs/governance/GOV-[0-9]{4}-[a-z0-9-]+\\.md$"},
              "language": {"const": "en"}
            }
          }
        },
        {
          "if": {"properties": {"type": {"const": "rfc"}}, "required": ["type"]},
          "then": {
            "properties": {
              "id": {"pattern": "^RFC-[0-9]{4}$"},
              "status": {"enum": ["draft", "in_review", "accepted", "rejected", "withdrawn"]},
              "path": {"pattern": "^docs/rfcs/RFC-[0-9]{4}-[a-z0-9-]+\\.md$"},
              "language": {"const": "en"}
            }
          }
        },
        {
          "if": {"properties": {"type": {"const": "adr"}}, "required": ["type"]},
          "then": {
            "properties": {
              "id": {"pattern": "^ADR-[0-9]{4}$"},
              "status": {"enum": ["proposed", "accepted", "deprecated", "superseded"]},
              "path": {"pattern": "^docs/decisions/ADR-[0-9]{4}-[a-z0-9-]+\\.md$"},
              "language": {"const": "en"}
            }
          }
        },
        {
          "if": {"properties": {"type": {"const": "specification"}}, "required": ["type"]},
          "then": {
            "properties": {
              "id": {"pattern": "^SPEC-[0-9]{4}$"},
              "status": {"enum": ["draft", "active", "deprecated", "superseded"]},
              "path": {"pattern": "^docs/specifications/SPEC-[0-9]{4}-[a-z0-9-]+\\.md$"},
              "language": {"const": "en"}
            }
          }
        },
        {
          "if": {"properties": {"type": {"const": "experiment"}}, "required": ["type"]},
          "then": {
            "properties": {
              "id": {"pattern": "^EXP-[0-9]{4}$"},
              "status": {"enum": ["planned", "running", "completed", "abandoned"]},
              "path": {"pattern": "^docs/experiments/EXP-[0-9]{4}-[a-z0-9-]+\\.md$"},
              "language": {"const": "en"}
            }
          }
        },
        {
          "if": {"properties": {"type": {"const": "note"}}, "required": ["type"]},
          "then": {
            "properties": {
              "id": {"pattern": "^NOTE-[0-9]{4}$"},
              "status": {"const": "archived"},
              "path": {"pattern": "^docs/notes/[a-z0-9.-]+\\.md$"}
            }
          }
        }
      ]
    }
  }
}
```

- [ ] **Step 5: Implement JSON loading, schema validation, and the CLI**

Create `tools/docs/validate.py`:

```python
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
```

- [ ] **Step 6: Run the schema-level tests**

Run:

```powershell
python -m unittest tests.docs.test_validate -v
```

Expected: 2 tests pass.

- [ ] **Step 7: Commit the bootstrap**

```powershell
git add docs/registry.schema.json tools/docs/requirements.txt tools/docs/validate.py tests/docs/test_validate.py
git commit -m "feat(docs): add registry schema validation"
```

---

### Task 2: Validate Identity, Paths, Ordering, and Filesystem Coverage

**Files:**

- Modify: `tools/docs/validate.py`
- Modify: `tests/docs/test_validate.py`

**Interfaces:**

- Consumes: schema-valid document entries.
- Produces: deterministic errors for duplicate IDs/paths, non-normalized paths, missing registered files, unregistered governed files, and unsorted IDs.
- Governed directories: `docs/governance`, `docs/rfcs`, `docs/decisions`, `docs/specifications`, `docs/experiments`, and `docs/notes`.

- [ ] **Step 1: Add failing identity and filesystem tests**

Add these tests to `ValidatorTestCase`:

```python
    def test_duplicate_id_and_path_are_reported(self):
        duplicate = dict(VALID_ENTRY)
        self.write_registry([VALID_ENTRY, duplicate])
        self.write_document(VALID_ENTRY["path"])
        errors = validate_repository(self.repo)
        self.assertTrue(any("duplicate document ID GOV-0001" in error for error in errors))
        self.assertTrue(any("duplicate document path" in error for error in errors))

    def test_missing_registered_file_is_reported(self):
        self.write_registry([VALID_ENTRY])
        errors = validate_repository(self.repo)
        self.assertTrue(any("registered document does not exist" in error for error in errors))

    def test_unregistered_governed_markdown_is_reported(self):
        self.write_registry([VALID_ENTRY])
        self.write_document(VALID_ENTRY["path"])
        self.write_document("docs/notes/orphan.md")
        errors = validate_repository(self.repo)
        self.assertTrue(any("unregistered governed document" in error for error in errors))

    def test_non_deterministic_document_order_is_reported(self):
        note = {
            "id": "NOTE-0001",
            "title": "Note",
            "type": "note",
            "status": "archived",
            "path": "docs/notes/note.md",
            "language": "zh-TW",
            "summary": "Historical note.",
            "depends_on": [],
            "supersedes": [],
            "informed_by": [],
        }
        self.write_registry([note, VALID_ENTRY])
        self.write_document(note["path"])
        self.write_document(VALID_ENTRY["path"])
        errors = validate_repository(self.repo)
        self.assertTrue(any("documents must be sorted by id" in error for error in errors))

    def test_path_traversal_is_rejected(self):
        invalid = dict(VALID_ENTRY, path="docs/governance/../governance/GOV-0001-documentation-system.md")
        self.write_registry([invalid])
        errors = validate_repository(self.repo)
        self.assertTrue(any("schema error" in error or "normalized POSIX path" in error for error in errors))

    def test_invalid_status_prefix_path_and_language_are_schema_errors(self):
        cases = [
            dict(VALID_ENTRY, status="draft"),
            dict(VALID_ENTRY, id="SPEC-0001"),
            dict(VALID_ENTRY, path="docs/specifications/SPEC-0001-wrong.md"),
            dict(VALID_ENTRY, language="zh-TW"),
        ]
        for entry in cases:
            with self.subTest(entry=entry):
                self.write_registry([entry])
                errors = validate_repository(self.repo)
                self.assertTrue(any("schema error" in error for error in errors))
```

- [ ] **Step 2: Run the new tests and verify they fail**

Run:

```powershell
python -m unittest tests.docs.test_validate -v
```

Expected: the schema-only tests pass; the new identity, coverage, and ordering tests fail because those checks do not exist.

- [ ] **Step 3: Implement identity, normalization, and coverage helpers**

Add these imports and constants to `tools/docs/validate.py`:

```python
import os
from pathlib import PurePosixPath


GOVERNED_DIRECTORIES = (
    "docs/governance",
    "docs/rfcs",
    "docs/decisions",
    "docs/specifications",
    "docs/experiments",
    "docs/notes",
)
```

Add these helpers:

```python
def _duplicates(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return sorted(repeated)


def _check_identity_and_order(documents: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    ids = [document["id"] for document in documents]
    paths = [document["path"] for document in documents]
    for document_id in _duplicates(ids):
        errors.append(f"duplicate document ID {document_id}")
    for path in _duplicates(paths):
        errors.append(f"duplicate document path {path}")
    if ids != sorted(ids):
        errors.append("registry documents must be sorted by id")
    return errors


def _is_within(root: Path, candidate: Path) -> bool:
    try:
        return os.path.commonpath([str(root), str(candidate)]) == str(root)
    except ValueError:
        return False


def _check_document_paths(repo_root: Path, documents: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    registered_paths = {document["path"] for document in documents}

    for document in documents:
        raw_path = document["path"]
        posix_path = PurePosixPath(raw_path)
        if (
            "\\" in raw_path
            or posix_path.is_absolute()
            or any(part in {".", ".."} for part in posix_path.parts)
            or str(posix_path) != raw_path
        ):
            errors.append(f"{document['id']} path is not a normalized POSIX path: {raw_path}")
            continue

        resolved = (repo_root / Path(*posix_path.parts)).resolve()
        if not _is_within(repo_root, resolved):
            errors.append(f"{document['id']} path escapes repository root: {raw_path}")
        elif not resolved.is_file():
            errors.append(f"registered document does not exist: {raw_path}")

    governed_paths: set[str] = set()
    for directory in GOVERNED_DIRECTORIES:
        base = repo_root / directory
        if base.is_dir():
            governed_paths.update(
                path.relative_to(repo_root).as_posix()
                for path in base.rglob("*.md")
                if path.name != "README.md"
            )

    for path in sorted(governed_paths - registered_paths):
        errors.append(f"unregistered governed document: {path}")
    for path in sorted(registered_paths - governed_paths):
        if (repo_root / Path(*PurePosixPath(path).parts)).is_file():
            errors.append(f"registered path is outside governed document set: {path}")
    return errors
```

After schema validation, return early if schema errors exist because later checks assume the required fields are present. Otherwise extend `validate_repository` with:

```python
    if errors:
        return sorted(errors)

    documents = registry["documents"]
    errors.extend(_check_identity_and_order(documents))
    errors.extend(_check_document_paths(root, documents))
    return sorted(errors)
```

- [ ] **Step 4: Run the validator tests**

Run:

```powershell
python -m unittest tests.docs.test_validate -v
```

Expected: all identity, path, order, and coverage tests pass.

- [ ] **Step 5: Commit filesystem validation**

```powershell
git add tools/docs/validate.py tests/docs/test_validate.py
git commit -m "feat(docs): validate registry paths and coverage"
```

---

### Task 3: Validate Relationships, Graphs, and Supersession

**Files:**

- Modify: `tools/docs/validate.py`
- Modify: `tests/docs/test_validate.py`

**Interfaces:**

- Consumes: schema-valid entries with unique IDs and paths.
- Produces: deterministic errors for unsorted relation arrays, missing/self/invalid targets, forbidden supersession, dependency cycles, supersession cycles, and inconsistent superseded state.
- Dependency target contract: an active governance document, accepted ADR, active specification, or same-type work-in-progress document.
- Work-in-progress statuses: `draft`, `in_review`, `proposed`, `planned`, and `running`.

- [ ] **Step 1: Refactor the fixture to support multiple document types**

Add this helper to `ValidatorTestCase`:

```python
    def entry(self, document_id, document_type, status, path, **relations):
        return {
            "id": document_id,
            "title": document_id,
            "type": document_type,
            "status": status,
            "path": path,
            "language": "en",
            "summary": f"Fixture for {document_id}.",
            "depends_on": relations.get("depends_on", []),
            "supersedes": relations.get("supersedes", []),
            "informed_by": relations.get("informed_by", []),
        }

    def write_documents(self, documents):
        self.write_registry(sorted(documents, key=lambda item: item["id"]))
        for document in documents:
            self.write_document(document["path"])
```

- [ ] **Step 2: Add failing reference and ordering tests**

Add:

```python
    def test_broken_reference_is_reported(self):
        source = dict(VALID_ENTRY, informed_by=["NOTE-9999"])
        self.write_documents([source])
        errors = validate_repository(self.repo)
        self.assertTrue(any("unknown target NOTE-9999" in error for error in errors))

    def test_self_reference_is_reported(self):
        source = dict(VALID_ENTRY, informed_by=["GOV-0001"])
        self.write_documents([source])
        errors = validate_repository(self.repo)
        self.assertTrue(any("must not reference itself" in error for error in errors))

    def test_duplicate_relation_is_schema_error(self):
        source = dict(VALID_ENTRY, informed_by=["NOTE-0001", "NOTE-0001"])
        self.write_registry([source])
        self.write_document(source["path"])
        errors = validate_repository(self.repo)
        self.assertTrue(any("schema error" in error and "non-unique" in error for error in errors))

    def test_relation_arrays_must_be_sorted(self):
        note1 = self.entry("NOTE-0001", "note", "archived", "docs/notes/one.md")
        note2 = self.entry("NOTE-0002", "note", "archived", "docs/notes/two.md")
        source = dict(VALID_ENTRY, informed_by=["NOTE-0002", "NOTE-0001"])
        self.write_documents([source, note1, note2])
        errors = validate_repository(self.repo)
        self.assertTrue(any("GOV-0001 informed_by must be sorted" in error for error in errors))

    def test_invalid_dependency_target_is_reported(self):
        rejected = self.entry(
            "RFC-0001", "rfc", "rejected", "docs/rfcs/RFC-0001-rejected.md"
        )
        source = dict(VALID_ENTRY, depends_on=["RFC-0001"])
        self.write_documents([source, rejected])
        errors = validate_repository(self.repo)
        self.assertTrue(any("invalid depends_on target RFC-0001" in error for error in errors))
```

- [ ] **Step 3: Add failing graph and supersession tests**

Add:

```python
    def test_dependency_cycle_is_reported(self):
        first = self.entry(
            "SPEC-0001", "specification", "draft",
            "docs/specifications/SPEC-0001-first.md", depends_on=["SPEC-0002"]
        )
        second = self.entry(
            "SPEC-0002", "specification", "draft",
            "docs/specifications/SPEC-0002-second.md", depends_on=["SPEC-0001"]
        )
        self.write_documents([first, second])
        errors = validate_repository(self.repo)
        self.assertTrue(any("depends_on cycle" in error for error in errors))

    def test_supersession_cycle_is_reported(self):
        first = self.entry(
            "ADR-0001", "adr", "superseded", "docs/decisions/ADR-0001-first.md",
            supersedes=["ADR-0002"]
        )
        second = self.entry(
            "ADR-0002", "adr", "superseded", "docs/decisions/ADR-0002-second.md",
            supersedes=["ADR-0001"]
        )
        self.write_documents([first, second])
        errors = validate_repository(self.repo)
        self.assertTrue(any("supersedes cycle" in error for error in errors))

    def test_supersession_requires_same_type_and_superseded_target(self):
        old = self.entry(
            "ADR-0001", "adr", "accepted", "docs/decisions/ADR-0001-old.md"
        )
        replacement = self.entry(
            "SPEC-0001", "specification", "active",
            "docs/specifications/SPEC-0001-new.md", supersedes=["ADR-0001"]
        )
        self.write_documents([old, replacement])
        errors = validate_repository(self.repo)
        self.assertTrue(any("may supersede only the same type" in error for error in errors))
        self.assertTrue(any("must have status superseded" in error for error in errors))

    def test_superseded_document_requires_replacement(self):
        old = self.entry(
            "GOV-0001", "governance", "superseded",
            "docs/governance/GOV-0001-old.md"
        )
        self.write_documents([old])
        errors = validate_repository(self.repo)
        self.assertTrue(any("has no replacement" in error for error in errors))

    def test_experiment_cannot_supersede(self):
        old = self.entry(
            "EXP-0001", "experiment", "completed", "docs/experiments/EXP-0001-old.md"
        )
        new = self.entry(
            "EXP-0002", "experiment", "running", "docs/experiments/EXP-0002-new.md",
            supersedes=["EXP-0001"]
        )
        self.write_documents([old, new])
        errors = validate_repository(self.repo)
        self.assertTrue(any("experiment documents may not supersede" in error for error in errors))
```

- [ ] **Step 4: Run the relationship tests and verify failure**

Run:

```powershell
python -m unittest tests.docs.test_validate -v
```

Expected: the new relationship, graph, and supersession tests fail; earlier tests remain green.

- [ ] **Step 5: Implement relation checks and deterministic cycle detection**

Add to `tools/docs/validate.py`:

```python
RELATION_FIELDS = ("depends_on", "supersedes", "informed_by")
SUPERSEDING_TYPES = {"governance", "adr", "specification"}
WORK_IN_PROGRESS_STATUSES = {"draft", "in_review", "proposed", "planned", "running"}


def _dependency_target_is_allowed(source: dict[str, Any], target: dict[str, Any]) -> bool:
    binding_target = (
        (target["type"] == "governance" and target["status"] == "active")
        or (target["type"] == "adr" and target["status"] == "accepted")
        or (target["type"] == "specification" and target["status"] == "active")
    )
    same_type_work = (
        source["type"] == target["type"]
        and target["status"] in WORK_IN_PROGRESS_STATUSES
    )
    return binding_target or same_type_work


def _find_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    visited: set[str] = set()
    active: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        if node in active:
            start = stack.index(node)
            return stack[start:] + [node]
        if node in visited:
            return None
        visited.add(node)
        active.add(node)
        stack.append(node)
        for target in sorted(graph.get(node, [])):
            cycle = visit(target)
            if cycle:
                return cycle
        stack.pop()
        active.remove(node)
        return None

    for node in sorted(graph):
        cycle = visit(node)
        if cycle:
            return cycle
    return None


def _check_relations(documents: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    by_id = {document["id"]: document for document in documents}

    for source in documents:
        for field in RELATION_FIELDS:
            targets = source[field]
            if targets != sorted(targets):
                errors.append(f"{source['id']} {field} must be sorted")
            for target_id in targets:
                if target_id == source["id"]:
                    errors.append(f"{source['id']} {field} must not reference itself")
                    continue
                target = by_id.get(target_id)
                if target is None:
                    errors.append(f"{source['id']} {field} has unknown target {target_id}")
                    continue
                if field == "depends_on" and not _dependency_target_is_allowed(source, target):
                    errors.append(f"{source['id']} has invalid depends_on target {target_id}")
                if field == "supersedes":
                    if source["type"] not in SUPERSEDING_TYPES:
                        errors.append(f"{source['type']} documents may not supersede other documents")
                    if source["type"] != target["type"]:
                        errors.append(f"{source['id']} may supersede only the same type; got {target_id}")
                    if target["status"] != "superseded":
                        errors.append(f"superseded target {target_id} must have status superseded")

    for field in ("depends_on", "supersedes"):
        graph = {
            document["id"]: [target for target in document[field] if target in by_id]
            for document in documents
        }
        cycle = _find_cycle(graph)
        if cycle:
            errors.append(f"{field} cycle: {' -> '.join(cycle)}")

    replacements = {
        target
        for document in documents
        for target in document["supersedes"]
        if target in by_id and document["type"] == by_id[target]["type"]
    }
    for document in documents:
        if document["status"] == "superseded" and document["id"] not in replacements:
            errors.append(f"superseded document {document['id']} has no replacement")

    return errors
```

Extend `validate_repository` after the filesystem checks:

```python
    errors.extend(_check_relations(documents))
```

- [ ] **Step 6: Run the complete validator unit suite**

Run:

```powershell
python -m unittest tests.docs.test_validate -v
```

Expected: all tests pass, including broken reference, duplicate/self relation, dependency cycle, supersession cycle, and supersession consistency cases.

- [ ] **Step 7: Commit relationship validation**

```powershell
git add tools/docs/validate.py tests/docs/test_validate.py
git commit -m "feat(docs): validate document relationships"
```

---

### Task 4: Establish the Governed Documentation Corpus

**Files:**

- Create: `README.md`
- Create: `docs/README.md`
- Create: `docs/registry.json`
- Create: `docs/governance/GOV-0001-documentation-system.md`
- Create: `docs/notes/README.md`
- Move: `docs/從通用 LLM 到 ARC 專用推理架構.md` to `docs/notes/early-arc-specialized-reasoning-concept.zh-TW.md`
- Create: `tests/docs/test_repository_contract.py`

**Interfaces:**

- Consumes: schema and validator from Tasks 1-3; the untracked original Chinese concept note.
- Produces: a valid live registry containing exactly `GOV-0001` and `NOTE-0001`, plus the binding governance document and non-normative archive.
- Preservation contract: the original concept paragraphs remain byte-for-byte present after the newly added archival notice, allowing only newline normalization caused by the move/edit tool.

- [ ] **Step 1: Add failing live-repository contract tests**

Create `tests/docs/test_repository_contract.py`:

```python
import json
import unittest
from pathlib import Path

from tools.docs.validate import validate_repository


ROOT = Path(__file__).resolve().parents[2]


class RepositoryContractTests(unittest.TestCase):
    def test_live_repository_documentation_is_valid(self):
        self.assertEqual([], validate_repository(ROOT))

    def test_initial_registry_contains_only_governance_and_note(self):
        registry = json.loads((ROOT / "docs" / "registry.json").read_text(encoding="utf-8"))
        self.assertEqual(["GOV-0001", "NOTE-0001"], [item["id"] for item in registry["documents"]])

    def test_readmes_disclaim_an_approved_research_architecture(self):
        for path in (ROOT / "README.md", ROOT / "docs" / "README.md"):
            text = path.read_text(encoding="utf-8")
            self.assertIn("no formally approved research architecture", text.lower())

    def test_archived_note_has_non_normative_warning(self):
        path = ROOT / "docs" / "notes" / "early-arc-specialized-reasoning-concept.zh-TW.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("Archived Non-Normative Concept Note", text)
        self.assertIn("must not be treated as a requirement", text)
        self.assertIn("ARC 的高分方法", text)

    def test_governance_defines_conflict_and_synchronization_rules(self):
        text = (
            ROOT / "docs" / "governance" / "GOV-0001-documentation-system.md"
        ).read_text(encoding="utf-8")
        self.assertIn("## Authority", text)
        self.assertIn("## Registry Synchronization", text)
        self.assertIn("## Authority Conflicts", text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the contract tests and verify missing-corpus failures**

Run:

```powershell
python -m unittest tests.docs.test_repository_contract -v
```

Expected: FAIL because the live registry, READMEs, governance file, and archived note do not yet exist.

- [ ] **Step 3: Verify and move the exact concept-note paths**

Run these read-only checks before the move:

```powershell
$source = (Resolve-Path -LiteralPath 'docs\從通用 LLM 到 ARC 專用推理架構.md').Path
$targetDirectory = Join-Path (Resolve-Path -LiteralPath 'docs').Path 'notes'
Write-Output $source
Write-Output $targetDirectory
```

Expected: both resolved paths are inside the Eidos workspace. Then create the directory and move the single file:

```powershell
New-Item -ItemType Directory -Force -Path 'docs\notes' | Out-Null
Move-Item -LiteralPath 'docs\從通用 LLM 到 ARC 專用推理架構.md' -Destination 'docs\notes\early-arc-specialized-reasoning-concept.zh-TW.md'
```

- [ ] **Step 4: Prepend the exact archival warning**

Use `apply_patch` to insert this text before the first Chinese paragraph without rewriting the remaining content:

```markdown
# Archived Non-Normative Concept Note

> **Status:** Historical input only. This document is not an approved vision, roadmap, architecture, specification, or decision. It must not be treated as a requirement. Technology references and research claims require independent verification. Agents may use this note only as background or provenance; adopting any idea requires the formal RFC, ADR, specification, or experiment process.

---

```

- [ ] **Step 5: Create the initial registry**

Create `docs/registry.json`:

```json
{
  "schema_version": 1,
  "documents": [
    {
      "id": "GOV-0001",
      "title": "Documentation System Governance",
      "type": "governance",
      "status": "active",
      "path": "docs/governance/GOV-0001-documentation-system.md",
      "language": "en",
      "summary": "Defines document authority, lifecycle, synchronization, and conflict handling.",
      "depends_on": [],
      "supersedes": [],
      "informed_by": []
    },
    {
      "id": "NOTE-0001",
      "title": "Early ARC-Specialized Reasoning Concept",
      "type": "note",
      "status": "archived",
      "path": "docs/notes/early-arc-specialized-reasoning-concept.zh-TW.md",
      "language": "zh-TW",
      "summary": "Preserves the original pre-governance concept for historical context only.",
      "depends_on": [],
      "supersedes": [],
      "informed_by": []
    }
  ]
}
```

- [ ] **Step 6: Create the binding governance document**

Create `docs/governance/GOV-0001-documentation-system.md` with the following requirements, written as complete prose under these exact headings:

```markdown
# GOV-0001: Documentation System Governance

## Purpose

This document governs how Eidos creates, discovers, reviews, accepts, replaces, and validates project documentation. It governs documentation behavior only and does not approve a research architecture.

## Authority

Agents follow `AGENTS.md` for operational workflow. Active governance documents govern documentation; active specifications define required behavior; accepted ADRs record binding decisions. RFCs are proposals, experiments are evidence, notes are background, and `docs/superpowers/` contains non-normative workflow artifacts. An accepted RFC becomes binding only when its outcome is represented by an accepted ADR or active specification.

## Document Classification

Every governed document MUST be classified before creation as governance, RFC, ADR, specification, experiment, or note. Authors MUST use the matching template when one exists. Formal documents MUST be English. Notes MAY preserve their source language and MUST remain archived and non-normative.

## Registry Synchronization

`docs/registry.json` is the sole metadata authority. A governed Markdown document and its registry entry MUST be created, modified, and reviewed in the same change. Published IDs and paths MUST NOT change. Metadata MUST NOT be duplicated in Markdown front matter. Registry entries and relation arrays MUST remain lexicographically sorted.

## Lifecycle Policy

Governance transitions from active to superseded or archived. RFCs transition from draft to in_review, then to accepted, rejected, or withdrawn. ADRs transition from proposed to accepted, then to deprecated or superseded. Specifications transition from draft to active, then to deprecated or superseded. Experiments transition from planned to running, then to completed or abandoned. Notes remain archived. Changes outside these forward transitions require a new document or a governance amendment.

## Relationships and Supersession

Every relationship MUST target a registered ID and MUST NOT create a self-reference or cycle. `informed_by` records provenance without transferring authority. Governance documents, ADRs, and specifications MAY supersede only same-type documents. A replacement MUST list each replaced ID, and every replaced document MUST have status `superseded`.

## Authority Conflicts

When active authorities disagree, the conflict is a repository defect. An agent MUST identify the conflicting IDs, stop work that depends on the disputed requirement, and request an explicit ADR, specification, or governance change. It MUST NOT silently select one authority.

## Validation

Agents MUST run `python tools/docs/validate.py` and `python -m unittest discover -s tests/docs -v` before claiming completion for changes to governed documentation or documentation tooling. Validation failures MUST be corrected; the validator MUST NOT rewrite project files automatically.

## Amendments

Material changes to this system require a new governance document that supersedes this one. Non-binding explanatory corrections may update this document only when they do not change an obligation, lifecycle, authority rule, or validation contract.
```

- [ ] **Step 7: Create project and documentation indexes**

Create `README.md` with:

```markdown
# Eidos

Eidos is an early-stage research repository. It currently has no formally approved research architecture, roadmap, or technology selection.

Repository work begins with [AGENTS.md](AGENTS.md). The documentation authority model and registry are described in [docs/README.md](docs/README.md). Early ideas are preserved as non-normative notes and must pass through the formal documentation process before adoption.
```

Create `docs/README.md`:

````markdown
# Eidos Documentation

## Current Status

Eidos has no formally approved research architecture. The registry currently contains documentation governance and one archived concept note only.

This index explains how to find authority; it is not itself a governed or binding document.

## Authority Order

1. `AGENTS.md` defines mandatory agent workflow.
2. Active governance documents govern documentation behavior.
3. Active specifications define required current system behavior.
4. Accepted ADRs record binding decisions and rationale.
5. RFCs are non-normative proposals, including accepted RFCs whose outcomes have not yet been represented by an ADR or specification.
6. Experiments provide evidence, not requirements.
7. Notes and `docs/superpowers/` artifacts are non-normative background or workflow material.

Conflicting active authorities are a repository defect. Report the conflicting IDs and stop affected work rather than silently choosing one.

## Document Types

| Type | Prefix | Location | Purpose |
| --- | --- | --- | --- |
| Governance | `GOV` | `docs/governance/` | Binding documentation-system rules. |
| RFC | `RFC` | `docs/rfcs/` | Proposals for review. |
| ADR | `ADR` | `docs/decisions/` | Binding decisions and rationale. |
| Specification | `SPEC` | `docs/specifications/` | Normative system behavior. |
| Experiment | `EXP` | `docs/experiments/` | Hypotheses, methods, evidence, and interpretation. |
| Note | `NOTE` | `docs/notes/` | Archived non-normative context. |

Directories for RFCs, ADRs, specifications, and experiments are created only when their first document is introduced. Templates live in `docs/templates/` and are not registered documents.

## Registry Workflow

`docs/registry.json` is the sole source of document metadata. Before adding a document:

1. Classify it and copy the matching template.
2. Allocate the next unused four-digit ID for that type.
3. Create the Markdown file at the type's governed path.
4. Add its metadata to `docs/registry.json` in ID order.
5. Keep relation arrays sorted and ensure every target ID exists.
6. Submit the document and registry update in the same change.

Do not add YAML front matter to governed Markdown. Published IDs and paths are immutable.

## Lifecycle Summary

- Governance: `active` to `superseded` or `archived`.
- RFC: `draft` to `in_review`, then `accepted`, `rejected`, or `withdrawn`.
- ADR: `proposed` to `accepted`, then `deprecated` or `superseded`.
- Specification: `draft` to `active`, then `deprecated` or `superseded`.
- Experiment: `planned` to `running`, then `completed` or `abandoned`.
- Note: `archived` only.

See `GOV-0001` through the registry for binding lifecycle and conflict rules.

## Local Validation

From the repository root:

```powershell
python -m pip install -r tools/docs/requirements.txt
python tools/docs/validate.py
python -m unittest discover -s tests/docs -v
```
````

Create `docs/notes/README.md` with:

```markdown
# Notes

Files in this directory are archived, non-normative background material. They may preserve early reasoning, external observations, or source-language text, but they do not define requirements or decisions. Any idea adopted by Eidos must pass through the applicable RFC, ADR, specification, or experiment process.
```

- [ ] **Step 8: Run live validation and contract tests**

Run:

```powershell
python tools/docs/validate.py
python -m unittest tests.docs.test_repository_contract -v
python -m unittest discover -s tests/docs -v
```

Expected: validator prints `Documentation validation passed.` and all tests pass.

- [ ] **Step 9: Confirm the scope boundary**

Run:

```powershell
rg -n -i "approved (research )?(architecture|roadmap)|selected (tokenizer|backbone)|must use (RWKV|Mamba|DeltaNet|Titans|MIRAS)" README.md docs
```

Expected: no statement approves a research architecture or technology; matches may occur only in explicit disclaimers, the archived note, or the non-normative design/plan.

- [ ] **Step 10: Commit the governed corpus**

```powershell
git add README.md docs/README.md docs/registry.json docs/governance/GOV-0001-documentation-system.md docs/notes tests/docs/test_repository_contract.py
git commit -m "docs: establish documentation governance corpus"
```

---

### Task 5: Add the Agent Contract and Authoring Templates

**Files:**

- Create: `AGENTS.md`
- Create: `docs/templates/rfc.md`
- Create: `docs/templates/adr.md`
- Create: `docs/templates/specification.md`
- Create: `docs/templates/experiment.md`
- Modify: `tests/docs/test_repository_contract.py`

**Interfaces:**

- Consumes: authority and lifecycle rules from `GOV-0001` and metadata from `docs/registry.json`.
- Produces: the mandatory agent discovery/change/validation workflow and four copy-ready Markdown templates.
- Templates are excluded from the registry and contain no YAML front matter.

- [ ] **Step 1: Add failing agent and template contract tests**

Add to `RepositoryContractTests`:

```python
    def test_agents_file_defines_required_workflow(self):
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for required in (
            "docs/README.md",
            "docs/registry.json",
            "Classify",
            "same change",
            "python tools/docs/validate.py",
            "Authority Conflicts",
        ):
            self.assertIn(required, text)

    def test_templates_have_required_sections(self):
        required = {
            "rfc.md": (
                "## Problem", "## Context", "## Proposal", "## Alternatives Considered",
                "## Risks and Mitigations", "## Unresolved Questions",
                "## Acceptance Criteria", "## Expected Binding Outputs",
            ),
            "adr.md": (
                "## Context", "## Decision", "## Consequences",
                "## Rejected Alternatives", "## Supersession", "## Verification Impact",
            ),
            "specification.md": (
                "## Scope", "## Definitions", "## Normative Requirements",
                "## Interfaces", "## Invariants", "## Failure Behavior",
                "## Verification", "## Dependencies and Related Decisions",
            ),
            "experiment.md": (
                "## Hypothesis", "## Variables", "## Controls", "## Dataset or Task Set",
                "## Metrics", "## Procedure", "## Results", "## Artifacts",
                "## Interpretation", "## Threats to Validity",
            ),
        }
        for filename, headings in required.items():
            text = (ROOT / "docs" / "templates" / filename).read_text(encoding="utf-8")
            self.assertFalse(text.startswith("---\n"), filename)
            for heading in headings:
                self.assertIn(heading, text, f"{filename}: {heading}")
```

- [ ] **Step 2: Run the contract tests and verify missing-file failures**

Run:

```powershell
python -m unittest tests.docs.test_repository_contract -v
```

Expected: the new tests fail because `AGENTS.md` and `docs/templates/*.md` do not exist.

- [ ] **Step 3: Create the root agent contract**

Create `AGENTS.md` with these exact sections and obligations:

```markdown
# Eidos Agent Instructions

## Required Discovery

Before substantive work, read this file, `docs/README.md`, and `docs/registry.json`. Use registry relationships to locate applicable active governance documents, active specifications, and accepted ADRs. Do not infer authority from filenames or directory placement alone.

## Authority Semantics

Active governance documents govern documentation. Active specifications define required behavior. Accepted ADRs record binding decisions. RFCs are proposals, experiments are evidence, notes are background, and `docs/superpowers/` contains non-normative workflow artifacts. The repository currently has no formally approved research architecture.

## Documentation Changes

Classify each new governed document before creating it and start from the matching file in `docs/templates/`. Update the Markdown document and `docs/registry.json` in the same change. Do not add registry metadata as Markdown front matter. Preserve published IDs and paths. Keep formal documents in English.

## Implementation Changes

Before implementation, resolve all applicable active specifications and accepted ADRs through the registry. If behavior, an interface, or a binding decision changes, update or create the required formal documentation in the same change. Do not promote claims from notes, RFCs, or experiments into requirements without the formal acceptance path.

## Authority Conflicts

If active authorities conflict, identify the conflicting IDs and stop the affected work. Do not silently choose one. Resolve the defect through an explicit governance, ADR, or specification change.

## Required Validation

For governed documentation or documentation-tooling changes, run:

```powershell
python tools/docs/validate.py
python -m unittest discover -s tests/docs -v
```

Report the commands and results when claiming completion. Fix validation errors; do not bypass or auto-rewrite them.
```

- [ ] **Step 4: Create the RFC and ADR templates**

Create `docs/templates/rfc.md`:

```markdown
# RFC-NNNN: Title

> An RFC is a non-normative proposal. Acceptance does not make it binding; list the ADRs or specifications required to represent the accepted outcome.

## Problem

<!-- State the concrete problem, affected users or systems, and why it requires a decision. -->

## Context

<!-- Cite registered documents and verified evidence needed to evaluate the proposal. -->

## Proposal

<!-- Describe the proposed behavior, boundaries, and migration path precisely. -->

## Alternatives Considered

<!-- Compare credible alternatives, including retaining the current state. -->

## Risks and Mitigations

<!-- Pair each material risk with a concrete mitigation or acceptance rationale. -->

## Unresolved Questions

<!-- List questions that must be resolved during review; write `None` when review is unblocked. -->

## Acceptance Criteria

<!-- List observable conditions reviewers will use to accept or reject this proposal. -->

## Expected Binding Outputs

<!-- List the ADR or specification IDs that will represent an accepted outcome; write `None` if no binding output is intended. -->
```

Create `docs/templates/adr.md`:

```markdown
# ADR-NNNN: Title

## Context

<!-- Describe the forces and registered inputs that require a binding decision. -->

## Decision

<!-- State the decision explicitly in present tense, including its scope and boundaries. -->

## Consequences

<!-- Record positive, negative, operational, and migration consequences. -->

## Rejected Alternatives

<!-- Name each serious alternative and the concrete reason it was rejected. -->

## Supersession

<!-- List same-type ADR IDs replaced by this decision; write `None` when it replaces none. -->

## Verification Impact

<!-- Identify tests, specifications, experiments, or audits that verify adherence to the decision. -->
```

- [ ] **Step 5: Create the specification and experiment templates**

Create `docs/templates/specification.md`:

```markdown
# SPEC-NNNN: Title

## Scope

<!-- Define what this specification governs and explicitly excludes. -->

## Definitions

<!-- Define domain terms whose interpretation affects a requirement. -->

## Normative Requirements

Use `MUST` for obligations, `SHOULD` for recommendations whose exceptions require justification, and `MAY` for permitted options. Every requirement must be externally verifiable or mapped to a verification method.

<!-- Give each requirement a stable local label and one unambiguous obligation. -->

## Interfaces

<!-- Define inputs, outputs, schemas, protocols, or callable signatures. -->

## Invariants

<!-- State conditions that remain true across valid operations and state changes. -->

## Failure Behavior

<!-- Define invalid input, failure reporting, recovery, and partial-state behavior. -->

## Verification

<!-- Map every MUST and SHOULD requirement to a test, inspection, metric, or review. -->

## Dependencies and Related Decisions

<!-- List applicable GOV, ADR, SPEC, and accepted RFC IDs and explain their relevance. -->
```

Create `docs/templates/experiment.md`:

```markdown
# EXP-NNNN: Title

> An experiment records evidence and interpretation. It does not create a requirement or binding decision.

## Hypothesis

<!-- State a falsifiable prediction and its expected direction or threshold. -->

## Variables

<!-- Identify independent, dependent, and measured nuisance variables. -->

## Controls

<!-- Define baselines, ablations, seeds, budgets, and fixed conditions. -->

## Dataset or Task Set

<!-- Identify exact versions, splits, generation procedures, and exclusions. -->

## Metrics

<!-- Define metric computation, aggregation, uncertainty, and success thresholds. -->

## Procedure

<!-- Give a reproducible ordered procedure, including environment and commands. -->

## Results

<!-- Record raw measurements and artifact locations separately from interpretation. -->

## Artifacts

<!-- List immutable or content-addressed paths for configs, logs, checkpoints, and outputs. -->

## Interpretation

<!-- Explain what the results support, challenge, or leave unresolved without creating requirements. -->

## Threats to Validity

<!-- Record known confounders, leakage risks, measurement weaknesses, and limits on generalization. -->
```

- [ ] **Step 6: Run all documentation tests and the live validator**

Run:

```powershell
python tools/docs/validate.py
python -m unittest discover -s tests/docs -v
```

Expected: validation succeeds and the entire test suite passes.

- [ ] **Step 7: Perform the final acceptance audit**

Run:

```powershell
git diff --check
$redFlags = @('T'+'BD', 'T'+'ODO', 'FIX'+'ME', 'implement'+' later', 'fill'+' in')
foreach ($redFlag in $redFlags) {
    rg -n -i --fixed-strings $redFlag AGENTS.md README.md docs/README.md docs/governance docs/notes docs/templates tools/docs tests/docs
}
git status --short
```

Expected:

- `git diff --check` has no output.
- Placeholder scan has no matches in governed documents or implementation code. Template-only author prompts such as `Title`, `NNNN`, and `None` are intentional and must not appear in registered documents.
- `git status --short` lists only the intended Task 5 files before commit.

Then verify acceptance criteria explicitly:

```powershell
python -c "import json; from pathlib import Path; d=json.loads(Path('docs/registry.json').read_text(encoding='utf-8')); assert [x['id'] for x in d['documents']] == ['GOV-0001','NOTE-0001']; print('initial registry IDs verified')"
python -c "from pathlib import Path; p=Path('docs/notes/early-arc-specialized-reasoning-concept.zh-TW.md').read_text(encoding='utf-8'); assert 'ARC 的高分方法' in p and 'Archived Non-Normative Concept Note' in p; print('archived note verified')"
```

Expected: both commands print their verification message.

- [ ] **Step 8: Commit the agent contract and templates**

```powershell
git add AGENTS.md docs/templates tests/docs/test_repository_contract.py
git commit -m "docs: add agent workflow and authoring templates"
```

---

## Final Verification

After all task commits, run from the repository root:

```powershell
python tools/docs/validate.py
python -m unittest discover -s tests/docs -v
git diff --check HEAD~5..HEAD
git status --short --branch
```

Expected:

- Validator prints `Documentation validation passed.`
- All tests pass.
- The five implementation commits contain no whitespace errors.
- The working tree is clean.
- The only registered documents are `GOV-0001` and `NOTE-0001`.
- No formal research architecture, roadmap, or technology selection has been approved.

Review the final diff to confirm the archived Chinese concept content remains present, templates are excluded from the registry, `AGENTS.md` stays operational rather than architectural, and all implementation claims correspond to validator or test evidence.
