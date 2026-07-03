"""Tests for the discharge recommender generator (T3.4f)."""
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
from generators.discharge_recommender import generate_discharge_recommendations
from generators.discharge_scorer import generate_discharge_scores
from generators.encounter_generator import generate_encounters


SIM_RUN_ID = "sim-run-discharge-rec-test"
ALL_ACTIONS = {
    "discharge-today",
    "discharge-tomorrow",
    "discharge-blocked",
    "escalate",
    "no-action",
}


def _pipeline(hospital_short: str, adm_hours: int, score_hours: int, seed: int = 42):
    start = datetime(2027, 1, 15, 8, 0)
    preset = load_preset(hospital_short)
    profile = SeasonalProfile.from_preset(preset, seed=seed)
    sampler = build_acuity_sampler(hospital_short, seed=seed)

    encs = list(
        generate_encounters(
            preset=preset,
            profile=profile,
            sampler=sampler,
            sim_run_id=SIM_RUN_ID,
            seed=seed,
            start_time=start,
            duration_hours=adm_hours,
        )
    )
    scored = list(
        generate_discharge_scores(
            preset=preset,
            encounter_events=encs,
            sim_run_id=SIM_RUN_ID,
            seed=seed,
            start_time=start,
            duration_hours=score_hours,
        )
    )
    recs = list(
        generate_discharge_recommendations(
            preset=preset,
            scored_events=scored,
            sim_run_id=SIM_RUN_ID,
            seed=seed,
            top_k_per_hour=5,
        )
    )
    return encs, scored, recs


def test_envelope_shape_conforms():
    _, _, recs = _pipeline("LUKS", adm_hours=6, score_hours=24 * 8)
    assert recs
    for e in recs:
        assert set(e.keys()) == ENVELOPE_REQUIRED_KEYS
        assert e["eventKind"] == "discharge.recommended"
        p = e["payload"]
        assert p["recommendedAction"] in ALL_ACTIONS
        assert isinstance(p["blockers"], list)
        assert p["rank"] >= 1


def test_top_k_correctness_per_hour():
    _, scored, recs = _pipeline("LUKS", adm_hours=6, score_hours=24 * 8)
    from collections import defaultdict
    top_k = 5

    scored_by_hour: dict[str, list[dict]] = defaultdict(list)
    for e in scored:
        scored_by_hour[e["simulatedAt"][:13]].append(e)

    recs_by_hour: dict[str, list[dict]] = defaultdict(list)
    for e in recs:
        recs_by_hour[e["simulatedAt"][:13]].append(e)

    for hour, evs in recs_by_hour.items():
        assert len(evs) <= top_k, f"hour {hour} produced {len(evs)} recs (>{top_k})"
        # Ranks are 1..K, dense
        ranks = sorted(ev["payload"]["rank"] for ev in evs)
        assert ranks == list(range(1, len(evs) + 1)), f"hour {hour} ranks {ranks}"

        # The recommended encounter set must be the top-K by score from the
        # scored bucket (tie-broken by encounterId).
        pool = scored_by_hour[hour]
        expected_top = sorted(
            pool, key=lambda ev: (-ev["payload"]["score"], ev["payload"]["encounterId"])
        )[:top_k]
        expected_enc_ids = [ev["payload"]["encounterId"] for ev in expected_top]
        actual_enc_ids = sorted(
            (ev["payload"]["rank"], ev["payload"]["encounterId"]) for ev in evs
        )
        actual_ordered = [enc_id for _, enc_id in actual_enc_ids]
        assert actual_ordered == expected_enc_ids


def test_blocked_recommendations_have_blockers():
    _, _, recs = _pipeline("LUKS", adm_hours=8, score_hours=24 * 12)
    blocked = [e for e in recs if e["payload"]["recommendedAction"] == "discharge-blocked"]
    # Might be zero in a very small run, but with 8 hours of admits & 12 days
    # scoring window we expect at least one blocked case.
    assert blocked, "no blocked recommendations produced — check score distribution"
    for e in blocked:
        assert e["payload"]["blockers"], f"blocked rec {e['payload']['recommendationId']} has empty blockers"


def test_deterministic_by_seed():
    _, _, a = _pipeline("SZB", adm_hours=6, score_hours=24 * 6, seed=3)
    _, _, b = _pipeline("SZB", adm_hours=6, score_hours=24 * 6, seed=3)
    key = lambda ev: (
        ev["simulatedAt"],
        ev["payload"]["encounterId"],
        ev["payload"]["rank"],
        ev["payload"]["recommendedAction"],
        tuple(ev["payload"]["blockers"]),
    )
    assert [key(x) for x in a] == [key(x) for x in b]


def test_ignores_non_scored_events():
    encs, _, _ = _pipeline("LUKS", adm_hours=4, score_hours=1)
    preset = load_preset("LUKS")
    recs = list(
        generate_discharge_recommendations(
            preset=preset,
            scored_events=encs,  # wrong event kind
            sim_run_id=SIM_RUN_ID,
            seed=42,
        )
    )
    assert recs == []
