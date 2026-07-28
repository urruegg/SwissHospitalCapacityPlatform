"""Integration test — #424 M4 live-verifiable RLS over the golden read surface.

M4 makes row-level security observable now (not just at M5) by routing the
golden read through the ``RlsProvider`` seam and adding a server-only,
multi-site ``network`` resource whose rows carry ``hospital`` tags. The
in-process provider filters per the caller's proven ``hospitalScope``:
aggregated => all sites; a single site => that site's rows + untagged rows;
no scope => deny-by-default (401). Every response carries an ``_rls`` block and
``X-Rls-*`` headers describing the enforcement point. Synthetic-only, no PHI.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.app import create_app, get_state

_AGG = {
    "X-User-Oid": "11111111-1111-1111-1111-111111111111",
    "X-Hospital-Scope": "aggregated",
    "X-Active-Role": "HCC.Viewer",
}
_USZ = {
    "X-User-Oid": "22222222-2222-2222-2222-222222222222",
    "X-Hospital-Scope": "hospital-usz",
    "X-Active-Role": "HCC.Viewer",
}


def _client() -> TestClient:
    get_state.cache_clear()
    return TestClient(create_app())


def test_network_aggregated_returns_all_sites():
    resp = _client().get("/golden/network", headers=_AGG)
    assert resp.status_code == 200
    body = resp.json()
    assert {s["id"] for s in body["sites"]} == {"usz", "ksa", "bern"}
    # transfers: 2 site-tagged + 1 untagged all visible under aggregated.
    assert {t["id"] for t in body["transfers"]} == {"t1", "t2", "t3"}


def test_network_site_scope_filters_to_that_site_plus_untagged():
    resp = _client().get("/golden/network", headers=_USZ)
    assert resp.status_code == 200
    body = resp.json()
    # Only the USZ site row survives.
    assert {s["id"] for s in body["sites"]} == {"usz"}
    # USZ-tagged transfer + the untagged (site-agnostic) transfer survive; the
    # KSA-tagged transfer is filtered out.
    assert {t["id"] for t in body["transfers"]} == {"t1", "t3"}


def test_network_deny_by_default_without_scope():
    resp = _client().get("/golden/network")
    assert resp.status_code == 401


def test_network_rls_metadata_present():
    resp = _client().get("/golden/network", headers=_AGG)
    assert resp.status_code == 200
    rls = resp.json()["_rls"]
    assert rls == {"scope": "aggregated", "provider": "simulated", "provenance": "simulated"}
    assert resp.headers.get("x-rls-provider") == "simulated"
    assert resp.headers.get("x-rls-provenance") == "simulated"
    assert resp.headers.get("x-applied-scope") == "aggregated"
    # The HTTP read itself is live (M2 semantic), distinct from the RLS mode.
    assert resp.headers.get("x-data-provenance") == "live"


def test_existing_boards_still_ok_and_carry_rls_block():
    client = _client()
    for resource in ("occupancy", "discharge", "bed-manager", "or-steering", "staffing", "crisis"):
        resp = client.get(f"/golden/{resource}", headers=_AGG)
        assert resp.status_code == 200, resource
        assert resp.json()["_rls"]["provider"] == "simulated", resource


def test_unknown_resource_still_404():
    resp = _client().get("/golden/not-a-board", headers=_AGG)
    assert resp.status_code == 404
