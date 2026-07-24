"""Sprint 21 M3 - Gold projection for the Trusted External Signals lane.

Projects clean Silver DC-EXT-SIGNAL-v1 records onto the star-schema Gold layer
that the forecast overlay + semantic model consume: a ``gold.ext_fact_signal``
fact plus ``gold.ext_dim_source`` / ``gold.ext_dim_hazard_type`` /
``gold.ext_dim_region`` dimensions. Column names are prefixed ``ext_`` to keep
the external-signal spine distinct from the internal capacity gold tables.

The pure functions here are unit-tested without Spark (see
``tests/test_signals_pure.py``), following the CSA notebook pattern.
"""
from __future__ import annotations

import sys


_DATA_MODE = {"live": "Live", "simulated": "Simulated", "internal": "Internal"}


def data_mode_for(active_binding: str) -> str:
    """Map a provenance active binding to its display trust-badge data mode."""
    return _DATA_MODE[active_binding]


def ext_dim_source_row(rec: dict) -> dict:
    """Build one gold.ext_dim_source row, carrying the trust badge."""
    prov = rec.get("provenance", {})
    binding = prov.get("activeBinding", "live")
    return {
        "ext_source_id": rec.get("sourceId"),
        "ext_source_authority": rec.get("sourceAuthority"),
        "ext_trust_tier": rec.get("trustTier"),
        "ext_data_mode": data_mode_for(binding),
        "ext_fell_back_from": prov.get("fellBackFrom"),
        "ext_last_live_at": prov.get("ingestedAt") if binding == "live" else None,
    }


def to_gold_signal(rec: dict) -> dict:
    """Project one Silver signal record onto a ``gold.ext_fact_signal`` row."""
    return {
        "ext_signal_id": rec.get("signalId"),
        "ext_source_id": rec.get("sourceId"),
        "ext_hazard_type": rec.get("hazardType"),
        "ext_severity": rec.get("severity"),
        "ext_scenario_template": rec.get("mappedScenarioTemplate"),
        "ext_lage_tier": rec.get("defaultLageTier"),
        "ext_cantons": list((rec.get("region") or {}).get("cantons", [])),
        "ext_onset": rec.get("onset"),
        "ext_status": rec.get("status"),
    }


def to_gold_dims(records: list[dict]) -> dict[str, list[dict]]:
    """Derive the three Gold dimensions from a batch of Silver records."""
    sources: dict[str, dict] = {}
    source_seen_at: dict[str, str] = {}
    hazards: dict[str, dict] = {}
    regions: dict[str, dict] = {}
    for rec in records:
        sid = rec.get("sourceId")
        if sid:
            ingested = (rec.get("provenance") or {}).get("ingestedAt") or ""
            if sid not in sources or ingested >= source_seen_at.get(sid, ""):
                sources[sid] = ext_dim_source_row(rec)
                source_seen_at[sid] = ingested
        haz = rec.get("hazardType")
        if haz and haz not in hazards:
            hazards[haz] = {
                "ext_hazard_type": haz,
                "ext_scenario_template": rec.get("mappedScenarioTemplate"),
                "ext_default_lage_tier": rec.get("defaultLageTier"),
            }
        for canton in (rec.get("region") or {}).get("cantons", []):
            if canton not in regions:
                regions[canton] = {"ext_canton": canton}
    return {
        "ext_dim_source": [sources[k] for k in sorted(sources)],
        "ext_dim_hazard_type": [hazards[k] for k in sorted(hazards)],
        "ext_dim_region": [regions[k] for k in sorted(regions)],
    }


def gold_tables(records: list[dict]) -> dict[str, list[dict]]:
    """Bundle the fact + three dimensions for a batch of Silver records."""
    dims = to_gold_dims(records)
    return {
        "ext_fact_signal": [to_gold_signal(r) for r in records],
        "ext_dim_source": dims["ext_dim_source"],
        "ext_dim_hazard_type": dims["ext_dim_hazard_type"],
        "ext_dim_region": dims["ext_dim_region"],
    }


GOLD_SCHEMA = "gold"
SILVER_TABLE = "silver.ext_signals"


def _write(df, table: str) -> None:
    df.write.format("delta").mode("overwrite").option(
        "overwriteSchema", "true"
    ).saveAsTable(f"{GOLD_SCHEMA}.{table}")
    print(f"gold: wrote {GOLD_SCHEMA}.{table} ({df.count()} rows)")


def _empty_schema(name: str):
    from pyspark.sql.types import (  # noqa: PLC0415 - lazy import for offline compat
        ArrayType,
        LongType,
        StringType,
        StructField,
        StructType,
    )

    schemas = {
        "ext_fact_signal": StructType([
            StructField("ext_signal_id", StringType(), True),
            StructField("ext_source_id", StringType(), True),
            StructField("ext_hazard_type", StringType(), True),
            StructField("ext_severity", StringType(), True),
            StructField("ext_scenario_template", StringType(), True),
            StructField("ext_lage_tier", LongType(), True),
            StructField("ext_cantons", ArrayType(StringType()), True),
            StructField("ext_onset", StringType(), True),
            StructField("ext_status", StringType(), True),
        ]),
        "ext_dim_source": StructType([
            StructField("ext_source_id", StringType(), True),
            StructField("ext_source_authority", StringType(), True),
            StructField("ext_trust_tier", StringType(), True),
            StructField("ext_data_mode", StringType(), True),
            StructField("ext_fell_back_from", StringType(), True),
            StructField("ext_last_live_at", StringType(), True),
        ]),
        "ext_dim_hazard_type": StructType([
            StructField("ext_hazard_type", StringType(), True),
            StructField("ext_scenario_template", StringType(), True),
            StructField("ext_default_lage_tier", LongType(), True),
        ]),
        "ext_dim_region": StructType([
            StructField("ext_canton", StringType(), True),
        ]),
    }
    return schemas[name]


def build_gold_signals(spark) -> None:  # pragma: no cover - Fabric runtime only
    """Read Silver ext_signals and write all Gold ext tables."""
    df = spark.read.table(SILVER_TABLE)
    rows = [r.asDict(recursive=True) for r in df.collect()]
    tables = gold_tables(rows)
    for name, data in tables.items():
        out_df = spark.createDataFrame(data, _empty_schema(name))
        _write(out_df, name)


def run() -> None:  # pragma: no cover - Fabric runtime only
    """Fabric entrypoint. Reads Silver, writes gold.ext_fact_signal + dims."""
    from pyspark.sql import SparkSession  # noqa: PLC0415 - Fabric-provided

    build_gold_signals(SparkSession.builder.getOrCreate())


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
