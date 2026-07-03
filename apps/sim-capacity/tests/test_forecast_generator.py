"""Tests for the forecast generator (T3.4d)."""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from calibration.hospital_presets import load_preset
from calibration.seasonal_profile import SeasonalProfile
from calibration.ward_topology import load_ward_topology
from envelope import ENVELOPE_REQUIRED_KEYS
from generators.forecast_generator import (
    _FORECAST_HORIZON_HOURS,
    generate_forecasts,
)


SIM_RUN_ID = "sim-run-forecast-test"


def _run(hospital_short: str, hours: int = 3, seed: int = 42):
    preset = load_preset(hospital_short)
    profile = SeasonalProfile.from_preset(preset, seed=seed)
    return list(
        generate_forecasts(
            preset=preset,
            profile=profile,
            sim_run_id=SIM_RUN_ID,
            seed=seed,
            start_time=datetime(2027, 1, 15, 8, 0),
            duration_hours=hours,
        )
    )


def test_envelope_shape_conforms():
    events = _run("LUKS", hours=2)
    assert events
    for e in events:
        assert set(e.keys()) == ENVELOPE_REQUIRED_KEYS
        assert e["eventKind"] == "forecast.published"
        assert e["hospitalId"] == "H_LUKS"
        p = e["payload"]
        assert p["specialtyId"]
        assert p["horizonHours"] == _FORECAST_HORIZON_HOURS
        assert p["refreshCadence"] == "PT1H"


def test_each_forecast_covers_72_hourly_buckets():
    events = _run("LUKS", hours=1)
    for e in events:
        buckets = e["payload"]["hourlyBuckets"]
        assert len(buckets) == _FORECAST_HORIZON_HOURS
        for i, b in enumerate(buckets):
            assert b["hourOffset"] == i
            assert b["expectedCount"] >= 0
            assert 0 <= b["lowerCI"] <= b["expectedCount"] <= b["upperCI"]


def test_one_forecast_per_specialty_per_hour():
    events = _run("LUKS", hours=3)
    wards = load_ward_topology("LUKS")
    specialties = {w.specialty_id for w in wards.values() if w.specialty_id and (w.bed_count or 0) > 0}

    per_hour: dict[str, set[str]] = {}
    for e in events:
        hour = e["simulatedAt"][:13]
        per_hour.setdefault(hour, set()).add(e["payload"]["specialtyId"])

    assert len(per_hour) == 3
    for hour, sids in per_hour.items():
        assert sids == specialties, f"hour {hour} missing specialties: {specialties - sids}"


def test_deterministic_by_seed():
    a = _run("SZB", hours=2, seed=101)
    b = _run("SZB", hours=2, seed=101)
    key = lambda e: (
        e["simulatedAt"],
        e["payload"]["specialtyId"],
        e["payload"]["forecastId"],
        len(e["payload"]["hourlyBuckets"]),
        e["payload"]["hourlyBuckets"][0]["expectedCount"],
    )
    assert [key(x) for x in a] == [key(x) for x in b]


def test_confidence_intervals_widen_over_horizon():
    events = _run("LUKS", hours=1)
    e = events[0]
    buckets = e["payload"]["hourlyBuckets"]
    # Spread proportion at h=0 should be smaller than at h=71.
    def spread(b):
        return b["upperCI"] - b["lowerCI"]
    assert spread(buckets[0]) < spread(buckets[-1]), (
        f"CI at h=0 ({spread(buckets[0])}) not narrower than at h=71 ({spread(buckets[-1])})"
    )
