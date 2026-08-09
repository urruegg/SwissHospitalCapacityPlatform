"""Role decision handler (Sprint 39 P2). Drives the REAL decision-tier HITL
(propose -> approve -> apply -> outcome) for a single accept/deny on the in-host
SimState. Accept runs plan_runtime.approve_action (which refuses bot/self
approvers) then ActuationConsumer.apply_approved against the LIVE sim; deny
records a no-op DC-SIM-OUTCOME-v1 with no state mutation. Deterministic; the
impact is compute_expected_impact on the seeded occupancy, never an LLM guess."""
from __future__ import annotations

from typing import Any, Dict

from closedloop.actuation import ActuationConsumer
from closedloop.sim_state import SimState
from coordination import plan_runtime
from coordination.store import InMemoryStore

from .role_levers import ROLE_LEVERS
from .ward_scope import require_single_ward, ward_of

_NOW = "1970-01-01T00:00:00Z"
_BARRIER_TYPE = "transport"
_LEVER_ID = "DCA-UNBLOCK-BARRIER"

# The one lever with a Sprint 38 effect; the effect the ActuationConsumer applies.
_EFFECT = {
    "applies_to": "DischargeBarrier", "mutation": "set_status",
    "from": "open", "to": "cleared", "select_by": "barrier_type",
    "cascade": [{"when": "patient_all_barriers_cleared", "set": "Patient.stage=DISCHARGED"}],
}
_CATALOG = [{"lever_id": _LEVER_ID, "owner_role": "dca", "impact_formula_ref": "unblock_barrier_beds"}]


def _gold_for_impact(sim: SimState, ward: str, horizon_h: int = 72) -> Dict[str, Any]:
    return {"forecast": [{
        "wardId": ward, "horizonH": horizon_h,
        "bedCapacity": sim.ward(ward).staffed_capacity,
        "forecastOccupiedBeds": sim.occupancy(ward),
    }]}


def _provenance_of(state: Any, sim: SimState) -> str:
    # Provenance tracks the gold source (simulated fixture today, live later). The
    # unit tests pass state=None, so default honestly to "simulated".
    loader = getattr(state, "load_gold_snapshot", None)
    if callable(loader):
        gold = loader(getattr(sim, "hospital_id", "USZ"))
        return gold.get("provenance", "simulated")
    return "simulated"


def _noop_outcome(action: Dict[str, Any], provenance: str) -> Dict[str, Any]:
    predicted = int(action["expected_impact"]["delta"])
    return {
        "contract": "DC-SIM-OUTCOME-v1", "cosmos_id": action["id"], "plan_id": action["plan_id"],
        "golden_thread": action.get("golden_thread", f"gt-{action['plan_id']}"),
        "lever_id": action["lever_id"], "applied_ts": _NOW,
        "predicted_impact": {"metric": "beds_freed", "value": predicted},
        "realised_impact": {"metric": "beds_freed", "value": 0},
        "state_delta": {"beds_freed": [], "patients_discharged": [], "patients_promoted": []},
        "divergence": 0.0, "provenance": provenance, "applied": False,
    }


def _nothing_to_do(plan_id: str, decision: str, provenance: str) -> Dict[str, Any]:
    # No open barriers: compute_expected_impact rejects n<=0, so we never propose.
    # Honest zero-impact no-op for both accept and deny.
    return {
        "contract": "DC-SIM-OUTCOME-v1", "cosmos_id": None, "plan_id": plan_id,
        "golden_thread": f"gt-{plan_id}", "lever_id": _LEVER_ID, "applied_ts": _NOW,
        "predicted_impact": {"metric": "beds_freed", "value": 0},
        "realised_impact": {"metric": "beds_freed", "value": 0},
        "state_delta": {"beds_freed": [], "patients_discharged": [], "patients_promoted": []},
        "divergence": 0.0, "provenance": provenance, "applied": False,
        "branch": decision, "decision": decision,
    }


def decide(
    role: str,
    decision: str,
    approver: str,
    state: Any,
    sim: SimState,
    params: Dict[str, Any],
    provenance: str | None = None,
) -> Dict[str, Any]:
    if decision not in ("accept", "deny"):
        raise ValueError(f"decision must be 'accept' or 'deny', got {decision!r}")

    # Single-ward MVP (see loop/ward_scope) + validate any caller-supplied ward so
    # an unknown ward is a 400, never an unhandled KeyError 500 at the mutation.
    require_single_ward(sim)

    lever = ROLE_LEVERS.get(role)
    if lever is not None and not lever.has_effect:
        # ooa/bmca: real, catalog-grounded math (Sprint 26 WS-B), but no
        # `effect:` mapping exists yet -- a real, tracked decision on a real
        # number, honestly never applied to SimState.
        if plan_runtime._is_bot_approver(approver):
            raise PermissionError(f"bot approver refused: {approver!r}")
        ward = params.get("ward") or ward_of(sim)
        if ward not in sim.wards:
            raise ValueError(f"unknown ward {ward!r}")
        if provenance is None:
            provenance = _provenance_of(state, sim)
        from .worklist import build_worklist  # reuse the same grounded math

        reco = build_worklist(role, sim, provenance=provenance)["recommendation"]
        plan_id = f"plan-decide-{sim.hospital_id}-{role}"
        return {
            "contract": "DC-SIM-OUTCOME-v1", "cosmos_id": None, "plan_id": plan_id,
            "golden_thread": f"gt-{plan_id}", "lever_id": lever.lever_id, "applied_ts": _NOW,
            "predicted_impact": reco["predicted_impact"],
            "realised_impact": {"metric": reco["predicted_impact"]["metric"], "value": 0},
            "state_delta": {"beds_freed": [], "patients_discharged": [], "patients_promoted": []},
            "divergence": 0.0, "provenance": provenance, "applied": False,
            "applyReason": "actuation_not_modeled_for_lever",
            "branch": decision, "decision": decision, "approver": approver,
        }

    barrier_type = params.get("barrier_type", _BARRIER_TYPE)
    ward = params.get("ward") or ward_of(sim)
    if ward not in sim.wards:
        raise ValueError(f"unknown ward {ward!r}")
    if provenance is None:
        provenance = _provenance_of(state, sim)
    plan_id = f"plan-decide-{sim.hospital_id}"

    n = len(sim.open_barriers(barrier_type))
    if n == 0:
        return _nothing_to_do(plan_id, decision, provenance)

    lever_params = {"barrier_type": barrier_type, "n": n, "ward": ward}
    impact_gold = _gold_for_impact(sim, ward)
    store = InMemoryStore()
    plan = plan_runtime.open_plan(
        store, episode_key=f"decide-{sim.hospital_id}", ward=ward,
        bed_capacity=sim.ward(ward).staffed_capacity,
        baseline_occupied_beds=sim.occupancy(ward), target_pct=90, now=_NOW,
    )
    golden_thread = f"gt-{plan['id']}"
    consumer = ActuationConsumer(store, {_LEVER_ID: _EFFECT})
    action = plan_runtime.propose_action(
        store, plan_id=plan["id"], role=role, lever_id=_LEVER_ID,
        params=lever_params, gold=impact_gold, catalog=_CATALOG, proposed_by=role, now=_NOW,
    )

    if decision == "accept":
        # Real HITL: approve_action refuses bot/self approvers (PermissionError
        # propagates to the route -> 403). Only a human oid gets past this gate.
        plan_runtime.approve_action(
            store, action_id=action["id"], approver=approver,
            gold=impact_gold, catalog=_CATALOG, now=_NOW,
        )
        outcomes = consumer.apply_approved(plan["id"], sim, now=_NOW)
        if outcomes:
            outcome = {**outcomes[-1], "applied": True}
        else:  # nothing applied -> honest zero-impact, never applied=True/realised=0
            outcome = {**_noop_outcome(action, provenance), "applied": False}
    else:  # deny — no approval, no apply, no state mutation
        outcome = {**_noop_outcome(action, provenance), "applied": False}

    return {
        **outcome,
        "golden_thread": golden_thread,
        "provenance": provenance,
        "branch": decision,
        "decision": decision,
        "approver": approver,
    }
