"""Ensure dim_persona TMDL and CSV seed align with the M1 synthetic persona contract.

M1 regression test for the Power BI Demoable Redesign. Verifies the persona seed
CSV exists, carries the required app roles, and that the dim_persona TMDL table
is present. The seed is the *temporary* M1 synthetic source that Sprint 12
replaces with a Fabric mirror of Entra ID; this check pins the seed contract
until that swap lands (design spec §6.1).

Exit 0 = PASS, 1 = FAIL.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

CSV_PATH = Path("data/synthetic/personas.csv")
TMDL_PATH = Path(
    "data-platform/reports/capacity-dashboard.SemanticModel/definition/tables/dim_persona.tmdl"
)

EXPECTED_ROLES = [
    "HCC.BedManager",
    "HCC.ORCoordinator",
    "HCC.OperationsLead",
    "HCC.DemoOperator",
    "HCC.SuperAdmin",
    "HCC.GuestReadOnly",
]
EXPECTED_COLUMNS = {"upn", "display_name", "app_role", "default_hospital"}


def main() -> int:
    if not CSV_PATH.exists():
        print(f"FAIL: {CSV_PATH} not found")
        return 1
    with CSV_PATH.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        header = set(reader.fieldnames or [])
    missing_cols = EXPECTED_COLUMNS - header
    if missing_cols:
        print(f"FAIL: personas.csv missing columns {sorted(missing_cols)}")
        return 1
    roles_found = {r["app_role"] for r in rows}
    missing = [r for r in EXPECTED_ROLES if r not in roles_found]
    if missing:
        print(f"FAIL: missing roles in seed {missing}")
        return 1
    if not TMDL_PATH.exists():
        print("FAIL: dim_persona.tmdl not found")
        return 1
    print(f"PASS: dim_persona seed ({len(rows)} rows) and TMDL present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
