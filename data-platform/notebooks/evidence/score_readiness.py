# Fabric notebook — evidence: score_readiness
#
# Sprint 14 · T3 — Showcase Evidence medallion (readiness scoring, Silver -> Gold).
# Applies the pure T-SHOW / T-PROD scoring rules (ADR-0021) to the Silver
# evidence tables and writes gold.fact_readiness_snapshot. The scoring logic
# lives in readiness_rules.py so it can be unit-tested off-cluster with a
# byte-stable golden regression fixture.
#
# Runtime: Microsoft Fabric notebook (PySpark). Publish gated by
# `approved-to-apply` (AGENTS.md §4).

SILVER_SCHEMA = "silver"
GOLD_SCHEMA = "gold"

# In a Fabric notebook, co-locate readiness_rules.py or attach it as a resource.
from readiness_rules import aggregate_readiness, score_readiness  # noqa: E402


def score_readiness_gold(spark) -> None:
    """Score readiness from Silver and write the Gold snapshot + aggregate."""
    bom_rows = [r.asDict() for r in spark.read.table(f"{SILVER_SCHEMA}.evidence_bom").collect()]
    dep_rows = [r.asDict() for r in spark.read.table(f"{SILVER_SCHEMA}.evidence_dependencies").collect()]
    avail_rows = [
        r.asDict()
        for r in spark.read.table(f"{SILVER_SCHEMA}.evidence_region_availability").collect()
    ]

    # Reattach dependency edges to their BOM items for the pure scorer.
    deps_by_from: dict = {}
    for edge in dep_rows:
        deps_by_from.setdefault(edge["fromId"], []).append({"to": edge["toId"], "type": edge["type"]})
    bom_items = [{"id": b["id"], "dependsOn": deps_by_from.get(b["id"], [])} for b in bom_rows]

    rows = score_readiness(bom_items, avail_rows)
    summary = aggregate_readiness(rows)

    spark.createDataFrame(rows).write.format("delta").mode("overwrite").option(
        "overwriteSchema", "true"
    ).saveAsTable(f"{GOLD_SCHEMA}.fact_readiness_snapshot")
    spark.createDataFrame(summary).write.format("delta").mode("overwrite").option(
        "overwriteSchema", "true"
    ).saveAsTable(f"{GOLD_SCHEMA}.fact_readiness_summary")
    print(f"gold: fact_readiness_snapshot ({len(rows)} rows), summary ({len(summary)} rows)")


if __name__ == "__main__":  # pragma: no cover - Fabric runtime only
    score_readiness_gold(spark)  # noqa: F821
