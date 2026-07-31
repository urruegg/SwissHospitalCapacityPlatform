# apps/sim-capacity/src/closedloop/outcome.py
"""DC-SIM-OUTCOME-v1 builder (Sprint 38 M3, design spec Sec 6.3). PHI-free by
construction: synthetic bed/patient IDs only. Divergence is the normalised gap
between the agent's predicted impact and the simulator's realised impact — the
single signal the M5 learning slice consumes."""
from __future__ import annotations

from typing import Any, Dict


def build_sim_outcome(
    action: Dict[str, Any],
    pre_state: Dict[str, Any],
    post_state: Dict[str, Any],
    realised: Dict[str, Any],
    applied_ts: str,
) -> Dict[str, Any]:
    predicted_value = int(action.get("expected_impact", {}).get("delta", 0))
    realised_value = int(realised.get("delta", 0))
    denom = max(abs(predicted_value), abs(realised_value), 1)
    divergence = round(abs(predicted_value - realised_value) / denom, 4)
    return {
        "contract": "DC-SIM-OUTCOME-v1",
        "cosmos_id": action["id"],
        "plan_id": action["plan_id"],
        "golden_thread": action.get("golden_thread", action["plan_id"]),
        "lever_id": action["lever_id"],
        "applied_ts": applied_ts,
        "predicted_impact": {"metric": realised.get("metric", "beds"), "value": predicted_value},
        "realised_impact": {"metric": realised.get("metric", "beds"), "value": realised_value},
        "state_delta": realised.get("state_delta", {}),
        "divergence": divergence,
        "provenance": "simulated",
    }
