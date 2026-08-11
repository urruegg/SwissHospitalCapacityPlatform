# Fabric notebook — bva: build_gold_bva_evidence
#
# BVA evidence & narrative Gold data product (additive to Sprint 33 WS-A
# cost-basis). Reads the ten committed evidence master-data CSVs from OneLake
# Files and delegates all transform logic to the pure `evidence_grounding`
# module, so every ROI/TCO/build-cost figure a PO/BVA agent cites carries its
# `evidence_status` (measured / modelled / ROM / ...).
#
# Gold outputs: gold.bva_evidence_assumption_dim, gold.bva_evidence_cost_element_dim,
#   gold.bva_evidence_source_dim, gold.bva_evidence_azure_cost_weekly_fact,
#   gold.bva_evidence_build_cost_actual_fact, gold.bva_evidence_copilot_usage_weekly_fact,
#   gold.bva_evidence_effort_fact, gold.bva_evidence_roi_scenario_fact,
#   gold.bva_evidence_unit_economics_fact, gold.bva_evidence_value_lever_fact
#
# Runtime: Microsoft Fabric notebook (PySpark). OneLake load + publish gated by approved-to-apply (AGENTS.md §4).

# The pure transform (data-platform/bva/evidence_grounding.py) is uploaded
# alongside this notebook in Fabric. Import defensively so the module resolves
# whether it is a sibling file or importable as `bva.evidence_grounding`.
try:
    from bva.evidence_grounding import _MASTER_FILES, build_gold_table  # packaged import
except ImportError:  # pragma: no cover - Fabric runtime only
    from evidence_grounding import _MASTER_FILES, build_gold_table  # type: ignore[no-redef]  # sibling upload

GOLD_SCHEMA = "gold"
MASTER_DATA_DIR = "Files/master-data/bva"

_GOLD_TABLE_NAMES = {
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


def _write(spark, rows, table: str) -> None:  # pragma: no cover - Fabric runtime only
    df = spark.createDataFrame(rows)
    (
        df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(f"{GOLD_SCHEMA}.{table}")
    )
    print(f"gold: wrote {GOLD_SCHEMA}.{table} ({df.count()} rows)")


def _read_csv(spark, filename: str) -> list[dict]:  # pragma: no cover - Fabric runtime only
    rows = (
        spark.read.option("header", True)
        .csv(f"{MASTER_DATA_DIR}/{filename}")
        .collect()
    )
    return [row.asDict() for row in rows]


def build_gold_bva_evidence(spark) -> None:  # pragma: no cover - Fabric runtime only
    for filename in _MASTER_FILES:
        stem = filename.removesuffix(".csv")
        rows = _read_csv(spark, filename)
        gold_rows = build_gold_table(stem, rows)
        _write(spark, gold_rows, _GOLD_TABLE_NAMES[stem])
    print(f"gold: wrote BVA evidence & narrative tables ({len(_GOLD_TABLE_NAMES)})")


if __name__ == "__main__":  # pragma: no cover - Fabric runtime only
    build_gold_bva_evidence(spark)  # noqa: F821
