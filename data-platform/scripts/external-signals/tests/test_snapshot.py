"""Sprint 44 live path (Slice 2) — gold-shaped signals snapshot (pure, offline).

Mirrors the gold projection so the runner can write a Blob snapshot the agent-host
golden surface consumes without an OneLake external read. Includes a drift guard
asserting the 9 canonical gold columns match build_gold_signals.to_gold_signal.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/external-signals

from snapshot import build_snapshot  # noqa: E402


def _rec(**over):
    base = {
        "signalId": "webiq-0-https://x", "sourceId": "webiq",
        "sourceAuthority": "Microsoft Web IQ", "trustTier": "B",
        "hazardType": "epidemic", "severity": "Moderate",
        "mappedScenarioTemplate": "F6", "defaultLageTier": 2,
        "onset": "2026-08-12T06:00:00Z", "status": "Actual",
        "region": {"cantons": ["ZH"]},
        "provenance": {"activeBinding": "live", "fellBackFrom": None,
                       "ingestedAt": "2026-08-12T06:05:00Z"},
        "webCitations": [{"title": "t", "uri": "https://x",
                          "publishedAt": "2026-08-12T06:00:00Z", "snippet": "s"}],
    }
    base.update(over)
    return base


def test_build_snapshot_shapes_fact_and_source():
    snap = build_snapshot([_rec()], generated_at="2026-08-12T06:06:00Z")
    assert snap["generatedAt"] == "2026-08-12T06:06:00Z"
    fact = snap["ext_fact_signal"][0]
    assert fact["ext_signal_id"] == "webiq-0-https://x"
    assert fact["ext_source_id"] == "webiq"
    assert fact["ext_cantons"] == ["ZH"]
    assert fact["ext_web_citations"][0]["uri"] == "https://x"
    src = snap["ext_dim_source"][0]
    assert src["ext_source_authority"] == "Microsoft Web IQ"
    assert src["ext_trust_tier"] == "B"
    assert src["ext_data_mode"] == "Live"


def test_source_dedup_latest_wins():
    old = _rec(provenance={"activeBinding": "simulated", "ingestedAt": "2026-08-12T05:00:00Z"})
    new = _rec(provenance={"activeBinding": "live", "ingestedAt": "2026-08-12T06:00:00Z"})
    snap = build_snapshot([old, new])
    assert len(snap["ext_dim_source"]) == 1
    assert snap["ext_dim_source"][0]["ext_data_mode"] == "Live"  # latest ingest wins


def test_empty_records_yield_empty_tables():
    snap = build_snapshot([])
    assert snap["ext_fact_signal"] == []
    assert snap["ext_dim_source"] == []


def test_fact_matches_canonical_gold_projection():
    """Drift guard: the 9 canonical gold columns match to_gold_signal exactly."""
    nb = Path(__file__).resolve().parents[3] / "notebooks" / "external-signals" / "build_gold_signals.py"
    spec = importlib.util.spec_from_file_location("build_gold_signals", nb)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rec = _rec()
    snap_fact = build_snapshot([rec])["ext_fact_signal"][0]
    canonical = mod.to_gold_signal(rec)
    assert {k: v for k, v in snap_fact.items() if k != "ext_web_citations"} == canonical
