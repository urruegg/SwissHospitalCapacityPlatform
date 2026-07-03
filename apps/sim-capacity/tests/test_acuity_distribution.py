import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from calibration.acuity_distribution import build_acuity_sampler


def test_same_seed_same_sequence():
    s1 = build_acuity_sampler("USZ", seed=42)
    s2 = build_acuity_sampler("USZ", seed=42)
    seq1 = [s1.sample() for _ in range(10)]
    seq2 = [s2.sample() for _ in range(10)]
    assert seq1 == seq2


def test_different_seed_different_sequence():
    s1 = build_acuity_sampler("USZ", seed=42)
    s2 = build_acuity_sampler("USZ", seed=99)
    seq1 = [s1.sample() for _ in range(20)]
    seq2 = [s2.sample() for _ in range(20)]
    assert seq1 != seq2


def test_same_sampler_advances_state():
    s = build_acuity_sampler("USZ", seed=42)
    draws = [s.sample() for _ in range(50)]
    assert len({d for d in draws}) >= 3


def test_reseed_resets_sequence():
    s = build_acuity_sampler("USZ", seed=42)
    first_draw = s.sample()
    for _ in range(5):
        s.sample()
    s.reseed(42)
    after_reseed = s.sample()
    assert first_draw == after_reseed
