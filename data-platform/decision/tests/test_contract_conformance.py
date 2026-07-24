"""Contract-conformance tests for the DC-INSIGHT-v1 5-beat actionable-insight tuple.

Sprint 26 WS-D: grounded copilot answers must conform to
data/synthetic/schema/dc-insight-v1.schema.json (design spec Sec 3.1). This test
loads the JSON Schema (draft-07) and asserts:
  * a VALID fixture (all six beats present) validates successfully.
  * an INVALID fixture (missing the "provenance" beat) fails validation.
"""

import json
import pathlib
import unittest

import jsonschema

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SCHEMA_PATH = REPO_ROOT / "data" / "synthetic" / "schema" / "dc-insight-v1.schema.json"
FIXTURES_DIR = pathlib.Path(__file__).resolve().parent / "fixtures"

VALID_FIXTURE = FIXTURES_DIR / "dc-insight-v1.valid.json"
INVALID_FIXTURE = FIXTURES_DIR / "dc-insight-v1.invalid-missing-provenance.json"


class TestDcInsightV1ContractConformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            cls.schema = json.load(f)

    def _load_fixture(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_schema_is_draft07_with_additional_properties_false_at_top_level(self):
        self.assertEqual(
            self.schema.get("$schema"), "http://json-schema.org/draft-07/schema#"
        )
        self.assertFalse(self.schema.get("additionalProperties", True))

    def test_valid_fixture_conforms_to_schema(self):
        instance = self._load_fixture(VALID_FIXTURE)
        # Must not raise.
        jsonschema.validate(instance=instance, schema=self.schema)

    def test_invalid_fixture_missing_provenance_fails_validation(self):
        instance = self._load_fixture(INVALID_FIXTURE)
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            jsonschema.validate(instance=instance, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
