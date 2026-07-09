# Fabric notebook — bva: ingest_bronze_adoption
#
# Sprint 15 · T3/T4 — BVA medallion Bronze ingest for adoption telemetry. Reads
# the Sprint 12 sign-in exports (or the 30-day synthetic backfill produced by
# data-platform/scripts/adoption_seed_synthetic.py, per design spec §14) from
# Files/Bronze/adoption/YYYY-MM-DD/signins.json and lands them as a Delta table
# bronze.bva_adoption. The Gold value-realization join (T4) reads this table.
#
# Runtime: Microsoft Fabric notebook (PySpark). Publish gated by
# `approved-to-apply` (AGENTS.md §4).

BRONZE_SCHEMA = "bronze"
ADOPTION_PATH = "Files/Bronze/adoption"


def ingest_bronze_adoption(spark) -> None:  # pragma: no cover - Fabric runtime only
    df = (
        spark.read.option("recursiveFileLookup", "true")
        .option("multiLine", "true")
        .json(ADOPTION_PATH)
    )
    (
        df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(f"{BRONZE_SCHEMA}.bva_adoption")
    )
    print(f"bronze: wrote {BRONZE_SCHEMA}.bva_adoption ({df.count()} rows)")


if __name__ == "__main__":  # pragma: no cover - Fabric runtime only
    ingest_bronze_adoption(spark)  # noqa: F821
