"""Integration test — #424 M2 golden-source HTTP surface of the agent-host.

``GET /golden/{resource}`` is the live golden-data read path consumed by the
hcc-app-fluent RoleBoard loaders when the Live/Simulated toggle is `live`. It
requires the OBO/RLS scope headers the app attaches (``X-User-Oid`` /
``X-Hospital-Scope`` / ``X-Active-Role``) and refuses deny-by-default when they
are absent. Synthetic-only, no PHI (ADR-0016).
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.app import create_app, get_state

_SCOPE_HEADERS = {
    "X-User-Oid": "11111111-1111-1111-1111-111111111111",
    "X-Hospital-Scope": "aggregated",
    "X-Active-Role": "HCC.Viewer",
}


def _client() -> TestClient:
    get_state.cache_clear()
    return TestClient(create_app())


def test_golden_occupancy_returns_full_payload():
    resp = _client().get("/golden/occupancy?hospital=aggregated&window=72", headers=_SCOPE_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["siteOccupancyPct"] == 81
    assert len(body["wards"]) == 4
    assert resp.headers.get("x-data-provenance") == "live"
    assert resp.headers.get("x-applied-scope") == "aggregated"


def test_golden_all_boards_ok():
    client = _client()
    for resource in ("occupancy", "discharge", "bed-manager", "or-steering", "staffing", "crisis"):
        resp = client.get(f"/golden/{resource}?hospital=aggregated&window=72", headers=_SCOPE_HEADERS)
        assert resp.status_code == 200, resource
        assert resp.json(), resource


def test_golden_refuses_without_scope_headers():
    # Deny-by-default: ungrounded read (no scope headers) is refused.
    resp = _client().get("/golden/occupancy?hospital=aggregated&window=72")
    assert resp.status_code == 401


def test_golden_refuses_without_user_oid():
    headers = {"X-Hospital-Scope": "aggregated", "X-Active-Role": "HCC.Viewer"}
    resp = _client().get("/golden/occupancy?hospital=aggregated&window=72", headers=headers)
    assert resp.status_code == 401


def test_golden_unknown_resource_404():
    resp = _client().get("/golden/not-a-board?hospital=aggregated&window=72", headers=_SCOPE_HEADERS)
    assert resp.status_code == 404


def test_golden_cors_preflight_allows_scope_headers():
    resp = _client().options(
        "/golden/occupancy",
        headers={
            "Origin": "https://appsit.curavias.ch",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "x-user-oid,x-hospital-scope,x-active-role",
        },
    )
    assert resp.status_code in (200, 204)
    assert resp.headers.get("access-control-allow-origin") == "https://appsit.curavias.ch"
    allowed = (resp.headers.get("access-control-allow-headers") or "").lower()
    assert "x-hospital-scope" in allowed
