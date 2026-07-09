# Fabric notebook — bva: ingest_bronze_consumption
#
# Sprint 15 · T3 — BVA medallion Bronze ingest for synthetic FOCUS consumption.
# Reads the daily-partitioned FOCUS files uploaded by the bva-sim-refresh
# workflow (T2) from Files/Bronze/consumption/ and lands them as a Delta table
# bronze.bva_consumption with the FOCUS column shape preserved.
#
# Runtime: Microsoft Fabric notebook (PySpark). Publish gated by
# `approved-to-apply` (AGENTS.md §4).

BRONZE_SCHEMA = "bronze"
CONSUMPTION_PATH = "Files/Bronze/consumption"


def ingest_bronze_consumption(spark) -> None:  # pragma: no cover - Fabric runtime only
    df = (
        spark.read.option("recursiveFileLookup", "true")
        .parquet(CONSUMPTION_PATH)
    )
    (
        df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(f"{BRONZE_SCHEMA}.bva_consumption")
    )
    print(f"bronze: wrote {BRONZE_SCHEMA}.bva_consumption ({df.count()} rows)")


if __name__ == "__main__":  # pragma: no cover - Fabric runtime only
    ingest_bronze_consumption(spark)  # noqa: F821
