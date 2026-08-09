"""Integration test — Sprint 39 P2 GET /agents/{role}/worklist (Task A2).

The host seeds the in-host SimState from the committed Plan 1 USZ gold fixture
(the simulated-MVP default of load_gold_snapshot, so no stub is needed) and
returns the role's live observations + a grounded DC-INSIGHT-style recommendation.
Synthetic-only, no PHI (ADR-0016).
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from api.app import create_app, get_state


def _client() -> TestClient:
    get_state.cache_clear()  # fresh host state (and fresh SimRegistry) per test
    return TestClient(create_app())


def test_dca_worklist_endpoint_returns_observations_and_reco():
    resp = _client().get("/agents/dca/worklist")
    assert resp.status_code == 200
    body = resp.json()
    assert body["role"] == "dca"
    assert len(body["observations"]) == 3  # 3 open transport barriers in the fixture
    assert body["recommendation"]["lever_id"] == "DCA-UNBLOCK-BARRIER"
    assert body["recommendation"]["predicted_impact"]["value"] >= 1
    # The fixture is provenance "simulated"; every observation is badged honestly.
    assert body["provenance"] == "simulated"
    assert all(o["provenance"] == "simulated" for o in body["observations"])


def test_worklist_with_authorization_header_still_returns_valid_worklist(monkeypatch):
    # worklist() has no per-caller content variation (unlike chat/golden): the
    # OBO context is built only to gate a live Fabric grounding read. This test
    # proves that path doesn't break the response shape, and that a stray
    # X-User-Oid header (no longer a worklist() parameter) has no effect.
    import api.app as app_module

    class _Ctx:
        user_oid = "obo-oid-999"
        obo_token = ""
        roles = ("HCC.DischargeCoordinator",)
        hospital = "aggregated"

    monkeypatch.setattr(app_module, "build_obo_context", lambda _a: _Ctx())
    resp = _client().get(
        "/agents/dca/worklist",
        headers={"Authorization": "Bearer ok", "X-User-Oid": "header-oid-should-be-ignored"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["role"] == "dca"
    assert len(body["observations"]) == 3  # unchanged: same seeded fixture
