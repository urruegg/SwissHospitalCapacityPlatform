"""Forecast generator — ``forecast.published`` events.

Emits a rolling 72-hour demand forecast per specialty. At every hour tick,
each specialty (drawn from :mod:`ward_topology`) publishes a new forecast
covering the next 72 hours in hourly buckets.

Bucket expected counts are derived from:
  base_hourly * seasonal_multiplier * specialty_share

Confidence intervals are ±20% (widening in later buckets, to reflect drift).

Rate target: ~10/hr aggregate (10 specialties × 1/hr each) per hospital.

Design spec: §4.3 (event kinds) + §3 (``hcp:ForecastOutput``).
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Dict, Iterator, List, Optional

from calibration.hospital_presets import HospitalPreset
from calibration.seasonal_profile import SeasonalProfile
from calibration.ward_topology import WardInfo, load_ward_topology
from envelope import build_envelope, _iso_utc

_FORECAST_HORIZON_HOURS = 72
_MODEL_RUN_ID = "forecast-generator-v0.1"
_REFRESH_CADENCE = "PT1H"


def _specialties_by_share(wards: Dict[str, WardInfo]) -> Dict[str, float]:
    """Return ``{specialty_id: share}`` weighted by ward bed count."""
    totals: Dict[str, int] = {}
    for ward in wards.values():
        if not ward.specialty_id:
            continue
        totals[ward.specialty_id] = totals.get(ward.specialty_id, 0) + (ward.bed_count or 0)
    total_beds = sum(totals.values()) or 1
    return {sid: n / total_beds for sid, n in totals.items() if n > 0}


def generate_forecasts(
    preset: HospitalPreset,
    profile: SeasonalProfile,
    sim_run_id: str,
    seed: int,
    start_time: datetime,
    duration_hours: int,
    hospital_id: Optional[str] = None,
    ward_topology: Optional[Dict[str, WardInfo]] = None,
) -> Iterator[dict]:
    """Yield ``forecast.published`` envelopes — one per specialty per hour."""
    hid = hospital_id or preset.hospital_id
    wards = ward_topology if ward_topology is not None else load_ward_topology(preset.short_name)
    shares = _specialties_by_share(wards)
    if not shares:
        return
    stationary_yr = preset.stationary_cases_yr or 40_000
    base_hourly = stationary_yr / (365 * 24)
    rng = random.Random(seed)

    for hour_offset in range(duration_hours):
        produced_at = start_time + timedelta(hours=hour_offset)
        for specialty_id, share in sorted(shares.items()):
            buckets: List[dict] = []
            for h in range(_FORECAST_HORIZON_HOURS):
                bucket_start = produced_at + timedelta(hours=h)
                multiplier = profile.demand_multiplier(bucket_start)
                expected = base_hourly * share * multiplier
                # CI widens with horizon: ±20% at h=0, up to ±50% at h=72.
                spread = 0.20 + (h / _FORECAST_HORIZON_HOURS) * 0.30
                lower = max(0.0, expected * (1 - spread))
                upper = expected * (1 + spread)
                buckets.append(
                    {
                        "hourOffset": h,
                        "bucketStart": _iso_utc(bucket_start),
                        "expectedCount": round(expected, 3),
                        "lowerCI": round(lower, 3),
                        "upperCI": round(upper, 3),
                    }
                )

            forecast_id = f"FCAST-{preset.short_name}-{specialty_id}-{produced_at.strftime('%Y%m%dT%H')}"
            payload = {
                "forecastId": forecast_id,
                "specialtyId": specialty_id,
                "producedAt": _iso_utc(produced_at),
                "validFrom": _iso_utc(produced_at),
                "validUntil": _iso_utc(produced_at + timedelta(hours=_FORECAST_HORIZON_HOURS)),
                "horizonHours": _FORECAST_HORIZON_HOURS,
                "refreshCadence": _REFRESH_CADENCE,
                "producedByModelRunId": _MODEL_RUN_ID,
                "hourlyBuckets": buckets,
                "purposeTag": "capacity-planning",
            }
            # rng advanced but unused for now — keeps forecast_id deterministic
            _ = rng.random()
            yield build_envelope(
                event_kind="forecast.published",
                hospital_id=hid,
                simulated_at=produced_at,
                payload=payload,
                sim_run_id=sim_run_id,
                seed=seed,
            )
