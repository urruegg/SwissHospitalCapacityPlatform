"""Sprint 44 live path (Slice 3) — SnapshotSource reader unit tests (offline)."""

from __future__ import annotations

import json

import pytest

from golden.signals_source import SnapshotSource


def _snapshot_bytes() -> bytes:
    return json.dumps({
        "ext_fact_signal": [{
            "ext_signal_id": "webiq-0", "ext_source_id": "webiq",
            "ext_hazard_type": "epidemic", "ext_severity": "Moderate",
            "ext_cantons": ["ZH"], "ext_status": "Actual",
            "ext_web_citations": [{"title": "t", "uri": "https://x"}],
        }],
        "ext_dim_source": [{
            "ext_source_id": "webiq", "ext_source_authority": "Microsoft Web IQ",
            "ext_trust_tier": "B", "ext_data_mode": "Live",
        }],
    }).encode("utf-8")


def test_disabled_without_fetcher_or_env(monkeypatch):
    monkeypatch.delenv("SIGNALS_SNAPSHOT_URL", raising=False)
    assert SnapshotSource().external_signals() is None


def test_maps_snapshot_to_board_signals():
    sigs = SnapshotSource(fetcher=_snapshot_bytes).external_signals()
    assert len(sigs) == 1
    assert sigs[0]["id"] == "webiq-0"
    assert sigs[0]["scope"] == "external"
    assert sigs[0]["provenance"] == "live"
    assert sigs[0]["trustClass"] == "Trust-B"
    assert sigs[0]["webCitations"][0]["uri"] == "https://x"


def test_malformed_blob_returns_none():
    assert SnapshotSource(fetcher=lambda: b"not json").external_signals() is None


def test_empty_snapshot_yields_empty_list():
    empty = json.dumps({"ext_fact_signal": [], "ext_dim_source": []}).encode("utf-8")
    assert SnapshotSource(fetcher=lambda: empty).external_signals() == []


def test_ttl_caches_then_refetches():
    calls = {"n": 0}

    def fetch() -> bytes:
        calls["n"] += 1
        return _snapshot_bytes()

    clock = {"t": 0.0}
    src = SnapshotSource(fetcher=fetch, ttl_seconds=10.0, clock=lambda: clock["t"])
    src.external_signals()
    src.external_signals()
    assert calls["n"] == 1  # served from cache within TTL
    clock["t"] = 20.0
    src.external_signals()
    assert calls["n"] == 2  # TTL expired -> refetched
