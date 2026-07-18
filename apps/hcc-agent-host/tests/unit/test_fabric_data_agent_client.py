"""Unit tests for the live Fabric Data Agent client (M5)."""

from __future__ import annotations

from tools.fabric_data_agent_client import FabricDataAgentClient


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


def test_ask_maps_answer_and_citations():
    captured = {}

    def fake_post(url, json, headers, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        return _FakeResponse(
            {"answer": "Ward B 92% occupied", "citations": ["hcp:CapacityUnit", "hcp:Bed"], "refused": False}
        )

    client = FabricDataAgentClient(
        endpoint="https://da.example/query",
        workspace_id="ws-1",
        data_agent_id="da-1",
        token_provider=lambda: "tok",
        http_post=fake_post,
    )
    out = client.ask("bed occupancy ward B?")
    assert out["refused"] is False
    assert "hcp:Bed" in out["citations"]
    assert captured["json"]["question"] == "bed occupancy ward B?"
    assert captured["headers"]["Authorization"] == "Bearer tok"


def test_ask_passes_refusal_through():
    def fake_post(url, json, headers, timeout):
        return _FakeResponse({"answer": "REFUSE: re-identification-risk", "citations": [], "refused": True})

    client = FabricDataAgentClient(
        endpoint="https://da.example/query",
        workspace_id="ws-1",
        data_agent_id="da-1",
        token_provider=lambda: "tok",
        http_post=fake_post,
    )
    out = client.ask("patient name for bed 3?")
    assert out["refused"] is True
    assert out["answer"] == "REFUSE: re-identification-risk"
    assert out["citations"] == []


def test_ask_treats_null_citations_as_empty_list():
    def fake_post(url, json, headers, timeout):
        return _FakeResponse({"answer": "No cited entities", "citations": None, "refused": False})

    client = FabricDataAgentClient(
        endpoint="https://da.example/query",
        workspace_id="ws-1",
        data_agent_id="da-1",
        token_provider=lambda: "tok",
        http_post=fake_post,
    )
    out = client.ask("status?")
    assert out["citations"] == []
