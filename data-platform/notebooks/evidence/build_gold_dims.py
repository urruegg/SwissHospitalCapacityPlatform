# Fabric notebook — evidence: build_gold_dims
#
# Sprint 14 · T3 — Showcase Evidence medallion (Gold dimensions).
# Projects Silver evidence into the Gold star-schema dimensions using
# snake_case + `gold.` schema prefix (per PR #153 naming reconciliation).
#
# Gold dims (design spec §3 / anchor idea §5.1):
#   gold.dim_resource, gold.dim_region, gold.dim_track, gold.dim_maturity_status,
#   gold.dim_requirement, gold.dim_adr, gold.dim_environment, gold.dim_date
#
# Runtime: Microsoft Fabric notebook (PySpark). Publish gated by
# `approved-to-apply` (AGENTS.md §4).

SILVER_SCHEMA = "silver"
GOLD_SCHEMA = "gold"

STATIC_TRACKS = ["T-SHOW", "T-PROD"]
STATIC_MATURITY = ["GA", "Preview", "NotAvailable"]
STATIC_ENVIRONMENTS = ["dev", "sit", "prod"]


def _write(df, table: str) -> None:
    df.write.format("delta").mode("overwrite").option(
        "overwriteSchema", "true"
    ).saveAsTable(f"{GOLD_SCHEMA}.{table}")
    print(f"gold: wrote {GOLD_SCHEMA}.{table} ({df.count()} rows)")


def build_gold_dims(spark) -> None:
    from pyspark.sql import functions as F

    bom = spark.read.table(f"{SILVER_SCHEMA}.evidence_bom")
    _write(
        bom.select(
            F.col("id").alias("resource_key"),
            "name",
            "type",
            "category",
            "sku",
            "sourcePath",
            "sourceCommit",
        ),
        "dim_resource",
    )

    region = spark.read.table(f"{SILVER_SCHEMA}.evidence_region_availability")
    _write(region.select("region").distinct().withColumnRenamed("region", "region_key"), "dim_region")

    _write(spark.createDataFrame([(t,) for t in STATIC_TRACKS], ["track_key"]), "dim_track")
    _write(spark.createDataFrame([(m,) for m in STATIC_MATURITY], ["maturity_key"]), "dim_maturity_status")
    _write(spark.createDataFrame([(e,) for e in STATIC_ENVIRONMENTS], ["environment_key"]), "dim_environment")

    req = spark.read.table(f"{SILVER_SCHEMA}.evidence_requirements")
    _write(
        req.select(
            F.col("id").alias("requirement_key"), "family", "kind", "title", "mvp",
            "sourcePath", "sourceCommit",
        ),
        "dim_requirement",
    )

    adr = spark.read.table(f"{SILVER_SCHEMA}.evidence_adrs")
    _write(
        adr.select(
            F.col("id").alias("adr_key"), "title", "status", "decisionSummary",
            "sourcePath", "sourceCommit",
        ),
        "dim_adr",
    )

    # Degenerate date dimension keyed on the availability as-of dates.
    as_of = region.select(F.col("asOf").alias("date_key")).distinct()
    _write(as_of, "dim_date")


if __name__ == "__main__":  # pragma: no cover - Fabric runtime only
    build_gold_dims(spark)  # noqa: F821
