"""Pure transforms used by silver/gold notebooks. Local-testable, no Fabric runtime."""
from __future__ import annotations

from typing import Tuple

from pyspark.sql import DataFrame, functions as F

_EPISODE_ALLOWLIST = ["episode_id", "patient_id", "admit_ts", "discharge_ts", "ward"]
_PSEUDONYM_RE = r"^pseudo-[a-z0-9]{16}$"


def bronze_to_silver_episode(bronze: DataFrame) -> DataFrame:
    silver, _ = bronze_to_silver_episode_with_quarantine(bronze)
    return silver


def bronze_to_silver_episode_with_quarantine(bronze: DataFrame) -> Tuple[DataFrame, DataFrame]:
    projected = bronze.select(*[c for c in _EPISODE_ALLOWLIST if c in bronze.columns])
    valid = projected.filter(F.col("patient_id").rlike(_PSEUDONYM_RE))
    invalid = projected.filter(~F.col("patient_id").rlike(_PSEUDONYM_RE))
    quarantine = (
        invalid
        .withColumn("quarantine_reason", F.lit("pii-shape-mismatch"))
        .withColumn("quarantine_ts", F.current_timestamp())
    )
    return valid, quarantine


def silver_episode_to_gold_demand_encounter(silver: DataFrame, provenance_source: str) -> DataFrame:
    return (
        silver
        .withColumn("provenance_source", F.lit(provenance_source))
        .withColumn("purpose_tags", F.array(F.lit("capacity-planning")))
        .withColumn("residency", F.lit("CH"))
        .withColumn("emitted_ts", F.current_timestamp())
    )
