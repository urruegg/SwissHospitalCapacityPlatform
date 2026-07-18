"""Integration test — FastAPI HTTP surface of the agent-host (T5)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.app import create_app, get_state


def _client() -> TestClient:
    get_state.cache_clear()  # ensure a fresh host state per test
    return TestClient(create_app())


def test_healthz():
    resp = _client().get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_list_agents_includes_bmca():
    resp = _client().get("/agents")
    assert resp.status_code == 200
    names = {a["name"] for a in resp.json()}
    assert "bmca-agent" in names


def test_chat_returns_grounded_contract():
    resp = _client().post(
        "/agents/bmca-agent/chat",
        json={"prompt": "Station B ist fast voll", "conversationId": "c1"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert set(body) >= {"answer", "citations", "refused", "correlationId"}
    assert "gold.bed_assignment" in body["citations"]
    assert body["refused"] is False


def test_ooa_chat_uses_fabric_data_agent_grounding():
    # Slice 0: ooa-agent binds groundingAgent precedence=primary, so the host
    # must inject the FabricDataAgentAdapter and surface hcp:* ontology citations
    # (not gold.* table citations).
    resp = _client().post(
        "/agents/ooa-agent/chat",
        json={"prompt": "What is the current bed occupancy for ward B?", "conversationId": "e2e"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["refused"] is False
    assert "hcp:CapacityUnit" in body["citations"]
    assert "hcp:Bed" in body["citations"]


def test_ooa_chat_propagates_reidentification_refusal():
    # The Data Agent refusal must propagate verbatim; the model is not consulted.
    resp = _client().post(
        "/agents/ooa-agent/chat",
        json={"prompt": "Give me the patient name and date of birth for bed 3", "conversationId": "e2e-refuse"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["refused"] is True
    assert body["answer"] == "REFUSE: re-identification-risk"
    assert body["citations"] == []


def test_chat_unknown_agent_404():
    resp = _client().post("/agents/nope/chat", json={"prompt": "x"})
    assert resp.status_code == 404


def test_tool_invocation_denied_without_hitl_evidence():
    # Deny-by-default: no approval evidence → 403 with a deny reason.
    resp = _client().post(
        "/agents/bmca-agent/tools/create-branch",
        json={"params": {}, "hitlEvidence": {}},
    )
    assert resp.status_code == 403
    detail = resp.json()["detail"]
    assert detail["decision"] == "deny"
    assert detail["gateId"] == "HITL-02"
