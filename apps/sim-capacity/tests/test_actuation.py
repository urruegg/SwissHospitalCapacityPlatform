# apps/sim-capacity/tests/test_actuation.py
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from closedloop.sim_state import build_sim_state
from closedloop.actuation import ActuationConsumer

EFFECT = {
    "applies_to": "DischargeBarrier", "mutation": "set_status",
    "from": "open", "to": "cleared", "select_by": "barrier_type",
    "cascade": [{"when": "patient_all_barriers_cleared", "set": "Patient.stage=DISCHARGED"}],
}


class FakePlanStore:
    """Minimal PlanStore stand-in matching coordination.store.PlanStore's surface."""
    def __init__(self):
        self._actions = {}
        self._order = []

    def create_action(self, a):
        self._actions[a["id"]] = dict(a)
        self._order.append(a["id"])

    def get_action(self, aid):
        return dict(self._actions[aid]) if aid in self._actions else None

    def upsert_action(self, a):
        self._actions[a["id"]] = dict(a)

    def list_actions(self, plan_id):
        return [dict(self._actions[i]) for i in self._order if self._actions[i]["plan_id"] == plan_id]


def _approved_action(aid, delta):
    return {
        "id": aid, "plan_id": "plan-ep1", "role": "dca",
        "lever_id": "DCA-UNBLOCK-BARRIER", "params": {"barrier_type": "transport", "n": 2},
        "expected_impact": {"metric": "beds", "delta": delta},
        "status": "applied", "hitl_approver": "alice",
    }


def test_consumer_applies_approved_action_to_state():
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    store = FakePlanStore()
    store.create_action(_approved_action("a0", 2))
    consumer = ActuationConsumer(store, {"DCA-UNBLOCK-BARRIER": EFFECT})
    outcomes = consumer.apply_approved("plan-ep1", s)
    assert len(outcomes) == 1
    assert outcomes[0]["realised_impact"]["value"] == 2
    assert store.get_action("a0")["sim_applied_at"] is not None


def test_consumer_is_idempotent():
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    store = FakePlanStore()
    store.create_action(_approved_action("a0", 2))
    consumer = ActuationConsumer(store, {"DCA-UNBLOCK-BARRIER": EFFECT})
    consumer.apply_approved("plan-ep1", s)
    second = consumer.apply_approved("plan-ep1", s)  # already actuated
    assert second == []


def test_consumer_refuses_unapproved_action():
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    store = FakePlanStore()
    proposed = _approved_action("a0", 2)
    proposed["status"] = "proposed"  # NOT yet HITL-approved
    store.create_action(proposed)
    consumer = ActuationConsumer(store, {"DCA-UNBLOCK-BARRIER": EFFECT})
    assert consumer.apply_approved("plan-ep1", s) == []
