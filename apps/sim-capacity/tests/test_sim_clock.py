import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from clock.sim_clock import SimClock


def test_clock_accelerates_60x():
    c = SimClock(start=datetime(2027, 1, 1), rate=60.0)
    real_ticks = []
    for _ in range(5):
        real_ticks.append(c.now())
        time.sleep(0.1)  # 100ms real = 6 sim seconds
    elapsed_sim = (real_ticks[-1] - real_ticks[0]).total_seconds()
    assert 20 < elapsed_sim < 30  # ~24s sim time (0.4s real x 60)


def test_clock_deterministic_seed():
    c1 = SimClock(start=datetime(2027, 1, 1), rate=60.0, seed=42)
    c2 = SimClock(start=datetime(2027, 1, 1), rate=60.0, seed=42)
    seq1 = [c1.random_uniform() for _ in range(10)]
    seq2 = [c2.random_uniform() for _ in range(10)]
    assert seq1 == seq2


def test_clock_zero_rate_freezes_time():
    c = SimClock(start=datetime(2027, 1, 1), rate=0.0)
    t1 = c.now()
    time.sleep(0.1)
    t2 = c.now()
    assert (t2 - t1).total_seconds() == 0
