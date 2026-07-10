#!/usr/bin/env python3
"""Entra demo-org master-data contract gate (Sprint 12 follow-up, S12.10).

Validates the tenant-agnostic Entra master-data CSV artefacts under
``data/entra`` — organisations, app roles, security groups, and users — and
reconciles them against the two authoritative sources they are derived from:

* the Bicep parameter files ``infra/modules/entra/parameters/{sit,prod}.bicepparam``
  (the ``deploy``-ceiling source of truth the Microsoft Graph modules consume), and
* the persona seed ``data/synthetic/personas.csv`` (the Power BI / RLS seed).

Purpose. These CSVs are the portable master data an IaC script can replay to
(re)create the orgs, users, and security roles in Microsoft Entra — including a
future *tenant migration*, where only the UPN domain changes and every other
attribute (local UPN part, display name, app role, hospital context) is carried
over verbatim. Keeping them in lock-step with the Bicep source prevents drift
between the human-reviewable master data and what actually gets deployed.

The gate is intentionally dependency-free (Python 3 standard library only) so it
runs identically in CI and on a developer machine. Exit 0 = PASS, non-zero =
FAIL.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ENTRA_DIR = REPO_ROOT / "data" / "entra"

ORGANIZATIONS_CSV = ENTRA_DIR / "organizations.csv"
APP_ROLES_CSV = ENTRA_DIR / "app-roles.csv"
SECURITY_GROUPS_CSV = ENTRA_DIR / "security-groups.csv"
USERS_CSV = ENTRA_DIR / "users.csv"

PERSONAS_SEED_CSV = REPO_ROOT / "data" / "synthetic" / "personas.csv"
BICEPPARAMS = [
    REPO_ROOT / "infra" / "modules" / "entra" / "parameters" / "sit.bicepparam",
    REPO_ROOT / "infra" / "modules" / "entra" / "parameters" / "prod.bicepparam",
]

EXPECTED_USER_COUNT = 23
EXPECTED_ROLE_COUNT = 17
SUPER_ROLES = {"HCC.SuperAdmin", "HCC.GuestReadOnly"}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader]
    return rows


def _require_columns(errors: list[str], name: str, rows: list[dict[str, str]], columns: set[str]) -> None:
    header = set(rows[0].keys()) if rows else set()
    missing = columns - header
    if missing:
        errors.append(f"{name}: missing columns {sorted(missing)}")


def validate() -> list[str]:
    """Run every check and return a list of human-readable error strings."""
    errors: list[str] = []

    for path in (ORGANIZATIONS_CSV, APP_ROLES_CSV, SECURITY_GROUPS_CSV, USERS_CSV, PERSONAS_SEED_CSV):
        if not path.exists():
            errors.append(f"missing required file: {path.relative_to(REPO_ROOT)}")
    if errors:
        return errors

    orgs = _read_csv(ORGANIZATIONS_CSV)
    roles = _read_csv(APP_ROLES_CSV)
    groups = _read_csv(SECURITY_GROUPS_CSV)
    users = _read_csv(USERS_CSV)
    personas = _read_csv(PERSONAS_SEED_CSV)

    _require_columns(errors, "organizations.csv", orgs, {"org_key", "display_name", "org_type", "canton", "scope"})
    _require_columns(errors, "app-roles.csv", roles, {"role_value", "display_name", "category", "description"})
    _require_columns(errors, "security-groups.csv", groups, {"group_name", "mail_nickname", "backing_role", "env_scope", "description"})
    _require_columns(errors, "users.csv", users, {"upn_local", "display_name", "app_role", "default_hospital", "usage_location"})
    if errors:
        return errors

    # --- organisations ---
    org_keys = [o["org_key"] for o in orgs]
    if len(org_keys) != len(set(org_keys)):
        errors.append("organizations.csv: duplicate org_key values")
    org_key_set = set(org_keys)
    for required in ("USZ", "LUKS", "Zollikerberg", "Aggregated", "All"):
        if required not in org_key_set:
            errors.append(f"organizations.csv: missing required org_key '{required}'")

    # --- app roles ---
    role_values = [r["role_value"] for r in roles]
    if len(role_values) != len(set(role_values)):
        errors.append("app-roles.csv: duplicate role_value values")
    role_value_set = set(role_values)
    if len(role_values) != EXPECTED_ROLE_COUNT:
        errors.append(f"app-roles.csv: expected {EXPECTED_ROLE_COUNT} roles, found {len(role_values)}")
    super_found = {r["role_value"] for r in roles if r["category"] == "super"}
    if super_found != SUPER_ROLES:
        errors.append(f"app-roles.csv: super-role set {sorted(super_found)} != {sorted(SUPER_ROLES)}")
    for role in roles:
        if not role["display_name"]:
            errors.append(f"app-roles.csv: role '{role['role_value']}' has empty display_name")
        if not role["description"]:
            errors.append(f"app-roles.csv: role '{role['role_value']}' has empty description")

    # --- security groups: exactly one per app role ---
    group_backing = [g["backing_role"] for g in groups]
    if set(group_backing) != role_value_set:
        missing = role_value_set - set(group_backing)
        extra = set(group_backing) - role_value_set
        if missing:
            errors.append(f"security-groups.csv: no group for roles {sorted(missing)}")
        if extra:
            errors.append(f"security-groups.csv: group backs unknown roles {sorted(extra)}")
    if len(group_backing) != len(set(group_backing)):
        errors.append("security-groups.csv: duplicate backing_role values")
    for group in groups:
        # Convention (security-groups.bicep): displayName == role value,
        # mailNickname == role value with '.' replaced by '-'.
        if group["group_name"] != group["backing_role"]:
            errors.append(f"security-groups.csv: group_name '{group['group_name']}' != backing_role '{group['backing_role']}'")
        expected_nick = group["backing_role"].replace(".", "-")
        if group["mail_nickname"] != expected_nick:
            errors.append(f"security-groups.csv: mail_nickname '{group['mail_nickname']}' != '{expected_nick}'")

    # --- users ---
    if len(users) != EXPECTED_USER_COUNT:
        errors.append(f"users.csv: expected {EXPECTED_USER_COUNT} users, found {len(users)}")
    upn_locals = [u["upn_local"] for u in users]
    if len(upn_locals) != len(set(upn_locals)):
        errors.append("users.csv: duplicate upn_local values")
    for user in users:
        if user["app_role"] not in role_value_set:
            errors.append(f"users.csv: user '{user['upn_local']}' references unknown app_role '{user['app_role']}'")
        if user["default_hospital"] not in org_key_set:
            errors.append(f"users.csv: user '{user['upn_local']}' references unknown default_hospital '{user['default_hospital']}'")
        if not user["usage_location"]:
            errors.append(f"users.csv: user '{user['upn_local']}' has empty usage_location")
        if user["upn_local"] != user["upn_local"].lower():
            errors.append(f"users.csv: upn_local '{user['upn_local']}' must be lowercase")

    # --- reconciliation with the persona seed (data/synthetic/personas.csv) ---
    seed_by_nick = {p["mail_nickname"]: p for p in personas}
    users_by_local = {u["upn_local"]: u for u in users}
    if set(seed_by_nick) != set(users_by_local):
        only_seed = sorted(set(seed_by_nick) - set(users_by_local))
        only_users = sorted(set(users_by_local) - set(seed_by_nick))
        if only_seed:
            errors.append(f"users.csv missing personas present in personas.csv seed: {only_seed}")
        if only_users:
            errors.append(f"users.csv has personas absent from personas.csv seed: {only_users}")
    for nick, user in users_by_local.items():
        seed = seed_by_nick.get(nick)
        if seed is None:
            continue
        if user["display_name"] != seed["display_name"]:
            errors.append(f"users.csv/{nick}: display_name '{user['display_name']}' != seed '{seed['display_name']}'")
        if user["app_role"] != seed["app_role"]:
            errors.append(f"users.csv/{nick}: app_role '{user['app_role']}' != seed '{seed['app_role']}'")
        if user["default_hospital"] != seed["default_hospital"]:
            errors.append(f"users.csv/{nick}: default_hospital '{user['default_hospital']}' != seed '{seed['default_hospital']}'")

    # --- reconciliation with the Bicep parameter files (deploy source of truth) ---
    for param_path in BICEPPARAMS:
        if not param_path.exists():
            errors.append(f"missing bicepparam: {param_path.relative_to(REPO_ROOT)}")
            continue
        text = param_path.read_text(encoding="utf-8")
        block_count = text.count("mailNickname:")
        if block_count != EXPECTED_USER_COUNT:
            errors.append(f"{param_path.name}: expected {EXPECTED_USER_COUNT} personas (mailNickname entries), found {block_count}")
        for user in users:
            if f"mailNickname: '{user['upn_local']}'" not in text:
                errors.append(f"{param_path.name}: missing persona mailNickname '{user['upn_local']}'")
            if f"appRole: '{user['app_role']}'" not in text:
                errors.append(f"{param_path.name}: missing appRole '{user['app_role']}' referenced by users.csv")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the Entra demo-org master-data CSV artefacts.")
    parser.parse_args(argv)

    errors = validate()
    if errors:
        print("FAIL: Entra master-data validation found problems:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(
        "PASS: Entra master-data CSVs are internally consistent and reconcile with "
        "the persona seed and both bicepparam files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
