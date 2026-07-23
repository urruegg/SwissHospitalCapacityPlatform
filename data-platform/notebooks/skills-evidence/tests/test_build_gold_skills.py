"""Unit tests for the Curavias skills-domain gold projection (issue #255).

Runs without Spark against the real master-data CSVs, asserting the WS-C2
invariants: supply/demand/gap/eligibility project cleanly, the care-setting
split is explicit on demand/gap and derivable (via ISCO) for occupation-grained
tables, the live-vs-simulated ``source_mode`` badge reads a real flag, and the
domains are validated (never invented).
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
PKG_DIR = Path(__file__).resolve().parents[1]
MASTER = REPO_ROOT / "data" / "master-data" / "curavias-org-skills"

sys.path.insert(0, str(PKG_DIR))

from build_gold_skills import (  # noqa: E402
    CARE_SETTINGS,
    ISCO_CARE_SETTING,
    SOURCE_MODES,
    derive_occupation_care_setting,
    to_gold_care_setting,
    to_gold_demand_template,
    to_gold_eligibility,
    to_gold_occupation_role,
    to_gold_skill,
    to_gold_skill_assertion,
    to_gold_skill_demand,
    to_gold_skill_gap,
)


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _occupations() -> list[dict]:
    return _read(MASTER / "dim_occupation_role.csv")


def _care_setting_ids() -> set:
    return {r["care_setting_id"] for r in _read(MASTER / "dim_care_setting.csv")}


# --- care-setting dimension + ISCO derivation ---------------------------------

def test_care_setting_dim_is_bed_and_ops():
    rows = [to_gold_care_setting(r) for r in _read(MASTER / "dim_care_setting.csv")]
    assert {r["care_setting_id"] for r in rows} == {"bed", "ops"}


def test_every_occupation_isco_is_classified():
    for r in _occupations():
        assert str(r["isco_08_code"]).strip() in ISCO_CARE_SETTING


def test_derive_occupation_care_setting_maps_all_roles():
    occ = _occupations()
    mapping = derive_occupation_care_setting(occ)
    assert len(mapping) == len(occ)
    assert set(mapping.values()) <= CARE_SETTINGS
    # Spot-check the two poles: a nurse is bed, a physician is ops.
    assert mapping["OCC-RN"] == "bed"
    assert mapping["OCC-PHYS-SURG"] == "ops"


def test_derive_fails_fast_on_unknown_isco():
    with pytest.raises(ValueError):
        derive_occupation_care_setting([
            {"occupation_id": "OCC-X", "isco_08_code": "9999"},
        ])


def test_occupation_role_gold_carries_derived_care_setting():
    mapping = derive_occupation_care_setting(_occupations())
    rows = [to_gold_occupation_role(r, mapping) for r in _occupations()]
    assert all(r["care_setting_id"] in CARE_SETTINGS for r in rows)


# --- demand templates (occupation-grained, derived) ---------------------------

def test_demand_template_derives_care_setting_from_occupation():
    mapping = derive_occupation_care_setting(_occupations())
    tmpl = _read(MASTER / "bridge_role_skill_demand_template.csv")
    rows = [to_gold_demand_template(r, mapping) for r in tmpl]
    assert all(r["care_setting_id"] in CARE_SETTINGS for r in rows)
    assert all(isinstance(r["is_mandatory"], bool) for r in rows)
    # A template on a nursing role is bed; on a physician role is ops.
    by_id = {r["template_id"]: r for r in rows}
    for r in rows:
        expected = mapping[r["applies_to_id"]]
        assert by_id[r["template_id"]]["care_setting_id"] == expected


def test_demand_template_rejects_non_occupation_scope():
    mapping = derive_occupation_care_setting(_occupations())
    with pytest.raises(ValueError):
        to_gold_demand_template(
            {"template_id": "T-X", "applies_to_type": "unit",
             "applies_to_id": "CN-D1-U02", "is_mandatory": "TRUE"},
            mapping,
        )


# --- demand fact (explicit care_setting + source_mode) ------------------------

def test_demand_gold_validates_domains_and_casts_numerics():
    valid = _care_setting_ids()
    rows = [to_gold_skill_demand(r) for r in _read(MASTER / "fact_skill_demand.csv")]
    for r in rows:
        assert r["care_setting_id"] in valid
        assert r["source_mode"] in SOURCE_MODES
        assert isinstance(r["headcount_required"], int)
        assert isinstance(r["min_proficiency"], int)


def test_demand_has_both_care_settings_and_both_source_modes():
    rows = [to_gold_skill_demand(r) for r in _read(MASTER / "fact_skill_demand.csv")]
    assert {r["care_setting_id"] for r in rows} == {"bed", "ops"}
    assert {r["source_mode"] for r in rows} == {"live", "simulated"}


def test_demand_gold_rejects_bad_care_setting():
    with pytest.raises(ValueError):
        to_gold_skill_demand({
            "demand_id": "DEM-BAD", "care_setting_id": "theatre",
            "source_mode": "live", "min_proficiency": "3",
            "headcount_required": "1",
        })


def test_demand_gold_rejects_bad_source_mode():
    with pytest.raises(ValueError):
        to_gold_skill_demand({
            "demand_id": "DEM-BAD", "care_setting_id": "bed",
            "source_mode": "guessed", "min_proficiency": "3",
            "headcount_required": "1",
        })


# --- gap fact (explicit care_setting + source_mode, consistent with demand) ---

def test_gap_gold_validates_domains_and_casts_numerics():
    rows = [to_gold_skill_gap(r) for r in _read(MASTER / "fact_skill_gap.csv")]
    for r in rows:
        assert r["care_setting_id"] in CARE_SETTINGS
        assert r["source_mode"] in SOURCE_MODES
        for num in ("headcount_required", "valid_supply", "gap",
                    "redeploy_candidates_count"):
            assert isinstance(r[num], int)


def test_gap_care_setting_matches_demand_on_shared_grain():
    key = ("tenant_id", "department_id", "unit_id", "skill_id", "shift_window")
    dem = {tuple(r[k] for k in key): r
           for r in (to_gold_skill_demand(x)
                     for x in _read(MASTER / "fact_skill_demand.csv"))}
    for g in (to_gold_skill_gap(x) for x in _read(MASTER / "fact_skill_gap.csv")):
        d = dem[tuple(g[k] for k in key)]
        assert g["care_setting_id"] == d["care_setting_id"]
        assert g["source_mode"] == d["source_mode"]


# --- supply (assertion) + eligibility -----------------------------------------

def test_assertion_gold_validates_source_mode():
    rows = [to_gold_skill_assertion(r)
            for r in _read(MASTER / "fact_skill_assertion.csv")]
    assert all(r["source_mode"] in SOURCE_MODES for r in rows)
    assert all(isinstance(r["proficiency_level"], int) for r in rows)


def test_skill_gold_casts_boolean_flags():
    rows = [to_gold_skill(r) for r in _read(MASTER / "dim_skill.csv")]
    assert all(isinstance(r["is_safety_critical"], bool) for r in rows)
    assert all(isinstance(r["has_expiry"], bool) for r in rows)
    assert any(r["is_safety_critical"] for r in rows)


def test_eligibility_gold_casts_flag():
    rows = [to_gold_eligibility(r)
            for r in _read(MASTER / "bridge_worker_unit_eligibility.csv")]
    assert all(isinstance(r["is_eligible"], bool) for r in rows)
