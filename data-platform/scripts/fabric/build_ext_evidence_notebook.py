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
    }


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
    StructField("ext_cantons", ArrayType(StringType()), True),
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


def _write(rows, schema, table):
    df = spark.createDataFrame(rows, schema)
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

    def lit(rows, cols):
        # tuples must round-trip through JSON as lists; Spark accepts lists too.
        return _rows_literal(rows, cols)

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
        f"fact_rows = {lit(tables['gold.ext_fact_signal'], fact_cols)}\n"
        f"source_rows = {lit(tables['gold.ext_dim_source'], source_cols)}\n"
        f"hazard_rows = {lit(tables['gold.ext_dim_hazard_type'], hazard_cols)}\n"
        f"region_rows = {lit(tables['gold.ext_dim_region'], region_cols)}\n"
        "_write(fact_rows, FACT_SCHEMA, \"gold.ext_fact_signal\")\n"
        "_write(source_rows, SOURCE_SCHEMA, \"gold.ext_dim_source\")\n"
        "_write(hazard_rows, HAZARD_SCHEMA, \"gold.ext_dim_hazard_type\")\n"
        "_write(region_rows, REGION_SCHEMA, \"gold.ext_dim_region\")\n"
    )
    verify_cell = (
        "# Inline verification -- print counts + distinct data modes for the evidence doc\n"
        "for t in [\"bronze.ext_signals_raw\", \"silver.ext_signals\",\n"
        "          \"silver.ext_signals_quarantine\", \"gold.ext_fact_signal\",\n"
        "          \"gold.ext_dim_source\", \"gold.ext_dim_hazard_type\",\n"
        "          \"gold.ext_dim_region\"]:\n"
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
