"""Stateful patient-flow twin (Sprint 38 M0, design spec Sec 5).

Synthetic, PHI-free by construction: only synthetic IDs (PT-*, BED-*) and
non-identifying attributes (acuity, specialty, stage). Deterministic: the
builder draws from a seeded ``random.Random`` so the same (hospital, seed,
wards) always yields the same state.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class Stage(str, Enum):
    ARRIVAL = "ARRIVAL"
    TRIAGE = "TRIAGE"
    ADMIT = "ADMIT"
    INPATIENT = "INPATIENT"
    DISCHARGE_READY = "DISCHARGE_READY"
    DISCHARGED = "DISCHARGED"


@dataclass
class Patient:
    patient_id: str
    acuity: int
    specialty: str
    journey_stage: Stage


@dataclass
class Bed:
    bed_id: str
    ward_id: str
    state: str  # available | occupied | blocked | planned
    patient_id: str | None = None


@dataclass
class Ward:
    ward_id: str
    specialty: str
    staffed_capacity: int


@dataclass
class DischargeBarrier:
    barrier_id: str
    patient_id: str
    barrier_type: str
    status: str  # open | cleared
    aged_h: int


@dataclass
class SimState:
    hospital_id: str
    patients: Dict[str, Patient] = field(default_factory=dict)
    beds: Dict[str, Bed] = field(default_factory=dict)
    wards: Dict[str, Ward] = field(default_factory=dict)
    barriers: Dict[str, DischargeBarrier] = field(default_factory=dict)

    def ward(self, ward_id: str) -> Ward:
        return self.wards[ward_id]

    def beds_in_ward(self, ward_id: str) -> List[Bed]:
        return [b for b in self.beds.values() if b.ward_id == ward_id]

    def occupancy(self, ward_id: str) -> int:
        return sum(1 for b in self.beds_in_ward(ward_id) if b.state == "occupied")

    def patients_in_stage(self, stage: Stage) -> List[Patient]:
        return [p for p in self.patients.values() if p.journey_stage == stage]

    def open_barriers(self, barrier_type: str) -> List[DischargeBarrier]:
        return [
            b for b in self.barriers.values()
            if b.barrier_type == barrier_type and b.status == "open"
        ]

    def snapshot(self) -> Dict[str, Any]:
        """Deterministic, order-stable dict of the whole state (for equality/JSON)."""
        return {
            "hospital_id": self.hospital_id,
            "patients": [vars(self.patients[k]) | {"journey_stage": self.patients[k].journey_stage.value}
                         for k in sorted(self.patients)],
            "beds": [vars(self.beds[k]) for k in sorted(self.beds)],
            "wards": [vars(self.wards[k]) for k in sorted(self.wards)],
            "barriers": [vars(self.barriers[k]) for k in sorted(self.barriers)],
        }


def build_sim_state(hospital_id: str, seed: int, wards: List[tuple[str, str, int]]) -> SimState:
    """Deterministically construct an initial twin. ``wards`` is a list of
    ``(ward_id, specialty, staffed_capacity)``. Roughly 80% of beds start
    occupied; ~15% of inpatients start discharge-ready, half of those with an
    open ``transport`` barrier — enough structure for the journey levers."""
    rng = random.Random(seed)
    state = SimState(hospital_id=hospital_id)
    pt_seq = 0
    for ward_id, specialty, cap in wards:
        state.wards[ward_id] = Ward(ward_id=ward_id, specialty=specialty, staffed_capacity=cap)
        for i in range(cap):
            bed_id = f"BED-{ward_id}-{i:02d}"
            occupied = rng.random() < 0.80
            patient_id = None
            if occupied:
                pt_seq += 1
                patient_id = f"PT-{pt_seq:04d}"
                ready = rng.random() < 0.15
                stage = Stage.DISCHARGE_READY if ready else Stage.INPATIENT
                state.patients[patient_id] = Patient(
                    patient_id=patient_id,
                    acuity=rng.randint(1, 4),
                    specialty=specialty,
                    journey_stage=stage,
                )
                if ready and rng.random() < 0.5:
                    bid = f"BAR-{patient_id}"
                    state.barriers[bid] = DischargeBarrier(
                        barrier_id=bid, patient_id=patient_id,
                        barrier_type="transport", status="open",
                        aged_h=rng.randint(6, 48),
                    )
            state.beds[bed_id] = Bed(
                bed_id=bed_id, ward_id=ward_id,
                state="occupied" if occupied else "available",
                patient_id=patient_id,
            )
    return state
