# Fabric notebook — bva: build_gold_bva_dims
#
# Sprint 15 · T3 — BVA medallion Gold dimensions. Projects Silver into the Gold
# star-schema dimensions (design spec §5) using snake_case + `gold.` prefix (per
# PR #153 naming reconciliation) via the pure, unit-tested `bva_transforms`.
#
# Gold dims: gold.dim_service, gold.dim_meter, gold.dim_resource,
#   gold.dim_environment, gold.dim_hospital, gold.dim_capability,
#   gold.dim_date, gold.dim_exec_role
#
# Runtime: Microsoft Fabric notebook (PySpark). Publish gated by
# `approved-to-apply` (AGENTS.md §4).

import bva_transforms as T

GOLD_SCHEMA = "gold"


def _write(spark, rows, table: str) -> None:  # pragma: no cover - Fabric runtime only
    df = spark.createDataFrame(rows)
    (
        df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(f"{GOLD_SCHEMA}.{table}")
    )
    print(f"gold: wrote {GOLD_SCHEMA}.{table} ({df.count()} rows)")


def build_gold_bva_dims(spark) -> None:  # pragma: no cover - Fabric runtime only
    silver = spark.read.table("silver.bva_consumption")
    # dim builders read the raw FOCUS columns; re-read Bronze for the source shape.
    focus_rows = [r.asDict() for r in spark.read.table("bronze.bva_consumption").collect()]

    _write(spark, T.dim_service(focus_rows), "dim_service")
    _write(spark, T.dim_meter(focus_rows), "dim_meter")
    _write(spark, T.dim_resource(focus_rows), "dim_resource")
    _write(spark, T.dim_environment(focus_rows), "dim_environment")
    _write(spark, T.dim_hospital(focus_rows), "dim_hospital")
    _write(spark, T.dim_capability(focus_rows), "dim_capability")
    _write(spark, T.dim_date(focus_rows), "dim_date")
    _write(spark, T.dim_exec_role(), "dim_exec_role")
    print(f"silver source rows: {silver.count()}")


if __name__ == "__main__":  # pragma: no cover - Fabric runtime only
    build_gold_bva_dims(spark)  # noqa: F821
