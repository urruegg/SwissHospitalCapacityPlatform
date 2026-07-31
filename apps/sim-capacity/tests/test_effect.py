# apps/sim-capacity/tests/test_effect.py
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from closedloop.sim_state import build_sim_state, Stage
from closedloop.effect import apply_effect

UNBLOCK_BARRIER_EFFECT = {
    "applies_to": "DischargeBarrier",
    "mutation": "set_status",
    "from": "open",
    "to": "cleared",
    "select_by": "barrier_type",
    "cascade": [{"when": "patient_all_barriers_cleared", "set": "Patient.stage=DISCHARGE_READY"}],
}


def test_unblock_barrier_clears_n_barriers_and_frees_beds():
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    open_before = len(s.open_barriers("transport"))
    assert open_before >= 2  # seed 42 guarantees barriers to clear
    delta = apply_effect(s, UNBLOCK_BARRIER_EFFECT, {"barrier_type": "transport", "n": 2})
    assert len(s.open_barriers("transport")) == open_before - 2
    assert delta["metric"] == "beds_freed"
    assert delta["delta"] == 2
    assert len(delta["state_delta"]["beds_freed"]) == 2


def test_effect_is_bounded_by_available_barriers():
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    open_before = len(s.open_barriers("transport"))
    delta = apply_effect(s, UNBLOCK_BARRIER_EFFECT, {"barrier_type": "transport", "n": open_before + 5})
    assert delta["delta"] == open_before  # cannot clear more than exist
