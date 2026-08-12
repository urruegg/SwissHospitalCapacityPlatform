"""Unit tests — #424 M2 golden-source read service.

The agent-host exposes a real, RLS-scoped golden-data read surface backed by the
synthetic gold fixtures (single source of truth: the hcc-app-fluent RoleBoard
fixtures, exported to ``src/golden/data/*.json``). Deny-by-default: a read with no
proven hospital scope returns nothing. Synthetic-only, no PHI (ADR-0016).
"""

from __future__ import annotations

import json

import pytest

from golden.service import (
    GOLDEN_RESOURCES,
    GoldenScopeError,
    UnknownResourceError,
    load_golden,
)
from golden.signals_source import SnapshotSource


def test_all_six_boards_resolve_full_payloads():
    for resource in GOLDEN_RESOURCES:
        payload = load_golden(resource, hospital_scope="aggregated", user_oid="u-1")
        assert isinstance(payload, dict)
        assert payload, f"{resource} payload is empty"


def test_occupancy_payload_matches_fixture_shape():
    payload = load_golden("occupancy", hospital_scope="aggregated", user_oid="u-1")
    assert payload["siteOccupancyPct"] == 81
    assert len(payload["wards"]) == 4
    assert payload["wards"][0]["label"] == "Medicine A"
    assert payload["wards"][0]["forecastPct"] == 102


def test_deny_by_default_without_scope():
    # No proven hospital scope -> refuse (do not leak a wider scope than proven).
    with pytest.raises(GoldenScopeError):
        load_golden("occupancy", hospital_scope="", user_oid="u-1")


def test_deny_by_default_without_user_oid():
    with pytest.raises(GoldenScopeError):
        load_golden("occupancy", hospital_scope="aggregated", user_oid="")


def _live_snapshot_bytes() -> bytes:
    return json.dumps({
        "ext_fact_signal": [{
            "ext_signal_id": "webiq-0", "ext_source_id": "webiq",
            "ext_hazard_type": "epidemic", "ext_severity": "Moderate",
            "ext_status": "Actual", "ext_cantons": ["ZH"],
        }],
        "ext_dim_source": [{
            "ext_source_id": "webiq", "ext_source_authority": "Microsoft Web IQ",
            "ext_trust_tier": "B", "ext_data_mode": "Live",
        }],
    }).encode("utf-8")


def test_occupancy_carries_live_signals_when_snapshot_available():
    src = SnapshotSource(fetcher=_live_snapshot_bytes)
    payload = load_golden("occupancy", hospital_scope="aggregated", user_oid="u-1", signals_source=src)
    assert payload["signals"][0]["id"] == "webiq-0"
    assert payload["signals"][0]["provenance"] == "live"
    assert payload["signals"][0]["trustClass"] == "Trust-B"


def test_occupancy_unchanged_when_snapshot_unreadable():
    # Malformed snapshot => source yields None => no signals key (app uses built-ins).
    src = SnapshotSource(fetcher=lambda: b"not json")
    payload = load_golden("occupancy", hospital_scope="aggregated", user_oid="u-1", signals_source=src)
    assert "signals" not in payload


def test_non_occupancy_boards_never_get_live_signals_injected():
    src = SnapshotSource(fetcher=_live_snapshot_bytes)
    payload = load_golden("discharge", hospital_scope="aggregated", user_oid="u-1", signals_source=src)
    # discharge fixture has no external-signals surface; the merge is occupancy-only.
    assert payload.get("signals") != [{"id": "webiq-0"}]  # not injected


def test_unknown_resource_raises():
    with pytest.raises(UnknownResourceError):
        load_golden("not-a-board", hospital_scope="aggregated", user_oid="u-1")


def test_site_scoped_rows_are_filtered():
    # Rows carrying a `hospital` tag are filtered to the caller's scope; rows
    # without the tag (site-agnostic demo fixtures) pass through. `aggregated`
    # returns everything.
    rows = [
        {"id": "a", "hospital": "usz", "v": 1},
        {"id": "b", "hospital": "ksw", "v": 2},
        {"id": "c", "v": 3},
    ]
    from golden.service import apply_row_scope

    assert [r["id"] for r in apply_row_scope(rows, "aggregated")] == ["a", "b", "c"]
    assert [r["id"] for r in apply_row_scope(rows, "usz")] == ["a", "c"]
    assert [r["id"] for r in apply_row_scope(rows, "ksw")] == ["b", "c"]
