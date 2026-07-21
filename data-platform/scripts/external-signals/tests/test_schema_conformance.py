import json
import unittest
from pathlib import Path

SCHEMA = (
    Path(__file__).resolve().parents[4]
    / "data" / "synthetic" / "schema" / "dc-ext-signal-v1.schema.json"
)


class TestSchemaShape(unittest.TestCase):
    def test_schema_loads_and_has_envelope(self):
        doc = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(doc["properties"]["contractId"]["enum"], ["DC-EXT-SIGNAL-v1"])
        required = set(doc["required"])
        self.assertTrue(
            {"datasetId", "contractId", "contractVersion", "classification",
             "residency", "purposeTags", "records"} <= required
        )

    def test_record_requires_core_signal_fields(self):
        doc = json.loads(SCHEMA.read_text(encoding="utf-8"))
        rec = doc["properties"]["records"]["items"]
        for field in ("signalId", "sourceId", "trustTier", "hazardType",
                      "severity", "status", "onset", "provenance"):
            self.assertIn(field, rec["properties"], field)


if __name__ == "__main__":
    unittest.main()
