"""ADR-0016 Gate 1 — simulator produces no PHI-shaped tokens (T3.6).

Runs every generator (encounter, bed_state, matching, forecast, discharge_scorer,
discharge_recommender) against every hospital preset (USZ, LUKS, SZB) and sweeps
the emitted envelopes with the same PHI regex bundle used by the Silver-layer
ingestion gate in ``data-platform/notebooks/reference/02_silver_master_data.ipynb``.

Any hit fails the run. The test also asserts an aggregate floor of 10 000
envelopes swept so nobody can silently shrink coverage.

Structural envelope/ID fields are exempt from the scan — they carry ISO
timestamps and opaque IDs whose shape overlaps the PHI regexes by construction.
This mirrors the Silver notebook's ``STRUCTURAL_STRING_ALLOWLIST`` discipline;
the extra IDs listed below are the sim-capacity-specific counterparts.
"""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, List, Tuple

import pytest

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from calibration.acuity_distribution import build_acuity_sampler  # noqa: E402
from calibration.hospital_presets import load_preset  # noqa: E402
from calibration.seasonal_profile import SeasonalProfile  # noqa: E402
from generators.bed_state_generator import generate_bed_states  # noqa: E402
from generators.discharge_recommender import (  # noqa: E402
    generate_discharge_recommendations,
)
from generators.discharge_scorer import generate_discharge_scores  # noqa: E402
from generators.encounter_generator import generate_encounters  # noqa: E402
from generators.forecast_generator import generate_forecasts  # noqa: E402
from generators.matching_engine import generate_bed_assignments  # noqa: E402

SIM_RUN_ID = "sim-run-no-phi-test"
START = datetime(2027, 1, 15, 8, 0)
SEED = 42
HOSPITALS = ("USZ", "LUKS", "SZB")

# ---------------------------------------------------------------------------
# PHI regex bundle — mirrors data-platform/notebooks/reference/
# 02_silver_master_data.ipynb (ADR-0016 Gate 2).
# ---------------------------------------------------------------------------
PHI_PATTERNS = {
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "phone": re.compile(r"\+?\d[\d\s().-]{6,}"),
    "dob": re.compile(r"\d{4}-\d{2}-\d{2}"),
    "ch_ahv_13": re.compile(r"756\.\d{4}\.\d{4}\.\d{2}"),
}

# Structural fields exempt from the scan. Two classes:
#   1. Timestamps: shaped like DOB by design (RFC 3339).
#   2. Opaque identifiers: shaped like phone numbers due to embedded numeric
#      spans (e.g. ENC-USZ-2027-000001). None of these carry PHI.
# Extending this set requires justifying that the field is a system-generated
# structural token, not free text.
STRUCTURAL_STRING_ALLOWLIST = {
    # Envelope timestamps (Silver notebook parity).
    "simulatedAt",
    "emittedAt",
    "asOfTimestamp",
    # Envelope identifiers (Silver notebook parity).
    "eventId",
    "simRunId",
    # Additional payload timestamps present in sim-capacity events.
    "expectedArrivalTimestamp",
    "expectedDischargeTimestamp",
    "validFrom",
    "validUntil",
    "assignedAt",
    "unassignedAt",
    "assessedAt",
    "producedAt",
    "bucketStart",
    # Structural payload identifiers (sim-capacity-specific).
    "hospitalId",
    "encounterId",
    "pseudonymId",
    "bedId",
    "wardId",
    "specialtyId",
    "unitType",
    "diseaseId",
    "drgCode",
    "requestedSpecialtyServiceId",
    "requestedSpecialtyId",
    "assignmentId",
    "scoreId",
    "basedOnScoreId",
    "recommendationId",
    "forecastId",
    "producedByModelRunId",
}


def _scan_for_phi(node: Any, path: str = "") -> List[Tuple[str, str, str]]:
    """Recursively scan ``node``; return list of (path, pattern_name, value)."""
    hits: List[Tuple[str, str, str]] = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k in STRUCTURAL_STRING_ALLOWLIST or k.startswith("_"):
                continue
            hits.extend(_scan_for_phi(v, f"{path}.{k}" if path else k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            hits.extend(_scan_for_phi(v, f"{path}[{i}]"))
    elif isinstance(node, str):
        for pname, patt in PHI_PATTERNS.items():
            if patt.search(node):
                hits.append((path, pname, node))
    return hits


# ---------------------------------------------------------------------------
# Fixtures — build per-hospital encounter streams once and reuse.
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def encounter_streams() -> dict:
    """Encounter events per hospital, reused by matching / scoring / recommender."""
    streams: dict = {}
    for h in HOSPITALS:
        preset = load_preset(h)
        profile = SeasonalProfile.from_preset(preset, seed=SEED)
        sampler = build_acuity_sampler(h, seed=SEED)
        streams[h] = list(
            generate_encounters(
                preset=preset,
                profile=profile,
                sampler=sampler,
                sim_run_id=SIM_RUN_ID,
                seed=SEED,
                start_time=START,
                duration_hours=48,
            )
        )
    return streams


@pytest.fixture(scope="module")
def scored_streams(encounter_streams: dict) -> dict:
    """Discharge scores per hospital, reused by the recommender test."""
    streams: dict = {}
    for h in HOSPITALS:
        preset = load_preset(h)
        streams[h] = list(
            generate_discharge_scores(
                preset=preset,
                encounter_events=encounter_streams[h],
                sim_run_id=SIM_RUN_ID,
                seed=SEED,
                start_time=START,
                duration_hours=72,
            )
        )
    return streams


# Shared counter so we can assert the aggregate floor.
_TOTAL_SWEPT: dict = {"count": 0}


def _assert_no_phi(events: Iterable[dict], label: str) -> int:
    n = 0
    for env in events:
        n += 1
        hits = _scan_for_phi(env)
        assert hits == [], f"{label}: PHI hit(s) {hits[:3]}"
    _TOTAL_SWEPT["count"] += n
    return n


# ---------------------------------------------------------------------------
# Per-generator × per-hospital tests (18 combinations).
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("hospital", HOSPITALS)
def test_encounter_generator_no_phi(hospital: str, encounter_streams: dict) -> None:
    n = _assert_no_phi(encounter_streams[hospital], f"encounter/{hospital}")
    assert n > 0, f"encounter/{hospital}: no events produced"


@pytest.mark.parametrize("hospital", HOSPITALS)
def test_bed_state_generator_no_phi(hospital: str) -> None:
    preset = load_preset(hospital)
    events = generate_bed_states(
        preset=preset,
        sim_run_id=SIM_RUN_ID,
        seed=SEED,
        start_time=START,
        duration_hours=24,
    )
    n = _assert_no_phi(events, f"bed_state/{hospital}")
    assert n > 0, f"bed_state/{hospital}: no events produced"


@pytest.mark.parametrize("hospital", HOSPITALS)
def test_matching_engine_no_phi(hospital: str, encounter_streams: dict) -> None:
    preset = load_preset(hospital)
    events = generate_bed_assignments(
        preset=preset,
        encounter_events=encounter_streams[hospital],
        sim_run_id=SIM_RUN_ID,
        seed=SEED,
    )
    n = _assert_no_phi(events, f"matching/{hospital}")
    assert n > 0, f"matching/{hospital}: no events produced"


@pytest.mark.parametrize("hospital", HOSPITALS)
def test_forecast_generator_no_phi(hospital: str) -> None:
    preset = load_preset(hospital)
    profile = SeasonalProfile.from_preset(preset, seed=SEED)
    events = generate_forecasts(
        preset=preset,
        profile=profile,
        sim_run_id=SIM_RUN_ID,
        seed=SEED,
        start_time=START,
        duration_hours=3,
    )
    n = _assert_no_phi(events, f"forecast/{hospital}")
    assert n > 0, f"forecast/{hospital}: no events produced"


@pytest.mark.parametrize("hospital", HOSPITALS)
def test_discharge_scorer_no_phi(hospital: str, scored_streams: dict) -> None:
    n = _assert_no_phi(scored_streams[hospital], f"discharge_scorer/{hospital}")
    assert n > 0, f"discharge_scorer/{hospital}: no events produced"


@pytest.mark.parametrize("hospital", HOSPITALS)
def test_discharge_recommender_no_phi(
    hospital: str, scored_streams: dict
) -> None:
    preset = load_preset(hospital)
    events = generate_discharge_recommendations(
        preset=preset,
        scored_events=scored_streams[hospital],
        sim_run_id=SIM_RUN_ID,
        seed=SEED,
        top_k_per_hour=10,
    )
    n = _assert_no_phi(events, f"discharge_recommender/{hospital}")
    assert n > 0, f"discharge_recommender/{hospital}: no events produced"


# ---------------------------------------------------------------------------
# Sanity check on the regex bundle itself — proves the scan would fire on
# real PHI shapes if any were present.
# ---------------------------------------------------------------------------
def test_phi_scan_detects_known_positive_samples() -> None:
    positives = {
        "email": {"payload": {"note": "contact patient at jane.doe@example.com"}},
        "phone": {"payload": {"note": "call +41 44 123 45 67"}},
        "dob": {"payload": {"note": "born 1974-03-21"}},
        "ch_ahv_13": {"payload": {"note": "AHV 756.1234.5678.90"}},
    }
    for name, sample in positives.items():
        hits = _scan_for_phi(sample)
        assert hits, f"regex bundle failed to catch {name}: {sample}"


def test_total_events_swept_meets_coverage_floor() -> None:
    """Guard against silent test-shrinking. Must run after the 18 param tests."""
    assert _TOTAL_SWEPT["count"] >= 10_000, (
        f"only {_TOTAL_SWEPT['count']} envelopes swept (floor: 10 000); "
        "raise generator durations or lower the floor with justification"
    )
