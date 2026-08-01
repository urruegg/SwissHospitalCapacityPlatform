"""Unit test — Sprint 39 P2 in-host SimState registry (Task A1).

The agent-host holds one stateful SimState per hospital, seeded from a
materialized gold snapshot via the Plan 1 gold_seed. Deterministic + PHI-free
(synthetic ids only).
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

from loop.sim_registry import SimRegistry

_GOLD = json.loads(
    (ROOT / "apps" / "sim-capacity" / "tests" / "fixtures" / "gold-snapshot-usz.json").read_text(
        encoding="utf-8"
    )
)


def test_registry_seeds_and_returns_state():
    reg = SimRegistry()
    state = reg.get_or_seed("USZ", _GOLD)
    assert state.hospital_id == "USZ"
    assert state.occupancy("C3") == 6
    # same hospital returns the same (stateful) instance
    assert reg.get_or_seed("USZ", _GOLD) is state


def test_reset_reseeds():
    reg = SimRegistry()
    first = reg.get_or_seed("USZ", _GOLD)
    reg.reset("USZ")
    second = reg.get_or_seed("USZ", _GOLD)
    assert second is not first
    assert second.snapshot() == first.snapshot()
