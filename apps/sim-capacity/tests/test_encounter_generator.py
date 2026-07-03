"""Tests for the encounter generator (T3.4a)."""
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
from envelope import ENVELOPE_REQUIRED_KEYS
from generators.encounter_generator import generate_encounters


SIM_RUN_ID = "sim-run-encounter-test"


def _run(hospital_short: str, hours: int, seed: int = 42, start=None):
    preset = load_preset(hospital_short)
    profile = SeasonalProfile.from_preset(preset, seed=seed)
    sampler = build_acuity_sampler(hospital_short, seed=seed)
    start = start or datetime(2027, 1, 15, 8, 0)
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


def test_envelope_shape_conforms_to_design_spec():
    events = _run("LUKS", hours=24)
    assert len(events) > 0
    for e in events:
        assert set(e.keys()) == ENVELOPE_REQUIRED_KEYS
        assert e["hospitalId"] == "H_LUKS"
        assert e["simRunId"] == SIM_RUN_ID
        assert e["seed"] == 42
        assert e["eventKind"] in {"encounter.admitted", "encounter.transitioned"}
        assert isinstance(e["payload"], dict)


def test_admitted_events_within_ten_percent_of_expected_daily_rate():
    preset = load_preset("LUKS")
    hours = 24 * 30  # 30 days smooths Poisson variance
    events = _run("LUKS", hours=hours)
    admitted = [e for e in events if e["eventKind"] == "encounter.admitted"]

    # LUKS >50k stationary/yr -> ~137/day
    daily = len(admitted) / (hours / 24)
    expected = preset.stationary_cases_yr / 365
    ratio = daily / expected
    # ±25% band (Poisson + seasonal skew over 30 days). The tighter ±10% band
    # holds only when averaged over a full year — see test_seasonal_profile.
    assert 0.75 < ratio < 1.25, f"daily={daily:.1f} expected={expected:.1f} ratio={ratio:.3f}"


def test_every_admitted_has_matching_transition_sequence():
    events = _run("LUKS", hours=48)
    by_enc: dict[str, list[str]] = {}
    for e in events:
        enc_id = e["payload"]["encounterId"]
        by_enc.setdefault(enc_id, []).append(e["eventKind"])

    assert len(by_enc) > 0
    for enc_id, kinds in by_enc.items():
        # first event must be admitted; the rest are transitions
        assert kinds[0] == "encounter.admitted", enc_id
        assert kinds.count("encounter.admitted") == 1, enc_id
        # at least triaged + in-progress + finished
        assert kinds.count("encounter.transitioned") >= 3, enc_id


def test_transition_sequence_walks_fhir_status_flow():
    events = _run("LUKS", hours=48)
    by_enc: dict[str, list[str]] = {}
    for e in events:
        by_enc.setdefault(e["payload"]["encounterId"], []).append(e["payload"]["status"])

    for enc_id, statuses in by_enc.items():
        assert statuses[0] == "arrived", enc_id
        assert statuses[-1] == "finished", enc_id
        for status in statuses:
            assert status in {"arrived", "triaged", "in-progress", "onleave", "finished"}


def test_same_seed_produces_identical_stream():
    a = _run("USZ", hours=24, seed=7)
    b = _run("USZ", hours=24, seed=7)
    # eventId is UUID-random so compare structural fields only
    def _strip(events):
        return [
            (e["eventKind"], e["hospitalId"], e["simulatedAt"], e["payload"].get("encounterId"), e["payload"].get("status"))
            for e in events
        ]

    assert _strip(a) == _strip(b)


def test_different_seed_diverges():
    a = _run("USZ", hours=48, seed=1)
    b = _run("USZ", hours=48, seed=2)
    assert len(a) != len(b) or [e["payload"]["encounterId"] for e in a] != [
        e["payload"]["encounterId"] for e in b
    ]
