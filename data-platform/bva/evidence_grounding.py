"""Pure transform rules for the BVA evidence & narrative master-data product.

Framework-agnostic (no PySpark) implementation. This is a **separate, additive**
data product from ``costbasis.py`` (which feeds the hospital-onboarding
simulation baseline via BOM/effort/weekly-cost/FX rows). This module instead
grounds ROI/TCO/build-cost **narrative and Q&A** answers — the ten dim/fact
CSVs under ``data/master-data/bva/`` each carry an ``evidence_status`` (or
``confidence``) column so every figure a PO/BVA agent cites can be labelled
measured vs. modelled vs. ROM, never presented as one undifferentiated number.

Callers read the committed CSV master data into plain dict rows, apply
``build_evidence_gold_tables``, and write or assert the Gold table shapes
outside this module — the same convention as ``costbasis.py``.

Gold tables (one per source file, ``bva_evidence_`` prefixed, numeric columns
coerced to float/None, rows sorted by their id column for byte-stable output):

* ``bva_evidence_assumption_dim`` <- ``dim_assumption.csv``
* ``bva_evidence_cost_element_dim`` <- ``dim_cost_element.csv``
* ``bva_evidence_source_dim`` <- ``dim_evidence_source.csv``
* ``bva_evidence_azure_cost_weekly_fact`` <- ``fact_azure_cost_weekly.csv``
* ``bva_evidence_build_cost_actual_fact`` <- ``fact_build_cost_actual.csv``
* ``bva_evidence_copilot_usage_weekly_fact`` <- ``fact_copilot_usage_weekly.csv``
* ``bva_evidence_effort_fact`` <- ``fact_effort.csv``
* ``bva_evidence_roi_scenario_fact`` <- ``fact_roi_scenario.csv``
* ``bva_evidence_unit_economics_fact`` <- ``fact_unit_economics.csv``
* ``bva_evidence_value_lever_fact`` <- ``fact_value_lever.csv``
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Mapping

_MASTER_FILES: tuple[str, ...] = (
    "dim_assumption.csv",
    "dim_cost_element.csv",
    "dim_evidence_source.csv",
    "fact_azure_cost_weekly.csv",
    "fact_build_cost_actual.csv",
    "fact_copilot_usage_weekly.csv",
    "fact_effort.csv",
    "fact_roi_scenario.csv",
    "fact_unit_economics.csv",
    "fact_value_lever.csv",
)

# Numeric columns to coerce per source stem; an empty CSV cell becomes ``None``
# (genuinely not tracked for that row), never ``0.0`` (which would misrepresent
# a real zero). Every other column stays a string.
_NUMERIC_COLUMNS: dict[str, tuple[str, ...]] = {
    "dim_assumption": ("value",),
    "dim_cost_element": ("amount_chf",),
    "dim_evidence_source": (),
    "fact_azure_cost_weekly": ("amount_usd", "amount_chf"),
    "fact_build_cost_actual": ("amount_chf", "amount_usd", "share_pct"),
    "fact_copilot_usage_weekly": (
        "sessions",
        "input_tokens",
        "output_tokens",
        "cache_read_tokens",
        "reasoning_tokens",
        "aiu_consumed",
    ),
    "fact_effort": ("quantity", "hours", "hourly_rate_chf", "cost_chf"),
    "fact_roi_scenario": (
        "annual_benefit_chf",
        "annual_run_cost_chf",
        "one_time_cost_chf",
        "tco_3yr_chf",
        "gross_benefit_3yr_chf",
        "net_value_3yr_chf",
        "roi_3yr_pct",
        "payback_months",
    ),
    "fact_unit_economics": ("value_chf", "denominator_count"),
    "fact_value_lever": ("annual_benefit_chf",),
}

# First (id) column per source stem, used to sort gold rows deterministically.
_ID_COLUMNS: dict[str, str] = {
    "dim_assumption": "assumption_id",
    "dim_cost_element": "cost_element_id",
    "dim_evidence_source": "source_id",
    "fact_azure_cost_weekly": "azure_cost_id",
    "fact_build_cost_actual": "build_cost_id",
    "fact_copilot_usage_weekly": "copilot_usage_id",
    "fact_effort": "effort_id",
    "fact_roi_scenario": "scenario_id",
    "fact_unit_economics": "unit_id",
    "fact_value_lever": "value_lever_id",
}

# Explicit Gold table name per source stem (avoids deriving names
# programmatically, which double-counts "evidence" for dim_evidence_source).
_GOLD_TABLE_NAMES: dict[str, str] = {
    "dim_assumption": "bva_evidence_assumption_dim",
    "dim_cost_element": "bva_evidence_cost_element_dim",
    "dim_evidence_source": "bva_evidence_source_dim",
    "fact_azure_cost_weekly": "bva_evidence_azure_cost_weekly_fact",
    "fact_build_cost_actual": "bva_evidence_build_cost_actual_fact",
    "fact_copilot_usage_weekly": "bva_evidence_copilot_usage_weekly_fact",
    "fact_effort": "bva_evidence_effort_fact",
    "fact_roi_scenario": "bva_evidence_roi_scenario_fact",
    "fact_unit_economics": "bva_evidence_unit_economics_fact",
    "fact_value_lever": "bva_evidence_value_lever_fact",
}

# "derived" is not in docs/README's core vocabulary but is used by
# fact_unit_economics.csv for a rate computed deterministically from two other
# measured assumptions (e.g. the blended hourly rate) -- distinct from
# "estimated" (a non-authoritative rate) or "measured" (from a tracked record).
VALID_EVIDENCE_STATUS: frozenset[str] = frozenset(
    {
        "measured",
        "measured_extrapolated",
        "estimated",
        "telemetry",
        "modelled",
        "modelled_on_measured",
        "ROM",
        "mixed",
        "derived",
    }
)


def _coerce_numeric(value: str) -> float | None:
    stripped = value.strip()
    if not stripped:
        return None
    return float(stripped)


def load_master_data(bva_dir: Path) -> dict[str, list[dict[str, str]]]:
    """Read the ten committed BVA evidence master-data CSVs by stem name."""
    tables: dict[str, list[dict[str, str]]] = {}
    for filename in _MASTER_FILES:
        path = bva_dir / filename
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            tables[path.stem] = list(csv.DictReader(handle))
    return tables


def build_gold_table(stem: str, rows: Iterable[Mapping[str, str]]) -> list[dict]:
    """Coerce one source table's numeric columns and sort by its id column."""
    numeric_columns = _NUMERIC_COLUMNS[stem]
    out: list[dict] = []
    for row in rows:
        coerced: dict[str, object] = dict(row)
        for column in numeric_columns:
            coerced[column] = _coerce_numeric(str(row.get(column, "")))
        out.append(coerced)
    id_column = _ID_COLUMNS[stem]
    out.sort(key=lambda r: str(r.get(id_column, "")))
    return out


def build_evidence_gold_tables(bva_dir: Path) -> dict[str, list[dict]]:
    """Load committed master data and return all ten evidence Gold tables."""
    master = load_master_data(bva_dir)
    return {
        _GOLD_TABLE_NAMES[stem]: build_gold_table(stem, rows) for stem, rows in master.items()
    }
