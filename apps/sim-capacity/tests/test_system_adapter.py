# apps/sim-capacity/tests/test_system_adapter.py
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from closedloop.sim_state import build_sim_state
from closedloop.system_adapter import EpicAdapter

_PHI_TOKEN = re.compile(r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b")  # SSN-like guard


def test_adapter_emits_bed_state_envelopes():
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 10)])
    adapter = EpicAdapter(s)
    envs = adapter.read_demand(simulated_at=datetime(2027, 1, 15, 8), sim_run_id="run-x", seed=42)
    bed_states = [e for e in envs if e["eventKind"] == "bed_state"]
    assert len(bed_states) == 10
    assert all(e["hospitalId"] == "USZ" for e in bed_states)


def test_adapter_derives_ward_occupancy_summary():
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 10)])
    adapter = EpicAdapter(s)
    envs = adapter.read_demand(simulated_at=datetime(2027, 1, 15, 8), sim_run_id="run-x", seed=42)
    summary = next(e for e in envs if e["eventKind"] == "ward_occupancy")
    assert summary["payload"]["wardId"] == "C3"
    assert summary["payload"]["occupiedBeds"] == s.occupancy("C3")


def test_adapter_output_is_phi_free():
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 10)])
    adapter = EpicAdapter(s)
    envs = adapter.read_demand(simulated_at=datetime(2027, 1, 15, 8), sim_run_id="run-x", seed=42)
    blob = str(envs)
    assert not _PHI_TOKEN.search(blob)
