import unittest

from scripts.evidence.publish import OUTPUT_FILES, build_outputs, publish
from scripts.evidence.parsers.common import dumps
from scripts.evidence.tests._helpers import (
    FIXED_COMMIT,
    FIXTURE_REPO,
    REPO_ROOT,
    assert_valid,
)

SCHEMA_BY_FILE = {
    "requirements.json": "requirements",
    "adrs.json": "adrs",
    "req_adr_map.json": "req_adr_map",
    "bom.json": "bom",
    "dependencies.json": "dependencies",
    "region_availability.json": "region_availability",
    "deployed_bom.json": "deployed_bom",
}


class TestPublishOrchestrator(unittest.TestCase):
    def test_all_outputs_present_and_valid(self):
        outputs = build_outputs(FIXTURE_REPO, source_commit=FIXED_COMMIT)
        self.assertEqual(set(outputs), set(OUTPUT_FILES))
        for filename, schema in SCHEMA_BY_FILE.items():
            assert_valid(outputs[filename], schema)

    def test_curated_map_merged(self):
        outputs = build_outputs(FIXTURE_REPO, source_commit=FIXED_COMMIT)
        edges = {(r["requirementId"], r["adrId"], r.get("relationship")) for r in outputs["req_adr_map.json"]}
        # Comes from the curated adr-requirement-map.yaml overlay.
        self.assertIn(("FR-DATA-001", "ADR-0002", "governs"), edges)

    def test_byte_stable(self):
        first = build_outputs(FIXTURE_REPO, source_commit=FIXED_COMMIT)
        second = build_outputs(FIXTURE_REPO, source_commit=FIXED_COMMIT)
        for filename in OUTPUT_FILES:
            self.assertEqual(dumps(first[filename]), dumps(second[filename]))

    def test_publish_writes_files(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            written = publish(FIXTURE_REPO, out, source_commit=FIXED_COMMIT)
            self.assertEqual({p.name for p in written}, set(OUTPUT_FILES))
            for path in written:
                self.assertTrue(path.exists())

    def test_real_repo_outputs_valid(self):
        outputs = build_outputs(REPO_ROOT, source_commit=FIXED_COMMIT)
        for filename, schema in SCHEMA_BY_FILE.items():
            assert_valid(outputs[filename], schema)
        self.assertGreaterEqual(len(outputs["bom.json"]), 25)
        self.assertGreaterEqual(len(outputs["adrs.json"]), 10)


if __name__ == "__main__":
    unittest.main()
