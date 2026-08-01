# apps/sim-capacity/tests/test_evidence.py
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SIM_SRC = ROOT / "apps" / "sim-capacity" / "src"
DEC_SRC = ROOT / "data-platform" / "decision"
for p in (SIM_SRC, DEC_SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from closedloop.evidence import build_evidence_trace

_GOLD = json.loads((Path(__file__).parent / "fixtures" / "gold-snapshot-usz.json").read_text(encoding="utf-8"))
_SCHEMA = json.loads((ROOT / "data" / "synthetic" / "schema" / "dc-evidence-trace-v1.schema.json").read_text(encoding="utf-8"))
_PHI = re.compile(r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b")


def test_accept_branch_frees_beds_and_records_outcome():
    trace = build_evidence_trace(_GOLD, branch="accept")
    assert trace["contract"] == "DC-EVIDENCE-TRACE-v1"
    assert trace["branch"] == "accept"
    dca = next(s for s in trace["steps"] if s["role"] == "dca")
    assert dca["copilot"]["decision"] == "accept"
    assert dca["action"]["status"] == "applied"
    assert dca["outcome"]["realised_impact"]["value"] >= 1


def test_deny_branch_changes_nothing():
    trace = build_evidence_trace(_GOLD, branch="deny")
    dca = next(s for s in trace["steps"] if s["role"] == "dca")
    assert dca["copilot"]["decision"] == "deny"
    assert dca["action"]["status"] == "denied"
    assert dca["outcome"]["realised_impact"]["value"] == 0


def test_trace_is_schema_valid_and_threaded():
    trace = build_evidence_trace(_GOLD, branch="accept")
    for key in _SCHEMA["required"]:
        assert key in trace
    assert trace["golden_thread"]
    assert all(s.get("epic_input", {}).get("provenance") in ("simulated", "live") for s in trace["steps"])


def test_trace_is_phi_free():
    trace = build_evidence_trace(_GOLD, branch="accept")
    assert not _PHI.search(json.dumps(trace))
    assert trace["patient"]["provenance"] in ("simulated", "live")
