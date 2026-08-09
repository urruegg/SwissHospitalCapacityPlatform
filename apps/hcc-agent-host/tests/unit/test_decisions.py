"""Unit test — Sprint 39 P2 role decision handler (Task A3).

``decide`` drives the REAL decision-tier HITL on the in-host SimState:
accept -> plan_runtime.approve_action (refuses bot/self approvers) ->
ActuationConsumer.apply_approved -> DC-SIM-OUTCOME-v1; deny -> no-op, no state
mutation. Deterministic + PHI-free (synthetic ids only).
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
for p in (
    ROOT / "apps" / "hcc-agent-host" / "src",
    ROOT / "apps" / "sim-capacity" / "src",
    ROOT / "data-platform" / "decision",
):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from closedloop.gold_seed import seed_sim_state_from_gold
from loop.decisions import decide

_GOLD = json.loads(
    (ROOT / "apps" / "sim-capacity" / "tests" / "fixtures" / "gold-snapshot-usz.json").read_text(
        encoding="utf-8"
    )
)


def test_accept_frees_beds_and_mutates_state():
    sim = seed_sim_state_from_gold(_GOLD)
    before = sim.occupancy("C3")
    out = decide("dca", "accept", approver="clinician@usz.ch", state=None, sim=sim, params={})
    assert out["contract"] == "DC-SIM-OUTCOME-v1"
    assert out["realised_impact"]["value"] >= 1
    assert out["applied"] is True
    assert out["divergence"] == 0.0
    assert sim.occupancy("C3") < before  # beds were freed in the live sim


def test_deny_is_noop_and_leaves_state_unchanged():
    sim = seed_sim_state_from_gold(_GOLD)
    before = sim.snapshot()
    out = decide("dca", "deny", approver="clinician@usz.ch", state=None, sim=sim, params={})
    assert out["realised_impact"]["value"] == 0
    assert out["divergence"] == 0.0
    assert out["applied"] is False
    assert sim.snapshot() == before  # deny mutates nothing


def test_bot_approver_is_refused_and_leaves_state_unchanged():
    sim = seed_sim_state_from_gold(_GOLD)
    before = sim.occupancy("C3")
    with pytest.raises(PermissionError):
        decide("dca", "accept", approver="github-actions[bot]", state=None, sim=sim, params={})
    assert sim.occupancy("C3") == before  # refusal happens before any apply


def test_self_approver_is_refused():
    sim = seed_sim_state_from_gold(_GOLD)
    # proposed_by == role ("dca"); an approver equal to the proposing identity is
    # self-approval and must be refused by approve_action.
    with pytest.raises(PermissionError):
        decide("dca", "accept", approver="dca", state=None, sim=sim, params={})


def test_accept_with_no_open_barriers_is_a_safe_noop():
    sim = seed_sim_state_from_gold(_GOLD)
    for b in list(sim.barriers.values()):
        b.status = "cleared"
    out = decide("dca", "accept", approver="clinician@usz.ch", state=None, sim=sim, params={})
    assert out["realised_impact"]["value"] == 0
    assert out["applied"] is False


def test_ooa_decide_accept_is_tracked_but_not_applied():
    sim = seed_sim_state_from_gold(_GOLD)
    out = decide("ooa", "accept", approver="clinician@usz.ch", state=None, sim=sim, params={})
    assert out["lever_id"] == "OOA-EXPEDITE-DISCHARGE"
    assert out["applied"] is False
    assert out["decision"] == "accept"
    assert out["approver"] == "clinician@usz.ch"
    assert out["applyReason"] == "actuation_not_modeled_for_lever"


def test_bmca_decide_deny_is_tracked_but_not_applied():
    sim = seed_sim_state_from_gold(_GOLD)
    out = decide("bmca", "deny", approver="clinician@usz.ch", state=None, sim=sim, params={})
    assert out["lever_id"] == "BMCA-REBALANCE-CENSUS"
    assert out["applied"] is False
    assert out["decision"] == "deny"


def test_ooa_decide_bot_approver_still_refused():
    sim = seed_sim_state_from_gold(_GOLD)
    with pytest.raises(PermissionError):
        decide("ooa", "accept", approver="dependabot[bot]", state=None, sim=sim, params={})


def test_orsa_decide_accept_does_not_mutate_state_and_has_no_lever():
    # Final holistic review CRITICAL fix: orsa has no ROLE_LEVERS entry at all,
    # so it must never fall through to DCA's real barrier-clearing mutation.
    sim = seed_sim_state_from_gold(_GOLD)
    before = sim.snapshot()
    out = decide("orsa", "accept", approver="clinician@usz.ch", state=None, sim=sim, params={})
    assert out["contract"] == "DC-SIM-OUTCOME-v1"
    assert out["lever_id"] is None
    assert out["applied"] is False
    assert out["applyReason"] == "no_lever_for_role"
    assert out["decision"] == "accept"
    assert out["approver"] == "clinician@usz.ch"
    assert sim.snapshot() == before  # no beds freed, no patients discharged


def test_sba_decide_deny_does_not_mutate_state_and_has_no_lever():
    sim = seed_sim_state_from_gold(_GOLD)
    before = sim.snapshot()
    out = decide("sba", "deny", approver="clinician@usz.ch", state=None, sim=sim, params={})
    assert out["lever_id"] is None
    assert out["applied"] is False
    assert out["applyReason"] == "no_lever_for_role"
    assert out["decision"] == "deny"
    assert sim.snapshot() == before


def test_unknown_role_decide_accept_is_safe_and_non_mutating():
    # A typo'd/unrecognised agent name must never raise, and must never reach
    # DCA's mutation logic -- same safe behavior as orsa/sba.
    sim = seed_sim_state_from_gold(_GOLD)
    before = sim.snapshot()
    out = decide(
        "not-a-real-role", "accept", approver="clinician@usz.ch", state=None, sim=sim, params={}
    )
    assert out["lever_id"] is None
    assert out["applied"] is False
    assert out["applyReason"] == "no_lever_for_role"
    assert sim.snapshot() == before
