"""Sprint 23 - Gold projection for the Curavias organisation spine.

Folds the legacy real-hospital ``gold.dim_hospital`` into the Curavias demo
organisation spine (issue #255). The Curavias master data
(``data/master-data/curavias-org-skills/``) was authored to shadow three real
hospitals **1:1** (beds/FTE grounded): ``CN`` (Uniklinik CuraNova) shadows USZ,
``CP`` (Kantonsspital Curalp) shadows the LUKS group, ``VT`` (Spital Vialta)
shadows Spital Zollikerberg. The fourth legacy hospital ``H_HSL`` (Hirslanden)
has **no Curavias tenant** and is dropped/parked so the demo is a clean
tenant<->hospital 1:1 (design + #255 T4/T5).

This transform:

* re-brands the surviving ``gold.dim_hospital`` rows to the Curavias identity
  (display name, code, tenant attributes, fictional geography) while keeping
  ``hospital_id`` as the primary key so every downstream fact, relationship and
  RLS role that keys on ``hospital_id`` keeps working unchanged;
* projects the Curavias ``dim_org_unit`` / ``dim_department`` /
  ``dim_capacity_unit`` sub-hierarchy onto the ``gold.*`` layer, **stripping the
  real-name provenance** (``grounded_on``) and real geography so no real
  hospital name/city/canton can surface in the demo.

The pure functions here are unit-tested without Spark (see
``tests/test_build_gold_org_spine.py``), following the external-signals /
CSA notebook pattern. ``run()`` is the Fabric Spark entrypoint.
"""
from __future__ import annotations

import sys

# Deterministic 1:1 legacy-hospital -> Curavias-tenant map. Grounded on the
# beds/FTE the Curavias generator authored to shadow each real hospital:
#   H_USZ  ~ CN (Uniklinik CuraNova)   ~900 beds / 8600 FTE
#   H_LUKS ~ CP (Kantonsspital Curalp) ~840 beds / 8600 FTE (LUKS 839 / 8628)
#   H_SZB  ~ VT (Spital Vialta)         174 beds / 1200 FTE (exact)
# H_HSL (Hirslanden) is intentionally ABSENT -> dropped/parked from the demo.
HOSPITAL_TENANT_MAP = {
    "H_USZ": "CN",
    "H_LUKS": "CP",
    "H_SZB": "VT",
}

# Real-name / real-geography provenance columns that must never reach gold.
_PROVENANCE_DROP = {"grounded_on"}


def _as_bool(value) -> bool:
    """Parse a CSV truthy token ('TRUE'/'true'/'1') to a real bool."""
    return str(value).strip().lower() in {"true", "1", "yes"}


def _index_by(rows: list[dict], key: str) -> dict[str, dict]:
    return {r[key]: r for r in rows}


def rebrand_hospital_dimension(
    hospital_rows: list[dict],
    tenant_rows: list[dict],
    org_unit_rows: list[dict],
) -> list[dict]:
    """Re-brand legacy ``gold.dim_hospital`` rows to Curavias identities.

    Drops any hospital with no Curavias tenant (H_HSL). Keeps ``hospital_id``
    as the key; overrides display name, short code and geography with Curavias
    values so no real hospital name/city/canton surfaces. Returns rows sorted
    by ``hospital_id`` for deterministic output.
    """
    tenants = _index_by(tenant_rows, "tenant_id")
    # The level-0 org unit shares its id with the tenant and carries the
    # fictional Curavias location (e.g. "Stadt Helvetia-Nord").
    top_org = {r["org_unit_id"]: r for r in org_unit_rows
               if str(r.get("org_level")) == "0"}

    out: list[dict] = []
    for h in hospital_rows:
        hid = h.get("hospital_id")
        tenant_id = HOSPITAL_TENANT_MAP.get(hid)
        if tenant_id is None:
            continue  # H_HSL and any unmapped legacy hospital: parked
        t = tenants[tenant_id]
        org = top_org.get(tenant_id, {})
        row = dict(h)
        row["hospital_id"] = hid
        row["tenant_id"] = tenant_id
        row["name"] = t["tenant_name"]
        row["short_name"] = tenant_id
        row["tenant_subdomain"] = t["tenant_subdomain"]
        row["archetype"] = t["archetype"]
        row["legal_form"] = t["legal_form"]
        row["canton"] = t["primary_canton"]
        row["city"] = org.get("location", "")
        row["source"] = "curavias-org-skills/dim_tenant"
        out.append(row)
    return sorted(out, key=lambda r: r["hospital_id"])


def _strip_provenance(row: dict) -> dict:
    """Drop real-name provenance columns from an org/skills gold row."""
    return {k: v for k, v in row.items() if k not in _PROVENANCE_DROP}


def to_gold_org_unit(row: dict) -> dict:
    """Project one ``dim_org_unit`` CSV row onto ``gold.dim_org_unit``."""
    out = _strip_provenance(row)
    out["is_active"] = _as_bool(row.get("is_active"))
    return out


def to_gold_department(row: dict) -> dict:
    """Project one ``dim_department`` CSV row onto ``gold.dim_department``."""
    return _strip_provenance(row)


def to_gold_capacity_unit(row: dict) -> dict:
    """Project one ``dim_capacity_unit`` CSV row onto ``gold.dim_capacity_unit``."""
    out = _strip_provenance(row)
    out["is_safety_critical"] = _as_bool(row.get("is_safety_critical"))
    return out


def build_org_spine_gold(
    hospital_rows: list[dict],
    tenant_rows: list[dict],
    org_unit_rows: list[dict],
    department_rows: list[dict],
    capacity_unit_rows: list[dict],
) -> dict[str, list[dict]]:
    """Pure core of ``run()``: build every org-spine gold table as plain rows.

    Returns ``{gold_table_name: [row, ...]}`` for the four org-spine tables the
    Curavias demo needs. The ``run()`` Spark bridge only has to read the source
    CSVs / ``gold.dim_hospital`` and write these rows as Delta, so all the
    re-brand + provenance-stripping logic stays unit-tested here (no Spark).
    """
    return {
        "dim_hospital": rebrand_hospital_dimension(
            hospital_rows, tenant_rows, org_unit_rows),
        "dim_org_unit": [to_gold_org_unit(r) for r in org_unit_rows],
        "dim_department": [to_gold_department(r) for r in department_rows],
        "dim_capacity_unit": [to_gold_capacity_unit(r) for r in capacity_unit_rows],
    }


# --------------------------------------------------------------------------- #
# Fabric Spark entrypoint (deploy-class; exercised only in the Fabric runtime) #
# --------------------------------------------------------------------------- #
# Lakehouse Files/ mount for the relocated Curavias master data (uploaded by
# upload_to_onelake.py to Files/master-data/curavias-org-skills/).
_MASTER_MOUNT = "/lakehouse/default/Files/master-data/curavias-org-skills"


def run() -> None:  # pragma: no cover - requires a live Fabric Spark session
    """Fabric entrypoint. Folds ``gold.dim_hospital`` + lands the org spine.

    Reads the Curavias master-data CSVs from the lakehouse ``Files/`` mount and
    the existing ``gold.dim_hospital`` (so capacity/governance columns survive
    the re-brand), applies :func:`build_org_spine_gold`, and overwrites each
    ``gold.*`` table as Delta with the sprint-09 governance stamp.
    """
    from _fabric_gold_io import (  # provided alongside this module in Files/
        read_csv_rows, rows_of_table, write_gold,
    )

    hospital_rows = rows_of_table("gold.dim_hospital")
    tables = build_org_spine_gold(
        hospital_rows=hospital_rows,
        tenant_rows=read_csv_rows(f"{_MASTER_MOUNT}/dim_tenant.csv"),
        org_unit_rows=read_csv_rows(f"{_MASTER_MOUNT}/dim_org_unit.csv"),
        department_rows=read_csv_rows(f"{_MASTER_MOUNT}/dim_department.csv"),
        capacity_unit_rows=read_csv_rows(f"{_MASTER_MOUNT}/dim_capacity_unit.csv"),
    )
    for name, rows in tables.items():
        write_gold(name, rows)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
