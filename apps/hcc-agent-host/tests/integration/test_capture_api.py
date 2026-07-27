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


def test_append_user_event_endpoint():
    client = TestClient(create_app())
    chat = client.post("/agents/ooa-agent/chat", json={"prompt": "Wie ist die Auslastung?"}).json()
    iid = chat["interactionId"]
    res = client.post(
        f"/agents/ooa-agent/interactions/{iid}/events",
        json={"type": "thumbs", "value": "up"},
    )
    assert res.status_code == 200
    assert res.json()["ok"] is True


def test_append_user_event_unknown_id_is_404():
    client = TestClient(create_app())
    res = client.post(
        "/agents/ooa-agent/interactions/AIX-missing/events",
        json={"type": "thumbs", "value": "up"},
    )
    assert res.status_code == 404
