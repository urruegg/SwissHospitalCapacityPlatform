"""Integration test — Sprint 39 P2 POST /agents/{role}/decisions (Task A3).

A human accept applies the lever on the in-host SimState (the worklist shrinks
on a re-GET); a deny is a no-op; a missing X-User-Oid is refused 401
(NFR-UXL-001: only a human oid may act). Synthetic-only, no PHI (ADR-0016).
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from api.app import create_app, get_state

_OID = {"X-User-Oid": "11111111-1111-1111-1111-111111111111"}


def _client() -> TestClient:
    get_state.cache_clear()  # fresh host state (and fresh SimRegistry) per test
    return TestClient(create_app())


def test_accept_applies_and_worklist_shrinks_on_regen():
    client = _client()
    r0 = client.get("/agents/dca/worklist")
    assert r0.status_code == 200
    assert len(r0.json()["observations"]) == 3  # baseline: 3 open transport barriers

    ra = client.post(
        "/agents/dca/decisions",
        json={"decision": "accept", "hospital": "USZ", "params": {}},
        headers=_OID,
    )
    assert ra.status_code == 200
    out = ra.json()
    assert out["realised_impact"]["value"] >= 1
    assert out["applied"] is True

    # Same in-host SimState: the applied lever cleared the barriers, so the
    # worklist observations shrink on a re-GET (the outcome flows back).
    r1 = client.get("/agents/dca/worklist")
    assert r1.status_code == 200
    assert len(r1.json()["observations"]) == 0


def test_deny_is_a_noop_and_worklist_is_unchanged():
    client = _client()
    rd = client.post(
        "/agents/dca/decisions",
        json={"decision": "deny", "hospital": "USZ", "params": {}},
        headers={"X-User-Oid": "22222222-2222-2222-2222-222222222222"},
    )
    assert rd.status_code == 200
    out = rd.json()
    assert out["realised_impact"]["value"] == 0
    assert out["applied"] is False

    r1 = client.get("/agents/dca/worklist")
    assert len(r1.json()["observations"]) == 3  # unchanged


def test_missing_user_oid_is_refused_401():
    resp = _client().post(
        "/agents/dca/decisions",
        json={"decision": "accept", "hospital": "USZ", "params": {}},
    )
    assert resp.status_code == 401
