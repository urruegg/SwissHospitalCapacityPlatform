"""Unit tests for the Curavias org-spine gold projection (issue #255).

Runs without Spark against the real relocated master data CSVs, asserting the
bug-fix invariants: legacy real hospital names/geography never surface, H_HSL is
dropped, the demo is a clean tenant<->hospital 1:1, and real-name provenance is
stripped from the org-spine gold tables.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
PKG_DIR = Path(__file__).resolve().parents[1]
MASTER = REPO_ROOT / "data" / "master-data" / "curavias-org-skills"
CAPACITY = REPO_ROOT / "data" / "master-data" / "capacity"

sys.path.insert(0, str(PKG_DIR))

from build_gold_org_spine import (  # noqa: E402
    HOSPITAL_KEYED_CAPACITY_TABLES,
    HOSPITAL_TENANT_MAP,
    build_org_spine_gold,
    prune_orphan_hospital_rows,
    rebrand_hospital_dimension,
    surviving_hospital_ids,
    to_gold_capacity_unit,
    to_gold_department,
    to_gold_org_unit,
)

# Distinctive real identifiers that must never reach a demo display/geo column.
# Deliberately specific (full real names / cities / source domains) to avoid
# false positives on legitimate Curavias text (e.g. archetype "Universitaeres
# Zentrumsspital"). The opaque hospital_id PK is excluded from the scan below
# because it is an internal join key, not a surfaced name.
_REAL_NAME_FRAGMENTS = [
    "Universitatsspital", "Universit\u00e4tsspital", "Luzerner", "Luzern",
    "Hirslanden", "Zollikerberg", "Z\u00fcrich", "Zurich",
    "usz.", "luks.", "hirslanden.", "spitalzollikerberg.",
]


def _read(path: Path) -> list[dict]:
    # utf-8-sig tolerates the capacity CSVs' UTF-8 BOM and plain UTF-8 alike.
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _hospitals() -> list[dict]:
    return _read(CAPACITY / "01_dim_hospital.csv")


def _tenants() -> list[dict]:
    return _read(MASTER / "dim_tenant.csv")


def _org_units() -> list[dict]:
    return _read(MASTER / "dim_org_unit.csv")


def test_hslinkl_hospital_is_dropped():
    out = rebrand_hospital_dimension(_hospitals(), _tenants(), _org_units())
    ids = {r["hospital_id"] for r in out}
    assert "H_HSL" not in ids
    assert len(out) == 3


def test_rebrand_is_bijective_1to1():
    out = rebrand_hospital_dimension(_hospitals(), _tenants(), _org_units())
    tenant_ids = [r["tenant_id"] for r in out]
    assert sorted(tenant_ids) == ["CN", "CP", "VT"]
    assert len(set(tenant_ids)) == len(tenant_ids)  # no tenant reused
    assert set(HOSPITAL_TENANT_MAP.values()) == set(tenant_ids)


def test_rebrand_uses_curavias_display_names():
    out = rebrand_hospital_dimension(_hospitals(), _tenants(), _org_units())
    names = {r["name"] for r in out}
    assert names == {
        "Uniklinik CuraNova",
        "Kantonsspital Curalp",
        "Spital Vialta",
    }


def test_no_real_names_or_geography_in_rebranded_hospitals():
    out = rebrand_hospital_dimension(_hospitals(), _tenants(), _org_units())
    for row in out:
        # Scan EVERY output column (except the opaque hospital_id join key) so a
        # future dim_hospital schema column cannot silently leak a real value.
        for col, val in row.items():
            if col == "hospital_id":
                continue
            text = str(val)
            for frag in _REAL_NAME_FRAGMENTS:
                assert frag not in text, (
                    f"real fragment {frag!r} leaked in column {col!r}={text!r}"
                )
        # Positive geography guard: only fictional Curavias cantons survive.
        assert row["canton"] in {"HN", "CA"}


def test_hospital_id_preserved_as_key():
    out = rebrand_hospital_dimension(_hospitals(), _tenants(), _org_units())
    ids = sorted(r["hospital_id"] for r in out)
    assert ids == ["H_LUKS", "H_SZB", "H_USZ"]
    for row in out:
        assert row["tenant_id"] == HOSPITAL_TENANT_MAP[row["hospital_id"]]


def test_output_is_deterministic():
    a = rebrand_hospital_dimension(_hospitals(), _tenants(), _org_units())
    b = rebrand_hospital_dimension(_hospitals(), _tenants(), _org_units())
    assert a == b
    assert [r["hospital_id"] for r in a] == sorted(r["hospital_id"] for r in a)


def test_org_spine_gold_strips_grounded_on():
    for row in _org_units():
        assert "grounded_on" not in to_gold_org_unit(row)
    for row in _read(MASTER / "dim_department.csv"):
        assert "grounded_on" not in to_gold_department(row)


def test_org_unit_is_active_cast_to_bool():
    rows = [to_gold_org_unit(r) for r in _org_units()]
    assert all(isinstance(r["is_active"], bool) for r in rows)


def test_capacity_unit_safety_flag_cast_to_bool():
    rows = [to_gold_capacity_unit(r) for r in _read(MASTER / "dim_capacity_unit.csv")]
    assert all(isinstance(r["is_safety_critical"], bool) for r in rows)
    assert any(r["is_safety_critical"] for r in rows)  # at least one OR_slot


# --- run() aggregator (the Fabric glue's pure core) ---------------------------

def _org_spine_gold() -> dict:
    return build_org_spine_gold(
        hospital_rows=_hospitals(),
        tenant_rows=_tenants(),
        org_unit_rows=_org_units(),
        department_rows=_read(MASTER / "dim_department.csv"),
        capacity_unit_rows=_read(MASTER / "dim_capacity_unit.csv"),
    )


def test_org_spine_gold_produces_the_four_tables():
    out = _org_spine_gold()
    assert set(out) == {
        "dim_hospital", "dim_org_unit", "dim_department", "dim_capacity_unit",
    }


def test_org_spine_gold_dim_hospital_is_rebranded_1to1():
    out = _org_spine_gold()
    hosp = out["dim_hospital"]
    assert len(hosp) == 3
    assert {r["name"] for r in hosp} == {
        "Uniklinik CuraNova", "Kantonsspital Curalp", "Spital Vialta",
    }
    assert sorted(r["tenant_id"] for r in hosp) == ["CN", "CP", "VT"]


def test_org_spine_gold_projections_preserve_row_counts_and_strip_provenance():
    out = _org_spine_gold()
    assert len(out["dim_org_unit"]) == len(_org_units())
    assert len(out["dim_department"]) == len(_read(MASTER / "dim_department.csv"))
    assert len(out["dim_capacity_unit"]) == len(_read(MASTER / "dim_capacity_unit.csv"))
    for table in ("dim_org_unit", "dim_department", "dim_capacity_unit"):
        for row in out[table]:
            assert "grounded_on" not in row


def test_org_spine_gold_leaks_no_real_names():
    out = _org_spine_gold()
    for rows in out.values():
        for row in rows:
            for col, val in row.items():
                if col == "hospital_id":
                    continue
                for frag in _REAL_NAME_FRAGMENTS:
                    assert frag not in str(val), (
                        f"real fragment {frag!r} leaked in {col!r}={val!r}"
                    )


# --- H_HSL orphan prune of hospital-keyed capacity gold (issue #349) ----------

def _capacity(name: str) -> list[dict]:
    return _read(CAPACITY / name)


def test_surviving_hospital_ids_are_the_three_curavias_hospitals():
    assert surviving_hospital_ids() == {"H_USZ", "H_LUKS", "H_SZB"}
    # The surviving set is exactly the domain of the 1:1 tenant map.
    assert surviving_hospital_ids() == set(HOSPITAL_TENANT_MAP)


def test_capacity_table_registry_covers_every_hospital_keyed_gold_table():
    # These are the capacity gold tables that carry hospital_id and would
    # otherwise orphan the dropped H_HSL rows under the (Blank) member.
    assert HOSPITAL_KEYED_CAPACITY_TABLES == (
        "dim_specialty",
        "dim_hospital_service",
        "dim_ward_capacityunit",
        "fact_capacity_baseline",
        "map_disease_treatment_specialty_service",
    )


def test_prune_drops_hsl_rows_only():
    rows = _capacity("02_dim_specialty.csv")
    assert any(r["hospital_id"] == "H_HSL" for r in rows)  # precondition
    pruned = prune_orphan_hospital_rows(rows)
    assert all(r["hospital_id"] != "H_HSL" for r in pruned)
    assert {r["hospital_id"] for r in pruned} <= surviving_hospital_ids()
    # Nothing but H_HSL rows removed.
    dropped = len(rows) - len(pruned)
    assert dropped == sum(1 for r in rows if r["hospital_id"] == "H_HSL")


def test_prune_is_idempotent():
    rows = _capacity("08_fact_capacity_baseline.csv")
    once = prune_orphan_hospital_rows(rows)
    twice = prune_orphan_hospital_rows(once)
    assert once == twice


def test_prune_preserves_surviving_rows_and_order():
    rows = _capacity("09_map_disease_treatment_specialty_service.csv")
    pruned = prune_orphan_hospital_rows(rows)
    expected = [r for r in rows if r["hospital_id"] in surviving_hospital_ids()]
    assert pruned == expected  # order + row content preserved


def test_prune_removes_all_hsl_from_every_capacity_table():
    for name in (
        "02_dim_specialty.csv",
        "03_dim_hospital_service.csv",
        "07_dim_ward_capacityunit.csv",
        "08_fact_capacity_baseline.csv",
        "09_map_disease_treatment_specialty_service.csv",
    ):
        rows = _capacity(name)
        pruned = prune_orphan_hospital_rows(rows)
        assert not any(r["hospital_id"] == "H_HSL" for r in pruned), name
        assert len(pruned) < len(rows), f"{name}: expected H_HSL rows removed"


def test_prune_accepts_explicit_surviving_set():
    rows = _capacity("07_dim_ward_capacityunit.csv")
    pruned = prune_orphan_hospital_rows(rows, {"H_LUKS"})
    assert {r["hospital_id"] for r in pruned} == {"H_LUKS"}
