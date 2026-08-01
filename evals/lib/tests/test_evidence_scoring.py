# evals/lib/tests/test_evidence_scoring.py
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for p in (ROOT / "apps" / "sim-capacity" / "src", ROOT / "data-platform" / "decision"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from closedloop.evidence import build_evidence_trace
from lib.sim_outcome_eval import run_calibration_gate, outcome_divergence

_GOLD = json.loads((ROOT / "apps" / "sim-capacity" / "tests" / "fixtures" / "gold-snapshot-usz.json").read_text(encoding="utf-8"))


def test_accept_outcomes_pass_the_calibration_gate():
    trace = build_evidence_trace(_GOLD, branch="accept")
    outcomes = [s["outcome"] for s in trace["steps"] if s["action"]["status"] == "applied"]
    assert outcomes, "accept branch produced at least one applied outcome"
    report = run_calibration_gate(outcomes)
    assert report["passed"]
    assert all(outcome_divergence(o).passed for o in outcomes)
