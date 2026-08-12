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

    def test_note_allows_uppercase_region_language_subtag(self):
        note = dict(
            VALID_ENTRY,
            id="NOTE-0001",
            type="note",
            status="archived",
            path="docs/notes/early-arc-specialized-reasoning-concept.zh-TW.md",
            language="zh-TW",
        )
        self.write_registry([note])
        self.write_document(note["path"])
        self.assertEqual([], validate_repository(self.repo))

    def test_schema_rejects_path_traversal_syntax(self):
        invalid = dict(
            VALID_ENTRY,
            id="NOTE-0001",
            type="note",
            status="archived",
            path="docs/notes/../outside.md",
            language="zh-TW",
        )
        self.write_registry([invalid])
        errors = validate_repository(self.repo)
        self.assertTrue(any("schema" in error and "path" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
