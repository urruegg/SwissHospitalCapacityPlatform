import json
import unittest
from pathlib import Path

from providers.registry import (
    load_manifest, validate_manifest, discover, catalog_rows, ProviderSpec,
)

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


class TestRegistry(unittest.TestCase):
    def test_discover_finds_sed_and_validates(self):
        specs = discover()
        by_id = {s.source_id: s for s in specs}
        self.assertIn("sed", by_id)
        self.assertIsInstance(by_id["sed"], ProviderSpec)
        self.assertEqual(by_id["sed"].channel_kind, "external")
        self.assertEqual(by_id["sed"].default_mode, "live")

    def test_invalid_manifest_reports_errors(self):
        errors = validate_manifest({"sourceId": "x"})  # missing required keys
        self.assertTrue(errors)

    def test_catalog_rows_shape(self):
        rows = catalog_rows(discover())
        sed = next(r for r in rows if r["sourceId"] == "sed")
        self.assertEqual(
            set(sed) >= {"sourceId", "authority", "trustTier", "defaultMode", "channelKind"},
            True,
        )



if __name__ == "__main__":
    unittest.main()

