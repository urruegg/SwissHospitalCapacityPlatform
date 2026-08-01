"""Integration test - Sprint 39 P2 B3/B4 GET /agents/{role}/evidence.

The endpoint returns the Plan 1 DC-EVIDENCE-TRACE-v1 built on the seeded gold,
for the accept and deny branches; an invalid branch is a 400. Read-only (no
oid). Synthetic-only, no PHI (ADR-0016).
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from api.app import create_app, get_state


def _client() -> TestClient:
    get_state.cache_clear()
    return TestClient(create_app())


def test_accept_trace_has_five_part_steps_and_golden_thread():
    r = _client().get("/agents/dca/evidence?branch=accept")
    assert r.status_code == 200
    trace = r.json()
    assert trace["contract"] == "DC-EVIDENCE-TRACE-v1"
    assert trace["branch"] == "accept"
    assert trace["golden_thread"]
    assert trace["steps"]
    step = trace["steps"][0]
    for part in ("epic_input", "agent_read", "recommendation", "copilot", "action", "outcome"):
        assert part in step
    # The accept branch applied the lever, so the outcome is realised.
    assert step["outcome"]["provenance"] in ("simulated", "live")


def test_deny_branch_differs_from_accept():
    accept = _client().get("/agents/dca/evidence?branch=accept").json()
    deny = _client().get("/agents/dca/evidence?branch=deny").json()
    assert deny["branch"] == "deny"
    # Same golden thread contract shape; the deny branch withholds approval so its
    # action is not applied (distinct from accept).
    assert accept["steps"][0]["action"]["status"] != deny["steps"][0]["action"]["status"]


def test_invalid_branch_is_400():
    r = _client().get("/agents/dca/evidence?branch=maybe")
    assert r.status_code == 400
