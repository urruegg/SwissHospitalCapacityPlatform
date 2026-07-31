# apps/sim-capacity/tests/test_state_store.py
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from closedloop.sim_state import build_sim_state
from closedloop.state_store import InMemorySimStateStore, save_snapshot, load_snapshot


def test_store_put_get_roundtrip():
    store = InMemorySimStateStore()
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 10)])
    store.put(s)
    assert store.get("USZ").snapshot() == s.snapshot()


def test_json_snapshot_roundtrip(tmp_path):
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 10)])
    p = tmp_path / "state.json"
    save_snapshot(s, p)
    reloaded = load_snapshot(p)
    assert reloaded.snapshot() == s.snapshot()
