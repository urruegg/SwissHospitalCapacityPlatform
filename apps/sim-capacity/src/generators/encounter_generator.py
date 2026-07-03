"""Encounter generator — ``encounter.admitted`` + ``encounter.transitioned`` events.

Advances sim time hour by hour over ``duration_hours``. Each hour, computes the
expected admissions using the hospital's yearly stationary case rate multiplied
by the :class:`SeasonalProfile` factor. The integer count of admissions for
that hour is drawn deterministically via ``sampler`` (seeded RNG).

For every ``encounter.admitted`` event, the generator yields a matching sequence
of ``encounter.transitioned`` events walking the FHIR EncounterStatusHistory
flow (arrived → triaged → in-progress → onleave → finished). Not every
encounter goes on leave — that step fires with probability 0.35.

Design spec: §4.3 (event kinds) + §4.5 (calibration).
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta
from typing import Iterator, List, Optional

from calibration.acuity_distribution import AcuitySampler
from calibration.hospital_presets import HospitalPreset
from calibration.seasonal_profile import SeasonalProfile
from envelope import build_envelope

# FHIR EncounterStatusHistory flow — subset used in the demo.
_STATUS_FLOW: List[str] = ["arrived", "triaged", "in-progress", "onleave", "finished"]
_ONLEAVE_PROBABILITY = 0.35

# Admission-type mix (matches HCC PNG: elective dominates weekdays, emergency dominates evenings).
_ADMISSION_TYPES = ["elective", "emergency", "transfer"]
_ADMISSION_WEIGHTS = [0.55, 0.35, 0.10]

_ACUITY_BANDS = ["routine", "urgent", "critical"]
_ACUITY_WEIGHTS = [0.55, 0.35, 0.10]


def _encounter_id(hospital_short: str, year: int, seq: int) -> str:
    return f"ENC-{hospital_short}-{year}-{seq:06d}"


def _pseudonym_id(rng: random.Random) -> str:
    return f"PID-{rng.getrandbits(48):012X}"


def generate_encounters(
    preset: HospitalPreset,
    profile: SeasonalProfile,
    sampler: AcuitySampler,
    sim_run_id: str,
    seed: int,
    start_time: datetime,
    duration_hours: int,
    hospital_id: Optional[str] = None,
) -> Iterator[dict]:
    """Yield ``encounter.admitted`` and ``encounter.transitioned`` envelopes."""
    hid = hospital_id or preset.hospital_id
    stationary_yr = preset.stationary_cases_yr or 40_000
    base_hourly = stationary_yr / (365 * 24)

    rng = random.Random(seed)
    seq = 0

    for hour_offset in range(duration_hours):
        when = start_time + timedelta(hours=hour_offset)
        multiplier = profile.demand_multiplier(when)
        expected = base_hourly * multiplier
        n_admits = _poisson_like(expected, rng)

        for _ in range(n_admits):
            seq += 1
            disease_id, drg_code, mean_los = sampler.sample()
            admission_minute = rng.randint(0, 59)
            admitted_at = when + timedelta(minutes=admission_minute)
            encounter_id = _encounter_id(preset.short_name, admitted_at.year, seq)
            pseudonym_id = _pseudonym_id(rng)

            specialty_id = sampler.specialty_id or "SPEC_INNERE"
            requested_specialty = f"{hid}__{specialty_id}"
            admission_type = rng.choices(_ADMISSION_TYPES, weights=_ADMISSION_WEIGHTS)[0]
            acuity_band = rng.choices(_ACUITY_BANDS, weights=_ACUITY_WEIGHTS)[0]
            expected_los = max(1, round(mean_los))

            base_payload = {
                "encounterId": encounter_id,
                "pseudonymId": pseudonym_id,
                "class": "IMP",
                "diseaseId": disease_id,
                "drgCode": drg_code,
                "admissionType": admission_type,
                "requestedSpecialtyServiceId": requested_specialty,
                "acuityBand": acuity_band,
                "expectedArrivalTimestamp": _z(admitted_at),
                "expectedLOSDays": expected_los,
                "purposeTag": "bed-management",
            }

            yield build_envelope(
                event_kind="encounter.admitted",
                hospital_id=hid,
                simulated_at=admitted_at,
                payload={**base_payload, "status": "arrived"},
                sim_run_id=sim_run_id,
                seed=seed,
            )

            yield from _emit_transitions(
                base_payload=base_payload,
                admitted_at=admitted_at,
                expected_los_days=expected_los,
                sim_run_id=sim_run_id,
                seed=seed,
                hospital_id=hid,
                rng=rng,
            )


def _emit_transitions(
    base_payload: dict,
    admitted_at: datetime,
    expected_los_days: int,
    sim_run_id: str,
    seed: int,
    hospital_id: str,
    rng: random.Random,
) -> Iterator[dict]:
    """Yield the sequence of encounter.transitioned events for one encounter."""
    include_onleave = rng.random() < _ONLEAVE_PROBABILITY

    # Rough offsets in hours from arrival to each status change.
    offsets = {
        "triaged": timedelta(minutes=15 + rng.randint(0, 45)),
        "in-progress": timedelta(hours=1 + rng.randint(0, 2)),
        "onleave": timedelta(days=max(1, expected_los_days // 2)),
        "finished": timedelta(days=expected_los_days),
    }

    prev_status = "arrived"
    for status in _STATUS_FLOW[1:]:
        if status == "onleave" and not include_onleave:
            continue
        when = admitted_at + offsets[status]
        payload = {**base_payload, "status": status, "previousStatus": prev_status}
        yield build_envelope(
            event_kind="encounter.transitioned",
            hospital_id=hospital_id,
            simulated_at=when,
            payload=payload,
            sim_run_id=sim_run_id,
            seed=seed,
        )
        prev_status = status


def _poisson_like(mean: float, rng: random.Random) -> int:
    """Simple Poisson draw via Knuth's algorithm. Deterministic given ``rng``."""
    if mean <= 0:
        return 0
    import math

    L = math.exp(-mean)
    k = 0
    p = 1.0
    while True:
        k += 1
        p *= rng.random()
        if p <= L:
            return k - 1


def _z(when: datetime) -> str:
    from envelope import _iso_utc  # local import to keep public surface small

    return _iso_utc(when)
