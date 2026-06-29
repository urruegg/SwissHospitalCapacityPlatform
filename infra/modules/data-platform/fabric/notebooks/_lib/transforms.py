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


def simulator_records_to_gold_demand_encounter(records: DataFrame) -> DataFrame:
    # Parse explicit UTC ISO-8601 timestamps from simulator envelopes.
    arrival_ts = F.to_timestamp(F.col("expectedArrivalTimestamp"), "yyyy-MM-dd'T'HH:mm:ssX")
    los_days = F.coalesce(F.col("expectedLOSDays"), F.lit(1))
    # Keep patient_id aligned to silver pseudonym regex: pseudo-[a-z0-9]{16}.
    pseudo_seed = F.lower(F.regexp_replace(F.col("pseudonymId"), r"^PID-", ""))

    return (
        records
        .withColumn("episode_id", F.col("encounterId"))
        .withColumn("patient_id", F.concat(F.lit("pseudo-"), F.concat(pseudo_seed, pseudo_seed)))
        .withColumn("admit_ts", arrival_ts)
        .withColumn(
            "discharge_ts",
            F.from_unixtime(F.unix_timestamp(arrival_ts) + (los_days * F.lit(86400))).cast("timestamp"),
        )
        .withColumn("ward", F.col("requestedSpecialtyServiceId"))
        .withColumn("provenance_source", F.lit("simulator"))
        .withColumn("purpose_tags", F.array(F.lit("capacity-planning")))
        .withColumn("residency", F.lit("CH"))
        .withColumn("emitted_ts", F.to_timestamp(F.col("asOfTimestamp"), "yyyy-MM-dd'T'HH:mm:ssX"))
        .select(
            "episode_id",
            "patient_id",
            "admit_ts",
            "discharge_ts",
            "ward",
            "provenance_source",
            "purpose_tags",
            "residency",
            "emitted_ts",
        )
    )
