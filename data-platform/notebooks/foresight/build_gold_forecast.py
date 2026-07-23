"""Sprint 26 WS-A — Foresight tier: deterministic synthetic occupancy-forecast
and driver-decomposition generator.

Turns the descriptive Gold occupancy surface into the predictive Foresight tier
(design §3.2 / D2). Two Gold Delta tables are produced from a **deterministic**
synthetic admission/discharge/transfer/seasonality series — no randomness, no
model, no LLM-guessed numbers:

- ``gold.fact_occupancy_forecast`` — one row per ward × horizon-hour (0..72h).
- ``gold.fact_forecast_driver``    — the "why": one row per forecast-point ×
  driver factor, whose deltas reconcile to the net forecast change.

The heavy Spark I/O lives in ``run()`` (``# pragma: no cover``); the transform
logic is Spark-free pure functions unit-tested offline (``tests/``), following
the external-signals notebook pattern.

**D2 seam:** ``MODEL_RUN_ID`` / ``build_occupancy_forecast`` is the single point
where a real forecasting model swaps in for the synthetic series; the Gold table
contract (DC-OCCUPANCY-FORECAST-v1) and the ontology binding stay unchanged.
"""
from __future__ import annotations

import re
import sys
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

FORECAST_HORIZON_HOURS = 72
MODEL_RUN_ID = "MRUN-FORESIGHT-SYNTH-V0-1"
MODEL_VERSION = "0.1.0"
CONTRACT_FORECAST = "DC-OCCUPANCY-FORECAST-v1"
CONTRACT_DRIVER = "DC-FORECAST-DRIVER-v1"
CONTRACT_VERSION = "1.0.0"
_DEFAULT_PURPOSE = "capacity-planning"
_DEFAULT_RESIDENCY = "switzerlandnorth"

# Deterministic default ward baselines for the OOA -> DCA golden-thread slice.
# Medicine A breaches capacity within 72h (+6 admissions vs -2 discharges).
DEFAULT_WARDS: List[dict] = [
    {
        "ward_id": "Medicine A", "hospital_id": "H_USZ", "bed_capacity": 50,
        "baseline_occupied": 51, "admissions_72h": 6, "discharges_72h": 2,
        "transfers_72h": 0, "seasonality_72h": 0, "seasonality_note": "flu season",
        "signal_id": "cap-2026-flu-zh-1",
    },
]

_FACTOR_NOTES = {
    "forecast_admissions": "forecast admissions",
    "planned_discharges": "planned discharges",
    "transfers": "net transfers",
    "seasonality": "seasonal baseline",
}


def _iso(ts: datetime) -> str:
    """ISO-8601 UTC with a trailing Z (mirrors the sim envelope convention)."""
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slug(value: str) -> str:
    """Uppercase A-Z0-9-only slug for the ``OF-`` forecast id pattern."""
    return re.sub(r"-+", "-", re.sub(r"[^A-Z0-9]+", "-", value.upper())).strip("-")


def forecast_id(ward: dict, produced_at: datetime) -> str:
    return f"OF-{_slug(ward['hospital_id'])}-{_slug(ward['ward_id'])}-{produced_at.strftime('%Y%m%dT%H')}"


def _factor_delta(total_72h: float, horizon_h: int, horizon_hours: int, sign: int = 1) -> float:
    """Deterministic linear ramp of a 72h total onto a single horizon bucket."""
    if horizon_hours <= 0:
        return 0.0
    return round(sign * float(total_72h) * horizon_h / horizon_hours, 3)


def _ward_driver_deltas(ward: dict, horizon_h: int, horizon_hours: int) -> Dict[str, float]:
    """The four signed driver deltas (beds) for a ward at a horizon."""
    return {
        "forecast_admissions": _factor_delta(ward.get("admissions_72h", 0), horizon_h, horizon_hours, +1),
        "planned_discharges": _factor_delta(ward.get("discharges_72h", 0), horizon_h, horizon_hours, -1),
        "transfers": _factor_delta(ward.get("transfers_72h", 0), horizon_h, horizon_hours, +1),
        "seasonality": _factor_delta(ward.get("seasonality_72h", 0), horizon_h, horizon_hours, +1),
    }


def build_occupancy_forecast(
    wards: List[dict],
    produced_at: datetime,
    horizon_hours: int = FORECAST_HORIZON_HOURS,
    as_of: Optional[datetime] = None,
) -> List[dict]:
    """Build ``gold.fact_occupancy_forecast`` rows — deterministic, flat, 1:1 with
    DC-OCCUPANCY-FORECAST-v1 records."""
    as_of = as_of or produced_at
    rows: List[dict] = []
    for ward in wards:
        fid = forecast_id(ward, produced_at)
        baseline = float(ward["baseline_occupied"])
        capacity = float(ward["bed_capacity"])
        for h in range(horizon_hours + 1):
            deltas = _ward_driver_deltas(ward, h, horizon_hours)
            occupied = round(baseline + sum(deltas.values()), 3)
            pct = round(occupied / capacity * 100, 3) if capacity else 0.0
            spread = 0.05 + (h / horizon_hours) * 0.15 if horizon_hours else 0.05
            rows.append({
                "contractId": CONTRACT_FORECAST,
                "forecastId": fid,
                "hospitalId": ward["hospital_id"],
                "wardId": ward["ward_id"],
                "producedAt": _iso(produced_at),
                "producedBy": MODEL_RUN_ID,
                "modelVersion": MODEL_VERSION,
                "horizonH": h,
                "bucketStart": _iso(produced_at + timedelta(hours=h)),
                "bedCapacity": capacity,
                "forecastOccupiedBeds": occupied,
                "forecastOccupancyPct": pct,
                "lowerCi": round(max(0.0, occupied * (1 - spread)), 3),
                "upperCi": round(occupied * (1 + spread), 3),
                "breach": pct > 100,
                "purposeTag": _DEFAULT_PURPOSE,
                "dataResidencyRegion": _DEFAULT_RESIDENCY,
                "asOfTimestamp": _iso(as_of),
            })
    return rows


def build_forecast_drivers(
    wards: List[dict],
    produced_at: datetime,
    horizon_hours: int = FORECAST_HORIZON_HOURS,
    as_of: Optional[datetime] = None,
) -> List[dict]:
    """Build ``gold.fact_forecast_driver`` rows — the decomposition that explains
    each forecast point. Deltas reconcile to occupied(h) - baseline_occupied."""
    as_of = as_of or produced_at
    rows: List[dict] = []
    for ward in wards:
        fid = forecast_id(ward, produced_at)
        season_note = ward.get("seasonality_note") or _FACTOR_NOTES["seasonality"]
        season_signal = ward.get("signal_id")
        for h in range(horizon_hours + 1):
            deltas = _ward_driver_deltas(ward, h, horizon_hours)
            for factor, delta in deltas.items():
                note = season_note if factor == "seasonality" else _FACTOR_NOTES[factor]
                rows.append({
                    "contractId": CONTRACT_DRIVER,
                    "forecastId": fid,
                    "hospitalId": ward["hospital_id"],
                    "wardId": ward["ward_id"],
                    "horizonH": h,
                    "factor": factor,
                    "delta": delta,
                    "note": note,
                    "signalId": season_signal if factor == "seasonality" else None,
                    "purposeTag": _DEFAULT_PURPOSE,
                    "asOfTimestamp": _iso(as_of),
                })
    return rows


def _envelope(contract: str, dataset_prefix: str, records: List[dict], suffix: str) -> dict:
    return {
        "datasetId": f"{dataset_prefix}-{suffix}",
        "contractId": contract,
        "contractVersion": CONTRACT_VERSION,
        "classification": "operational-confidential",
        "residency": "CH",
        "purposeTags": [_DEFAULT_PURPOSE],
        "_pseudonymisation_flag": True,
        "records": records,
    }


def occupancy_forecast_envelope(records: List[dict], suffix: str) -> dict:
    return _envelope(CONTRACT_FORECAST, "DS-OCCUPANCY-FORECAST", records, suffix)


def forecast_driver_envelope(records: List[dict], suffix: str) -> dict:
    return _envelope(CONTRACT_DRIVER, "DS-FORECAST-DRIVER", records, suffix)


# ---------------------------------------------------------------------------
# Fabric Spark runtime — heavy I/O only, exercised in the notebook, not offline.
# ---------------------------------------------------------------------------
def _empty_schema(name: str):  # pragma: no cover - requires pyspark
    from pyspark.sql.types import (
        BooleanType, DoubleType, LongType, StringType, StructField, StructType,
    )

    forecast = StructType([
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
    driver = StructType([
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
    return {"fact_occupancy_forecast": forecast, "fact_forecast_driver": driver}[name]


def _write(spark, rows: List[dict], name: str) -> None:  # pragma: no cover - Fabric runtime only
    schema = _empty_schema(name)
    df = spark.createDataFrame(rows, schema) if rows else spark.createDataFrame([], schema)
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"gold.{name}")
    print(f"gold: wrote gold.{name} ({df.count()} rows)")


def run(wards: Optional[List[dict]] = None, produced_at: Optional[datetime] = None) -> None:  # pragma: no cover - Fabric runtime only
    """Fabric entrypoint. Writes gold.fact_occupancy_forecast + gold.fact_forecast_driver."""
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.getOrCreate()
    spark.sql("CREATE SCHEMA IF NOT EXISTS gold")
    wards = wards if wards is not None else DEFAULT_WARDS
    produced_at = produced_at or datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)

    _write(spark, build_occupancy_forecast(wards, produced_at), "fact_occupancy_forecast")
    _write(spark, build_forecast_drivers(wards, produced_at), "fact_forecast_driver")


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
