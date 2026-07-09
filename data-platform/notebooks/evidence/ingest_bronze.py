# Fabric notebook — evidence: ingest_bronze
#
# Sprint 14 · T3 — Showcase Evidence medallion (Bronze layer).
# Reads the byte-stable evidence JSON published to the `evidence-latest` branch
# (or an OneLake shortcut) and lands it verbatim as Bronze Delta tables.
#
# Runtime: Microsoft Fabric notebook (PySpark) against workspace
# `ws-ihzhhpf-sit-data` / lakehouse `lh_ihzhhpf_sit`. Publishing this notebook
# and running the pipeline is a `deploy`-ceiling action gated by
# `approved-to-apply` (AGENTS.md §4).

# CELL: parameters -----------------------------------------------------------
EVIDENCE_SOURCE = "abfss://evidence-latest@onelake/data/evidence"  # OneLake shortcut
BRONZE_SCHEMA = "bronze"

EVIDENCE_FILES = [
    "requirements",
    "adrs",
    "req_adr_map",
    "bom",
    "dependencies",
    "region_availability",
    "deployed_bom",
]


# CELL: ingest ---------------------------------------------------------------
def ingest_bronze(spark, source: str = EVIDENCE_SOURCE, schema: str = BRONZE_SCHEMA) -> None:
    """Land each evidence JSON file as a raw Bronze Delta table (schema-on-read)."""
    for name in EVIDENCE_FILES:
        df = (
            spark.read.option("multiline", "true")
            .json(f"{source}/{name}.json")
        )
        target = f"{schema}.evidence_{name}"
        df.write.format("delta").mode("overwrite").option(
            "overwriteSchema", "true"
        ).saveAsTable(target)
        print(f"bronze: wrote {target} ({df.count()} rows)")


if __name__ == "__main__":  # pragma: no cover - Fabric runtime only
    ingest_bronze(spark)  # noqa: F821 - `spark` is injected by the Fabric runtime
