"""Fabric Spark I/O helpers shared by the org-spine + skills gold ``run()``s.

Deploy-class glue that executes **only inside the Fabric Spark runtime** (there
is no local unit test — the pure table-building logic lives in
``build_gold_org_spine.py`` / ``build_gold_skills.py`` and is unit-tested
without Spark). This module is uploaded to the lakehouse ``Files/`` mount
alongside those two modules so the ``05_gold_org_skills`` notebook can import
all three.

Responsibilities:

* ``read_csv_rows`` - read one relocated Curavias master-data CSV from the
  lakehouse ``Files/`` mount into ``list[dict]`` (``utf-8-sig`` to tolerate the
  UTF-8 BOM the capacity CSVs carry), matching the unit tests' reader exactly;
* ``rows_of_table`` - read an existing managed Delta table (e.g.
  ``gold.dim_hospital``) into ``list[dict]`` so the re-brand preserves the
  capacity/governance columns already in gold;
* ``table_exists`` - guard so a targeted ``--only 05_gold_org_skills`` re-run
  can skip pruning a capacity table that has not been landed yet;
* ``write_gold`` - write ``list[dict]`` rows to ``gold.<name>`` as Delta,
  stamping the sprint-09 seven-column governance contract (mirrors
  ``03_gold_master_data.ipynb``).

``pyspark`` is imported lazily inside the functions so importing this module in
a non-Fabric context (e.g. test discovery) does not require the package.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone

# Seven-column governance contract (sprint-09 §1.2 / 03_gold_master_data.ipynb).
GOVERNANCE_CONSTANTS = {
    "_classification": "Operational confidential",
    "_legal_basis": "nDSG/KVG",
    "_retention_class": "R3",
    "_pseudonymisation_flag": False,
}
DEFAULT_RESIDENCY_TAG = "US-West"   # demo scope per ADR-0013 (westus2 carve-out)
DEFAULT_DATA_QUALITY = "explicit"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _spark():
    from pyspark.sql import SparkSession
    return SparkSession.builder.getOrCreate()


def read_csv_rows(mount_path: str) -> list[dict]:
    """Read a CSV from the lakehouse Files mount into ``list[dict]``."""
    with open(mount_path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def rows_of_table(table: str) -> list[dict]:
    """Read an existing managed table into ``list[dict]`` (driver-side)."""
    return [r.asDict(recursive=True) for r in _spark().table(table).collect()]


def table_exists(table: str) -> bool:
    """Return ``True`` if a managed table (``schema.name``) exists."""
    return _spark().catalog.tableExists(table)


def _stamp_governance(rows: list[dict], table: str, gold_ts: str) -> list[dict]:
    """Apply the seven-column governance contract to each gold row."""
    out = []
    for row in rows:
        r = dict(row)
        r.update(GOVERNANCE_CONSTANTS)
        r.setdefault("_residency_tag", DEFAULT_RESIDENCY_TAG)
        r.setdefault("_data_quality", DEFAULT_DATA_QUALITY)
        r["_lineage_ref"] = f"curavias-org-skills:{table}:{gold_ts}"
        out.append(r)
    return out


def write_gold(name: str, rows: list[dict]) -> int:
    """Overwrite ``gold.<name>`` as Delta from ``list[dict]`` rows.

    Rows are serialised to JSON and read back with ``spark.read.json`` so the
    schema is inferred across **all** rows (robust to nullable numerics that are
    ``None`` in some rows), then the governance columns are stamped and the
    table is written managed-Delta with ``overwriteSchema``.
    """
    spark = _spark()
    spark.sql("CREATE SCHEMA IF NOT EXISTS gold")
    gold_ts = _now_iso()
    stamped = _stamp_governance(rows, name, gold_ts)
    if not stamped:
        raise ValueError(f"gold.{name}: refusing to write an empty table")
    rdd = spark.sparkContext.parallelize(
        [json.dumps(r, ensure_ascii=False) for r in stamped])
    df = spark.read.json(rdd)
    (df.write
       .format("delta")
       .mode("overwrite")
       .option("overwriteSchema", "true")
       .saveAsTable(f"gold.{name}"))
    n = df.count()
    print(f"  gold.{name:<38s} rows={n}")
    return n
