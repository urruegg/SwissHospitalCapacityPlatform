# apps/sim-capacity/tests/test_tick.py
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from closedloop.sim_state import build_sim_state
from closedloop.tick import advance_state


def test_tick_ages_open_barriers_by_one_hour():
    s = build_sim_state("USZ", 3, [("C3", "internal-medicine", 20)])
    before = {b.barrier_id: b.aged_h for b in s.barriers.values() if b.status == "open"}
    advance_state(s, random.Random(3))
    for bid, aged in before.items():
        assert s.barriers[bid].aged_h == aged + 1


def test_tick_is_deterministic_for_same_seed():
    a = build_sim_state("USZ", 5, [("C3", "internal-medicine", 20)])
    b = build_sim_state("USZ", 5, [("C3", "internal-medicine", 20)])
    for _ in range(5):
        advance_state(a, random.Random(99))
        advance_state(b, random.Random(99))
    assert a.snapshot() == b.snapshot()
