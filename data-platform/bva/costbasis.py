"""Pure transform rules for the Sprint 33 WS-A BVA cost-basis product.

Framework-agnostic (no PySpark) implementation of the BVA cost / bill of
materials transforms. Callers read the committed CSV master data into plain
dict rows, apply these functions, and write or assert the Gold table shapes
outside this module. Keeping the logic pure makes it unit-testable with
byte-stable JSON fixtures — the same convention as the Sprint 15 BVA transform
module.

Gold table schema:

* ``bva_bom_dim``: one row per BOM resource
  (``resource_type``, ``resource_group``, ``env``, ``resource_id``).
* ``bva_cost_fact``: source-week USD cost normalized to CHF
  (``source``, ``iso_week``, ``cost_usd``, ``usd_to_chf``, ``cost_chf``).
* ``bva_effort_fact``: role-week elective team effort cost
  (``role``, ``iso_week``, ``elective_hours``, ``role_rate_chf``,
  ``team_cost_chf``).
* ``bva_hospital_profile_dim``: hospital profile dimension
  (``tenant_id``, ``hospital_name``, ``beds``, ``occupancy_target``,
  ``archetype``).
* ``bva_baseline_kpi``: ROM baseline metric rows
  (``metric_id``, ``value``, ``unit``, ``as_of``, ``source_ref``).

All aggregation output is returned **sorted** so JSON serialisation is
byte-stable across runs for a fixed input (regression-testable).
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Mapping

_MASTER_FILES: tuple[str, ...] = (
    "bva_cost_element.csv",
    "bva_hospital_profile.csv",
    "bva_bom.csv",
    "bva_azure_cost_weekly.csv",
    "bva_copilot_usage_weekly.csv",
    "bva_team_effort.csv",
    "bva_fx_rate.csv",
)
_DEFAULT_AS_OF = "2026-07-28T00:00:00Z"
_BASELINE_SOURCE_REF = "docs/BVA.md ROM; data/master-data/bva/bva_cost_element.csv"
_AZURE_LEDGER_TARGET_CHF = 760_000.0
_BUILD_LEDGER_TARGET_CHF = 640_000.0
_ROM_BAND = 0.30
_WEEKS_PER_YEAR = 52.0


def _num(value: object) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0


def _round_money(value: float) -> float:
    return round(float(value), 2)


def load_master_data(bva_dir: Path) -> dict[str, list[dict[str, str]]]:
    """Read the seven committed BVA master-data CSVs by stem name."""
    tables: dict[str, list[dict[str, str]]] = {}
    for filename in _MASTER_FILES:
        path = bva_dir / filename
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            tables[path.stem] = list(csv.DictReader(handle))
    return tables


def build_bom_dim(bom_rows: Iterable[Mapping]) -> list[dict]:
    """Return one BOM resource row per committed resource, sorted by id."""
    out = [
        {
            "resource_type": row.get("resource_type", ""),
            "resource_group": row.get("resource_group", ""),
            "env": row.get("env", ""),
            "resource_id": row.get("resource_id", ""),
        }
        for row in bom_rows
    ]
    out.sort(key=lambda r: r["resource_id"])
    return out


def _fx_for_week(iso_week: str, fx_rows: Iterable[Mapping]) -> float:
    rows = list(fx_rows)
    if not rows:
        raise ValueError("fx_rows must contain at least one USD/CHF rate")
    if len(rows) == 1:
        return _num(rows[0].get("usd_to_chf"))

    year, week_text = iso_week.split("-W", maxsplit=1)
    period = f"{year}-H{1 if int(week_text) <= 26 else 2}"
    for row in rows:
        if row.get("period") == period:
            return _num(row.get("usd_to_chf"))
    raise ValueError(f"no USD/CHF FX row found for {iso_week} ({period})")


def _source_week_fact(source: str, weekly_usd: Mapping[str, float], fx_rows: Iterable[Mapping]) -> list[dict]:
    out = []
    for iso_week, cost_usd in weekly_usd.items():
        fx = _fx_for_week(iso_week, fx_rows)
        out.append(
            {
                "source": source,
                "iso_week": iso_week,
                "cost_usd": _round_money(cost_usd),
                "usd_to_chf": fx,
                "cost_chf": _round_money(cost_usd * fx),
            }
        )
    return out


def build_cost_fact(azure_rows: Iterable[Mapping], copilot_rows: Iterable[Mapping], fx_rows) -> list[dict]:
    """Normalize Azure and Copilot source-week costs to CHF via FX rows only."""
    fx = list(fx_rows)
    azure_weekly: dict[str, float] = {}
    for row in azure_rows:
        iso_week = str(row.get("iso_week", ""))
        azure_weekly[iso_week] = azure_weekly.get(iso_week, 0.0) + _num(row.get("cost_usd"))

    copilot_weekly: dict[str, float] = {}
    for row in copilot_rows:
        iso_week = str(row.get("iso_week", ""))
        copilot_weekly[iso_week] = copilot_weekly.get(iso_week, 0.0) + _num(row.get("cost_usd"))

    out = _source_week_fact("azure", azure_weekly, fx)
    out.extend(_source_week_fact("copilot", copilot_weekly, fx))
    out.sort(key=lambda r: (r["source"], r["iso_week"]))
    return out


def build_effort_fact(effort_rows: Iterable[Mapping]) -> list[dict]:
    """Return role-week elective team effort cost rows, sorted for stability."""
    out = []
    for row in effort_rows:
        elective_hours = _num(row.get("elective_hours"))
        role_rate_chf = _num(row.get("role_rate_chf"))
        out.append(
            {
                "role": row.get("role", ""),
                "iso_week": row.get("iso_week", ""),
                "elective_hours": elective_hours,
                "role_rate_chf": role_rate_chf,
                "team_cost_chf": _round_money(elective_hours * role_rate_chf),
            }
        )
    out.sort(key=lambda r: (r["role"], r["iso_week"]))
    return out


def build_hospital_profile_dim(hospital_rows: Iterable[Mapping]) -> list[dict]:
    """Return hospital profile rows with numeric beds / occupancy fields."""
    out = [
        {
            "tenant_id": row.get("tenant_id", ""),
            "hospital_name": row.get("hospital_name", ""),
            "beds": int(_num(row.get("beds"))),
            "occupancy_target": _num(row.get("occupancy_target")),
            "archetype": row.get("archetype", ""),
        }
        for row in hospital_rows
    ]
    out.sort(key=lambda r: r["tenant_id"])
    return out


def build_baseline_kpi(
    cost_element_rows: Iterable[Mapping],
    hospital_rows: Iterable[Mapping],
    *,
    as_of: str = _DEFAULT_AS_OF,
) -> list[dict]:
    """Build the ROM baseline KPI rows from the authoritative ledger."""
    by_type = {"one_time": 0.0, "annual_run": 0.0}
    for row in cost_element_rows:
        cost_type = row.get("cost_type")
        if cost_type in by_type:
            by_type[cost_type] += _num(row.get("amount_chf"))

    hospitals = list(hospital_rows)
    hospital_count = len(hospitals)
    total_beds = sum(int(_num(row.get("beds"))) for row in hospitals)
    one_time_chf = _round_money(by_type["one_time"])
    annual_run_chf = _round_money(by_type["annual_run"])
    total_cost_chf = _round_money(one_time_chf + annual_run_chf)

    metrics = [
        ("annualRunChf", annual_run_chf, "CHF"),
        ("costPerBedChf", _round_money(total_cost_chf / total_beds) if total_beds else 0.0, "CHF"),
        (
            "costPerForecastRunChf",
            _round_money(annual_run_chf / (24.0 * 365.0)),
            "CHF",
        ),
        (
            "costPerHospitalChf",
            _round_money(total_cost_chf / hospital_count) if hospital_count else 0.0,
            "CHF",
        ),
        ("hospitals", float(hospital_count), "count"),
        ("oneTimeChf", one_time_chf, "CHF"),
        ("totalCostChf", total_cost_chf, "CHF"),
    ]
    out = [
        {
            "metric_id": metric_id,
            "value": value,
            "unit": unit,
            "as_of": as_of,
            "source_ref": _BASELINE_SOURCE_REF,
        }
        for metric_id, value, unit in metrics
    ]
    out.sort(key=lambda r: r["metric_id"])
    return out


def build_all(bva_dir: Path) -> dict[str, list[dict]]:
    """Load committed master data and return all five cost-basis Gold tables."""
    master = load_master_data(bva_dir)
    return {
        "bva_bom_dim": build_bom_dim(master["bva_bom"]),
        "bva_cost_fact": build_cost_fact(
            master["bva_azure_cost_weekly"],
            master["bva_copilot_usage_weekly"],
            master["bva_fx_rate"],
        ),
        "bva_effort_fact": build_effort_fact(master["bva_team_effort"]),
        "bva_hospital_profile_dim": build_hospital_profile_dim(master["bva_hospital_profile"]),
        "bva_baseline_kpi": build_baseline_kpi(
            master["bva_cost_element"],
            master["bva_hospital_profile"],
        ),
    }


def _annualized_weekly_total(rows: Iterable[Mapping], value_key: str) -> float:
    by_week: dict[str, float] = {}
    for row in rows:
        iso_week = str(row.get("iso_week", ""))
        by_week[iso_week] = by_week.get(iso_week, 0.0) + _num(row.get(value_key))
    if not by_week:
        return 0.0
    return _round_money((sum(by_week.values()) / len(by_week)) * _WEEKS_PER_YEAR)


def _band_row(element: str, rollup_chf: float, ledger_target_chf: float) -> dict:
    variance = abs(rollup_chf - ledger_target_chf) / ledger_target_chf if ledger_target_chf else 0.0
    return {
        "metric_id": element,
        "element": element,
        "rollup_chf": _round_money(rollup_chf),
        "ledger_target_chf": ledger_target_chf,
        "within_rom_band": variance <= _ROM_BAND,
    }


def consistency_report(tables: dict) -> list[dict]:
    """Compare drill-down facts to ledger targets as an informational report."""
    azure_rows = [row for row in tables.get("bva_cost_fact", []) if row.get("source") == "azure"]
    effort_rows = tables.get("bva_effort_fact", [])
    out = [
        _band_row(
            "ot-build",
            _annualized_weekly_total(effort_rows, "team_cost_chf"),
            _BUILD_LEDGER_TARGET_CHF,
        ),
        _band_row(
            "run-azure",
            _annualized_weekly_total(azure_rows, "cost_chf"),
            _AZURE_LEDGER_TARGET_CHF,
        ),
    ]
    out.sort(key=lambda r: r["element"])
    return out
