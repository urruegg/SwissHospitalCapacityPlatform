"""Tests for the matching engine generator (T3.4c)."""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from calibration.acuity_distribution import build_acuity_sampler
from calibration.hospital_presets import load_preset
from calibration.seasonal_profile import SeasonalProfile
from calibration.ward_topology import load_ward_topology
from envelope import ENVELOPE_REQUIRED_KEYS
from generators.encounter_generator import generate_encounters
from generators.matching_engine import generate_bed_assignments


SIM_RUN_ID = "sim-run-matching-test"


def _encounters(hospital_short: str, hours: int, seed: int = 42):
    preset = load_preset(hospital_short)
    profile = SeasonalProfile.from_preset(preset, seed=seed)
    sampler = build_acuity_sampler(hospital_short, seed=seed)
    start = datetime(2027, 1, 15, 8, 0)
    return list(
        generate_encounters(
            preset=preset,
            profile=profile,
            sampler=sampler,
            sim_run_id=SIM_RUN_ID,
            seed=seed,
            start_time=start,
            duration_hours=hours,
        )
    )


def _assign(hospital_short: str, encounters, seed: int = 42, max_per_hour: int = 8):
    preset = load_preset(hospital_short)
    return list(
        generate_bed_assignments(
            preset=preset,
            encounter_events=encounters,
            sim_run_id=SIM_RUN_ID,
            seed=seed,
            max_per_hour=max_per_hour,
        )
    )


def test_envelope_shape_conforms_to_design_spec():
    encs = _encounters("LUKS", hours=6)
    events = _assign("LUKS", encs)
    assert len(events) > 0
    for e in events:
        assert set(e.keys()) == ENVELOPE_REQUIRED_KEYS
        assert e["eventKind"] == "bed.assigned"
        assert e["hospitalId"] == "H_LUKS"
        p = e["payload"]
        assert p["encounterId"].startswith("ENC-")
        assert p["bedId"].startswith("WARD_")
        assert 0.0 <= p["matchScore"] <= 1.0
        assert p["assignmentReason"] in {"specialty-match", "fallback"}
        assert isinstance(p["explanationTokens"], list) and p["explanationTokens"]


def test_specialty_match_uses_ward_of_matching_specialty():
    encs = _encounters("LUKS", hours=12)
    events = _assign("LUKS", encs)
    wards = load_ward_topology("LUKS")

    # For every specialty-match assignment, the bed's ward specialty must
    # equal the encounter's requested specialty.
    for e in events:
        p = e["payload"]
        if p["assignmentReason"] != "specialty-match":
            continue
        ward = wards[p["wardId"]]
        assert ward.specialty_id == p["requestedSpecialtyId"], (
            f"specialty-match assignment routed encounter {p['encounterId']} "
            f"(requested {p['requestedSpecialtyId']}) to ward with specialty "
            f"{ward.specialty_id}"
        )
        assert p["hardConstraintsMet"] is True


def test_rate_capped_at_max_per_hour():
    encs = _encounters("LUKS", hours=24)
    events = _assign("LUKS", encs, max_per_hour=5)
    # Bucket assignments by simulated hour of the encounter admit time; the
    # engine uses admit-hour for its cap, so the derived per-hour count of
    # assignments (from the admit-hour bucket) must not exceed max.
    by_hour: dict[str, int] = {}
    for e in events:
        p = e["payload"]
        hour = p["assignedAt"][:13]
        by_hour[hour] = by_hour.get(hour, 0) + 1
    for hour, n in by_hour.items():
        assert n <= 5, f"hour {hour} produced {n} assignments (>5)"


def test_deterministic_by_seed():
    encs_a = _encounters("SZB", hours=8, seed=7)
    encs_b = _encounters("SZB", hours=8, seed=7)
    a = _assign("SZB", encs_a, seed=7)
    b = _assign("SZB", encs_b, seed=7)
    key = lambda ev: (
        ev["payload"]["encounterId"],
        ev["payload"]["bedId"],
        ev["payload"]["assignmentReason"],
    )
    assert [key(x) for x in a] == [key(x) for x in b]


def test_ignores_non_admitted_events():
    encs = _encounters("LUKS", hours=8)
    # Filter to only transitioned events — matcher must produce nothing.
    transitions = [e for e in encs if e["eventKind"] == "encounter.transitioned"]
    events = _assign("LUKS", transitions)
    assert events == []


def test_bed_pool_missing_yields_nothing():
    """If ward topology yields no beds, generator must terminate cleanly."""
    from generators.matching_engine import generate_bed_assignments

    preset = load_preset("LUKS")
    encs = _encounters("LUKS", hours=4)
    empty_events = list(
        generate_bed_assignments(
            preset=preset,
            encounter_events=encs,
            sim_run_id=SIM_RUN_ID,
            seed=0,
            ward_topology={},
        )
    )
    assert empty_events == []
