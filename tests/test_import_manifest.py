import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_import import validate_manifest


ROOT = Path(__file__).parents[1]
MANIFEST = ROOT / "tests/fixtures/coursework_import.json"


class ImportManifestTests(unittest.TestCase):
    def test_existing_coursework_is_complete_and_unchanged(self):
        before = {path: path.stat().st_mtime_ns for path in validate_manifest(ROOT, MANIFEST)}
        validate_manifest(ROOT, MANIFEST)
        after = {path: path.stat().st_mtime_ns for path in before}
        self.assertEqual(before, after)

    def test_missing_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "dip").mkdir()
            (root / "dip" / "notes.md").write_text("notes", encoding="utf-8")
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps([
                {"subject": "dip", "path": "dip/missing.md", "kind": "document"},
            ]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing coursework file"):
                validate_manifest(root, manifest)

    def test_extensionless_guideline_is_supported(self):
        entries = json.loads(MANIFEST.read_text(encoding="utf-8"))
        entry = next(item for item in entries if item["path"].endswith("dip_guidelinespdf"))
        self.assertEqual(entry["kind"], "guideline")


if __name__ == "__main__":
    unittest.main()