"""SystemAdapter seam (Sprint 38 M0, design spec Sec 5.3). Only the EPIC twin
ships this sprint; the protocol makes SuccessFactors/LMS additive later. The
adapter derives demand/capacity envelopes from SimState using the shared
``build_envelope`` helper — the downstream envelope shape is unchanged."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from envelope import build_envelope
from closedloop.sim_state import SimState


class SystemAdapter(ABC):
    @abstractmethod
    def read_demand(self, simulated_at: datetime, sim_run_id: str, seed: int) -> List[dict]: ...


class EpicAdapter(SystemAdapter):
    def __init__(self, state: SimState) -> None:
        self._state = state

    def read_demand(self, simulated_at: datetime, sim_run_id: str, seed: int) -> List[dict]:
        s = self._state
        envelopes: List[dict] = []
        for bed in sorted(s.beds.values(), key=lambda b: b.bed_id):
            envelopes.append(build_envelope(
                event_kind="bed_state",
                hospital_id=s.hospital_id,
                simulated_at=simulated_at,
                payload={"bedId": bed.bed_id, "wardId": bed.ward_id, "state": bed.state},
                sim_run_id=sim_run_id, seed=seed,
            ))
        for ward_id in sorted(s.wards):
            ward = s.wards[ward_id]
            envelopes.append(build_envelope(
                event_kind="ward_occupancy",
                hospital_id=s.hospital_id,
                simulated_at=simulated_at,
                payload={
                    "wardId": ward_id,
                    "bedCapacity": ward.staffed_capacity,
                    "occupiedBeds": s.occupancy(ward_id),
                },
                sim_run_id=sim_run_id, seed=seed,
            ))
        return envelopes
