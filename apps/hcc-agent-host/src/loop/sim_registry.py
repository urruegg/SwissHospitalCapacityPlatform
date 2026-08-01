"""In-host SimState registry (Sprint 39 P2). One stateful SimState per hospital,
seeded from a materialized gold snapshot via the sim-capacity gold_seed. In-memory
only (snapshot, not live write-back to the running sim). Reuses closedloop; no new
Azure resource."""
from __future__ import annotations

from typing import Any, Dict

from closedloop.gold_seed import seed_sim_state_from_gold
from closedloop.sim_state import SimState


class SimRegistry:
    def __init__(self) -> None:
        self._by_hospital: Dict[str, SimState] = {}

    def get_or_seed(self, hospital_id: str, gold: Dict[str, Any]) -> SimState:
        if hospital_id not in self._by_hospital:
            self._by_hospital[hospital_id] = seed_sim_state_from_gold(gold)
        return self._by_hospital[hospital_id]

    def reset(self, hospital_id: str) -> None:
        self._by_hospital.pop(hospital_id, None)
