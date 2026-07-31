# apps/sim-capacity/src/closedloop/journey.py
"""Shared closed-loop journey definition (Sprint 38 M4, design spec Sec 7.1).

A journey is an ordered list of steps; each step names the agent role, the
lever it should propose, and the params. The SAME definition drives the CI
harness (Task 10) and the demo-able interactive run, so the two never diverge."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class JourneyStep:
    role: str
    lever_id: str
    params: Dict[str, Any]
    approver: str


CANONICAL_JOURNEY: List[JourneyStep] = [
    JourneyStep("dca", "DCA-UNBLOCK-BARRIER", {"barrier_type": "transport", "n": 2}, approver="alice"),
    JourneyStep("dca", "DCA-UNBLOCK-BARRIER", {"barrier_type": "transport", "n": 1}, approver="bob"),
]
