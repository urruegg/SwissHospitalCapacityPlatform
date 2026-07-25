"""Validation tests for the git-owned lever catalog (Sprint 26 WS-B).

Follows the repo convention established by
data-platform/decision/tests/test_contract_conformance.py:
  * PRIMARY validation is a dependency-free structural check (`_structural_validate`)
    that always runs, so this test executes even where `jsonschema` isn't installed.
  * OPTIONAL validation uses `jsonschema.validate` for the full draft-07 check when
    the package is available, skipping (not failing) otherwise.

YAML parsing follows the optional-PyYAML convention established by
data-platform/scripts/csa/tests/test_scenarios.py: skip (not fail) when PyYAML
isn't installed, since it isn't a guaranteed local dependency.
"""

import json
import pathlib
import unittest

try:
    import yaml  # noqa: F401

    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

LEVERS_DIR = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_PATH = LEVERS_DIR / "lever.schema.json"
ROLE_FILES = ["ooa.yaml", "dca.yaml", "bmca.yaml", "orsa.yaml", "sba.yaml", "csa.yaml"]
ALLOWED_ROLES = {"ooa", "dca", "bmca", "orsa", "sba", "csa"}
REQUIRED_I18N_KEYS = {"de", "en", "fr", "it"}


def _load_schema() -> dict:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_yaml(path: pathlib.Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _structural_validate(lever: dict, schema: dict) -> list[str]:
    """Dependency-free schema check. Returns a list of error strings (empty=ok)."""
    errors: list[str] = []

    top_required = set(schema.get("required", []))
    missing = top_required - set(lever)
    if missing:
        errors.append(f"lever {lever.get('lever_id')!r} missing fields: {sorted(missing)}")
        return errors

    if lever["role"] not in ALLOWED_ROLES:
        errors.append(f"role {lever['role']!r} not in {sorted(ALLOWED_ROLES)}")
    if lever["owner_role"] not in ALLOWED_ROLES:
        errors.append(f"owner_role {lever['owner_role']!r} not in {sorted(ALLOWED_ROLES)}")

    title_keys = set(lever["title_i18n"]) if isinstance(lever.get("title_i18n"), dict) else set()
    if title_keys != REQUIRED_I18N_KEYS:
        errors.append(
            f"lever {lever['lever_id']!r} title_i18n keys {sorted(title_keys)} != {sorted(REQUIRED_I18N_KEYS)}"
        )

    if "description_i18n" in lever:
        desc_keys = (
            set(lever["description_i18n"]) if isinstance(lever["description_i18n"], dict) else set()
        )
        if desc_keys != REQUIRED_I18N_KEYS:
            errors.append(
                f"lever {lever['lever_id']!r} description_i18n keys {sorted(desc_keys)} != {sorted(REQUIRED_I18N_KEYS)}"
            )

    if lever.get("hitl") is not True:
        errors.append(f"lever {lever['lever_id']!r} hitl must be true, got {lever.get('hitl')!r}")

    if not isinstance(lever.get("params_schema"), dict):
        errors.append(f"lever {lever['lever_id']!r} params_schema must be an object")

    if not isinstance(lever.get("impact_formula_ref"), str) or not lever["impact_formula_ref"]:
        errors.append(f"lever {lever['lever_id']!r} impact_formula_ref must be a non-empty string")

    return errors


@unittest.skipUnless(_HAS_YAML, "PyYAML not installed")
class TestLeverCatalogValid(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = _load_schema()
        cls.docs = {}
        for filename in ROLE_FILES:
            path = LEVERS_DIR / filename
            cls.docs[filename] = _load_yaml(path)

    def test_discovers_all_six_role_files(self) -> None:
        for filename in ROLE_FILES:
            self.assertTrue((LEVERS_DIR / filename).is_file(), f"missing {filename}")

    def test_each_file_has_role_and_levers(self) -> None:
        for filename, doc in self.docs.items():
            self.assertIn("role", doc, msg=filename)
            self.assertIn("levers", doc, msg=filename)
            self.assertIsInstance(doc["levers"], list, msg=filename)
            self.assertGreaterEqual(len(doc["levers"]), 1, msg=filename)

    def test_every_lever_passes_structural_validation(self) -> None:
        for filename, doc in self.docs.items():
            for lever in doc["levers"]:
                errors = _structural_validate(lever, self.schema)
                self.assertEqual(errors, [], msg=f"{filename}: {errors}")

    def test_every_lever_validates_against_jsonschema_if_available(self) -> None:
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed")
        for filename, doc in self.docs.items():
            for lever in doc["levers"]:
                jsonschema.validate(instance=lever, schema=self.schema)

    def test_fully_specified_lever_ids_exist(self) -> None:
        all_lever_ids = {
            lever["lever_id"] for doc in self.docs.values() for lever in doc["levers"]
        }
        for expected in ("OOA-EXPEDITE-DISCHARGE", "OOA-DIVERT-LOW-ACUITY", "DCA-UNBLOCK-BARRIER"):
            self.assertIn(expected, all_lever_ids)

    def test_ooa_expedite_discharge_owner_role_is_dca(self) -> None:
        ooa_levers = {lever["lever_id"]: lever for lever in self.docs["ooa.yaml"]["levers"]}
        self.assertEqual(ooa_levers["OOA-EXPEDITE-DISCHARGE"]["owner_role"], "dca")


if __name__ == "__main__":
    unittest.main()
