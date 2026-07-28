#!/usr/bin/env python3
"""Golden-source master-data contract gate.

Dependency-free (Python 3 stdlib only). Validates three master-data domains:

* ``data/master-data/capacity`` - capacity dimensions/facts: file presence,
  primary-key uniqueness, foreign-key integrity.
* ``data/master-data/curavias-org-skills`` - the Sprint 23 Curavias organisation
  spine + skills-evidence domain: file presence, primary-key uniqueness,
  foreign-key integrity, **GLN mod-10** check digits, **enum-domain** membership,
  and **load-order** (parents before children).
* ``data/master-data/bva`` - Sprint 33 BVA cost/BOM master data: file presence,
  primary-key uniqueness, tenant foreign-key integrity, enum-domain membership,
  and ROM ledger reconciliation.

This is the silver-gate logic (design D5): when the on-demand pipeline lands the
synthetic extracts, the same checks run against landed Bronze and quarantine bad
rows in Silver. Exit 0 = PASS, non-zero = FAIL.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CAPACITY_DIR = REPO_ROOT / "data" / "master-data" / "capacity"
ORG_SKILLS_DIR = REPO_ROOT / "data" / "master-data" / "curavias-org-skills"
BVA_DIR = REPO_ROOT / "data" / "master-data" / "bva"

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


# --------------------------------------------------------------------------- #
# Curavias organisation spine + skills-evidence domain (Sprint 23, design D5)  #
# --------------------------------------------------------------------------- #

# Deterministic load order: parents before children. Also the authoritative
# file list for presence checks.
ORG_SKILLS_LOAD_ORDER = [
    "dim_tenant.csv",
    "dim_org_unit.csv",
    "dim_department.csv",
    "dim_capacity_unit.csv",
    "dim_occupation_role.csv",
    "dim_issuing_authority.csv",
    "dim_assurance_level.csv",
    "dim_proficiency_level.csv",
    "dim_skill.csv",
    "dim_specialisation.csv",
    "dim_workforce_position.csv",
    "dim_employee.csv",
    "dim_work_id_profile.csv",
    "fact_skill_assertion.csv",
    "fact_skill_demand.csv",
    "bridge_role_skill_demand_template.csv",
    "bridge_worker_unit_eligibility.csv",
    "map_skill_crosswalk.csv",
    "fact_skill_gap.csv",
    "fact_skills_manager_sync_log.csv",
]

ORG_SKILLS_PRIMARY_KEYS = {
    "dim_tenant.csv": "tenant_id",
    "dim_org_unit.csv": "org_unit_id",
    "dim_department.csv": "department_id",
    "dim_capacity_unit.csv": "unit_id",
    "dim_occupation_role.csv": "occupation_id",
    "dim_issuing_authority.csv": "authority_id",
    "dim_assurance_level.csv": "assurance_level",
    "dim_proficiency_level.csv": "proficiency_level",
    "dim_skill.csv": "skill_id",
    "dim_specialisation.csv": "specialisation_id",
    "dim_workforce_position.csv": "position_id",
    "dim_employee.csv": "employee_id",
    "dim_work_id_profile.csv": "work_id_profile_id",
    "fact_skill_assertion.csv": "assertion_id",
    "fact_skill_demand.csv": "demand_id",
    "bridge_role_skill_demand_template.csv": "template_id",
    "bridge_worker_unit_eligibility.csv": "eligibility_id",
    "map_skill_crosswalk.csv": "crosswalk_id",
    "fact_skill_gap.csv": "gap_id",
    "fact_skills_manager_sync_log.csv": "sync_id",
}

# (child_file, child_col, parent_file, parent_col). Empty child values are skipped
# (nullable FK). assurance_level / proficiency_level are validated as FKs to their
# dimension tables (covers the L0-L4 and 1-5 domains).
ORG_SKILLS_FOREIGN_KEYS = [
    ("dim_org_unit.csv", "tenant_id", "dim_tenant.csv", "tenant_id"),
    ("dim_org_unit.csv", "parent_org_unit_id", "dim_org_unit.csv", "org_unit_id"),
    ("dim_department.csv", "tenant_id", "dim_tenant.csv", "tenant_id"),
    ("dim_department.csv", "site_id", "dim_org_unit.csv", "org_unit_id"),
    ("dim_capacity_unit.csv", "tenant_id", "dim_tenant.csv", "tenant_id"),
    ("dim_capacity_unit.csv", "department_id", "dim_department.csv", "department_id"),
    ("dim_skill.csv", "anchor_authority_id", "dim_issuing_authority.csv", "authority_id"),
    ("dim_skill.csv", "default_min_assurance", "dim_assurance_level.csv", "assurance_level"),
    ("dim_specialisation.csv", "related_skill_id", "dim_skill.csv", "skill_id"),
    ("dim_workforce_position.csv", "tenant_id", "dim_tenant.csv", "tenant_id"),
    ("dim_workforce_position.csv", "department_id", "dim_department.csv", "department_id"),
    ("dim_workforce_position.csv", "occupation_id", "dim_occupation_role.csv", "occupation_id"),
    ("dim_employee.csv", "tenant_id", "dim_tenant.csv", "tenant_id"),
    ("dim_employee.csv", "home_department_id", "dim_department.csv", "department_id"),
    ("dim_employee.csv", "position_id", "dim_workforce_position.csv", "position_id"),
    ("dim_employee.csv", "primary_occupation_id", "dim_occupation_role.csv", "occupation_id"),
    ("dim_work_id_profile.csv", "employee_id", "dim_employee.csv", "employee_id"),
    ("fact_skill_assertion.csv", "employee_id", "dim_employee.csv", "employee_id"),
    ("fact_skill_assertion.csv", "skill_id", "dim_skill.csv", "skill_id"),
    ("fact_skill_assertion.csv", "issuing_authority_id", "dim_issuing_authority.csv", "authority_id"),
    ("fact_skill_assertion.csv", "assurance_level", "dim_assurance_level.csv", "assurance_level"),
    ("fact_skill_assertion.csv", "proficiency_level", "dim_proficiency_level.csv", "proficiency_level"),
    ("fact_skill_demand.csv", "tenant_id", "dim_tenant.csv", "tenant_id"),
    ("fact_skill_demand.csv", "department_id", "dim_department.csv", "department_id"),
    ("fact_skill_demand.csv", "unit_id", "dim_capacity_unit.csv", "unit_id"),
    ("fact_skill_demand.csv", "skill_id", "dim_skill.csv", "skill_id"),
    ("fact_skill_demand.csv", "min_assurance", "dim_assurance_level.csv", "assurance_level"),
    ("fact_skill_demand.csv", "min_proficiency", "dim_proficiency_level.csv", "proficiency_level"),
    ("bridge_role_skill_demand_template.csv", "skill_id", "dim_skill.csv", "skill_id"),
    ("bridge_role_skill_demand_template.csv", "min_assurance", "dim_assurance_level.csv", "assurance_level"),
    ("bridge_role_skill_demand_template.csv", "min_proficiency", "dim_proficiency_level.csv", "proficiency_level"),
    ("bridge_worker_unit_eligibility.csv", "employee_id", "dim_employee.csv", "employee_id"),
    ("bridge_worker_unit_eligibility.csv", "unit_id", "dim_capacity_unit.csv", "unit_id"),
    ("bridge_worker_unit_eligibility.csv", "tenant_id", "dim_tenant.csv", "tenant_id"),
    ("map_skill_crosswalk.csv", "internal_skill_id", "dim_skill.csv", "skill_id"),
    ("fact_skill_gap.csv", "tenant_id", "dim_tenant.csv", "tenant_id"),
    ("fact_skill_gap.csv", "department_id", "dim_department.csv", "department_id"),
    ("fact_skill_gap.csv", "unit_id", "dim_capacity_unit.csv", "unit_id"),
    ("fact_skill_gap.csv", "skill_id", "dim_skill.csv", "skill_id"),
]

# (file, column) -> allowed literal value set. Empty values are skipped.
ORG_SKILLS_ENUM_DOMAINS = {
    ("dim_org_unit.csv", "entity_type"): {
        "Hospital-Group", "Legal-Entity", "Hospital-Org", "Site",
        "Department", "Governance-Body",
    },
    ("dim_employee.csv", "employment_status"): {"active", "active_parttime", "on_leave"},
    ("dim_work_id_profile.csv", "consent_status"): {"granted", "revoked", "pending"},
    ("dim_work_id_profile.csv", "external_system"): {"work_id"},
    ("fact_skill_assertion.csv", "verification_status"): {"register-verified", "issuer-confirmed", "self"},
    ("fact_skill_assertion.csv", "evidence_type"): {
        "registration", "diploma", "certificate", "signoff", "experience", "self_declared",
    },
    ("fact_skill_assertion.csv", "source_system"): {"HRIS", "LMS", "work_id"},
    ("fact_skill_assertion.csv", "sensitivity_class"): {"PII-personal"},
    ("fact_skill_assertion.csv", "consent_basis"): {"employment_contract", "worker_consent"},
    ("dim_capacity_unit.csv", "unit_type"): {
        "ward", "ICU", "OR_slot", "ED_bay", "delivery_room",
        "dialysis_station", "imaging", "transport",
    },
    ("dim_issuing_authority.csv", "authority_kind"): {
        "federal_register", "specialist_body", "cert_body", "education",
        "foreign_recognition", "labour_market", "language", "research", "taxonomy",
    },
    ("dim_skill.csv", "skill_category"): {
        "clinical", "regulatory", "technical", "digital", "leadership", "language",
    },
    ("dim_skill.csv", "skill_type"): {"knowledge", "skill", "transversal", "language"},
}

# (file, column) columns carrying a 13-digit GS1 worker GLN - the consent-gated
# golden thread, generated with a real mod-10 check digit (``person_gln``). Empty
# values are skipped. Facility GLNs on dim_org_unit / dim_department are
# structured synthetic identifiers (not GS1 mod-10 valid) and are intentionally
# excluded from the check-digit gate.
ORG_SKILLS_GLN_COLUMNS = [
    ("dim_employee.csv", "worker_gln"),
    ("dim_work_id_profile.csv", "worker_gln"),
    ("fact_skill_assertion.csv", "worker_gln"),
    ("bridge_worker_unit_eligibility.csv", "worker_gln"),
]


# --------------------------------------------------------------------------- #
# BVA cost/BOM master-data domain (Sprint 33 WS-A, Task A1)                   #
# --------------------------------------------------------------------------- #

BVA_FILES = [
    "bva_cost_element.csv",
    "bva_hospital_profile.csv",
    "bva_bom.csv",
    "bva_azure_cost_weekly.csv",
    "bva_copilot_usage_weekly.csv",
    "bva_team_effort.csv",
    "bva_fx_rate.csv",
]

BVA_PRIMARY_KEYS = {
    "bva_cost_element.csv": "element_id",
    "bva_hospital_profile.csv": "tenant_id",
    "bva_bom.csv": "resource_id",
    "bva_copilot_usage_weekly.csv": "iso_week",
    "bva_fx_rate.csv": "period",
}

BVA_FOREIGN_KEYS = [
    ("bva_hospital_profile.csv", "tenant_id", "dim_tenant.csv", "tenant_id"),
]

BVA_ENUM_DOMAINS = {
    ("bva_cost_element.csv", "cost_type"): {"one_time", "annual_run"},
    ("bva_hospital_profile.csv", "archetype"): {"acute", "rehab", "spitex"},
}

BVA_REQUIRED_NUMERIC_COLUMNS = [
    ("bva_cost_element.csv", "amount_chf"),
    ("bva_hospital_profile.csv", "beds"),
    ("bva_hospital_profile.csv", "occupancy_target"),
    ("bva_azure_cost_weekly.csv", "cost_usd"),
    ("bva_copilot_usage_weekly.csv", "aiu"),
    ("bva_copilot_usage_weekly.csv", "tokens_in"),
    ("bva_copilot_usage_weekly.csv", "tokens_out"),
    ("bva_copilot_usage_weekly.csv", "cost_usd"),
    ("bva_team_effort.csv", "elective_hours"),
    ("bva_team_effort.csv", "role_rate_chf"),
    ("bva_fx_rate.csv", "usd_to_chf"),
]

BVA_LEDGER_TARGETS = {
    "one_time": 1_300_000.0,
    "annual_run": 1_250_000.0,
}


def gln_is_valid(gln: str) -> bool:
    """GS1 mod-10 check for a 13-digit GLN (weights 1/3 from the right)."""
    if len(gln) != 13 or not gln.isdigit():
        return False
    body, check = gln[:12], gln[12]
    total = sum(int(ch) * (3 if i % 2 == 0 else 1) for i, ch in enumerate(reversed(body)))
    return str((10 - (total % 10)) % 10) == check


def validate_org_skills(dir_path: Path) -> list[str]:
    errors: list[str] = []
    tables: dict[str, list[dict[str, str]]] = {}

    for name in ORG_SKILLS_LOAD_ORDER:
        path = dir_path / name
        if not path.exists():
            errors.append(f"missing file: {name}")
            continue
        tables[name] = _read(path)

    # Primary-key uniqueness.
    for name, pk in ORG_SKILLS_PRIMARY_KEYS.items():
        rows = tables.get(name)
        if rows is None:
            continue
        seen: set[str] = set()
        for row in rows:
            key = row.get(pk, "")
            if key in seen:
                errors.append(f"{name}: duplicate primary key {pk}={key!r}")
            seen.add(key)

    # Foreign-key integrity.
    for name, col, parent_name, parent_col in ORG_SKILLS_FOREIGN_KEYS:
        rows = tables.get(name)
        parent_rows = tables.get(parent_name)
        if rows is None or parent_rows is None:
            continue
        parent_keys = {r.get(parent_col, "") for r in parent_rows}
        for row in rows:
            val = row.get(col, "")
            if val and val not in parent_keys:
                errors.append(f"{name}: {col}={val!r} has no matching {parent_name}.{parent_col}")

    # Enum-domain membership.
    for (name, col), allowed in ORG_SKILLS_ENUM_DOMAINS.items():
        rows = tables.get(name)
        if rows is None:
            continue
        for row in rows:
            val = row.get(col, "")
            if val and val not in allowed:
                errors.append(f"{name}: {col}={val!r} not in domain {sorted(allowed)}")

    # GLN mod-10 check digit.
    for name, col in ORG_SKILLS_GLN_COLUMNS:
        rows = tables.get(name)
        if rows is None:
            continue
        for row in rows:
            val = row.get(col, "")
            if val and not gln_is_valid(val):
                errors.append(f"{name}: {col}={val!r} fails GLN mod-10 check")

    # Load-order: every FK parent must load before (or with) its child.
    position = {name: i for i, name in enumerate(ORG_SKILLS_LOAD_ORDER)}
    for name, col, parent_name, parent_col in ORG_SKILLS_FOREIGN_KEYS:
        if name == parent_name:
            continue  # self-reference (hierarchy) is resolved within one load
        if position.get(parent_name, -1) > position.get(name, 1 << 30):
            errors.append(
                f"load-order: {parent_name} (parent of {name}.{col}) must load before {name}"
            )

    return errors


def validate_bva(bva_dir: Path, tenant_dir: Path | None = None) -> list[str]:
    errors: list[str] = []
    tables: dict[str, list[dict[str, str]]] = {}
    tenant_tables: dict[str, list[dict[str, str]]] = {}
    tenant_path = (tenant_dir or ORG_SKILLS_DIR) / "dim_tenant.csv"

    for name in BVA_FILES:
        path = bva_dir / name
        if not path.exists():
            errors.append(f"missing file: {name}")
            continue
        tables[name] = _read(path)

    if not tenant_path.exists():
        errors.append(f"missing file: {tenant_path.name}")
    else:
        tenant_tables["dim_tenant.csv"] = _read(tenant_path)

    # Primary-key uniqueness.
    for name, pk in BVA_PRIMARY_KEYS.items():
        rows = tables.get(name)
        if rows is None:
            continue
        seen: set[str] = set()
        for row in rows:
            key = row.get(pk, "")
            if key in seen:
                errors.append(f"{name}: duplicate primary key {pk}={key!r}")
            seen.add(key)

    # Foreign-key integrity. The BVA hospital profile references dim_tenant in
    # the curavias-org-skills domain, so parent tables are loaded separately.
    for name, col, parent_name, parent_col in BVA_FOREIGN_KEYS:
        rows = tables.get(name)
        parent_rows = tenant_tables.get(parent_name)
        if rows is None or parent_rows is None:
            continue
        parent_keys = {r.get(parent_col, "") for r in parent_rows}
        for row in rows:
            val = row.get(col, "")
            if val and val not in parent_keys:
                errors.append(f"{name}: {col}={val!r} has no matching {parent_name}.{parent_col}")

    # Enum-domain membership.
    for (name, col), allowed in BVA_ENUM_DOMAINS.items():
        rows = tables.get(name)
        if rows is None:
            continue
        for row in rows:
            val = row.get(col, "")
            if val and val not in allowed:
                errors.append(f"{name}: {col}={val!r} not in domain {sorted(allowed)}")

    # BVA is PHI-free synthetic cost/BOM data. Keep the gate scoped to this data
    # product: numeric evidence columns must be populated and parse as numbers.
    for name, col in BVA_REQUIRED_NUMERIC_COLUMNS:
        rows = tables.get(name)
        if rows is None:
            continue
        for row in rows:
            val = row.get(col, "")
            if val == "":
                errors.append(f"{name}: {col} must not be empty")
                continue
            try:
                float(val)
            except ValueError:
                errors.append(f"{name}: {col}={val!r} must be numeric")

    ledger_totals = {cost_type: 0.0 for cost_type in BVA_LEDGER_TARGETS}
    for row in tables.get("bva_cost_element.csv", []):
        cost_type = row.get("cost_type", "")
        if cost_type not in ledger_totals:
            continue
        try:
            ledger_totals[cost_type] += float(row.get("amount_chf", ""))
        except ValueError:
            continue
    for cost_type, expected in BVA_LEDGER_TARGETS.items():
        actual = ledger_totals[cost_type]
        if actual != expected:
            errors.append(
                f"bva_cost_element.csv: ledger ROM mismatch for {cost_type}: "
                f"expected {expected:g}, got {actual:g}"
            )

    return errors


def main() -> int:
    errors = validate_capacity(CAPACITY_DIR)
    errors += validate_org_skills(ORG_SKILLS_DIR)
    errors += validate_bva(BVA_DIR)
    if errors:
        print("MASTER-DATA VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(
        f"OK: capacity master-data valid ({len(CAPACITY_FILES)} tables); "
        f"curavias org/skills master-data valid ({len(ORG_SKILLS_LOAD_ORDER)} tables); "
        f"bva master-data valid ({len(BVA_FILES)} tables)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
