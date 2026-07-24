#!/usr/bin/env python3
"""Generate a self-contained Fabric evidence notebook for the external-signals medallion.

Why this exists (Sprint 21 signal Fabric evidence, Task 4):

The committed medallion notebooks under
``data-platform/notebooks/external-signals/*.py`` are authored as importable
libraries (pure functions + a ``run()`` Fabric entrypoint). They cannot be
imported into Fabric and executed as-is because (a) their module top uses
``__file__`` / ``sys.path`` injection and sibling-package imports
(``signals_synth`` / ``dedup``) that do not exist in the Fabric Spark runtime,
and (b) the all-``Live`` synthetic seed has columns that are ``None`` across all
rows (e.g. ``fellBackFrom``), which breaks Spark schema inference from Python
dicts.

This generator resolves both by pre-computing the deterministic bronze / silver
/ gold rows OFFLINE (reusing the committed pure functions and the committed
synthetic seeder) and emitting ONE self-contained ``.ipynb`` whose cells carry
the data as literals and write every table with an EXPLICIT schema. The emitted
notebook has no external imports, so it runs deterministically in Fabric against
the default lakehouse injected by ``import_notebooks.py``.

The result is the six evidence tables:
``bronze.ext_signals_raw`` -> ``silver.ext_signals`` (+ ``_quarantine``) ->
``gold.ext_fact_signal`` / ``ext_dim_source`` / ``ext_dim_hazard_type`` /
``ext_dim_region``.

Synthetic-only (ADR-0013 / ADR-0016). No PHI. The seed carries public Trust-A
authority hazard warnings only. Deployment + run of the emitted notebook is a
``deploy``-ceiling action gated by ``approved-to-apply`` (AGENTS.md Section 4).

Usage::

    python data-platform/scripts/fabric/build_ext_evidence_notebook.py
    # writes data-platform/notebooks/external-signals/run_ext_medallion.ipynb
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
NB_DIR = REPO_ROOT / "data-platform" / "notebooks" / "external-signals"
SCRIPTS_DIR = REPO_ROOT / "data-platform" / "scripts" / "external-signals"
OUTPUT = NB_DIR / "run_ext_medallion.ipynb"

# Flat bronze/silver column order (explicit schema keeps Fabric from having to
# infer types from all-None columns like ext_fell_back_from).
FLAT_COLUMNS = [
    "ext_signal_id",
    "ext_source_id",
    "ext_source_authority",
    "ext_trust_tier",
    "ext_hazard_type",
    "ext_severity",
    "ext_status",
    "ext_scenario_template",
    "ext_lage_tier",
    "ext_cantons",
    "ext_onset",
    "ext_active_binding",
    "ext_fell_back_from",
    "ext_ingested_at",
]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), NB_DIR / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _flat_row(rec: dict) -> dict:
    """Flatten one DC-EXT-SIGNAL-v1 record to the bronze/silver evidence shape."""
    prov = rec.get("provenance") or {}
    return {
        "ext_signal_id": rec.get("signalId"),
        "ext_source_id": rec.get("sourceId"),
        "ext_source_authority": rec.get("sourceAuthority"),
        "ext_trust_tier": rec.get("trustTier"),
        "ext_hazard_type": rec.get("hazardType"),
        "ext_severity": rec.get("severity"),
        "ext_status": rec.get("status"),
        "ext_scenario_template": rec.get("mappedScenarioTemplate"),
        "ext_lage_tier": rec.get("defaultLageTier"),
        "ext_cantons": list((rec.get("region") or {}).get("cantons", [])),
        "ext_onset": rec.get("onset"),
        "ext_active_binding": prov.get("activeBinding"),
        "ext_fell_back_from": prov.get("fellBackFrom"),
        "ext_ingested_at": prov.get("ingestedAt"),
    }


def compute_tables() -> dict[str, list[dict]]:
    """Compute all six evidence tables deterministically from the committed seed."""
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    from signals_synth import build_records

    silver = _load("build_silver_signals.py")
    gold = _load("build_gold_signals.py")

    records = build_records()
    kept, quarantined = silver.split_quarantine(records)
    gold_bundle = gold.gold_tables(kept)

    return {
        "bronze.ext_signals_raw": [_flat_row(r) for r in records],
        "silver.ext_signals": [_flat_row(r) for r in kept],
        "silver.ext_signals_quarantine": [_flat_row(r) for r in quarantined],
        "gold.ext_fact_signal": gold_bundle["ext_fact_signal"],
        "gold.ext_dim_source": gold_bundle["ext_dim_source"],
        "gold.ext_dim_hazard_type": gold_bundle["ext_dim_hazard_type"],
        "gold.ext_dim_region": gold_bundle["ext_dim_region"],
        "gold.ext_fact_trigger_event": _collapse_trigger_events(kept),
    }


def _collapse_trigger_events(kept: list[dict]) -> list[dict]:
    """Collapse kept signals into HazardEvents (one trigger-fired audit row per
    hazard type), mirroring the M2 ``dedup.collapse`` step so the modeled
    ``gold.ext_fact_trigger_event`` table (Direct Lake) has referentially-intact
    evidence rows for the trigger-audit badge measures."""
    groups: dict[str, list[dict]] = {}
    order: list[str] = []
    for rec in kept:
        hazard = rec.get("hazardType")
        if hazard not in groups:
            groups[hazard] = []
            order.append(hazard)
        groups[hazard].append(rec)

    events: list[dict] = []
    for index, hazard in enumerate(order, start=1):
        members = groups[hazard]
        first = members[0]
        onsets = [m.get("onset") for m in members if m.get("onset")]
        stamps = [
            (m.get("provenance") or {}).get("ingestedAt")
            for m in members
            if (m.get("provenance") or {}).get("ingestedAt")
        ]
        events.append({
            "ext_trigger_event_id": f"trg-{hazard}-{index:04d}",
            "ext_signal_id": first.get("signalId"),
            "ext_hazard_type": hazard,
            "ext_severity": first.get("severity"),
            "ext_lage_tier": first.get("defaultLageTier"),
            "ext_scenario_template": first.get("mappedScenarioTemplate"),
            "ext_sources": ",".join(m.get("sourceId") for m in members),
            "ext_signal_ids": ",".join(m.get("signalId") for m in members),
            "ext_dedup_keys": ",".join(f"{hazard}:{m.get('sourceId')}" for m in members),
            "ext_trigger_status": "trigger-fired",
            "ext_source_onset": min(onsets) if onsets else None,
            "ext_triggered_at": max(stamps) if stamps else None,
            "ext_run_id": "evidence-run",
        })
    return events


def _md_cell(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def _code_cell(text: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.splitlines(keepends=True),
    }


# Explicit-schema builders emitted verbatim into the notebook (no external import
# beyond pyspark.sql.types, which the Fabric runtime always provides).
_FLAT_SCHEMA_SRC = """from pyspark.sql.types import (
    StructType, StructField, StringType, LongType, ArrayType,
)
from pyspark.sql import functions as F

FLAT_SCHEMA = StructType([
    StructField("ext_signal_id", StringType(), True),
    StructField("ext_source_id", StringType(), True),
    StructField("ext_source_authority", StringType(), True),
    StructField("ext_trust_tier", StringType(), True),
    StructField("ext_hazard_type", StringType(), True),
    StructField("ext_severity", StringType(), True),
    StructField("ext_status", StringType(), True),
    StructField("ext_scenario_template", StringType(), True),
    StructField("ext_lage_tier", LongType(), True),
    StructField("ext_cantons", ArrayType(StringType()), True),
    StructField("ext_onset", StringType(), True),
    StructField("ext_active_binding", StringType(), True),
    StructField("ext_fell_back_from", StringType(), True),
    StructField("ext_ingested_at", StringType(), True),
])

FACT_SCHEMA = StructType([
    StructField("ext_signal_id", StringType(), True),
    StructField("ext_source_id", StringType(), True),
    StructField("ext_hazard_type", StringType(), True),
    StructField("ext_severity", StringType(), True),
    StructField("ext_scenario_template", StringType(), True),
    StructField("ext_lage_tier", LongType(), True),
    StructField("ext_cantons", StringType(), True),
    StructField("ext_onset", StringType(), True),
    StructField("ext_status", StringType(), True),
])

SOURCE_SCHEMA = StructType([
    StructField("ext_source_id", StringType(), True),
    StructField("ext_source_authority", StringType(), True),
    StructField("ext_trust_tier", StringType(), True),
    StructField("ext_data_mode", StringType(), True),
    StructField("ext_fell_back_from", StringType(), True),
    StructField("ext_last_live_at", StringType(), True),
])

HAZARD_SCHEMA = StructType([
    StructField("ext_hazard_type", StringType(), True),
    StructField("ext_scenario_template", StringType(), True),
    StructField("ext_default_lage_tier", LongType(), True),
])

REGION_SCHEMA = StructType([
    StructField("ext_canton", StringType(), True),
])

TRIGGER_SCHEMA = StructType([
    StructField("ext_trigger_event_id", StringType(), True),
    StructField("ext_signal_id", StringType(), True),
    StructField("ext_hazard_type", StringType(), True),
    StructField("ext_severity", StringType(), True),
    StructField("ext_lage_tier", LongType(), True),
    StructField("ext_scenario_template", StringType(), True),
    StructField("ext_sources", StringType(), True),
    StructField("ext_signal_ids", StringType(), True),
    StructField("ext_dedup_keys", StringType(), True),
    StructField("ext_trigger_status", StringType(), True),
    StructField("ext_source_onset", StringType(), True),
    StructField("ext_triggered_at", StringType(), True),
    StructField("ext_run_id", StringType(), True),
])


def _write(rows, schema, table, ts_cols=()):
    # Direct Lake models only consume scalar Delta columns; ISO-string date
    # columns modeled as dateTime are cast to real Spark timestamps on write.
    df = spark.createDataFrame(rows, schema)
    for col in ts_cols:
        df = df.withColumn(col, F.to_timestamp(col))
    df.write.format("delta").mode("overwrite").option(
        "overwriteSchema", "true"
    ).saveAsTable(table)
    print(f"wrote {table}: {df.count()} rows")
"""


def _rows_literal(rows: list[dict], columns: list[str]) -> str:
    """Emit rows as a Python list-of-lists literal in the given column order.

    Uses ``repr`` (not ``json.dumps``) so ``None`` renders as the Python
    literal ``None`` rather than JSON ``null`` -- the notebook cells are
    executed as Python, where a bare ``null`` raises ``NameError``.
    """
    lists = [[r.get(c) for c in columns] for r in rows]
    return repr(lists)


def build_notebook(tables: dict[str, list[dict]]) -> dict:
    fact_cols = ["ext_signal_id", "ext_source_id", "ext_hazard_type", "ext_severity",
                 "ext_scenario_template", "ext_lage_tier", "ext_cantons", "ext_onset",
                 "ext_status"]
    source_cols = ["ext_source_id", "ext_source_authority", "ext_trust_tier",
                   "ext_data_mode", "ext_fell_back_from", "ext_last_live_at"]
    hazard_cols = ["ext_hazard_type", "ext_scenario_template", "ext_default_lage_tier"]
    region_cols = ["ext_canton"]
    trigger_cols = ["ext_trigger_event_id", "ext_signal_id", "ext_hazard_type",
                    "ext_severity", "ext_lage_tier", "ext_scenario_template",
                    "ext_sources", "ext_signal_ids", "ext_dedup_keys",
                    "ext_trigger_status", "ext_source_onset", "ext_triggered_at",
                    "ext_run_id"]

    def lit(rows, cols):
        # Rows serialize to Python list-of-lists literals; Spark accepts lists.
        return _rows_literal(rows, cols)

    # ext_cantons is modeled as a scalar string (Direct Lake rejects arrays),
    # so collapse the canton list to a comma-joined string for the gold fact.
    fact_rows_scalar = [
        {**r, "ext_cantons": ",".join(r.get("ext_cantons") or [])}
        for r in tables["gold.ext_fact_signal"]
    ]

    bronze_cell = (
        "# Bronze -- raw external signals landed verbatim (flat evidence shape)\n"
        f"bronze_rows = {lit(tables['bronze.ext_signals_raw'], FLAT_COLUMNS)}\n"
        "_write(bronze_rows, FLAT_SCHEMA, \"bronze.ext_signals_raw\")\n"
    )
    silver_cell = (
        "# Silver -- kept Actual signals + (empty) quarantine, same schema\n"
        f"silver_rows = {lit(tables['silver.ext_signals'], FLAT_COLUMNS)}\n"
        f"quarantine_rows = {lit(tables['silver.ext_signals_quarantine'], FLAT_COLUMNS)}\n"
        "_write(silver_rows, FLAT_SCHEMA, \"silver.ext_signals\")\n"
        "_write(quarantine_rows, FLAT_SCHEMA, \"silver.ext_signals_quarantine\")\n"
    )
    gold_cell = (
        "# Gold -- star schema consumed by the semantic model + data agent\n"
        f"fact_rows = {lit(fact_rows_scalar, fact_cols)}\n"
        f"source_rows = {lit(tables['gold.ext_dim_source'], source_cols)}\n"
        f"hazard_rows = {lit(tables['gold.ext_dim_hazard_type'], hazard_cols)}\n"
        f"region_rows = {lit(tables['gold.ext_dim_region'], region_cols)}\n"
        "_write(fact_rows, FACT_SCHEMA, \"gold.ext_fact_signal\", ts_cols=(\"ext_onset\",))\n"
        "_write(source_rows, SOURCE_SCHEMA, \"gold.ext_dim_source\", ts_cols=(\"ext_last_live_at\",))\n"
        "_write(hazard_rows, HAZARD_SCHEMA, \"gold.ext_dim_hazard_type\")\n"
        "_write(region_rows, REGION_SCHEMA, \"gold.ext_dim_region\")\n"
    )
    trigger_cell = (
        "# Gold -- trigger-event audit fact (collapsed HazardEvents that fire a pre-seed)\n"
        f"trigger_rows = {lit(tables['gold.ext_fact_trigger_event'], trigger_cols)}\n"
        "_write(trigger_rows, TRIGGER_SCHEMA, \"gold.ext_fact_trigger_event\",\n"
        "       ts_cols=(\"ext_source_onset\", \"ext_triggered_at\"))\n"
    )
    verify_cell = (
        "# Inline verification -- print counts + distinct data modes for the evidence doc\n"
        "for t in [\"bronze.ext_signals_raw\", \"silver.ext_signals\",\n"
        "          \"silver.ext_signals_quarantine\", \"gold.ext_fact_signal\",\n"
        "          \"gold.ext_dim_source\", \"gold.ext_dim_hazard_type\",\n"
        "          \"gold.ext_dim_region\", \"gold.ext_fact_trigger_event\"]:\n"
        "    print(t, spark.table(t).count())\n"
        "display(spark.table(\"gold.ext_dim_source\").select(\n"
        "    \"ext_source_id\", \"ext_source_authority\", \"ext_trust_tier\", \"ext_data_mode\"))\n"
    )

    header = (
        "# External-Signals medallion -- SIT evidence run\n\n"
        "Sprint 21 signal Fabric evidence (Task 4). Deterministically materializes the\n"
        "bronze / silver / gold `ext_*` tables from the committed synthetic seed so the\n"
        "`external-signals` semantic model and the `da_hospital_capacity` data agent can\n"
        "be proven end to end. Synthetic-only, no PHI (ADR-0013 / ADR-0016).\n\n"
        "Generated by `data-platform/scripts/fabric/build_ext_evidence_notebook.py` --\n"
        "do not edit by hand; re-generate to update.\n"
    )

    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "language_info": {"name": "python"},
            "kernelspec": {"name": "synapse_pyspark", "display_name": "Synapse PySpark"},
        },
        "cells": [
            _md_cell(header),
            _code_cell(_FLAT_SCHEMA_SRC),
            _code_cell(bronze_cell),
            _code_cell(silver_cell),
            _code_cell(gold_cell),
            _code_cell(trigger_cell),
            _code_cell(verify_cell),
        ],
    }


def main() -> int:
    tables = compute_tables()
    nb = build_notebook(tables)
    OUTPUT.write_text(json.dumps(nb, indent=1) + "\n", encoding="utf-8")
    counts = {t: len(rows) for t, rows in tables.items()}
    print(f"wrote {OUTPUT.relative_to(REPO_ROOT).as_posix()}")
    for t, n in counts.items():
        print(f"  {t}: {n} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
