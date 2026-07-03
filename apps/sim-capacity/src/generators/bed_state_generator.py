"""Bed state generator — ``bed.state_changed`` events.

Enumerates beds using ``ward_topology`` per hospital and emits state transitions
per bed at a target aggregate rate (~200/hr for LUKS, scaled by bed count).

Valid state machine (design spec §4.3):

    available → occupied → cleaning → available
    available → blocked → available

Each transition carries the previous state so downstream FK integrity checks
can validate the chain.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Dict, Iterator, List, Optional

from calibration.hospital_presets import HospitalPreset
from calibration.ward_topology import WardInfo, load_ward_topology
from envelope import build_envelope

_STATE_TRANSITIONS = {
    "available": ["occupied", "blocked"],
    "occupied": ["cleaning"],
    "cleaning": ["available"],
    "blocked": ["available"],
}

# Time each state typically holds in hours (approximate — determinism from RNG).
_STATE_HOLD_HOURS = {
    "available": 1.0,   # short — beds turn over quickly at target occupancy
    "occupied": 5.5,    # avg LOS
    "cleaning": 0.5,
    "blocked": 2.0,
}


def _bed_ids_from_ward(ward: WardInfo) -> List[str]:
    n = ward.bed_count or 0
    return [f"{ward.ward_id}__BED_{i:03d}" for i in range(1, n + 1)]


def generate_bed_states(
    preset: HospitalPreset,
    sim_run_id: str,
    seed: int,
    start_time: datetime,
    duration_hours: int,
    hospital_id: Optional[str] = None,
    ward_topology: Optional[Dict[str, WardInfo]] = None,
) -> Iterator[dict]:
    """Yield ``bed.state_changed`` envelopes for every bed in the hospital."""
    hid = hospital_id or preset.hospital_id
    wards = ward_topology if ward_topology is not None else load_ward_topology(preset.short_name)

    rng = random.Random(seed)

    # Initialise every bed to a randomised starting state so the stream isn't
    # synchronised (mirrors how a real hospital wakes up mid-cycle).
    bed_state: Dict[str, str] = {}
    bed_next_change: Dict[str, datetime] = {}
    bed_ward: Dict[str, WardInfo] = {}
    for ward in wards.values():
        for bed_id in _bed_ids_from_ward(ward):
            bed_state[bed_id] = rng.choice(["available", "occupied", "cleaning"])
            offset_hours = rng.uniform(0, _STATE_HOLD_HOURS[bed_state[bed_id]])
            bed_next_change[bed_id] = start_time + timedelta(hours=offset_hours)
            bed_ward[bed_id] = ward

    end_time = start_time + timedelta(hours=duration_hours)

    # Emit events in chronological order using a simple heap-free sweep: at
    # every hour tick, fire every bed whose scheduled change fell in the past.
    for h in range(duration_hours):
        tick = start_time + timedelta(hours=h)
        for bed_id, ward in bed_ward.items():
            while bed_next_change[bed_id] <= tick and bed_next_change[bed_id] < end_time:
                prev_state = bed_state[bed_id]
                options = _STATE_TRANSITIONS[prev_state]
                new_state = rng.choices(options)[0]
                bed_state[bed_id] = new_state
                changed_at = bed_next_change[bed_id]
                hold_h = _STATE_HOLD_HOURS[new_state] * rng.uniform(0.5, 1.5)
                bed_next_change[bed_id] = changed_at + timedelta(hours=hold_h)

                payload = {
                    "bedId": bed_id,
                    "wardId": ward.ward_id,
                    "specialtyId": ward.specialty_id,
                    "unitType": ward.unit_type,
                    "state": new_state,
                    "previousState": prev_state,
                    "purposeTag": "bed-management",
                }
                yield build_envelope(
                    event_kind="bed.state_changed",
                    hospital_id=hid,
                    simulated_at=changed_at,
                    payload=payload,
                    sim_run_id=sim_run_id,
                    seed=seed,
                )
