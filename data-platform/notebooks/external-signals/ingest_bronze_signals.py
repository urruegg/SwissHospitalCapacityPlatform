"""Sprint 21 M3 — Bronze ingest for the Trusted External Signals lane.

Lands raw DC-EXT-SIGNAL-v1 connector output into the Fabric lakehouse Bronze
layer, partitioned by source and ingest date. The heavy Spark I/O is isolated in
``ingest_bronze_signals()`` so the path convention stays unit-testable without a
Spark session (see ``tests/test_signals_pure.py``), mirroring the CSA notebook
pattern (``data-platform/notebooks/csa/``).

Synthetic-only (ADR-0013 / ADR-0016). No PHI — external hazard feeds carry only
Trust-A public authority warnings.
"""
from __future__ import annotations

import sys
from pathlib import Path

# The M2 dedup/normalize package (and signals_synth) live with the connector
# scripts; inject so ``signals_synth`` resolves at Fabric runtime.
_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts" / "external-signals"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

_BRONZE_ROOT = "Files/Bronze/external-signals"

BRONZE_SCHEMA = "bronze"
BRONZE_TABLE = "ext_signals_raw"


def bronze_path(source: str, date: str) -> str:
    """Return the Bronze landing path for a source feed on a given ingest date.

    ``source`` is the connector ``source_id`` (e.g. ``meteoswiss``); ``date`` is
    an ISO ``YYYY-MM-DD`` partition key.
    """
    if not source:
        raise ValueError("source is required")
    if not date:
        raise ValueError("date is required")
    return f"{_BRONZE_ROOT}/{source}/{date}"


def ingest_bronze_signals(spark, records: list[dict]) -> None:  # pragma: no cover - Fabric runtime only
    """Write raw DC-EXT-SIGNAL-v1 records to bronze.ext_signals_raw (Delta, overwrite)."""
    df = spark.createDataFrame(records)
    df.write.format("delta").mode("overwrite").option(
        "overwriteSchema", "true"
    ).saveAsTable(f"{BRONZE_SCHEMA}.{BRONZE_TABLE}")
    print(f"bronze: wrote {BRONZE_SCHEMA}.{BRONZE_TABLE} ({df.count()} rows)")


def run() -> None:  # pragma: no cover - Fabric runtime only
    """Fabric entrypoint. Loads synthetic seed and writes bronze.ext_signals_raw."""
    from pyspark.sql import SparkSession  # noqa: PLC0415 - Fabric-provided
    from signals_synth import build_records  # noqa: PLC0415 - offline seeder

    ingest_bronze_signals(SparkSession.builder.getOrCreate(), build_records())


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())

