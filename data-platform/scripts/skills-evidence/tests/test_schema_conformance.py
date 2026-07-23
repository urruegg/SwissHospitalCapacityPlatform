import json
import unittest
from pathlib import Path

import skills_evidence_synth as seed
from skills_evidence_synth import _CONNECTORS, _load_fixture

SCHEMA = json.loads(seed.SCHEMA_PATH.read_text(encoding="utf-8"))


def _raw_record_count() -> int:
    return sum(len(conn.parse(_load_fixture(fx))) for conn, fx in _CONNECTORS)


class TestSchemaConformance(unittest.TestCase):
    def test_seeder_envelope_passes_dependency_free_validate(self):
        doc = seed.build_envelope()
        self.assertEqual(seed.validate(doc), [])

    def test_envelope_has_at_least_one_record(self):
        self.assertGreaterEqual(len(seed.build_envelope()["records"]), 1)

    def test_no_dedupe_count_equals_sum_of_fixture_rows(self):
        recs = seed.build_records(dedupe=False)
        self.assertEqual(len(recs), _raw_record_count())

    def test_default_dataset_id_matches_schema_pattern(self):
        import re
        pattern = SCHEMA["properties"]["datasetId"]["pattern"]
        self.assertRegex(seed.DEFAULT_DATASET_ID, pattern)

    def test_envelope_validates_against_jsonschema_if_available(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed")
        jsonschema.validate(seed.build_envelope(), SCHEMA)

    def test_invalid_record_is_reported(self):
        doc = seed.build_envelope()
        doc["records"][0]["selfOrConfirmed"] = "bogus"
        self.assertTrue(seed.validate(doc))


if __name__ == "__main__":
    unittest.main()
