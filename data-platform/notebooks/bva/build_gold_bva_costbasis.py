# Fabric notebook — bva: build_gold_bva_costbasis
#
# Sprint 33 WS-A — BVA cost-basis Gold data product. Reads the committed
# master-data CSVs from OneLake Files and delegates all transform logic to the
# pure `costbasis` module.
#
# Gold outputs: gold.bva_bom_dim, gold.bva_cost_fact, gold.bva_effort_fact,
#   gold.bva_hospital_profile_dim, gold.bva_baseline_kpi
#
# Runtime: Microsoft Fabric notebook (PySpark). OneLake load + publish gated by approved-to-apply (AGENTS.md §4).

# The pure transform (data-platform/bva/costbasis.py) is uploaded alongside this
# notebook in Fabric. Import defensively so the module resolves whether it is a
# sibling file or importable as `bva.costbasis`.
try:
    from bva.costbasis import (  # packaged import
        build_baseline_kpi,
        build_bom_dim,
        build_cost_fact,
        build_effort_fact,
        build_hospital_profile_dim,
    )
except ImportError:  # pragma: no cover - Fabric runtime only
    from costbasis import (  # type: ignore[no-redef]  # sibling upload
        build_baseline_kpi,
        build_bom_dim,
        build_cost_fact,
        build_effort_fact,
        build_hospital_profile_dim,
    )

GOLD_SCHEMA = "gold"
BVA_PREFIX = "bva_"
MASTER_DATA_DIR = "Files/master-data/bva"

MASTER_FILES = {
    "bva_cost_element": "bva_cost_element.csv",
    "bva_hospital_profile": "bva_hospital_profile.csv",
    "bva_bom": "bva_bom.csv",
    "bva_azure_cost_weekly": "bva_azure_cost_weekly.csv",
    "bva_copilot_usage_weekly": "bva_copilot_usage_weekly.csv",
    "bva_team_effort": "bva_team_effort.csv",
    "bva_fx_rate": "bva_fx_rate.csv",
}


def _write(spark, rows, table: str) -> None:  # pragma: no cover - Fabric runtime only
    df = spark.createDataFrame(rows)
    (
        df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(f"{GOLD_SCHEMA}.{BVA_PREFIX}{table}")
    )
    print(f"gold: wrote {GOLD_SCHEMA}.{BVA_PREFIX}{table} ({df.count()} rows)")


def _read_csv(spark, filename: str) -> list[dict]:  # pragma: no cover - Fabric runtime only
    rows = (
        spark.read.option("header", True)
        .csv(f"{MASTER_DATA_DIR}/{filename}")
        .collect()
    )
    return [row.asDict() for row in rows]


def _read_master_data(spark) -> dict[str, list[dict]]:  # pragma: no cover - Fabric runtime only
    return {name: _read_csv(spark, filename) for name, filename in MASTER_FILES.items()}


def build_gold_bva_costbasis(spark) -> None:  # pragma: no cover - Fabric runtime only
    master = _read_master_data(spark)

    _write(spark, build_bom_dim(master["bva_bom"]), "bom_dim")
    _write(
        spark,
        build_cost_fact(
            master["bva_azure_cost_weekly"],
            master["bva_copilot_usage_weekly"],
            master["bva_fx_rate"],
        ),
        "cost_fact",
    )
    _write(spark, build_effort_fact(master["bva_team_effort"]), "effort_fact")
    _write(
        spark,
        build_hospital_profile_dim(master["bva_hospital_profile"]),
        "hospital_profile_dim",
    )
    _write(
        spark,
        build_baseline_kpi(
            master["bva_cost_element"],
            master["bva_hospital_profile"],
        ),
        "baseline_kpi",
    )
    print("gold: wrote Sprint 33 WS-A BVA cost-basis tables (5)")


if __name__ == "__main__":  # pragma: no cover - Fabric runtime only
    build_gold_bva_costbasis(spark)  # noqa: F821
