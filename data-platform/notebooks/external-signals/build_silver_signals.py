"""Sprint 21 M3 — Silver transform for the Trusted External Signals lane.

Splits raw DC-EXT-SIGNAL-v1 records into a clean ``silver.ext_signals`` stream
(status == "Actual") and a ``silver.ext_signals_quarantine`` stream (drills,
exercises, tests, expired) so downstream forecasting never pre-seeds on a
non-actual warning. Overlapping actual warnings are collapsed into deduplicated
``HazardEvents`` via ``dedup.collapse``.

The pure functions here are unit-tested without Spark (see
``tests/test_signals_pure.py``), following the CSA notebook pattern. The M2
``dedup``/``normalize`` package is loaded by path so this file stays importable
from the notebook directory during offline tests.
"""
from __future__ import annotations

import sys
from pathlib import Path

# The M2 dedup/normalize package lives with the connector scripts; put it on the
# path so ``dedup`` (which does ``from normalize import dedup_key``) resolves.
_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts" / "external-signals"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from dedup import collapse  # noqa: E402 - path injected above

SILVER_SCHEMA = "silver"
SILVER_TABLE = "ext_signals"
SILVER_QUARANTINE_TABLE = "ext_signals_quarantine"
BRONZE_TABLE = "bronze.ext_signals_raw"


def split_quarantine(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """Partition records into (kept, quarantined).

    ``kept`` retains only ``status == "Actual"`` warnings that pre-seed
    downstream forecasts; everything else (Exercise, Test, Draft, expired) is
    quarantined for audit.
    """
    kept = [r for r in records if r.get("status") == "Actual"]
    quarantined = [r for r in records if r.get("status") != "Actual"]
    return kept, quarantined


def hazard_events(kept: list[dict]) -> list[dict]:
    """Collapse kept actual signals into deduplicated HazardEvents (M2 dedup)."""
    return collapse(kept)


def _write(df, table: str) -> None:
    df.write.format("delta").mode("overwrite").option(
        "overwriteSchema", "true"
    ).saveAsTable(f"{SILVER_SCHEMA}.{table}")
    print(f"silver: wrote {SILVER_SCHEMA}.{table} ({df.count()} rows)")


def build_silver_signals(spark) -> None:  # pragma: no cover - Fabric runtime only
    """Read Bronze ext_signals_raw, split, and write silver.ext_signals + quarantine."""
    df = spark.read.table(BRONZE_TABLE)
    schema = df.schema
    rows = [r.asDict(recursive=True) for r in df.collect()]
    kept, quarantined = split_quarantine(rows)
    _write(spark.createDataFrame(kept, schema), SILVER_TABLE)
    _write(spark.createDataFrame(quarantined, schema), SILVER_QUARANTINE_TABLE)


def run() -> None:  # pragma: no cover - Fabric runtime only
    """Fabric entrypoint. Reads Bronze, writes silver.ext_signals + quarantine."""
    from pyspark.sql import SparkSession  # noqa: PLC0415 - Fabric-provided

    build_silver_signals(SparkSession.builder.getOrCreate())


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
