# Fabric notebook — evidence: build_silver
#
# Sprint 14 · T3 — Showcase Evidence medallion (Silver layer).
# Types and de-duplicates the Bronze evidence tables, enforcing the provenance
# contract: every Silver row must carry sourcePath + sourceCommit (facts also
# require verifiedBy + asOf). Rows failing the contract are quarantined.
#
# Runtime: Microsoft Fabric notebook (PySpark). Publish gated by
# `approved-to-apply` (AGENTS.md §4).

# CELL: parameters -----------------------------------------------------------
BRONZE_SCHEMA = "bronze"
SILVER_SCHEMA = "silver"

# Provenance columns required per table family (design spec §3 "Silver typing").
PROVENANCE_DIM = ["sourcePath", "sourceCommit"]
PROVENANCE_FACT = ["sourcePath", "sourceCommit", "verifiedBy", "asOf"]

TABLES = {
    "requirements": PROVENANCE_DIM,
    "adrs": PROVENANCE_DIM,
    "req_adr_map": PROVENANCE_DIM,
    "bom": PROVENANCE_DIM,
    "dependencies": PROVENANCE_DIM,
    "region_availability": PROVENANCE_FACT,
    "deployed_bom": PROVENANCE_DIM,
}


# CELL: build silver ---------------------------------------------------------
def build_silver(spark, tables: dict = TABLES) -> None:
    """Type + enforce provenance from Bronze into Silver Delta tables."""
    from pyspark.sql import functions as F

    for name, required in tables.items():
        bronze = spark.read.table(f"{BRONZE_SCHEMA}.evidence_{name}")

        # Provenance gate — a row is valid only if every required column is set.
        condition = None
        for col in required:
            present = F.col(col).isNotNull() & (F.trim(F.col(col)) != "")
            condition = present if condition is None else (condition & present)

        valid = bronze.filter(condition)
        quarantined = bronze.filter(~condition)

        valid.write.format("delta").mode("overwrite").option(
            "overwriteSchema", "true"
        ).saveAsTable(f"{SILVER_SCHEMA}.evidence_{name}")

        q_count = quarantined.count()
        if q_count:
            quarantined.write.format("delta").mode("overwrite").option(
                "overwriteSchema", "true"
            ).saveAsTable(f"{SILVER_SCHEMA}.evidence_{name}_quarantine")
        print(f"silver: {name} -> {valid.count()} valid, {q_count} quarantined")


if __name__ == "__main__":  # pragma: no cover - Fabric runtime only
    build_silver(spark)  # noqa: F821
