"""Matching engine generator — ``bed.assigned`` events.

Advisory Encounter→Bed matcher. Takes an iterable of ``encounter.admitted``
envelopes plus a pool of available beds (from :mod:`ward_topology`) and
yields ``bed.assigned`` envelopes.

Matching rule (deterministic, seeded):

1. Filter beds to those whose ward specialty matches the encounter's
   ``requestedSpecialtyServiceId`` (parsed as ``<hospitalId>__<specialtyId>``).
2. If any specialty-matched beds are free, pick one at random from that pool.
3. Otherwise, fall back to any free bed and record ``fallback`` as the reason.

Rate target: ~5/hr (aggregate across all hospitals; capped internally).

Design spec: §4.3 (event kinds) + §4.4 (matching_engine responsibility).
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Dict, Iterable, Iterator, List, Optional

from calibration.hospital_presets import HospitalPreset
from calibration.ward_topology import WardInfo, load_ward_topology
from envelope import build_envelope

_MODEL_RUN_ID = "matching-engine-v0.1"


def _bed_ids_from_ward(ward: WardInfo) -> List[str]:
    n = ward.bed_count or 0
    return [f"{ward.ward_id}__BED_{i:03d}" for i in range(1, n + 1)]


def _bed_pool(wards: Dict[str, WardInfo]) -> List[tuple[str, WardInfo]]:
    """Flatten ward topology to a list of ``(bed_id, ward_info)``."""
    pool: List[tuple[str, WardInfo]] = []
    for ward in wards.values():
        for bed_id in _bed_ids_from_ward(ward):
            pool.append((bed_id, ward))
    return pool


def _parse_requested_specialty(encounter_payload: dict) -> Optional[str]:
    raw = encounter_payload.get("requestedSpecialtyServiceId")
    if not raw or "__" not in raw:
        return None
    return raw.split("__", 1)[1]


def generate_bed_assignments(
    preset: HospitalPreset,
    encounter_events: Iterable[dict],
    sim_run_id: str,
    seed: int,
    hospital_id: Optional[str] = None,
    ward_topology: Optional[Dict[str, WardInfo]] = None,
    max_per_hour: int = 8,
) -> Iterator[dict]:
    """Yield ``bed.assigned`` envelopes matching admitted encounters to beds.

    Only ``encounter.admitted`` events with ``status='arrived'`` are considered.
    ``max_per_hour`` caps the emit rate to keep the aggregate near ~5/hr; the
    remainder are dropped (matcher is advisory, not exhaustive).
    """
    hid = hospital_id or preset.hospital_id
    wards = ward_topology if ward_topology is not None else load_ward_topology(preset.short_name)
    pool = _bed_pool(wards)
    if not pool:
        return
    rng = random.Random(seed)

    hour_counts: Dict[str, int] = {}

    for env in encounter_events:
        if env.get("eventKind") != "encounter.admitted":
            continue
        payload = env.get("payload") or {}
        if payload.get("status") != "arrived":
            continue

        # Rate cap per simulated hour.
        simulated_at_str = env["simulatedAt"]
        hour_key = simulated_at_str[:13]  # YYYY-MM-DDTHH
        if hour_counts.get(hour_key, 0) >= max_per_hour:
            continue
        hour_counts[hour_key] = hour_counts.get(hour_key, 0) + 1

        requested_specialty = _parse_requested_specialty(payload)
        specialty_matches = [
            (bed_id, ward) for bed_id, ward in pool
            if requested_specialty and ward.specialty_id == requested_specialty
        ]
        if specialty_matches:
            bed_id, ward = rng.choice(specialty_matches)
            reason = "specialty-match"
            match_score = round(0.85 + 0.15 * rng.random(), 3)
            explanation = ["specialty-match", "capacity-headroom"]
            hard_ok = True
        else:
            bed_id, ward = rng.choice(pool)
            reason = "fallback"
            match_score = round(0.30 + 0.20 * rng.random(), 3)
            explanation = ["fallback", "specialty-mismatch"]
            hard_ok = False

        # Add a small delay so assignedAt is after the encounter's admit time.
        try:
            admit_dt = datetime.fromisoformat(simulated_at_str.replace("Z", "+00:00"))
        except ValueError:
            admit_dt = datetime.utcnow()
        assigned_at = admit_dt + timedelta(minutes=rng.randint(2, 20))

        assignment_id = f"BEDASSIGN-{payload['encounterId']}-{rng.getrandbits(24):06X}"
        assign_payload = {
            "assignmentId": assignment_id,
            "encounterId": payload["encounterId"],
            "bedId": bed_id,
            "wardId": ward.ward_id,
            "specialtyId": ward.specialty_id,
            "requestedSpecialtyId": requested_specialty,
            "assignmentReason": reason,
            "matchScore": match_score,
            "hardConstraintsMet": hard_ok,
            "explanationTokens": explanation,
            "assignedAt": simulated_at_str,
            "unassignedAt": None,
            "producedByModelRunId": _MODEL_RUN_ID,
            "purposeTag": "bed-management",
        }
        yield build_envelope(
            event_kind="bed.assigned",
            hospital_id=hid,
            simulated_at=assigned_at,
            payload=assign_payload,
            sim_run_id=sim_run_id,
            seed=seed,
        )
