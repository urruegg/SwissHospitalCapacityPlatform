# Fabric notebook — bva: build_silver_bva
#
# Sprint 15 · T3 — BVA medallion Silver. Normalises Bronze FOCUS rows into the
# Silver contract (foreign keys + date/month keys + provenance) using the pure,
# unit-tested `bva_transforms.to_silver` (single source of truth shared with the
# tests). For the synthetic seed (~12k rows) collecting to the driver is cheap
# and keeps one tested implementation — the same pattern as the evidence
# `score_readiness` notebook.
#
# Runtime: Microsoft Fabric notebook (PySpark). Publish gated by
# `approved-to-apply` (AGENTS.md §4).

from datetime import datetime, timezone

import bva_transforms as T  # colocated in the notebook environment

BRONZE_SCHEMA = "bronze"
SILVER_SCHEMA = "silver"


def build_silver_bva(spark) -> None:  # pragma: no cover - Fabric runtime only
    bronze = spark.read.table(f"{BRONZE_SCHEMA}.bva_consumption")
    focus_rows = [r.asDict() for r in bronze.collect()]

    # A single seed is carried on every synthetic row; use the first as provenance.
    source_seed = 0
    if focus_rows and "x_source_seed" in focus_rows[0]:
        source_seed = int(focus_rows[0]["x_source_seed"])

    silver = T.to_silver(
        focus_rows,
        ingest_utc=datetime.now(timezone.utc).isoformat(),
        source_seed=source_seed,
    )
    df = spark.createDataFrame(silver)
    (
        df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(f"{SILVER_SCHEMA}.bva_consumption")
    )
    print(f"silver: wrote {SILVER_SCHEMA}.bva_consumption ({df.count()} rows)")


if __name__ == "__main__":  # pragma: no cover - Fabric runtime only
    build_silver_bva(spark)  # noqa: F821
