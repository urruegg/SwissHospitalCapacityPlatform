"""Sprint 16 T3 — response-lever library + JSON Schema validation tests."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from _util import CSA_DIR, load_script

SCHEMA_DIR = CSA_DIR / "schema"
VALID_CATEGORIES = {
    "surge-capacity",
    "staffing",
    "patient-flow",
    "supply-chain",
    "coordination",
    "communication",
    "continuity",
}


class TestResponseLevers(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_script("csa-seed-response-levers.py")
        cls.levers = cls.mod.build_response_levers()

    def test_library_is_non_trivial_and_under_100(self) -> None:
        self.assertGreaterEqual(len(self.levers), 60)
        self.assertLess(len(self.levers), 100)

    def test_lever_ids_unique(self) -> None:
        ids = [lever["leverId"] for lever in self.levers]
        self.assertEqual(len(ids), len(set(ids)))

    def test_all_levers_advisory_only(self) -> None:
        self.assertTrue(all(lever["advisoryOnly"] is True for lever in self.levers))

    def test_categories_valid(self) -> None:
        for lever in self.levers:
            self.assertIn(lever["category"], VALID_CATEGORIES)

    def test_tiers_in_range(self) -> None:
        for lever in self.levers:
            self.assertIn(lever["doctrineTier"], (1, 2, 3))

    def test_levers_validate_against_schema(self) -> None:
        errors = self.mod.validate_all(self.levers)
        self.assertEqual(errors, [], msg="\n".join(errors))

    def test_all_seven_categories_present(self) -> None:
        present = {lever["category"] for lever in self.levers}
        self.assertEqual(present, VALID_CATEGORIES)


class TestSchemaFiles(unittest.TestCase):
    def test_all_four_container_schemas_are_valid_json(self) -> None:
        expected = {
            "scenarios",
            "agent-memory",
            "response-levers",
            "simulation-runs",
        }
        found = set()
        for path in SCHEMA_DIR.glob("*.schema.json"):
            with path.open(encoding="utf-8") as fh:
                doc = json.load(fh)
            self.assertEqual(doc.get("$schema"), "http://json-schema.org/draft-07/schema#")
            found.add(path.name.replace(".schema.json", ""))
        self.assertEqual(found, expected)


class TestSchemaUtil(unittest.TestCase):
    def test_validator_flags_missing_required(self) -> None:
        from _schema_util import validate

        schema = {"type": "object", "required": ["a"], "properties": {"a": {"type": "string"}}}
        self.assertEqual(validate({"a": "x"}, schema), [])
        self.assertTrue(validate({}, schema))

    def test_validator_flags_enum_and_pattern(self) -> None:
        from _schema_util import validate

        schema = {"type": "string", "enum": ["x", "y"]}
        self.assertTrue(validate("z", schema))
        schema2 = {"type": "string", "pattern": "^F[1-8]$"}
        self.assertEqual(validate("F3", schema2), [])
        self.assertTrue(validate("F9", schema2))


if __name__ == "__main__":
    unittest.main()
