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


def test_bot_approver_is_refused_403():
    # NFR-UXL-001 at the HTTP boundary: a bot oid reaches approve_action, which
    # raises PermissionError -> the route maps it to 403 (no state mutation).
    resp = _client().post(
        "/agents/dca/decisions",
        json={"decision": "accept", "hospital": "USZ", "params": {}},
        headers={"X-User-Oid": "github-actions[bot]"},
    )
    assert resp.status_code == 403


def test_unknown_ward_is_refused_400():
    # An authenticated but unvalidated params.ward must be a 400, not a 500.
    resp = _client().post(
        "/agents/dca/decisions",
        json={"decision": "accept", "hospital": "USZ", "params": {"ward": "NOPE"}},
        headers=_OID,
    )
    assert resp.status_code == 400


def test_decision_approver_comes_from_obo_oid_not_header(monkeypatch):
    import api.app as app_module

    class _Ctx:
        user_oid = "obo-approver-oid"
        obo_token = ""
        roles = ("HCC.DischargeCoordinator",)
        hospital = "aggregated"

    # monkeypatch (not importlib.reload) — reload mutates api.app's shared
    # __globals__ in place, which other already-imported test modules' route
    # closures resolve `get_state` against at call time, corrupting their state.
    monkeypatch.setattr(app_module, "build_obo_context", lambda _a: _Ctx())
    client = _client()
    resp = client.post(
        "/agents/dca/decisions",
        json={"decision": "deny", "hospital": "USZ", "params": {}},
        headers={"Authorization": "Bearer ok", "X-User-Oid": "header-oid-should-be-ignored"},
    )
    assert resp.status_code == 200
    assert resp.json()["approver"] == "obo-approver-oid"


def test_decision_outcome_is_persisted_to_approval_events():
    client = _client()
    resp = client.post(
        "/agents/dca/decisions",
        json={"decision": "deny", "hospital": "USZ", "params": {}},
        headers=_OID,
    )
    assert resp.status_code == 200
    state = get_state()
    records = state.persistence.query_by_correlation("approval-events", resp.json()["golden_thread"])
    assert len(records) == 1
    assert records[0]["decision"] == "deny"


def test_ooa_decision_outcome_is_persisted_to_approval_events():
    # Task 6/Task 7 composition (final holistic review follow-up): the same
    # generic approval-events write must also cover a role whose lever is
    # tracked-but-not-applied (ooa), not just dca's real-mutation path.
    client = _client()
    resp = client.post(
        "/agents/ooa/decisions",
        json={"decision": "accept", "hospital": "USZ", "params": {}},
        headers=_OID,
    )
    assert resp.status_code == 200
    out = resp.json()
    assert out["applied"] is False
    assert out["lever_id"] == "OOA-EXPEDITE-DISCHARGE"
    state = get_state()
    records = state.persistence.query_by_correlation("approval-events", out["golden_thread"])
    assert len(records) == 1
    assert records[0]["decision"] == "accept"
    assert records[0]["applied"] is False


def test_orsa_decision_does_not_mutate_dca_worklist():
    # CRITICAL fix regression at the HTTP boundary: an orsa accept must never
    # execute DCA's barrier-clearing mutation on the shared in-host SimState.
    client = _client()
    r0 = client.get("/agents/dca/worklist")
    assert len(r0.json()["observations"]) == 3  # baseline: 3 open transport barriers

    resp = client.post(
        "/agents/orsa/decisions",
        json={"decision": "accept", "hospital": "USZ", "params": {}},
        headers=_OID,
    )
    assert resp.status_code == 200
    out = resp.json()
    assert out["applied"] is False
    assert out["lever_id"] is None
    assert out["applyReason"] == "no_lever_for_role"

    r1 = client.get("/agents/dca/worklist")
    assert len(r1.json()["observations"]) == 3  # unchanged -- no barrier was cleared


def test_decision_outcome_survives_persistence_write_failure(monkeypatch):
    # Best-effort audit durability: a Cosmos write hiccup must never mask an
    # already-applied decision as a client-visible error (Task 7 review follow-up).
    client = _client()
    state = get_state()

    def _raise(*_args, **_kwargs):
        raise RuntimeError("simulated Cosmos write failure")

    monkeypatch.setattr(state.persistence, "write", _raise)

    resp = client.post(
        "/agents/dca/decisions",
        json={"decision": "accept", "hospital": "USZ", "params": {}},
        headers=_OID,
    )
    assert resp.status_code == 200
    out = resp.json()
    assert out["decision"] == "accept"
    assert out["applied"] is True

