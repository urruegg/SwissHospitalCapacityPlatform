"""Unit tests for FoundryResponsesChatModel (Sprint 43 WS-1).

No cloud calls -- token_provider and http_request are injected fakes, mirroring
tools/fabric_data_agent_client.py's test style.
"""

from __future__ import annotations

from orchestrator.foundry_chat_model import FoundryResponsesChatModel


class _FakeResponse:
    def __init__(self, json_body: dict, status_code: int = 200):
        self._json = json_body
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._json


def _ok_response(text: str) -> _FakeResponse:
    return _FakeResponse({
        "status": "completed",
        "output": [
            {"type": "reasoning", "content": []},
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": text}],
            },
        ],
    })


def _model(fake_http):
    return FoundryResponsesChatModel(
        project_endpoint="https://ai-example.services.ai.azure.com",
        project_name="proj-1",
        token_provider=lambda: "fake-token",
        http_request=fake_http,
    )


def test_complete_posts_agent_reference_and_returns_text():
    captured = {}

    def fake_http(method, url, headers=None, json=None, timeout=None):
        captured["method"] = method
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return _ok_response("The occupancy is 92%.")

    answer = _model(fake_http).complete(
        "You are bmca-agent.",
        "Wie ist die Auslastung?",
        [{"ward": "B", "occupied": 46, "capacity": 50}],
        agent_name="bmca-agent",
    )

    assert answer == "The occupancy is 92%."
    assert captured["method"] == "POST"
    assert captured["url"] == (
        "https://ai-example.services.ai.azure.com/api/projects/proj-1/openai/v1/responses"
    )
    assert "api-version" not in captured["url"]
    assert captured["headers"]["Authorization"] == "Bearer fake-token"
    assert captured["headers"]["Content-Type"] == "application/json"
    assert captured["json"]["agent_reference"] == {
        "name": "bmca-agent",
        "type": "agent_reference",
    }
    assert captured["json"]["instructions"] == "You are bmca-agent."
    assert "Wie ist die Auslastung?" in captured["json"]["input"]
    assert "occupied" in captured["json"]["input"]


def test_complete_with_no_grounding_says_so_in_input():
    captured = {}

    def fake_http(method, url, headers=None, json=None, timeout=None):
        captured["json"] = json
        return _ok_response("Please share bed-state figures.")

    answer = _model(fake_http).complete(
        "sys", "What's tonight's outlook?", [], agent_name="bmca-agent"
    )

    assert answer == "Please share bed-state figures."
    assert "No grounding data" in captured["json"]["input"]


def test_complete_extracts_first_message_text_skipping_reasoning():
    def fake_http(method, url, headers=None, json=None, timeout=None):
        return _ok_response("final text")

    answer = _model(fake_http).complete("sys", "q", [], agent_name="bmca-agent")
    assert answer == "final text"


def test_complete_returns_empty_string_when_no_message_output():
    def fake_http(method, url, headers=None, json=None, timeout=None):
        return _FakeResponse({"status": "completed", "output": [{"type": "reasoning", "content": []}]})

    answer = _model(fake_http).complete("sys", "q", [], agent_name="bmca-agent")
    assert answer == ""


def test_complete_raises_on_http_error():
    import pytest

    def fake_http(method, url, headers=None, json=None, timeout=None):
        return _FakeResponse({"error": {"message": "boom"}}, status_code=500)

    with pytest.raises(RuntimeError):
        _model(fake_http).complete("sys", "q", [], agent_name="bmca-agent")
