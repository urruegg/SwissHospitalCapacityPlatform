import json
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
SCHEMA = SCRIPTS_DIR / "providers" / "_schema" / "provider.schema.json"


class TestManifestSchema(unittest.TestCase):
    def test_schema_exists_and_declares_required_keys(self):
        doc = json.loads(SCHEMA.read_text(encoding="utf-8"))
        required = set(doc["required"])
        self.assertTrue(
            {"sourceId", "authority", "trustTier", "channelKind",
             "hazardTypes", "defaultMode", "licence", "providerVersion"} <= required
        )

    def test_mode_and_kind_enums(self):
        doc = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(
            set(doc["properties"]["channelKind"]["enum"]), {"external", "internal"}
        )
        self.assertEqual(
            set(doc["properties"]["defaultMode"]["enum"]),
            {"live", "simulated", "internal"},
        )


if __name__ == "__main__":
    unittest.main()
