import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SIM_SRC = ROOT / "apps" / "sim-capacity" / "src"
DEC_SRC = ROOT / "data-platform" / "decision"
for p in (SIM_SRC, DEC_SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from closedloop.sim_state import build_sim_state, Stage
from closedloop.actuation import ActuationConsumer
from coordination.store import InMemoryStore
from coordination import plan_runtime

EFFECT = {
    "applies_to": "DischargeBarrier", "mutation": "set_status",
    "from": "open", "to": "cleared", "select_by": "barrier_type",
}
CATALOG = [{
    "lever_id": "DCA-UNBLOCK-BARRIER", "owner_role": "dca",
    "impact_formula_ref": "unblock_barrier_beds",
}]


def _gold_from_state(state, ward="C3", horizon_h=72):
    cap = state.ward(ward).staffed_capacity
    return {"forecast": [{"wardId": ward, "horizonH": horizon_h,
                          "bedCapacity": cap, "forecastOccupiedBeds": state.occupancy(ward)}]}


def _open_plan(store, state, ward="C3"):
    return plan_runtime.open_plan(
        store, episode_key="ep1", ward=ward,
        bed_capacity=state.ward(ward).staffed_capacity,
        baseline_occupied_beds=state.occupancy(ward), target_pct=90,
    )


def test_happy_path_closes_the_loop():
    state = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    beds_free_before = sum(1 for b in state.beds_in_ward("C3") if b.state == "available")
    store = InMemoryStore()
    plan = _open_plan(store, state)
    gold = _gold_from_state(state)
    action = plan_runtime.propose_action(
        store, plan_id=plan["id"], role="dca", lever_id="DCA-UNBLOCK-BARRIER",
        params={"barrier_type": "transport", "n": 2, "ward": "C3"}, gold=gold, catalog=CATALOG,
        proposed_by="dca",
    )
    plan_runtime.approve_action(store, action_id=action["id"], approver="alice", gold=gold, catalog=CATALOG)

    consumer = ActuationConsumer(store, {"DCA-UNBLOCK-BARRIER": EFFECT})
    outcomes = consumer.apply_approved(plan["id"], state)

    beds_free_after = sum(1 for b in state.beds_in_ward("C3") if b.state == "available")
    assert beds_free_after == beds_free_before + 2       # loop closed: state changed
    assert len(outcomes) == 1
    assert outcomes[0]["divergence"] <= 0.5              # predicted ~ realised


def test_approval_withheld_does_not_change_trajectory():
    state = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    beds_free_before = sum(1 for b in state.beds_in_ward("C3") if b.state == "available")
    store = InMemoryStore()
    plan = _open_plan(store, state)
    gold = _gold_from_state(state)
    plan_runtime.propose_action(
        store, plan_id=plan["id"], role="dca", lever_id="DCA-UNBLOCK-BARRIER",
        params={"barrier_type": "transport", "n": 2, "ward": "C3"}, gold=gold, catalog=CATALOG,
        proposed_by="dca",
    )
    # No approve_action call — the human withheld approval.
    consumer = ActuationConsumer(store, {"DCA-UNBLOCK-BARRIER": EFFECT})
    outcomes = consumer.apply_approved(plan["id"], state)
    beds_free_after = sum(1 for b in state.beds_in_ward("C3") if b.state == "available")
    assert outcomes == []
    assert beds_free_after == beds_free_before           # trajectory unchanged


def test_self_approval_is_refused_by_decision_tier():
    state = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    store = InMemoryStore()
    plan = _open_plan(store, state)
    gold = _gold_from_state(state)
    action = plan_runtime.propose_action(
        store, plan_id=plan["id"], role="dca", lever_id="DCA-UNBLOCK-BARRIER",
        params={"barrier_type": "transport", "n": 2, "ward": "C3"}, gold=gold, catalog=CATALOG,
        proposed_by="dca",
    )
    import pytest
    with pytest.raises(Exception):
        plan_runtime.approve_action(store, action_id=action["id"], approver="dca", gold=gold, catalog=CATALOG)


def test_second_apply_is_idempotent():
    state = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    store = InMemoryStore()
    plan = _open_plan(store, state)
    gold = _gold_from_state(state)
    action = plan_runtime.propose_action(
        store, plan_id=plan["id"], role="dca", lever_id="DCA-UNBLOCK-BARRIER",
        params={"barrier_type": "transport", "n": 2, "ward": "C3"}, gold=gold, catalog=CATALOG,
        proposed_by="dca",
    )
    plan_runtime.approve_action(store, action_id=action["id"], approver="alice", gold=gold, catalog=CATALOG)
    consumer = ActuationConsumer(store, {"DCA-UNBLOCK-BARRIER": EFFECT})
    consumer.apply_approved(plan["id"], state)
    assert consumer.apply_approved(plan["id"], state) == []   # already actuated
