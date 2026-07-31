"""SimState persistence (Sprint 38 M0). In-memory for CI; JSON snapshot for
reproducible fixtures. The protocol keeps a Cosmos-backed store additive later
(design spec Sec 4, open question Q1)."""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict

from closedloop.sim_state import (
    Bed, DischargeBarrier, Patient, SimState, Stage, Ward,
)


class SimStateStore(ABC):
    @abstractmethod
    def put(self, state: SimState) -> None: ...

    @abstractmethod
    def get(self, hospital_id: str) -> SimState: ...


class InMemorySimStateStore(SimStateStore):
    def __init__(self) -> None:
        self._by_hospital: Dict[str, SimState] = {}

    def put(self, state: SimState) -> None:
        self._by_hospital[state.hospital_id] = state

    def get(self, hospital_id: str) -> SimState:
        return self._by_hospital[hospital_id]


def _state_from_snapshot(snap: dict) -> SimState:
    state = SimState(hospital_id=snap["hospital_id"])
    for w in snap["wards"]:
        state.wards[w["ward_id"]] = Ward(**w)
    for b in snap["beds"]:
        state.beds[b["bed_id"]] = Bed(**b)
    for p in snap["patients"]:
        state.patients[p["patient_id"]] = Patient(
            patient_id=p["patient_id"], acuity=p["acuity"],
            specialty=p["specialty"], journey_stage=Stage(p["journey_stage"]),
        )
    for br in snap["barriers"]:
        state.barriers[br["barrier_id"]] = DischargeBarrier(**br)
    return state


def save_snapshot(state: SimState, path: Path) -> None:
    Path(path).write_text(json.dumps(state.snapshot(), indent=2, sort_keys=True), encoding="utf-8")


def load_snapshot(path: Path) -> SimState:
    return _state_from_snapshot(json.loads(Path(path).read_text(encoding="utf-8")))
