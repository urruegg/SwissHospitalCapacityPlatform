"""Sprint 43 WS-6 -- /agents/{name}/chat honors an OBO bearer when
OBO_ENABLED is on, mirroring tests/integration/test_golden_obo_endpoint.py's
parity/deny-by-default shape for the golden read."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.app import create_app


def _client(monkeypatch) -> TestClient:
    monkeypatch.delenv("OBO_ENABLED", raising=False)
    return TestClient(create_app())


def test_chat_without_obo_is_unchanged(monkeypatch):
    client = _client(monkeypatch)
    resp = client.post(
        "/agents/bmca-agent/chat",
        json={"prompt": "Station B ist fast voll", "conversationId": "c1"},
    )
    assert resp.status_code == 200
    assert "citations" in resp.json()


def test_chat_with_obo_enabled_and_invalid_bearer_denies(monkeypatch):
    monkeypatch.setenv("OBO_ENABLED", "true")
    monkeypatch.setenv("OBO_AUDIENCE", "api://agent-host")
    monkeypatch.setenv("OBO_ISSUER", "https://sts.windows.net/tenant-abc/")
    monkeypatch.setenv("OBO_JWKS_URL", "https://example.invalid/keys")
    client = TestClient(create_app())
    resp = client.post(
        "/agents/bmca-agent/chat",
        json={"prompt": "Station B ist fast voll", "conversationId": "c1"},
        headers={"Authorization": "Bearer not-a-real-jwt"},
    )
    assert resp.status_code == 401
