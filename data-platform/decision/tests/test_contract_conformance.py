"""Contract-conformance tests for the DC-INSIGHT-v1 5-beat actionable-insight tuple.

Sprint 26 WS-D: grounded copilot answers must conform to
data/synthetic/schema/dc-insight-v1.schema.json (design spec Sec 3.1).

Follows the repo convention established by
data-platform/scripts/skills-evidence/tests/test_schema_conformance.py:
  * PRIMARY validation is a dependency-free structural check (`_structural_validate`)
    that always runs, so this test executes even where `jsonschema` isn't installed.
  * OPTIONAL validation uses `jsonschema.validate` for the full draft-07 check when
    the package is available, skipping (not failing) otherwise.
"""

import json
import pathlib
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SCHEMA_PATH = REPO_ROOT / "data" / "synthetic" / "schema" / "dc-insight-v1.schema.json"
FIXTURES_DIR = pathlib.Path(__file__).resolve().parent / "fixtures"

VALID_FIXTURE = FIXTURES_DIR / "dc-insight-v1.valid.json"
INVALID_FIXTURE = FIXTURES_DIR / "dc-insight-v1.invalid-missing-provenance.json"


def _load_json(path: pathlib.Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _structural_validate(doc: dict, schema: dict) -> list[str]:
    """Dependency-free schema check. Returns a list of error strings (empty=ok)."""
    errors: list[str] = []

    top_required = set(schema.get("required", []))
    missing_top = top_required - set(doc)
    if missing_top:
        errors.append(f"tuple missing beats: {sorted(missing_top)}")
        # The remaining checks assume the beats are present; bail out early.
        return errors

    action_schema = schema["properties"]["action"]
    status_enum = action_schema["properties"]["status"].get("enum", [])
    if doc["action"].get("status") not in status_enum:
        errors.append(f"action.status {doc['action'].get('status')!r} not in {status_enum}")
    hitl_enum = action_schema["properties"]["hitl"].get("enum", [])
    if doc["action"].get("hitl") not in hitl_enum:
        errors.append(f"action.hitl {doc['action'].get('hitl')!r} not in {hitl_enum}")

    provenance_schema = schema["properties"]["provenance"]
    concepts = doc["provenance"].get("concepts", [])
    if not concepts:
        errors.append("provenance.concepts must be non-empty")
    trust_enum = provenance_schema["properties"]["source_trust"].get("enum", [])
    if doc["provenance"].get("source_trust") not in trust_enum:
        errors.append(
            f"provenance.source_trust {doc['provenance'].get('source_trust')!r} not in {trust_enum}"
        )

    return errors


class TestDcInsightV1ContractConformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = _load_json(SCHEMA_PATH)

    def test_schema_is_draft07_with_additional_properties_false_at_top_level(self):
        self.assertEqual(
            self.schema.get("$schema"), "http://json-schema.org/draft-07/schema#"
        )
        self.assertFalse(self.schema.get("additionalProperties", True))

    def test_valid_fixture_passes_dependency_free_validate(self):
        doc = _load_json(VALID_FIXTURE)
        self.assertEqual(_structural_validate(doc, self.schema), [])

    def test_invalid_fixture_missing_provenance_is_reported(self):
        doc = _load_json(INVALID_FIXTURE)
        errors = _structural_validate(doc, self.schema)
        self.assertTrue(errors)
        self.assertTrue(any("provenance" in e for e in errors))

    def test_valid_fixture_validates_against_jsonschema_if_available(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed")
        jsonschema.validate(instance=_load_json(VALID_FIXTURE), schema=self.schema)

    def test_invalid_fixture_fails_jsonschema_validation_if_available(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed")
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            jsonschema.validate(instance=_load_json(INVALID_FIXTURE), schema=self.schema)


if __name__ == "__main__":
    unittest.main()
