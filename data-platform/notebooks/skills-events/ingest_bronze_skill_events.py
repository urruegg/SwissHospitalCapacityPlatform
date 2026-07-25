"""Sprint 23 WS-A4 -- Bronze ingest for the near-real-time skills-events lane.

Lands raw DC-SKILL-EVENT-v1 event records into the Fabric lakehouse Bronze layer
at ``Files/bronze/skills-events/`` (the destination the WS-A4 Eventstream module
writes to). The heavy Spark I/O is isolated in ``ingest_bronze_skill_events()`` so
the path convention stays unit-testable without a Spark session, mirroring the
``external-signals`` notebook pattern.

Synthetic-only (ADR-0013 / ADR-0016). No PHI -- the events describe individual
workers in shape only and carry synthetic identifiers.
"""
from __future__ import annotations

import sys
from pathlib import Path

# The normalize/synth package lives with the connector scripts; inject so
# ``skill_events_synth`` resolves at Fabric runtime.
_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts" / "skills-events"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

_BRONZE_ROOT = "Files/bronze/skills-events"

BRONZE_SCHEMA = "bronze"
BRONZE_TABLE = "skill_events_raw"


def bronze_path(event_kind: str, date: str) -> str:
    """Return the Bronze landing path for an event kind on a given ingest date.

    ``event_kind`` is the routing property the Eventstream lane filters on
    (e.g. ``credential-expiry``); ``date`` is an ISO ``YYYY-MM-DD`` partition key.
    """
    if not event_kind:
        raise ValueError("event_kind is required")
    if not date:
        raise ValueError("date is required")
    return f"{_BRONZE_ROOT}/{event_kind}/{date}"


def ingest_bronze_skill_events(spark, records: list[dict]) -> None:  # pragma: no cover - Fabric runtime only
    """Write raw DC-SKILL-EVENT-v1 records to bronze.skill_events_raw (Delta, overwrite)."""
    df = spark.createDataFrame(records)
    df.write.format("delta").mode("overwrite").option(
        "overwriteSchema", "true"
    ).saveAsTable(f"{BRONZE_SCHEMA}.{BRONZE_TABLE}")
    print(f"bronze: wrote {BRONZE_SCHEMA}.{BRONZE_TABLE} ({df.count()} rows)")


def run() -> None:  # pragma: no cover - Fabric runtime only
    """Fabric entrypoint. Loads the synthetic seed and writes bronze.skill_events_raw."""
    from pyspark.sql import SparkSession  # noqa: PLC0415 - Fabric-provided
    from skill_events_synth import build_records  # noqa: PLC0415 - offline seeder

    ingest_bronze_skill_events(SparkSession.builder.getOrCreate(), build_records())


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
