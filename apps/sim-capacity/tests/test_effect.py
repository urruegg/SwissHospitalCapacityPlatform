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
    "cascade": [{"when": "patient_all_barriers_cleared", "set": "Patient.stage=DISCHARGED"}],
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


def test_effect_honors_declared_cascade_stage_promote_without_bed_free():
    # A cascade that promotes to DISCHARGE_READY must NOT free a bed (patient still occupies it).
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    promote_effect = {
        "applies_to": "DischargeBarrier", "mutation": "set_status",
        "from": "open", "to": "cleared", "select_by": "barrier_type",
        "cascade": [{"when": "patient_all_barriers_cleared", "set": "Patient.stage=DISCHARGE_READY"}],
    }
    beds_free_before = sum(1 for b in s.beds_in_ward("C3") if b.state == "available")
    delta = apply_effect(s, promote_effect, {"barrier_type": "transport", "n": 2})
    beds_free_after = sum(1 for b in s.beds_in_ward("C3") if b.state == "available")
    assert delta["delta"] == 0
    assert beds_free_after == beds_free_before
    assert len(delta["state_delta"]["patients_promoted"]) == 2


def test_effect_fails_closed_on_unsupported_applies_to():
    import pytest
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    with pytest.raises(ValueError, match="applies_to"):
        apply_effect(s, {"applies_to": "Patient", "mutation": "set_status", "to": "x"}, {"barrier_type": "transport", "n": 1})


def test_effect_fails_closed_on_unsupported_cascade():
    import pytest
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    bad = {
        "applies_to": "DischargeBarrier", "mutation": "set_status", "from": "open",
        "to": "cleared", "select_by": "barrier_type",
        "cascade": [{"when": "something_else", "set": "Patient.stage=DISCHARGED"}],
    }
    with pytest.raises(ValueError, match="cascade"):
        apply_effect(s, bad, {"barrier_type": "transport", "n": 1})


def test_effect_honors_from_status_only_selects_matching():
    # Barriers not in the declared `from` status are not selected.
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    # Pre-clear one barrier so it is no longer in status "open".
    already = sorted(s.open_barriers("transport"), key=lambda b: b.barrier_id)[0]
    already.status = "cleared"
    open_after = len(s.open_barriers("transport"))
    eff = {
        "applies_to": "DischargeBarrier", "mutation": "set_status", "from": "open",
        "to": "cleared", "select_by": "barrier_type",
        "cascade": [{"when": "patient_all_barriers_cleared", "set": "Patient.stage=DISCHARGED"}],
    }
    delta = apply_effect(s, eff, {"barrier_type": "transport", "n": 99})
    # It clears only the still-open ones; the pre-cleared barrier is untouched.
    assert len(delta["state_delta"]["patients_discharged"]) == open_after
