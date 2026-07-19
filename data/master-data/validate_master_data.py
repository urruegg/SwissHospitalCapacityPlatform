#!/usr/bin/env python3
"""Golden-source master-data contract gate.

Dependency-free (Python 3 stdlib only). Validates the capacity master-data CSVs
under ``data/master-data/capacity`` for file presence, primary-key uniqueness,
and foreign-key integrity. Exit 0 = PASS, non-zero = FAIL.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CAPACITY_DIR = REPO_ROOT / "data" / "master-data" / "capacity"

CAPACITY_FILES = [
    "01_dim_hospital.csv", "02_dim_specialty.csv", "03_dim_hospital_service.csv",
    "04_dim_disease.csv", "05_dim_treatment.csv", "06_dim_drg.csv",
    "07_dim_ward_capacityunit.csv", "08_fact_capacity_baseline.csv",
    "09_map_disease_treatment_specialty_service.csv",
]

PRIMARY_KEYS = {
    "01_dim_hospital.csv": "hospital_id",
    "02_dim_specialty.csv": "specialty_hospital_id",
    "03_dim_hospital_service.csv": "service_id",
    "04_dim_disease.csv": "disease_id",
    "05_dim_treatment.csv": "treatment_id",
    "06_dim_drg.csv": "drg_code",
    "07_dim_ward_capacityunit.csv": "ward_id",
    "09_map_disease_treatment_specialty_service.csv": "map_id",
}

FOREIGN_KEYS = [
    ("02_dim_specialty.csv", "hospital_id", "01_dim_hospital.csv", "hospital_id"),
    ("03_dim_hospital_service.csv", "hospital_id", "01_dim_hospital.csv", "hospital_id"),
    ("07_dim_ward_capacityunit.csv", "hospital_id", "01_dim_hospital.csv", "hospital_id"),
    ("05_dim_treatment.csv", "disease_id", "04_dim_disease.csv", "disease_id"),
    ("06_dim_drg.csv", "disease_id", "04_dim_disease.csv", "disease_id"),
    ("08_fact_capacity_baseline.csv", "hospital_id", "01_dim_hospital.csv", "hospital_id"),
    ("09_map_disease_treatment_specialty_service.csv", "hospital_id", "01_dim_hospital.csv", "hospital_id"),
    ("09_map_disease_treatment_specialty_service.csv", "disease_id", "04_dim_disease.csv", "disease_id"),
    ("09_map_disease_treatment_specialty_service.csv", "treatment_id", "05_dim_treatment.csv", "treatment_id"),
    ("09_map_disease_treatment_specialty_service.csv", "drg_code", "06_dim_drg.csv", "drg_code"),
    ("09_map_disease_treatment_specialty_service.csv", "capacity_unit_ward_id", "07_dim_ward_capacityunit.csv", "ward_id"),
]


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def validate_capacity(cap_dir: Path) -> list[str]:
    errors: list[str] = []
    tables: dict[str, list[dict[str, str]]] = {}

    for name in CAPACITY_FILES:
        path = cap_dir / name
        if not path.exists():
            errors.append(f"missing file: {name}")
            continue
        tables[name] = _read(path)

    for name, pk in PRIMARY_KEYS.items():
        rows = tables.get(name)
        if rows is None:
            continue
        seen: set[str] = set()
        for row in rows:
            key = row.get(pk, "")
            if key in seen:
                errors.append(f"{name}: duplicate primary key {pk}={key!r}")
            seen.add(key)

    for name, col, parent_name, parent_col in FOREIGN_KEYS:
        rows = tables.get(name)
        parent_rows = tables.get(parent_name)
        if rows is None or parent_rows is None:
            continue
        parent_keys = {r.get(parent_col, "") for r in parent_rows}
        for row in rows:
            val = row.get(col, "")
            if val and val not in parent_keys:
                errors.append(f"{name}: {col}={val!r} has no matching {parent_name}.{parent_col}")

    return errors


def main() -> int:
    errors = validate_capacity(CAPACITY_DIR)
    if errors:
        print("MASTER-DATA VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: capacity master-data valid ({len(CAPACITY_FILES)} tables).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
