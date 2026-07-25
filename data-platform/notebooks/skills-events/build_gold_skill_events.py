"""Sprint 23 WS-A4 -- Gold projection for the near-real-time skills-events lane.

Projects clean Silver DC-SKILL-EVENT-v1 events onto a small star-schema Gold spine:
a ``gold.skillevt_fact_event`` fact plus ``gold.skillevt_dim_source`` and
``gold.skillevt_dim_kind`` dimensions. Column names are prefixed ``skillevt_`` to keep
this near-real-time event spine distinct from both the internal capacity gold tables
and the batch org/skills gold tables -- exactly as the ``external-signals`` lane keeps
its ``ext_*`` spine separate. Because it is NOT a Direct-Lake table in the
capacity-dashboard semantic model, it is not part of the derived gold contract
(``verify_gold_schema.contract_tables``) and does not affect that parity gate;
semantic-model surfacing is a documented follow-up.

The live-vs-simulated badge (``sourceMode`` -> ``skillevt_data_mode``) travels from the
contract and is never invented downstream. The pure functions here are unit-tested
without Spark (see ``tests/test_skill_events_pure.py``).
"""
from __future__ import annotations

import sys

_DATA_MODE = {"live": "Live", "simulated": "Simulated"}

_KIND_DESCRIPTION = {
    "credential-expiry": "A certification/credential lapsed; the associated assertion stops counting.",
    "consent-grant-or-revoke": "A Work-ID consent decision that grants or revokes GLN promotion + scope.",
    "newly-confirmed-assertion": "An employer confirmed a self-declared skill (L0 -> L1 transition).",
}


def data_mode_for(source_mode: str) -> str:
    """Map the live-vs-simulated source mode to its display trust-badge data mode."""
    return _DATA_MODE[source_mode]


def to_gold_event(rec: dict) -> dict:
    """Project one Silver event record onto a ``gold.skillevt_fact_event`` row."""
    return {
        "skillevt_event_id": rec.get("eventId"),
        "skillevt_kind": rec.get("eventKind"),
        "skillevt_external_system": rec.get("externalSystem"),
        "skillevt_data_mode": data_mode_for(rec.get("sourceMode")),
        "skillevt_trust_tier": rec.get("trustTier"),
        "skillevt_person_ref": rec.get("externalPersonRef"),
        "skillevt_worker_gln": rec.get("workerGln"),
        "skillevt_skill_code": rec.get("externalSkillCode"),
        "skillevt_skill_label": rec.get("externalSkillLabel"),
        "skillevt_consent_action": rec.get("consentAction"),
        "skillevt_consent_scope": rec.get("consentScope"),
        "skillevt_credential_valid": rec.get("credentialValid"),
        "skillevt_confirmed": rec.get("confirmed"),
        "skillevt_effective_at": rec.get("effectiveAt"),
    }


def skillevt_dim_source_row(rec: dict) -> dict:
    """Build one gold.skillevt_dim_source row, carrying the trust badge."""
    return {
        "skillevt_external_system": rec.get("externalSystem"),
        "skillevt_data_mode": data_mode_for(rec.get("sourceMode")),
        "skillevt_trust_tier": rec.get("trustTier"),
    }


def to_gold_dims(records: list[dict]) -> dict[str, list[dict]]:
    """Derive the source + kind dimensions from a batch of Silver events."""
    sources: dict[str, dict] = {}
    kinds: dict[str, dict] = {}
    for rec in records:
        sys_id = rec.get("externalSystem")
        if sys_id and sys_id not in sources:
            sources[sys_id] = skillevt_dim_source_row(rec)
        kind = rec.get("eventKind")
        if kind and kind not in kinds:
            kinds[kind] = {
                "skillevt_kind": kind,
                "skillevt_kind_description": _KIND_DESCRIPTION.get(kind, ""),
            }
    return {
        "skillevt_dim_source": [sources[k] for k in sorted(sources)],
        "skillevt_dim_kind": [kinds[k] for k in sorted(kinds)],
    }


def gold_tables(records: list[dict]) -> dict[str, list[dict]]:
    """Bundle the fact + two dimensions for a batch of Silver events."""
    dims = to_gold_dims(records)
    return {
        "skillevt_fact_event": [to_gold_event(r) for r in records],
        "skillevt_dim_source": dims["skillevt_dim_source"],
        "skillevt_dim_kind": dims["skillevt_dim_kind"],
    }


GOLD_SCHEMA = "gold"
SILVER_TABLE = "silver.skill_events"


def _write(df, table: str) -> None:  # pragma: no cover - Fabric runtime only
    df.write.format("delta").mode("overwrite").option(
        "overwriteSchema", "true"
    ).saveAsTable(f"{GOLD_SCHEMA}.{table}")
    print(f"gold: wrote {GOLD_SCHEMA}.{table} ({df.count()} rows)")


def _empty_schema(name: str):  # pragma: no cover - Fabric runtime only
    from pyspark.sql.types import (  # noqa: PLC0415 - lazy import for offline compat
        BooleanType,
        StringType,
        StructField,
        StructType,
    )

    schemas = {
        "skillevt_fact_event": StructType([
            StructField("skillevt_event_id", StringType(), True),
            StructField("skillevt_kind", StringType(), True),
            StructField("skillevt_external_system", StringType(), True),
            StructField("skillevt_data_mode", StringType(), True),
            StructField("skillevt_trust_tier", StringType(), True),
            StructField("skillevt_person_ref", StringType(), True),
            StructField("skillevt_worker_gln", StringType(), True),
            StructField("skillevt_skill_code", StringType(), True),
            StructField("skillevt_skill_label", StringType(), True),
            StructField("skillevt_consent_action", StringType(), True),
            StructField("skillevt_consent_scope", StringType(), True),
            StructField("skillevt_credential_valid", BooleanType(), True),
            StructField("skillevt_confirmed", BooleanType(), True),
            StructField("skillevt_effective_at", StringType(), True),
        ]),
        "skillevt_dim_source": StructType([
            StructField("skillevt_external_system", StringType(), True),
            StructField("skillevt_data_mode", StringType(), True),
            StructField("skillevt_trust_tier", StringType(), True),
        ]),
        "skillevt_dim_kind": StructType([
            StructField("skillevt_kind", StringType(), True),
            StructField("skillevt_kind_description", StringType(), True),
        ]),
    }
    return schemas[name]


def build_gold_skill_events(spark) -> None:  # pragma: no cover - Fabric runtime only
    """Read Silver skill_events and write all Gold skillevt tables."""
    df = spark.read.table(SILVER_TABLE)
    rows = [r.asDict(recursive=True) for r in df.collect()]
    tables = gold_tables(rows)
    for name, data in tables.items():
        out_df = spark.createDataFrame(data, _empty_schema(name))
        _write(out_df, name)


def run() -> None:  # pragma: no cover - Fabric runtime only
    """Fabric entrypoint. Reads Silver, writes gold.skillevt_fact_event + dims."""
    from pyspark.sql import SparkSession  # noqa: PLC0415 - Fabric-provided

    build_gold_skill_events(SparkSession.builder.getOrCreate())


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
