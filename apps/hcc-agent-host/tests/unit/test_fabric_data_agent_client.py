"""Unit tests for the live Fabric Data Agent client (M5, Option A).

The published Fabric Data Agent endpoint (``.../aiskills/{id}/aiassistant/openai``)
speaks the OpenAI *Assistants* protocol, not a single-shot ``/query``. These tests
drive the real create-assistant -> thread -> message -> run -> poll -> messages
flow with an injected transport so no cloud is required, and assert the client
normalises the free-text answer into ``{answer, citations, refused}`` by parsing
``hcp:*`` citations and the ``REFUSE:`` token.
"""

from __future__ import annotations

from typing import Any, Dict

from tools.fabric_data_agent_client import FabricDataAgentClient

_ENDPOINT = "https://api.fabric.microsoft.com/v1/workspaces/ws-1/aiskills/da-1/aiassistant/openai"


class _FakeResponse:
    def __init__(self, payload: Dict[str, Any]):
        self._payload = payload

    def json(self) -> Dict[str, Any]:
        return self._payload

    def raise_for_status(self) -> None:
        return None


class _FakeTransport:
    """Routes Assistants REST calls to canned responses and records the flow."""

    def __init__(self, assistant_text: str, run_statuses=("completed",)):
        self.assistant_text = assistant_text
        self._run_statuses = list(run_statuses)
        self.calls: list[tuple[str, str]] = []
        self.bodies: list[Dict[str, Any]] = []

    def __call__(self, method, url, headers=None, json=None, timeout=None):
        self.calls.append((method, url))
        self.bodies.append(json or {})
        path = url.split("?")[0]
        if method == "POST" and path.endswith("/assistants"):
            return _FakeResponse({"id": "asst_1"})
        if method == "POST" and path.endswith("/threads"):
            return _FakeResponse({"id": "thread_1"})
        if method == "POST" and path.endswith("/messages"):
            return _FakeResponse({"id": "msg_1"})
        if method == "POST" and path.endswith("/runs"):
            return _FakeResponse({"id": "run_1", "status": "queued"})
        if method == "GET" and "/runs/" in path:
            status = self._run_statuses.pop(0) if self._run_statuses else "completed"
            return _FakeResponse({"id": "run_1", "status": status})
        if method == "GET" and path.endswith("/messages"):
            return _FakeResponse(
                {
                    "data": [
                        {
                            "role": "assistant",
                            "content": [
                                {"type": "text", "text": {"value": self.assistant_text}}
                            ],
                        },
                        {"role": "user", "content": [{"type": "text", "text": {"value": "q"}}]},
                    ]
                }
            )
        raise AssertionError(f"unexpected call {method} {url}")


def _client(transport: _FakeTransport) -> FabricDataAgentClient:
    return FabricDataAgentClient(
        endpoint=_ENDPOINT,
        workspace_id="ws-1",
        data_agent_id="da-1",
        token_provider=lambda: "tok",
        http_request=transport,
        poll_interval=0,
    )


def test_ask_runs_full_assistants_flow_and_parses_citations():
    text = "Ward B is 92% occupied. Grounded on: dim_ward_capacityunit, hcp:CapacityUnit, hcp:Bed."
    transport = _FakeTransport(text)
    out = _client(transport).ask("bed occupancy ward B?")

    assert out["refused"] is False
    assert out["answer"] == text
    assert "hcp:CapacityUnit" in out["citations"]
    assert "hcp:Bed" in out["citations"]

    # the user question was posted to the thread
    posted = [b.get("content") for b in transport.bodies if b.get("role") == "user"]
    assert "bed occupancy ward B?" in posted
    # the run referenced the created assistant
    run_bodies = [b for b in transport.bodies if b.get("assistant_id")]
    assert run_bodies and run_bodies[0]["assistant_id"] == "asst_1"
    # every call carried the api-version query string
    assert all("api-version=" in url for _, url in transport.calls)


def test_ask_detects_refusal_token():
    transport = _FakeTransport("REFUSE: re-identification-risk")
    out = _client(transport).ask("patient name and DOB for bed 3?")
    assert out["refused"] is True
    assert out["answer"] == "REFUSE: re-identification-risk"
    assert out["citations"] == []


def test_ask_polls_until_run_completed():
    transport = _FakeTransport(
        "All good. hcp:Ward.", run_statuses=("queued", "in_progress", "completed")
    )
    out = _client(transport).ask("status?")
    assert out["refused"] is False
    assert "hcp:Ward" in out["citations"]
    # polled the run at least twice before completion
    run_polls = [c for c in transport.calls if c[0] == "GET" and "/runs/" in c[1]]
    assert len(run_polls) >= 3


def test_ask_raises_on_failed_run():
    transport = _FakeTransport("irrelevant", run_statuses=("failed",))
    try:
        _client(transport).ask("status?")
    except RuntimeError as exc:
        assert "failed" in str(exc).lower()
    else:  # pragma: no cover
        raise AssertionError("expected RuntimeError on failed run")
