"""Tests for the discharge scorer generator (T3.4e)."""
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
from generators.discharge_scorer import generate_discharge_scores
from generators.encounter_generator import generate_encounters


SIM_RUN_ID = "sim-run-discharge-score-test"


def _encounters(hospital_short: str, hours: int, seed: int = 42, start=None):
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


def _score(hospital_short: str, encounters, hours: int, seed: int = 42, start=None):
    preset = load_preset(hospital_short)
    start = start or datetime(2027, 1, 15, 8, 0)
    return list(
        generate_discharge_scores(
            preset=preset,
            encounter_events=encounters,
            sim_run_id=SIM_RUN_ID,
            seed=seed,
            start_time=start,
            duration_hours=hours,
        )
    )


def test_envelope_shape_conforms():
    encs = _encounters("LUKS", hours=12)
    events = _score("LUKS", encs, hours=12)
    assert events
    for e in events:
        assert set(e.keys()) == ENVELOPE_REQUIRED_KEYS
        assert e["eventKind"] == "discharge.scored"
        p = e["payload"]
        assert p["encounterId"].startswith("ENC-")
        assert 0.0 <= p["score"] <= 1.0


def test_score_bounded_and_monotonic_non_decreasing():
    encs = _encounters("LUKS", hours=6, start=datetime(2027, 1, 15, 8, 0))
    # Score over a much longer window so we can watch each encounter's score
    # walk from 0 towards 1.
    events = _score(
        "LUKS", encs, hours=24 * 10, start=datetime(2027, 1, 15, 8, 0)
    )
    by_enc: dict[str, list[float]] = {}
    for e in events:
        by_enc.setdefault(e["payload"]["encounterId"], []).append(e["payload"]["score"])

    assert by_enc
    for enc_id, scores in by_enc.items():
        assert scores, enc_id
        for a, b in zip(scores, scores[1:]):
            assert b >= a - 1e-9, f"{enc_id}: score decreased {a} -> {b}"
        assert scores[0] >= 0.0
        assert scores[-1] <= 1.0


def test_scores_only_between_admit_and_finish():
    start = datetime(2027, 1, 15, 8, 0)
    encs = _encounters("LUKS", hours=12, start=start)
    events = _score("LUKS", encs, hours=24 * 15, start=start)

    admitted_at = {
        e["payload"]["encounterId"]: e["simulatedAt"]
        for e in encs
        if e["eventKind"] == "encounter.admitted"
    }
    finished_at = {
        e["payload"]["encounterId"]: e["simulatedAt"]
        for e in encs
        if e["eventKind"] == "encounter.transitioned"
        and e["payload"]["status"] == "finished"
    }
    for e in events:
        enc_id = e["payload"]["encounterId"]
        assert e["simulatedAt"] >= admitted_at[enc_id]
        if enc_id in finished_at:
            assert e["simulatedAt"] < finished_at[enc_id]


def test_deterministic_by_seed():
    start = datetime(2027, 1, 15, 8, 0)
    encs_a = _encounters("SZB", hours=8, seed=17, start=start)
    encs_b = _encounters("SZB", hours=8, seed=17, start=start)
    a = _score("SZB", encs_a, hours=48, seed=17, start=start)
    b = _score("SZB", encs_b, hours=48, seed=17, start=start)
    key = lambda ev: (
        ev["simulatedAt"],
        ev["payload"]["encounterId"],
        ev["payload"]["score"],
    )
    assert [key(x) for x in a] == [key(x) for x in b]
