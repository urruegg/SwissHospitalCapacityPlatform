"""Unit tests for the Entra demo-org master-data gate (data/entra).

Run from the repository root:

    python3 -m unittest discover -s data/entra/tests -t .
"""

from __future__ import annotations

import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "data" / "entra" / "validate_entra_master_data.py"

_spec = importlib.util.spec_from_file_location("validate_entra_master_data", MODULE_PATH)
assert _spec and _spec.loader
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(r) for r in csv.DictReader(handle)]


class RepositoryMasterDataTest(unittest.TestCase):
    """The committed CSV artefacts must pass the gate as-is."""

    def test_committed_master_data_passes(self) -> None:
        self.assertEqual(validator.validate(), [])

    def test_expected_counts(self) -> None:
        roles = _rows(validator.APP_ROLES_CSV)
        groups = _rows(validator.SECURITY_GROUPS_CSV)
        users = _rows(validator.USERS_CSV)
        self.assertEqual(len(roles), validator.EXPECTED_ROLE_COUNT)
        self.assertEqual(len(groups), validator.EXPECTED_ROLE_COUNT)
        self.assertEqual(len(users), validator.EXPECTED_USER_COUNT)

    def test_one_group_per_role(self) -> None:
        roles = {r["role_value"] for r in _rows(validator.APP_ROLES_CSV)}
        backing = {g["backing_role"] for g in _rows(validator.SECURITY_GROUPS_CSV)}
        self.assertEqual(roles, backing)

    def test_every_user_role_and_hospital_resolves(self) -> None:
        roles = {r["role_value"] for r in _rows(validator.APP_ROLES_CSV)}
        orgs = {o["org_key"] for o in _rows(validator.ORGANIZATIONS_CSV)}
        for user in _rows(validator.USERS_CSV):
            self.assertIn(user["app_role"], roles)
            self.assertIn(user["default_hospital"], orgs)

    def test_users_reconcile_with_persona_seed(self) -> None:
        seed = {p["mail_nickname"] for p in _rows(validator.PERSONAS_SEED_CSV)}
        users = {u["upn_local"] for u in _rows(validator.USERS_CSV)}
        self.assertEqual(seed, users)


class TamperingTest(unittest.TestCase):
    """The gate must catch drift. We point the module at temp copies and mutate them."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        tmp = Path(self._tmp.name)
        self._orig = {
            "ORGANIZATIONS_CSV": validator.ORGANIZATIONS_CSV,
            "APP_ROLES_CSV": validator.APP_ROLES_CSV,
            "SECURITY_GROUPS_CSV": validator.SECURITY_GROUPS_CSV,
            "USERS_CSV": validator.USERS_CSV,
        }
        # Copy the four CSVs into a temp dir so we can mutate without touching the repo.
        self.paths = {}
        for attr, src in self._orig.items():
            dst = tmp / src.name
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            setattr(validator, attr, dst)
            self.paths[attr] = dst

    def tearDown(self) -> None:
        for attr, orig in self._orig.items():
            setattr(validator, attr, orig)

    def test_unknown_role_is_rejected(self) -> None:
        path = self.paths["USERS_CSV"]
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("HCC.BedManager", "HCC.DoesNotExist", 1), encoding="utf-8")
        errors = validator.validate()
        self.assertTrue(any("unknown app_role" in e for e in errors), errors)

    def test_dropping_a_group_is_rejected(self) -> None:
        path = self.paths["SECURITY_GROUPS_CSV"]
        lines = path.read_text(encoding="utf-8").splitlines()
        path.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
        errors = validator.validate()
        self.assertTrue(any("no group for roles" in e for e in errors), errors)

    def test_unknown_hospital_is_rejected(self) -> None:
        path = self.paths["USERS_CSV"]
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace(",USZ,CH", ",Nowhere,CH", 1), encoding="utf-8")
        errors = validator.validate()
        self.assertTrue(any("unknown default_hospital" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
