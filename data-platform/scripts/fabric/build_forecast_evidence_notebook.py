#!/usr/bin/env python3
"""Generate a self-contained Fabric evidence notebook for the WS-A Foresight tier.

Why this exists (Sprint 26 WS-A, Fabric SIT evidence):

The committed Foresight notebook modules under
``data-platform/notebooks/foresight/*.py`` are authored as importable libraries
(pure functions + a ``run()`` Fabric entrypoint). They cannot be imported into
Fabric and executed as-is because their ``run()`` paths import sibling modules
and (for the signal) read the Sprint 21 ``gold.ext_fact_signal`` /
``gold.ext_dim_source`` tables, whose gold fact stores ``ext_cantons`` as a
scalar comma-joined string (not the array the pure projection expects).

This generator resolves that by pre-computing the deterministic gold rows
OFFLINE (reusing the committed Foresight pure functions and, for the signal, the
committed external-signals synthetic seed + gold projection to reproduce the
Trust-A join) and emitting ONE self-contained ``.ipynb`` whose cells carry the
data as literals and write every table with an EXPLICIT schema that matches the
committed ``_empty_schema`` contracts exactly. The emitted notebook has no
external imports, so it runs deterministically in Fabric against the default
lakehouse injected by ``run_medallion.py`` / the create+run path.

The result is the three WS-A gold evidence tables:
``gold.fact_occupancy_forecast`` / ``gold.fact_forecast_driver`` /
``gold.fact_signal``.

Synthetic-only, deterministic (ADR-0013 / ADR-0016). No PHI. The forecast +
driver series is a fixed synthetic ramp (design D2 seam); the signal projection
is a deny-by-default Trust-A view over the committed public-authority hazard
seed. Deployment + run of the emitted notebook is a ``deploy``-ceiling action
gated by ``approved-to-apply`` (AGENTS.md Section 4).

Usage::

    python data-platform/scripts/fabric/build_forecast_evidence_notebook.py
    # writes data-platform/notebooks/foresight/run_foresight_evidence.ipynb
"""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
FORESIGHT_DIR = REPO_ROOT / "data-platform" / "notebooks" / "foresight"
EXT_NB_DIR = REPO_ROOT / "data-platform" / "notebooks" / "external-signals"
EXT_SCRIPTS_DIR = REPO_ROOT / "data-platform" / "scripts" / "external-signals"
OUTPUT = FORESIGHT_DIR / "run_foresight_evidence.ipynb"

# Fixed, deterministic run stamp so the evidence is byte-reproducible.
PRODUCED_AT = datetime(2026, 7, 23, 0, 0, 0, tzinfo=timezone.utc)


def _load(directory: Path, name: str):
    spec = importlib.util.spec_from_file_location(
        name.replace(".py", ""), directory / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def compute_tables() -> dict[str, list[dict]]:
    """Compute the three WS-A gold tables deterministically, offline."""
    forecast_mod = _load(FORESIGHT_DIR, "build_gold_forecast.py")
    signal_mod = _load(FORESIGHT_DIR, "build_gold_signal.py")

    wards = forecast_mod.DEFAULT_WARDS
    occupancy = forecast_mod.build_occupancy_forecast(wards, PRODUCED_AT)
    drivers = forecast_mod.build_forecast_drivers(wards, PRODUCED_AT)

    # Reproduce the Spark join (gold.ext_fact_signal x gold.ext_dim_source) that
    # build_gold_signal.build_gold_signal() performs at runtime, but offline
    # from the committed synthetic ext seed so ext_cantons stays an array.
    if str(EXT_SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(EXT_SCRIPTS_DIR))
    from signals_synth import build_records  # noqa: PLC0415

    ext_silver = _load(EXT_NB_DIR, "build_silver_signals.py")
    ext_gold = _load(EXT_NB_DIR, "build_gold_signals.py")

    records = build_records()
    kept, _quarantined = ext_silver.split_quarantine(records)
    ext_bundle = ext_gold.gold_tables(kept)
    trust_by_source = {
        r["ext_source_id"]: r["ext_trust_tier"]
        for r in ext_bundle["ext_dim_source"]
    }
    enriched = [
        {**r, "ext_trust_tier": trust_by_source.get(r["ext_source_id"])}
        for r in ext_bundle["ext_fact_signal"]
    ]
    signals = signal_mod.foresight_signals(enriched)

    return {
        "gold.fact_occupancy_forecast": occupancy,
        "gold.fact_forecast_driver": drivers,
        "gold.fact_signal": signals,
    }


# Column order per the committed _empty_schema contracts (build_gold_forecast /
# build_gold_signal). Kept explicit so Fabric never infers types from all-None
# columns (e.g. driver.signalId is None for non-seasonality factors).
FORECAST_COLUMNS = [
    "contractId", "forecastId", "hospitalId", "wardId", "producedAt",
    "producedBy", "modelVersion", "horizonH", "bucketStart", "bedCapacity",
    "forecastOccupiedBeds", "forecastOccupancyPct", "lowerCi", "upperCi",
    "breach", "purposeTag", "dataResidencyRegion", "asOfTimestamp",
]
DRIVER_COLUMNS = [
    "contractId", "forecastId", "hospitalId", "wardId", "horizonH", "factor",
    "delta", "note", "signalId", "purposeTag", "asOfTimestamp",
]
SIGNAL_COLUMNS = [
    "signal_id", "source_id", "hazard_type", "severity", "trust_tier",
    "probability", "evidences_factor", "cantons", "onset",
]

# Explicit-schema builders emitted verbatim into the notebook. These mirror the
# committed _empty_schema definitions exactly so the evidence tables carry the
# same schema the real run() would write.
_SCHEMA_SRC = """from pyspark.sql.types import (
    ArrayType, BooleanType, DoubleType, LongType, StringType,
    StructField, StructType,
)

FORECAST_SCHEMA = StructType([
    StructField("contractId", StringType(), True),
    StructField("forecastId", StringType(), True),
    StructField("hospitalId", StringType(), True),
    StructField("wardId", StringType(), True),
    StructField("producedAt", StringType(), True),
    StructField("producedBy", StringType(), True),
    StructField("modelVersion", StringType(), True),
    StructField("horizonH", LongType(), True),
    StructField("bucketStart", StringType(), True),
    StructField("bedCapacity", DoubleType(), True),
    StructField("forecastOccupiedBeds", DoubleType(), True),
    StructField("forecastOccupancyPct", DoubleType(), True),
    StructField("lowerCi", DoubleType(), True),
    StructField("upperCi", DoubleType(), True),
    StructField("breach", BooleanType(), True),
    StructField("purposeTag", StringType(), True),
    StructField("dataResidencyRegion", StringType(), True),
    StructField("asOfTimestamp", StringType(), True),
])

DRIVER_SCHEMA = StructType([
    StructField("contractId", StringType(), True),
    StructField("forecastId", StringType(), True),
    StructField("hospitalId", StringType(), True),
    StructField("wardId", StringType(), True),
    StructField("horizonH", LongType(), True),
    StructField("factor", StringType(), True),
    StructField("delta", DoubleType(), True),
    StructField("note", StringType(), True),
    StructField("signalId", StringType(), True),
    StructField("purposeTag", StringType(), True),
    StructField("asOfTimestamp", StringType(), True),
])

SIGNAL_SCHEMA = StructType([
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


def _write(rows, schema, table):
    df = spark.createDataFrame(rows, schema)
    df.write.format("delta").mode("overwrite").option(
        "overwriteSchema", "true"
    ).saveAsTable(table)
    print(f"wrote {table}: {df.count()} rows")
"""


def _md_cell(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {},
            "source": text.splitlines(keepends=True)}


def _code_cell(text: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": text.splitlines(keepends=True)}


def _rows_literal(rows: list[dict], columns: list[str]) -> str:
    """Emit rows as a Python list-of-lists literal in the given column order.

    Uses ``repr`` so ``None`` renders as the Python literal ``None`` (not JSON
    ``null``) and canton lists render as real Python lists.
    """
    return repr([[r.get(c) for c in columns] for r in rows])


def build_notebook(tables: dict[str, list[dict]]) -> dict:
    forecast_cell = (
        "# Gold - deterministic 72h occupancy forecast (one row per ward x horizon)\n"
        f"forecast_rows = {_rows_literal(tables['gold.fact_occupancy_forecast'], FORECAST_COLUMNS)}\n"
        "_write(forecast_rows, FORECAST_SCHEMA, \"gold.fact_occupancy_forecast\")\n"
    )
    driver_cell = (
        "# Gold - forecast driver decomposition (the 'why'; deltas reconcile to net change)\n"
        f"driver_rows = {_rows_literal(tables['gold.fact_forecast_driver'], DRIVER_COLUMNS)}\n"
        "_write(driver_rows, DRIVER_SCHEMA, \"gold.fact_forecast_driver\")\n"
    )
    signal_cell = (
        "# Gold - deny-by-default Trust-A signal projection over the S21 ext spine\n"
        f"signal_rows = {_rows_literal(tables['gold.fact_signal'], SIGNAL_COLUMNS)}\n"
        "_write(signal_rows, SIGNAL_SCHEMA, \"gold.fact_signal\")\n"
    )
    verify_cell = (
        "# Inline verification - print counts for the evidence doc\n"
        "for t in [\"gold.fact_occupancy_forecast\", \"gold.fact_forecast_driver\",\n"
        "          \"gold.fact_signal\"]:\n"
        "    print(t, spark.table(t).count())\n"
        "display(spark.table(\"gold.fact_occupancy_forecast\").where(\"horizonH = 72\").select(\n"
        "    \"wardId\", \"horizonH\", \"forecastOccupiedBeds\", \"forecastOccupancyPct\", \"breach\"))\n"
    )
    header = (
        "# Foresight tier medallion - SIT evidence run\n\n"
        "Sprint 26 WS-A (issue #335). Deterministically materializes the three\n"
        "WS-A gold tables - `gold.fact_occupancy_forecast`, `gold.fact_forecast_driver`,\n"
        "`gold.fact_signal` - so the Foresight tier can be proven live in the SIT\n"
        "lakehouse. Synthetic-only, deterministic, no PHI (ADR-0013 / ADR-0016).\n\n"
        "Generated by `data-platform/scripts/fabric/build_forecast_evidence_notebook.py` -\n"
        "do not edit by hand; re-generate to update.\n"
    )
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "language_info": {"name": "python"},
            "kernelspec": {"name": "synapse_pyspark",
                           "display_name": "Synapse PySpark"},
        },
        "cells": [
            _md_cell(header),
            _code_cell(_SCHEMA_SRC),
            _code_cell(forecast_cell),
            _code_cell(driver_cell),
            _code_cell(signal_cell),
            _code_cell(verify_cell),
        ],
    }


def main() -> int:
    tables = compute_tables()
    nb = build_notebook(tables)
    OUTPUT.write_text(json.dumps(nb, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(REPO_ROOT).as_posix()}")
    for t, rows in tables.items():
        print(f"  {t}: {len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
