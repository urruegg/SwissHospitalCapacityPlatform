# Fabric notebook — evidence: build_gold_facts
#
# Sprint 14 · T3 — Showcase Evidence medallion (Gold facts + bridges).
# Projects Silver evidence into the Gold star-schema facts and bridge tables
# using snake_case + `gold.` schema prefix (per PR #153 naming reconciliation).
#
# Gold facts (anchor idea §5.2):
#   gold.fact_availability_evidence, gold.fact_bom_deployment,
#   gold.fact_readiness_snapshot   (readiness written by score_readiness.py)
# Gold bridges:
#   gold.bridge_resource_dependency, gold.bridge_requirement_resource,
#   gold.bridge_requirement_adr
#
# Runtime: Microsoft Fabric notebook (PySpark). Publish gated by
# `approved-to-apply` (AGENTS.md §4).

SILVER_SCHEMA = "silver"
GOLD_SCHEMA = "gold"


def _write(df, table: str) -> None:
    df.write.format("delta").mode("overwrite").option(
        "overwriteSchema", "true"
    ).saveAsTable(f"{GOLD_SCHEMA}.{table}")
    print(f"gold: wrote {GOLD_SCHEMA}.{table} ({df.count()} rows)")


def build_gold_facts(spark) -> None:
    from pyspark.sql import functions as F

    region = spark.read.table(f"{SILVER_SCHEMA}.evidence_region_availability")
    _write(
        region.select(
            F.col("bomId").alias("resource_key"),
            F.col("region").alias("region_key"),
            F.col("maturity").alias("maturity_key"),
            F.col("asOf").alias("date_key"),
            "verifiedBy",
            "sourceUrl",
            "sourcePath",
            "sourceCommit",
        ),
        "fact_availability_evidence",
    )

    deployed = spark.read.table(f"{SILVER_SCHEMA}.evidence_deployed_bom")
    _write(
        deployed.select(
            "resourceId", "resourceType", "modulePath", "sourcePath", "sourceCommit"
        ),
        "fact_bom_deployment",
    )

    # Bridges.
    deps = spark.read.table(f"{SILVER_SCHEMA}.evidence_dependencies")
    _write(
        deps.select(
            F.col("fromId").alias("resource_key"),
            F.col("toId").alias("depends_on_key"),
            F.col("type").alias("edge_type"),
            "sourcePath",
            "sourceCommit",
        ),
        "bridge_resource_dependency",
    )

    bom = spark.read.table(f"{SILVER_SCHEMA}.evidence_bom")
    req_bridge = (
        bom.select(F.col("id").alias("resource_key"), F.explode_outer("realisesRequirements").alias("requirement_key"),
                   "sourcePath", "sourceCommit")
        .filter(F.col("requirement_key").isNotNull())
    )
    _write(req_bridge, "bridge_requirement_resource")

    req_adr = spark.read.table(f"{SILVER_SCHEMA}.evidence_req_adr_map")
    _write(
        req_adr.select(
            F.col("requirementId").alias("requirement_key"),
            F.col("adrId").alias("adr_key"),
            "relationship",
            "sourcePath",
            "sourceCommit",
        ),
        "bridge_requirement_adr",
    )


if __name__ == "__main__":  # pragma: no cover - Fabric runtime only
    build_gold_facts(spark)  # noqa: F821
