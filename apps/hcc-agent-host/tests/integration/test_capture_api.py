"""Sprint 30 — capture API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.app import create_app


def test_chat_returns_interaction_id():
    client = TestClient(create_app())
    res = client.post("/agents/ooa-agent/chat", json={"prompt": "Wie ist die Auslastung?"})
    assert res.status_code == 200
    body = res.json()
    assert body["interactionId"].startswith("AIX-")
