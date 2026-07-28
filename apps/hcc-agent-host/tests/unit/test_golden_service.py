"""Unit tests — #424 M2 golden-source read service.

The agent-host exposes a real, RLS-scoped golden-data read surface backed by the
synthetic gold fixtures (single source of truth: the hcc-app-fluent RoleBoard
fixtures, exported to ``src/golden/data/*.json``). Deny-by-default: a read with no
proven hospital scope returns nothing. Synthetic-only, no PHI (ADR-0016).
"""

from __future__ import annotations

import pytest

from golden.service import (
    GOLDEN_RESOURCES,
    GoldenScopeError,
    UnknownResourceError,
    load_golden,
)


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
