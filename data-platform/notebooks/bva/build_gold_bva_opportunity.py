# Fabric notebook — bva: build_gold_bva_opportunity
#
# Sprint 33 WS-D — one-way BVA Opportunity Gold projection. Cosmos DB remains
# the system of record; this notebook reads Opportunity documents and delegates
# all flattening / aggregate logic to the pure `opportunity_projection` module.
#
# Gold outputs: gold.bva_opportunity, gold.bva_opportunity_pipeline
#
# Runtime: Microsoft Fabric notebook (PySpark). Cosmos reads use managed
# identity / workload identity via the D2 Opportunity store helper; no secrets
# or connection strings are embedded here. Publishing remains gated by
# approved-to-apply (AGENTS.md §4).

try:
    from bva.opportunity_projection import build_all  # packaged import
    from bva.opportunity_store import OPPORTUNITIES_CONTAINER, get_database_client
except ImportError:  # pragma: no cover - Fabric runtime only
    from opportunity_projection import build_all  # type: ignore[no-redef]
    from opportunity_store import OPPORTUNITIES_CONTAINER, get_database_client  # type: ignore[no-redef]

GOLD_SCHEMA = "gold"
BVA_PREFIX = "bva_"


def _write(spark, rows, table: str) -> None:  # pragma: no cover - Fabric runtime only
    df = spark.createDataFrame(rows)
    (
        df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(f"{GOLD_SCHEMA}.{BVA_PREFIX}{table}")
    )
    print(f"gold: wrote {GOLD_SCHEMA}.{BVA_PREFIX}{table} ({df.count()} rows)")


def _read_opportunities_from_cosmos() -> list[dict]:  # pragma: no cover - Fabric runtime only
    database = get_database_client()
    if database is None:
        raise RuntimeError(
            "BVA Cosmos is not configured or Azure SDK authentication is unavailable; "
            "set BVA_COSMOS_ENDPOINT / BVA_COSMOS_DATABASE in the Fabric environment."
        )
    container = database.get_container_client(OPPORTUNITIES_CONTAINER)
    query = "SELECT * FROM c"
    return [dict(item) for item in container.query_items(query=query, enable_cross_partition_query=True)]


def build_gold_bva_opportunity(spark) -> None:  # pragma: no cover - Fabric runtime only
    tables = build_all(_read_opportunities_from_cosmos())

    _write(spark, tables["bva_opportunity"], "opportunity")
    _write(spark, tables["bva_opportunity_pipeline"], "opportunity_pipeline")
    print("gold: wrote Sprint 33 WS-D BVA Opportunity projection tables (2)")


if __name__ == "__main__":  # pragma: no cover - Fabric runtime only
    build_gold_bva_opportunity(spark)  # noqa: F821
