"""Tests for the bed state generator (T3.4b)."""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from calibration.hospital_presets import load_preset
from calibration.ward_topology import load_ward_topology
from envelope import ENVELOPE_REQUIRED_KEYS
from generators.bed_state_generator import (
    _STATE_TRANSITIONS,
    generate_bed_states,
)


def _run(hospital_short: str, hours: int = 24, seed: int = 42):
    preset = load_preset(hospital_short)
    return list(
        generate_bed_states(
            preset=preset,
            sim_run_id="sim-run-bed-test",
            seed=seed,
            start_time=datetime(2027, 1, 15, 8, 0),
            duration_hours=hours,
        )
    )


def test_envelope_shape_conforms():
    events = _run("LUKS", hours=2)
    assert events
    for e in events:
        assert set(e.keys()) == ENVELOPE_REQUIRED_KEYS
        assert e["eventKind"] == "bed.state_changed"
        assert e["hospitalId"] == "H_LUKS"
        p = e["payload"]
        assert p["state"] in {"available", "occupied", "cleaning", "blocked"}
        assert p["previousState"] in {"available", "occupied", "cleaning", "blocked"}
        assert p["bedId"].startswith("WARD_")


def test_transitions_respect_state_machine():
    events = _run("LUKS", hours=24)
    for e in events:
        p = e["payload"]
        allowed = _STATE_TRANSITIONS.get(p["previousState"], [])
        assert p["state"] in allowed, f"invalid transition {p['previousState']} -> {p['state']}"


def test_beds_enumerated_from_ward_topology():
    events = _run("LUKS", hours=24)
    bed_ids = {e["payload"]["bedId"] for e in events}
    wards = load_ward_topology("LUKS")
    total_beds = sum((w.bed_count or 0) for w in wards.values())
    # Not every bed will change state in 24h, but many will
    assert 0 < len(bed_ids) <= total_beds


def test_rate_near_target_for_luks():
    events = _run("LUKS", hours=24)
    rate = len(events) / 24
    # Target ~200/hr for LUKS per plan; tolerate wide band because it depends
    # on bed count and hold-time draws.
    assert 50 < rate < 500, f"observed rate={rate:.1f}/hr"


def test_deterministic_by_seed():
    a = _run("SZB", hours=8, seed=99)
    b = _run("SZB", hours=8, seed=99)
    key = lambda e: (e["simulatedAt"], e["payload"]["bedId"], e["payload"]["state"])
    assert [key(e) for e in a] == [key(e) for e in b]
