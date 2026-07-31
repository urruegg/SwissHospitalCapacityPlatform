# apps/sim-capacity/src/closedloop/tick.py
"""Stateful tick (Sprint 38 M1, design spec Sec 5.2). Advances time-driven
transitions on the persistent twin. Fully deterministic: all randomness comes
from the injected ``random.Random``; no wall-clock reads."""
from __future__ import annotations

import random

from closedloop.sim_state import SimState, Stage


def advance_state(state: SimState, rng: random.Random) -> None:
    """Advance the twin by one simulated hour: age open barriers, and promote a
    small deterministic fraction of INPATIENT to DISCHARGE_READY (LOS maturing).
    Applied approved actions are handled separately by the ActuationConsumer
    (M2); this function only models autonomous time transitions."""
    for barrier in state.barriers.values():
        if barrier.status == "open":
            barrier.aged_h += 1

    inpatients = sorted(state.patients_in_stage(Stage.INPATIENT), key=lambda p: p.patient_id)
    for patient in inpatients:
        if rng.random() < 0.05:
            patient.journey_stage = Stage.DISCHARGE_READY
