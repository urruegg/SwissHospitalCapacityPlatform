"""WS-C Class C cost: reconcile-to-BVA tests.

TDD step 1 (RED): a mocked cost run-rate for a bounded feed window must
reconcile to a GroundedChunk that

* presents the answer as a **range** within the BVA +/- 30% band,
* carries an **as-of** stamp, and
* **refuses to extrapolate** beyond the feed window.
"""

from pathlib import Path

import reconcile_bva
from reconcile_bva import CostObservation

REPO_ROOT = Path(__file__).resolve().parents[5]


def _monthly_observation(amount):
    # ~1/12 of the 1,250,000 CHF/yr BVA run-rate over a 30-day window.
    return CostObservation(
        amount=amount,
        currency="CHF",
        window_start="2026-07-01",
        window_end="2026-07-31",
        feed="Azure Cost Management + GitHub Copilot usage",
        as_of="2026-07-31",
    )


def test_cost_answer_is_a_range_within_bva_band_with_as_of():
    obs = _monthly_observation(102_000.0)  # ~ on-baseline monthly run-rate
    chunk = reconcile_bva.reconcile_bva(obs, repo_root=REPO_ROOT)

    assert chunk["classId"] == "C"
    # Presented as a range: a low and a high figure both appear.
    lo, hi = reconcile_bva.rom_range(102_000.0)
    assert f"{lo:,.0f}" in chunk["text"]
    assert f"{hi:,.0f}" in chunk["text"]
    # As-of stamp present in both the text and the structured field.
    assert "2026-07-31" in chunk["text"]
    assert chunk["asOf"].startswith("2026-07-31")
    # On-baseline monthly run-rate reconciles within the BVA band.
    assert chunk["status"] == "verified"
    assert chunk["liveness"] == "live"


def test_extrapolation_beyond_feed_window_is_refused():
    obs = _monthly_observation(102_000.0)
    # Ask for a full-year horizon from a single-month feed -> must refuse.
    chunk = reconcile_bva.reconcile_bva(
        obs, repo_root=REPO_ROOT, requested_horizon_end="2027-06-30"
    )
    assert chunk["classId"] == "C"
    assert chunk["status"] == "partial"
    assert "extrapolat" in chunk["text"].lower()
    assert "feed window" in chunk["text"].lower()
