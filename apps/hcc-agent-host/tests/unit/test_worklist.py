"""Unit test — Sprint 39 P2 role worklist builder (Task A2).

``build_worklist`` turns the in-host SimState into a role's live observations +
one grounded DC-INSIGHT-style recommendation. Deterministic: the predicted
impact is ``compute_expected_impact`` on the seeded occupancy, never an LLM
guess. Includes the n==0 guard (empty barriers must not call the impact tool,
which rejects n<=0).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
for p in (
    ROOT / "apps" / "hcc-agent-host" / "src",
    ROOT / "apps" / "sim-capacity" / "src",
    ROOT / "data-platform" / "decision",
):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from closedloop.gold_seed import seed_sim_state_from_gold
from loop.worklist import build_worklist

_GOLD = json.loads(
    (ROOT / "apps" / "sim-capacity" / "tests" / "fixtures" / "gold-snapshot-usz.json").read_text(
        encoding="utf-8"
    )
)


class _FakeFabric:
    def __init__(self, rows=None, raise_on_query=False):
        self._rows = rows or []
        self._raise = raise_on_query

    def query(self, table: str):
        if self._raise:
            raise RuntimeError("simulated fabric outage")
        return self._rows


def _seeded_state():
    return seed_sim_state_from_gold(_GOLD)


def test_dca_worklist_lists_open_barrier_candidates_and_a_recommendation():
    state = _seeded_state()
    wl = build_worklist("dca", state, provenance="live")
    assert wl["role"] == "dca"
    assert len(wl["observations"]) == 3  # 3 open transport barriers
    assert all(o["provenance"] == "live" for o in wl["observations"])
    rec = wl["recommendation"]
    assert rec["lever_id"] == "DCA-UNBLOCK-BARRIER"
    assert rec["predicted_impact"]["value"] >= 1
    assert rec["citations"]


def test_dca_worklist_provenance_passthrough():
    state = seed_sim_state_from_gold(_GOLD)
    wl = build_worklist("dca", state, provenance="simulated")
    assert wl["provenance"] == "simulated"
    assert all(o["provenance"] == "simulated" for o in wl["observations"])


def test_dca_worklist_no_open_barriers_is_a_safe_noop():
    # n==0 guard: compute_expected_impact rejects n<=0, so an empty state must
    # NOT call it. Expect an honest zero-impact recommendation, no crash.
    state = seed_sim_state_from_gold(_GOLD)
    for b in list(state.barriers.values()):
        b.status = "cleared"
    wl = build_worklist("dca", state, provenance="simulated")
    assert wl["observations"] == []
    rec = wl["recommendation"]
    assert rec["lever_id"] == "DCA-UNBLOCK-BARRIER"
    assert rec["predicted_impact"]["value"] == 0
    assert "no open transport barriers" in rec["insight_text"].lower()
    assert rec["citations"]


def test_dca_worklist_attaches_live_citation_when_fabric_present():
    state = _seeded_state()
    fake_rows = [{"patient": "p1", "ward": "B"}]
    fabric = _FakeFabric(rows=fake_rows)
    wl = build_worklist("dca", state, provenance="simulated", fabric=fabric)
    assert wl["recommendation"]["liveGroundingCitations"] == fake_rows


def test_dca_worklist_omits_live_citation_on_fabric_failure():
    state = _seeded_state()
    fabric = _FakeFabric(raise_on_query=True)
    wl = build_worklist("dca", state, provenance="simulated", fabric=fabric)
    assert wl["recommendation"]["liveGroundingCitations"] == []


def test_dca_worklist_no_fabric_means_no_live_citations_key_change():
    state = _seeded_state()
    wl = build_worklist("dca", state, provenance="simulated")
    assert wl["recommendation"]["liveGroundingCitations"] == []


def test_ooa_worklist_uses_real_formula_registry():
    state = _seeded_state()
    wl = build_worklist("ooa", state, provenance="simulated")
    assert wl["recommendation"]["lever_id"] == "OOA-EXPEDITE-DISCHARGE"
    assert wl["recommendation"]["predicted_impact"]["value"] >= 0
    assert wl["recommendation"]["params"]["before"] == "end-of-shift"


def test_bmca_worklist_uses_real_formula_registry():
    state = _seeded_state()
    wl = build_worklist("bmca", state, provenance="simulated")
    assert wl["recommendation"]["lever_id"] == "BMCA-REBALANCE-CENSUS"
    assert wl["recommendation"]["params"]["to_ward"] == "Medicine B"


def test_orsa_and_sba_worklist_are_unchanged_placeholder():
    state = _seeded_state()
    for role in ("orsa", "sba"):
        wl = build_worklist(role, state, provenance="simulated")
        assert wl["recommendation"]["lever_id"] is None
        assert "pending" in wl["recommendation"]["insight_text"]
