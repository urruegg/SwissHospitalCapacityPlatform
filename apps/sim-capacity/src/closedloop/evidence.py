# apps/sim-capacity/src/closedloop/evidence.py
"""Evidence-trace harness (Sprint 39 P1, design §4/§6).

Seeds a SimState from a materialized EPIC gold snapshot and walks
CANONICAL_JOURNEY through the REAL decision tier + Sprint 38 closed-loop engine,
emitting a DC-EVIDENCE-TRACE-v1 with an accept branch (approve every step -> apply
-> outcome) and a deny branch (withhold approval -> no apply -> breach persists).
Deterministic (fixed `now`), PHI-free. Live SIT gold backs it at runtime; a
captured snapshot backs CI. Requires both apps/sim-capacity/src and
data-platform/decision on sys.path (the test adds them)."""
from __future__ import annotations

from typing import Any, Dict, List

from closedloop.actuation import ActuationConsumer
from closedloop.gold_seed import seed_sim_state_from_gold
from closedloop.journey import CANONICAL_JOURNEY
from coordination import plan_runtime
from coordination.store import InMemoryStore

_NOW = "1970-01-01T00:00:00Z"

# The one lever with a Sprint 38 effect; the effect the ActuationConsumer applies.
_EFFECT = {
    "applies_to": "DischargeBarrier", "mutation": "set_status",
    "from": "open", "to": "cleared", "select_by": "barrier_type",
    "cascade": [{"when": "patient_all_barriers_cleared", "set": "Patient.stage=DISCHARGED"}],
}
_CATALOG = [{"lever_id": "DCA-UNBLOCK-BARRIER", "owner_role": "dca", "impact_formula_ref": "unblock_barrier_beds"}]
# lever -> the agent that owns it (for the evidence step's `agent` label)
_AGENT_BY_LEVER = {"DCA-UNBLOCK-BARRIER": "dca-agent"}


def _gold_for_impact(state, ward: str, horizon_h: int = 72) -> Dict[str, Any]:
    return {"forecast": [{
        "wardId": ward, "horizonH": horizon_h,
        "bedCapacity": state.ward(ward).staffed_capacity,
        "forecastOccupiedBeds": state.occupancy(ward),
    }]}


def build_evidence_trace(gold: Dict[str, Any], branch: str = "accept") -> Dict[str, Any]:
    """Build a DC-EVIDENCE-TRACE-v1 for ``branch`` in {"accept","deny"}."""
    if branch not in ("accept", "deny"):
        raise ValueError(f"branch must be 'accept' or 'deny', got {branch!r}")

    state = seed_sim_state_from_gold(gold)
    provenance = gold.get("provenance", "simulated")
    ward = next(iter(sorted(state.wards)))
    store = InMemoryStore()
    plan = plan_runtime.open_plan(
        store, episode_key="ev1", ward=ward,
        bed_capacity=state.ward(ward).staffed_capacity,
        baseline_occupied_beds=state.occupancy(ward), target_pct=90,
    )
    consumer = ActuationConsumer(store, {"DCA-UNBLOCK-BARRIER": _EFFECT})
    golden_thread = f"gt-{plan['id']}"

    steps: List[Dict[str, Any]] = []
    for js in CANONICAL_JOURNEY:
        impact_gold = _gold_for_impact(state, ward)
        occupied_before = state.occupancy(ward)
        params = {**js.params, "ward": ward}
        action = plan_runtime.propose_action(
            store, plan_id=plan["id"], role=js.role, lever_id=js.lever_id,
            params=params, gold=impact_gold, catalog=_CATALOG, proposed_by=js.role, now=_NOW,
        )
        predicted = int(action["expected_impact"]["delta"])

        if branch == "accept":
            plan_runtime.approve_action(
                store, action_id=action["id"], approver=js.approver,
                gold=impact_gold, catalog=_CATALOG, now=_NOW,
            )
            outcomes = consumer.apply_approved(plan["id"], state, now=_NOW)
            # Mirror decisions.py: carry the honest `applied` flag so the /evidence
            # outcome is the SAME DC-SIM-OUTCOME-v1 shape /decisions produces
            # (FR-UXL-004). build_sim_outcome omits it, so set it here.
            outcome = (
                {**outcomes[-1], "applied": True} if outcomes
                else {**_noop_outcome(action, provenance), "applied": False}
            )
            decision, status = "accept", "applied"
        else:
            outcome = _noop_outcome(action, provenance)
            decision, status = "deny", "denied"

        outcome = {**outcome, "golden_thread": golden_thread, "provenance": provenance}

        steps.append({
            "role": js.role,
            "agent": _AGENT_BY_LEVER.get(js.lever_id, f"{js.role}-agent"),
            "journey_stage": "DISCHARGE_READY",
            "epic_input": {
                "wardId": ward,
                "occupiedBeds": occupied_before,
                "bedCapacity": state.ward(ward).staffed_capacity,
                "citations": ["gold.fact_occupancy_forecast", "gold.bed_assignment"],
                "provenance": provenance,
            },
            "agent_read": {"signal": f"{js.params.get('n')} discharge-ready blocked by {js.params.get('barrier_type')} barriers on {ward}"},
            "recommendation": {
                "lever_id": js.lever_id, "params": params,
                "predicted_impact": {"metric": "beds", "value": predicted},
                "insight_text": f"Resolve {js.params.get('n')} {js.params.get('barrier_type')} barriers to free beds on {ward}",
            },
            "copilot": {"requiresApproval": True, "decision": decision, "approver": js.approver, "decision_ts": _NOW},
            "action": {"cosmos_id": action["id"], "status": status},
            "outcome": outcome,
        })

    return {
        "contract": "DC-EVIDENCE-TRACE-v1",
        "golden_thread": golden_thread,
        "patient": {"synthetic_id": "PT-0001", "specialty": gold.get("wards", [{}])[0].get("specialty", ""), "provenance": provenance},
        "branch": branch,
        "generated_ts": _NOW,
        "steps": steps,
    }


def _noop_outcome(action: Dict[str, Any], provenance: str) -> Dict[str, Any]:
    predicted = int(action["expected_impact"]["delta"])
    return {
        "contract": "DC-SIM-OUTCOME-v1", "cosmos_id": action["id"], "plan_id": action["plan_id"],
        "golden_thread": f"gt-{action['plan_id']}", "lever_id": action["lever_id"], "applied_ts": _NOW,
        "predicted_impact": {"metric": "beds_freed", "value": predicted},
        "realised_impact": {"metric": "beds_freed", "value": 0},
        "state_delta": {"beds_freed": [], "patients_discharged": [], "patients_promoted": []},
        "divergence": 0.0,
        "provenance": provenance,
        "applied": False,
    }
