"""Sprint 23 - Gold projection for the Curavias skills domain (issue #255).

Second half of the WS-C gold layer (the org spine lives in
``build_gold_org_spine.py``). Projects the Curavias skills master data
(``data/master-data/curavias-org-skills/``) onto the ``gold.*`` layer so the
semantic model can expose **supply / demand / gap / eligibility** measures
(T6), a **live-vs-simulated** badge driven by ``source_mode``, and a
**bed-vs-ops care-setting split** (T14):

* ``care_setting`` (``bed`` = Pflegepersonal/nursing, ``ops`` =
  Doctors + specialised) is **explicit** on the demand and gap facts, because
  those facts are skill-grained (no occupation) and cross-cutting skills
  (``SK-BLS``, ``SK-IPC``, ...) cannot be attributed by derivation;
* for the **occupation-grained** tables (``dim_occupation_role`` and the
  ``bridge_role_skill_demand_template``) the care setting is **derived** from
  the occupation ISCO-08 code, so supply/eligibility can also be split by
  care setting without any hand-authored data;
* ``source_mode`` (``live`` | ``simulated``) is preserved on demand / gap /
  assertion so the badge measure reads a real flag and is never invented.

The pure functions here are unit-tested without Spark (see
``tests/test_build_gold_skills.py``), following the org-spine / external-signals
notebook pattern. ``run()`` is the Fabric Spark entrypoint.
"""
from __future__ import annotations

import sys

# Allowed care-setting + source-mode domains (single source of truth for both
# the gold validators here and the test suite).
CARE_SETTINGS = {"bed", "ops"}
SOURCE_MODES = {"live", "simulated"}

# ISCO-08 major/unit code -> care setting. Nursing + allied-health staff that
# staff beds are ``bed``; physicians and management/support functions are
# ``ops``. Every ISCO code present in dim_occupation_role must appear here so a
# newly introduced occupation is classified deliberately (fail-fast below).
ISCO_CARE_SETTING = {
    "2221": "bed",   # registered / ICU / anaesthesia / emergency nurse
    "2222": "bed",   # midwife
    "3211": "bed",   # radiographer, scrub / OR technician
    "3258": "bed",   # paramedic
    "2264": "bed",   # physiotherapist
    "2212": "ops",   # specialist physicians
    "1342": "ops",   # health-services managers (bed/OR/crisis/ward lead)
    "2521": "ops",   # data / ontology steward
}


def _as_bool(value) -> bool:
    """Parse a CSV truthy token ('TRUE'/'true'/'1') to a real bool."""
    return str(value).strip().lower() in {"true", "1", "yes"}


def _as_int(value):
    """Parse an int CSV token; empty/blank -> None (nullable numeric)."""
    text = str(value).strip()
    if text == "":
        return None
    return int(text)


def _require_in(value, allowed: set, field: str, row_id: str) -> str:
    text = str(value).strip()
    if text not in allowed:
        raise ValueError(
            f"{field}={value!r} on row {row_id!r} is not one of {sorted(allowed)}"
        )
    return text


def derive_occupation_care_setting(occupation_rows: list[dict]) -> dict[str, str]:
    """Map ``occupation_id -> care_setting`` from the ISCO-08 code.

    Fails fast on any occupation whose ISCO code is not classified, so the
    demo never silently mis-buckets a new role.
    """
    out: dict[str, str] = {}
    for r in occupation_rows:
        isco = str(r.get("isco_08_code", "")).strip()
        if isco not in ISCO_CARE_SETTING:
            raise ValueError(
                f"occupation {r.get('occupation_id')!r} has unclassified "
                f"ISCO-08 code {isco!r}; add it to ISCO_CARE_SETTING"
            )
        out[r["occupation_id"]] = ISCO_CARE_SETTING[isco]
    return out


def to_gold_care_setting(row: dict) -> dict:
    """Project one ``dim_care_setting`` CSV row onto ``gold.dim_care_setting``."""
    return dict(row)


def to_gold_skill(row: dict) -> dict:
    """Project one ``dim_skill`` CSV row: cast the boolean flags."""
    out = dict(row)
    out["is_safety_critical"] = _as_bool(row.get("is_safety_critical"))
    out["has_expiry"] = _as_bool(row.get("has_expiry"))
    return out


def to_gold_occupation_role(row: dict, occ_care_setting: dict[str, str]) -> dict:
    """Project ``dim_occupation_role`` and attach the derived care setting."""
    out = dict(row)
    out["care_setting_id"] = occ_care_setting[row["occupation_id"]]
    return out


def to_gold_demand_template(row: dict, occ_care_setting: dict[str, str]) -> dict:
    """Project ``bridge_role_skill_demand_template`` with derived care setting.

    Every template row applies to an occupation (``applies_to_type`` ==
    ``occupation``), so the care setting follows from the occupation.
    """
    applies_to = str(row.get("applies_to_type", "")).strip()
    if applies_to != "occupation":
        raise ValueError(
            f"template {row.get('template_id')!r} applies_to_type={applies_to!r}; "
            "expected 'occupation'"
        )
    occ = row["applies_to_id"]
    if occ not in occ_care_setting:
        raise ValueError(
            f"template {row.get('template_id')!r} references unknown "
            f"occupation {occ!r}"
        )
    out = dict(row)
    out["is_mandatory"] = _as_bool(row.get("is_mandatory"))
    out["care_setting_id"] = occ_care_setting[occ]
    return out


def to_gold_skill_demand(row: dict) -> dict:
    """Project one ``fact_skill_demand`` row: validate domains, cast numerics."""
    rid = row.get("demand_id", "?")
    out = dict(row)
    out["care_setting_id"] = _require_in(
        row.get("care_setting_id"), CARE_SETTINGS, "care_setting_id", rid)
    out["source_mode"] = _require_in(
        row.get("source_mode"), SOURCE_MODES, "source_mode", rid)
    out["min_proficiency"] = _as_int(row.get("min_proficiency"))
    out["headcount_required"] = _as_int(row.get("headcount_required"))
    return out


def to_gold_skill_gap(row: dict) -> dict:
    """Project one ``fact_skill_gap`` row: validate domains, cast numerics."""
    rid = row.get("gap_id", "?")
    out = dict(row)
    out["care_setting_id"] = _require_in(
        row.get("care_setting_id"), CARE_SETTINGS, "care_setting_id", rid)
    out["source_mode"] = _require_in(
        row.get("source_mode"), SOURCE_MODES, "source_mode", rid)
    out["headcount_required"] = _as_int(row.get("headcount_required"))
    out["valid_supply"] = _as_int(row.get("valid_supply"))
    out["gap"] = _as_int(row.get("gap"))
    out["redeploy_candidates_count"] = _as_int(row.get("redeploy_candidates_count"))
    return out


def to_gold_skill_assertion(row: dict) -> dict:
    """Project one ``fact_skill_assertion`` row (supply): validate source_mode."""
    rid = row.get("assertion_id", "?")
    out = dict(row)
    out["source_mode"] = _require_in(
        row.get("source_mode"), SOURCE_MODES, "source_mode", rid)
    out["proficiency_level"] = _as_int(row.get("proficiency_level"))
    return out


def to_gold_eligibility(row: dict) -> dict:
    """Project one ``bridge_worker_unit_eligibility`` row: cast the flag."""
    out = dict(row)
    out["is_eligible"] = _as_bool(row.get("is_eligible"))
    return out


def build_skills_gold(
    care_setting_rows: list[dict],
    skill_rows: list[dict],
    occupation_rows: list[dict],
    demand_template_rows: list[dict],
    demand_rows: list[dict],
    gap_rows: list[dict],
    assertion_rows: list[dict],
    eligibility_rows: list[dict],
) -> dict[str, list[dict]]:
    """Pure core of ``run()``: build every skills-domain gold table as rows.

    Returns ``{gold_table_name: [row, ...]}`` for the eight skills tables. The
    occupation care setting is derived once (ISCO-08) and threaded into the
    occupation-grained tables; all domain validation happens in the row
    transforms above so the ``run()`` Spark bridge only reads CSVs and writes
    Delta.
    """
    occ_care_setting = derive_occupation_care_setting(occupation_rows)
    return {
        "dim_care_setting": [to_gold_care_setting(r) for r in care_setting_rows],
        "dim_skill": [to_gold_skill(r) for r in skill_rows],
        "dim_occupation_role": [
            to_gold_occupation_role(r, occ_care_setting) for r in occupation_rows],
        "bridge_role_skill_demand_template": [
            to_gold_demand_template(r, occ_care_setting)
            for r in demand_template_rows],
        "fact_skill_demand": [to_gold_skill_demand(r) for r in demand_rows],
        "fact_skill_gap": [to_gold_skill_gap(r) for r in gap_rows],
        "fact_skill_assertion": [to_gold_skill_assertion(r) for r in assertion_rows],
        "bridge_worker_unit_eligibility": [
            to_gold_eligibility(r) for r in eligibility_rows],
    }


# --------------------------------------------------------------------------- #
# Fabric Spark entrypoint (deploy-class; exercised only in the Fabric runtime) #
# --------------------------------------------------------------------------- #
_MASTER_MOUNT = "/lakehouse/default/Files/master-data/curavias-org-skills"


def run() -> None:  # pragma: no cover - requires a live Fabric Spark session
    """Fabric entrypoint. Lands the eight skills-domain ``gold.*`` tables.

    Reads the Curavias skills CSVs from the lakehouse ``Files/`` mount, applies
    :func:`build_skills_gold`, and overwrites each ``gold.*`` table as Delta
    with the sprint-09 governance stamp.
    """
    from _fabric_gold_io import read_csv_rows, write_gold  # in Files/ alongside

    tables = build_skills_gold(
        care_setting_rows=read_csv_rows(f"{_MASTER_MOUNT}/dim_care_setting.csv"),
        skill_rows=read_csv_rows(f"{_MASTER_MOUNT}/dim_skill.csv"),
        occupation_rows=read_csv_rows(f"{_MASTER_MOUNT}/dim_occupation_role.csv"),
        demand_template_rows=read_csv_rows(
            f"{_MASTER_MOUNT}/bridge_role_skill_demand_template.csv"),
        demand_rows=read_csv_rows(f"{_MASTER_MOUNT}/fact_skill_demand.csv"),
        gap_rows=read_csv_rows(f"{_MASTER_MOUNT}/fact_skill_gap.csv"),
        assertion_rows=read_csv_rows(f"{_MASTER_MOUNT}/fact_skill_assertion.csv"),
        eligibility_rows=read_csv_rows(
            f"{_MASTER_MOUNT}/bridge_worker_unit_eligibility.csv"),
    )
    for name, rows in tables.items():
        write_gold(name, rows)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
