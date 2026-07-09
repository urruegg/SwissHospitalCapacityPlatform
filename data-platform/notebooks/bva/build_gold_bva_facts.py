# Fabric notebook — bva: build_gold_bva_facts
#
# Sprint 15 · T3 — BVA medallion Gold facts. Aggregates Silver into the Gold
# star-schema facts (design spec §5) via the pure, unit-tested `bva_transforms`.
#
# Gold facts: gold.bva_fact_azure_consumption (resource × meter × day),
#   gold.bva_fact_budget (env × capability × month plan baseline),
#   gold.bva_fact_value_realization (capability × month × hospital)
#
# Adoption telemetry from Sprint 12 is joined into gold.bva_fact_value_realization in
# T4 (see build_gold_bva_facts adoption-join block). Until then adoption_count is
# 0 and benefit is cost-derived only.
#
# Runtime: Microsoft Fabric notebook (PySpark). Publish gated by
# `approved-to-apply` (AGENTS.md §4).

import bva_transforms as T

SILVER_SCHEMA = "silver"
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


def _persona_hospital(spark):  # pragma: no cover - Fabric runtime only
    """Map upn -> hospital from the persona dimension, for adoption attribution."""
    try:
        rows = [r.asDict() for r in spark.read.table("gold.dim_persona").collect()]
    except Exception:  # noqa: BLE001 - dim may be named differently / absent
        return {}
    mapping = {}
    for r in rows:
        upn = r.get("upn") or r.get("user_principal_name")
        hospital = r.get("default_hospital") or r.get("hospital_key")
        if upn and hospital:
            mapping[upn] = hospital
    return mapping


def _load_adoption_index(spark):  # pragma: no cover - Fabric runtime only
    """Build the (capability, month, hospital) -> active-user index from Bronze.

    Returns ``None`` when no adoption Bronze table is present (T3 baseline); T4
    wires the Sprint 12 sign-in join here.
    """
    try:
        signins = [r.asDict() for r in spark.read.table("bronze.bva_adoption").collect()]
    except Exception:  # noqa: BLE001 - table may not exist before T4
        return None
    return T.adoption_index_from_signins(signins, persona_hospital=_persona_hospital(spark))


def build_gold_bva_facts(spark) -> None:  # pragma: no cover - Fabric runtime only
    silver = [r.asDict() for r in spark.read.table(f"{SILVER_SCHEMA}.bva_consumption").collect()]

    _write(spark, T.fact_azure_consumption(silver), "fact_azure_consumption")
    _write(spark, T.fact_budget(silver), "fact_budget")

    adoption_index = _load_adoption_index(spark)
    _write(
        spark,
        T.fact_value_realization(silver, adoption_index=adoption_index),
        "fact_value_realization",
    )


if __name__ == "__main__":  # pragma: no cover - Fabric runtime only
    build_gold_bva_facts(spark)  # noqa: F821
