"""Sprint 26 WS-B — DCA barrier **Gold materialization**.

Projects the pure, runtime-derived barrier model (``derive_barriers``) onto a
deterministic Gold Delta table ``gold.fact_discharge_barrier`` that grounds the
reference ontology ``hcp:Barrier`` ICE and conforms to the
``DC-DISCHARGE-BARRIER-v1`` contract. This is the materialization follow-up to
the WS-B runtime builder: the aggregation logic is **not** duplicated — the
heavy lifting stays in ``derive_barriers`` and this module only adds the flat,
contract-shaped Gold row projection (ids, rank, run metadata, camelCase keys).

Mirrors the WS-A Foresight pattern (``notebooks/foresight/build_gold_forecast``):
the transform is a Spark-free pure function unit-tested offline (``tests/``);
the heavy Spark I/O lives in ``run()`` / ``_write`` (``# pragma: no cover``).
Empty inputs still write a well-typed Delta table via ``_empty_schema``.

**Synthetic + deterministic, no PHI, no LLM numbers** (ADR-0013 / ADR-0016):
candidates carry only an opaque ``candidate_key`` and ontology ward IDs, so the
Gold rows carry only aggregate counts, bed impact, age, clear time, and ward
IDs. ``DEFAULT_CANDIDATES`` is the design "8 candidates collapse into 5
barriers" fixture and is the seam a real discharge-candidate feed swaps into
later without changing the Gold contract or the ontology binding.
"""
from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional

from barriers.derive_barriers import derive_barriers

CONTRACT_BARRIER = "DC-DISCHARGE-BARRIER-v1"
CONTRACT_VERSION = "1.0.0"
BARRIER_RUN_ID = "MRUN-DECISION-BARRIER-SYNTH-V0-1"
_DEFAULT_HOSPITAL = "H_USZ"
_DEFAULT_PURPOSE = "discharge-planning"
_DEFAULT_RESIDENCY = "switzerlandnorth"

# The design's "8 candidates collapse into 5 barriers" fixture, scoped to a
# single hospital (H_USZ). Opaque candidate keys + ontology ward IDs only -- no
# PHI. This is the deterministic default feed the notebook materialises; a real
# discharge-candidate feed swaps in here (design D2 seam).
DEFAULT_CANDIDATES: List[dict] = [
    {"candidate_key": "C1", "ward": "hcp:Ward/Medicine A", "barrier_type": "pharmacy", "aged_h": 12, "clears_at": "2026-07-24T18:00:00Z"},
    {"candidate_key": "C2", "ward": "hcp:Ward/Medicine B", "barrier_type": "pharmacy", "aged_h": 30, "clears_at": "2026-07-25T06:00:00Z"},
    {"candidate_key": "C3", "ward": "hcp:Ward/Medicine A", "barrier_type": "transport", "aged_h": 8, "clears_at": "2026-07-24T14:00:00Z"},
    {"candidate_key": "C4", "ward": "hcp:Ward/Surgery A", "barrier_type": "transport", "aged_h": 20, "clears_at": "2026-07-25T02:00:00Z", "bed_impact": 2},
    {"candidate_key": "C5", "ward": "hcp:Ward/Medicine A", "barrier_type": "social_placement", "aged_h": 48, "clears_at": "2026-07-26T00:00:00Z", "bed_impact": 3},
    {"candidate_key": "C6", "ward": "hcp:Ward/Medicine B", "barrier_type": "imaging", "aged_h": 4, "clears_at": "2026-07-24T10:00:00Z"},
    {"candidate_key": "C7", "ward": "hcp:Ward/Surgery A", "barrier_type": "consult", "aged_h": 6, "clears_at": "2026-07-24T12:00:00Z"},
    {"candidate_key": "C8", "ward": "hcp:Ward/Surgery A", "barrier_type": "consult", "aged_h": 10, "clears_at": "2026-07-24T20:00:00Z"},
]


def _iso(ts: datetime) -> str:
    """ISO-8601 UTC with a trailing Z (mirrors the WS-A envelope convention)."""
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slug(value: str) -> str:
    """Uppercase A-Z0-9-only slug for the ``DB-`` barrier id pattern."""
    return re.sub(r"-+", "-", re.sub(r"[^A-Z0-9]+", "-", value.upper())).strip("-")


def barrier_id(hospital_id: str, barrier_type: str, produced_at: datetime) -> str:
    return f"DB-{_slug(hospital_id)}-{_slug(barrier_type)}-{produced_at.strftime('%Y%m%dT%H')}"


def build_discharge_barriers(
    candidates: List[dict],
    produced_at: datetime,
    hospital_id: str = _DEFAULT_HOSPITAL,
    owner_map: Optional[Dict[str, str]] = None,
    as_of: Optional[datetime] = None,
) -> List[dict]:
    """Build ``gold.fact_discharge_barrier`` rows from discharge-blocked
    ``candidates`` -- deterministic, flat, 1:1 with DC-DISCHARGE-BARRIER-v1
    records.

    Delegates the collapse/rank/aggregate to ``derive_barriers`` (pure) and only
    adds the materialization envelope: a deterministic ``barrierId``, a 1-based
    ``rank`` following the pure builder's deterministic order, run metadata, and
    camelCase contract keys. The input list/dicts are never mutated.
    """
    as_of = as_of or produced_at
    barriers = derive_barriers(candidates, owner_map=owner_map)
    produced_at_iso = _iso(produced_at)
    as_of_iso = _iso(as_of)

    rows: List[dict] = []
    for rank, barrier in enumerate(barriers, start=1):
        rows.append({
            "contractId": CONTRACT_BARRIER,
            "barrierId": barrier_id(hospital_id, barrier["barrier_type"], produced_at),
            "hospitalId": hospital_id,
            "producedAt": produced_at_iso,
            "producedBy": BARRIER_RUN_ID,
            "barrierType": barrier["barrier_type"],
            "ownerRole": barrier["owner_role"],
            "rank": rank,
            "candidateCount": barrier["candidate_count"],
            "bedImpact": barrier["bed_impact"],
            "agedH": barrier["aged_h"],
            "clearsAt": barrier["clears_at"],
            "wards": list(barrier["wards"]),
            "purposeTag": _DEFAULT_PURPOSE,
            "asOfTimestamp": as_of_iso,
        })
    return rows


def discharge_barrier_envelope(records: List[dict], suffix: str) -> dict:
    """Wrap Gold rows in the DC-DISCHARGE-BARRIER-v1 contract envelope."""
    return {
        "datasetId": f"DS-DISCHARGE-BARRIER-{suffix}",
        "contractId": CONTRACT_BARRIER,
        "contractVersion": CONTRACT_VERSION,
        "classification": "operational-confidential",
        "residency": "CH",
        "purposeTags": [_DEFAULT_PURPOSE],
        "_pseudonymisation_flag": True,
        "records": records,
    }


# ---------------------------------------------------------------------------
# Fabric Spark runtime — heavy I/O only, exercised in the notebook, not offline.
# ---------------------------------------------------------------------------
def _empty_schema():  # pragma: no cover - requires pyspark
    from pyspark.sql.types import (
        ArrayType, LongType, StringType, StructField, StructType,
    )

    return StructType([
        StructField("contractId", StringType(), True),
        StructField("barrierId", StringType(), True),
        StructField("hospitalId", StringType(), True),
        StructField("producedAt", StringType(), True),
        StructField("producedBy", StringType(), True),
        StructField("barrierType", StringType(), True),
        StructField("ownerRole", StringType(), True),
        StructField("rank", LongType(), True),
        StructField("candidateCount", LongType(), True),
        StructField("bedImpact", LongType(), True),
        StructField("agedH", LongType(), True),
        StructField("clearsAt", StringType(), True),
        StructField("wards", ArrayType(StringType()), True),
        StructField("purposeTag", StringType(), True),
        StructField("asOfTimestamp", StringType(), True),
    ])


def _write(spark, rows: List[dict]) -> None:  # pragma: no cover - Fabric runtime only
    schema = _empty_schema()
    df = spark.createDataFrame(rows, schema) if rows else spark.createDataFrame([], schema)
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("gold.fact_discharge_barrier")
    print(f"gold: wrote gold.fact_discharge_barrier ({df.count()} rows)")


def run(candidates: Optional[List[dict]] = None, produced_at: Optional[datetime] = None) -> None:  # pragma: no cover - Fabric runtime only
    """Fabric entrypoint. Writes gold.fact_discharge_barrier from the deterministic
    discharge-candidate feed (``DEFAULT_CANDIDATES`` today; real feed via the D2 seam)."""
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.getOrCreate()
    spark.sql("CREATE SCHEMA IF NOT EXISTS gold")
    candidates = candidates if candidates is not None else DEFAULT_CANDIDATES
    produced_at = produced_at or datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)

    _write(spark, build_discharge_barriers(candidates, produced_at))


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
