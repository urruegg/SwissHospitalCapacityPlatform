"""Sprint 26 WS-A — Foresight tier: ``gold.fact_signal`` projection.

The Foresight signal surface is a **deny-by-default, Trust-A** projection over the
Sprint 21 external-signal spine (``gold.ext_fact_signal`` joined with
``gold.ext_dim_source`` for the trust tier; DC-EXT-SIGNAL-v1). It carries a
**deterministic** probability derived from the signal severity and the
driver-evidence linkage (``evidencedBy`` -> ``hcp:ExternalSignal``). No new
contract is introduced — the Sprint 21 signal spine is reused, not duplicated.

Pure functions are unit-tested offline (``tests/test_signal_pure.py``); the
Spark ``run()`` wrapper is Fabric-runtime only.
"""
from __future__ import annotations

import sys
from typing import List

# Deterministic severity -> probability map (no model, no LLM estimate).
_SEVERITY_PROBABILITY = {
    "Extreme": 0.95,
    "Severe": 0.90,
    "Moderate": 0.60,
    "Minor": 0.30,
}
_DEFAULT_PROBABILITY = 0.10
_TRUST_A = "A"
# Foresight signals evidence the seasonality driver of the occupancy forecast.
_EVIDENCES_FACTOR = "seasonality"


def signal_probability(severity: str) -> float:
    """Deterministic probability for a signal severity; unknown -> conservative low."""
    return _SEVERITY_PROBABILITY.get(severity, _DEFAULT_PROBABILITY)


def _eligible(row: dict) -> bool:
    """Deny-by-default: keep only Trust-A signals."""
    return row.get("ext_trust_tier") == _TRUST_A


def to_foresight_signal(row: dict) -> dict:
    """Project one enriched ext_fact_signal row onto a ``gold.fact_signal`` row."""
    return {
        "signal_id": row.get("ext_signal_id"),
        "source_id": row.get("ext_source_id"),
        "hazard_type": row.get("ext_hazard_type"),
        "severity": row.get("ext_severity"),
        "trust_tier": row.get("ext_trust_tier"),
        "probability": signal_probability(row.get("ext_severity")),
        "evidences_factor": _EVIDENCES_FACTOR,
        "cantons": list(row.get("ext_cantons", [])),
        "onset": row.get("ext_onset"),
    }


def foresight_signals(ext_rows: List[dict]) -> List[dict]:
    """Trust-A projection of the external-signal spine for the Foresight tier."""
    return [to_foresight_signal(r) for r in ext_rows if _eligible(r)]


# ---------------------------------------------------------------------------
# Fabric Spark runtime — heavy I/O only, exercised in the notebook, not offline.
# ---------------------------------------------------------------------------
def _empty_schema():  # pragma: no cover - requires pyspark
    from pyspark.sql.types import (
        ArrayType, DoubleType, StringType, StructField, StructType,
    )

    return StructType([
        StructField("signal_id", StringType(), True),
        StructField("source_id", StringType(), True),
        StructField("hazard_type", StringType(), True),
        StructField("severity", StringType(), True),
        StructField("trust_tier", StringType(), True),
        StructField("probability", DoubleType(), True),
        StructField("evidences_factor", StringType(), True),
        StructField("cantons", ArrayType(StringType()), True),
        StructField("onset", StringType(), True),
    ])


def build_gold_signal(spark) -> None:  # pragma: no cover - Fabric runtime only
    """Read the Sprint 21 gold ext_fact_signal + ext_dim_source, write gold.fact_signal."""
    fact = spark.read.table("gold.ext_fact_signal")
    source = spark.read.table("gold.ext_dim_source").select("ext_source_id", "ext_trust_tier")
    enriched = fact.join(source, on="ext_source_id", how="left")
    rows = [r.asDict(recursive=True) for r in enriched.collect()]
    projected = foresight_signals(rows)
    schema = _empty_schema()
    df = spark.createDataFrame(projected, schema) if projected else spark.createDataFrame([], schema)
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("gold.fact_signal")
    print(f"gold: wrote gold.fact_signal ({df.count()} rows)")


def run() -> None:  # pragma: no cover - Fabric runtime only
    """Fabric entrypoint. Writes gold.fact_signal from the external-signal spine."""
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.getOrCreate()
    spark.sql("CREATE SCHEMA IF NOT EXISTS gold")
    build_gold_signal(spark)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
