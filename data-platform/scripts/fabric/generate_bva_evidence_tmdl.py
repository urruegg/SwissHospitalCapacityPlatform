"""One-off generator for the 10 bva_evidence_* TMDL table definitions.

Mirrors the existing bva_hospital_profile_dim.tmdl shape exactly (Direct Lake
partition over lh_ihzhhpf_sit, gold schema). Run once; the generated .tmdl
files are committed like any other source file.
"""
from __future__ import annotations

import csv
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
BVA_DIR = REPO_ROOT / "data" / "master-data" / "bva"
TABLES_DIR = REPO_ROOT / "data-platform" / "reports" / "sm_bva.SemanticModel" / "definition" / "tables"

_NUMERIC_COLUMNS: dict[str, tuple[str, ...]] = {
    "dim_assumption": ("value",),
    "dim_cost_element": ("amount_chf",),
    "dim_evidence_source": (),
    "fact_azure_cost_weekly": ("amount_usd", "amount_chf"),
    "fact_build_cost_actual": ("amount_chf", "amount_usd", "share_pct"),
    "fact_copilot_usage_weekly": (
        "sessions", "input_tokens", "output_tokens",
        "cache_read_tokens", "reasoning_tokens", "aiu_consumed",
    ),
    "fact_effort": ("quantity", "hours", "hourly_rate_chf", "cost_chf"),
    "fact_roi_scenario": (
        "annual_benefit_chf", "annual_run_cost_chf", "one_time_cost_chf",
        "tco_3yr_chf", "gross_benefit_3yr_chf", "net_value_3yr_chf",
        "roi_3yr_pct", "payback_months",
    ),
    "fact_unit_economics": ("value_chf", "denominator_count"),
    "fact_value_lever": ("annual_benefit_chf",),
}

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

_DESCRIPTIONS: dict[str, str] = {
    "dim_assumption": "BVA evidence assumptions (rates, factors) with confidence.",
    "dim_cost_element": "BVA evidence cost-element catalogue (per model version).",
    "dim_evidence_source": "BVA evidence source register (authority, period, caveats).",
    "fact_azure_cost_weekly": "BVA evidence weekly Azure cost by service (USD/CHF).",
    "fact_build_cost_actual": "BVA evidence measured MVP build-cost breakdown.",
    "fact_copilot_usage_weekly": "BVA evidence weekly GitHub Copilot usage/token telemetry.",
    "fact_effort": "BVA evidence human effort cost by person/period.",
    "fact_roi_scenario": "BVA evidence ROI/TCO scenarios (conservative/base/upside).",
    "fact_unit_economics": "BVA evidence unit-economics computed rates.",
    "fact_value_lever": "BVA evidence value levers (annual benefit, validation status).",
}


def _read_header(stem: str) -> list[str]:
    with (BVA_DIR / f"{stem}.csv").open("r", encoding="utf-8-sig", newline="") as handle:
        return next(csv.reader(handle))


def _column_block(name: str, is_numeric: bool) -> str:
    tag = uuid.uuid4()
    if is_numeric:
        return (
            f"\tcolumn {name}\n"
            f"\t\tdataType: double\n"
            f"\t\tformatString: #,0.00\n"
            f"\t\tlineageTag: {tag}\n"
            f"\t\tsourceLineageTag: {name}\n"
            f"\t\tsummarizeBy: none\n"
            f"\t\tsourceColumn: {name}\n\n"
            f"\t\tannotation SummarizationSetBy = Automatic\n"
        )
    return (
        f"\tcolumn {name}\n"
        f"\t\tdataType: string\n"
        f"\t\tlineageTag: {tag}\n"
        f"\t\tsourceLineageTag: {name}\n"
        f"\t\tsummarizeBy: none\n"
        f"\t\tsourceColumn: {name}\n\n"
        f"\t\tannotation SummarizationSetBy = Automatic\n"
    )


def build_tmdl(stem: str) -> str:
    gold_name = _GOLD_TABLE_NAMES[stem]
    numeric = set(_NUMERIC_COLUMNS[stem])
    header = _read_header(stem)
    table_tag = uuid.uuid4()

    columns = "\n".join(_column_block(col, col in numeric) for col in header)

    return (
        f"/// {_DESCRIPTIONS[stem]} Direct Lake over lh_ihzhhpf_sit.\n"
        f"table {gold_name}\n"
        f"\tlineageTag: {table_tag}\n"
        f"\tsourceLineageTag: [gold].[{gold_name}]\n\n"
        f"{columns}\n"
        f"\tpartition {gold_name} = entity\n"
        f"\t\tmode: directLake\n"
        f"\t\tsource\n"
        f"\t\t\tentityName: {gold_name}\n"
        f"\t\t\tschemaName: gold\n"
        f"\t\t\texpressionSource: 'DirectLake - lh_ihzhhpf_sit'\n"
    )


def main() -> None:
    for stem, gold_name in _GOLD_TABLE_NAMES.items():
        content = build_tmdl(stem)
        out_path = TABLES_DIR / f"{gold_name}.tmdl"
        out_path.write_text(content, encoding="utf-8", newline="\n")
        print(f"wrote {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
