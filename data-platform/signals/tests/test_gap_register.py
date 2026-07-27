"""Sprint 32 SGA — Signal Gap Register tests."""
from __future__ import annotations

from signals.gap_register import build_gap_register


def test_ranks_referenced_but_unwired_and_dq_gaps_first():
    referenced = {"certification-register", "or-anaesthesia-status", "rostering-feed"}
    wired = {"rostering-feed"}
    dq_gaps = [{"domain": "staffing.skills", "recommendedSource": {"kind": "certification-register"}, "impactScore": 0.42, "newSourceNeeded": True}]
    reg = build_gap_register(referenced, wired, dq_gaps)
    kinds = [r["signal"] for r in reg]
    # DQ-demanded certification-register ranks first (has an impact score); unwired next
    assert kinds[0] == "certification-register"
    assert "or-anaesthesia-status" in kinds
    assert "rostering-feed" not in kinds  # already wired
    assert reg[0]["demandedByDq"] is True
    assert all(0.0 <= r["rank"] for r in reg)


def test_empty_when_all_wired_and_no_dq_gap():
    assert build_gap_register({"a"}, {"a"}, []) == []
