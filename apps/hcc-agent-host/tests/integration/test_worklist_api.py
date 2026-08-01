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
