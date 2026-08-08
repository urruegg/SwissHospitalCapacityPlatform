"""Unit tests for the env-gated live chat-model factory (Sprint 43 WS-1)."""

from __future__ import annotations

import api.app as appmod


def _clear_env(monkeypatch):
    for k in ("FOUNDRY_PROJECT_ENDPOINT", "FOUNDRY_PROJECT_NAME"):
        monkeypatch.delenv(k, raising=False)


def test_returns_none_when_no_env(monkeypatch):
    _clear_env(monkeypatch)
    assert appmod._build_chat_model() is None


def test_returns_none_on_partial_env(monkeypatch, caplog):
    _clear_env(monkeypatch)
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://ai-example.services.ai.azure.com")
    assert appmod._build_chat_model() is None
    assert "FOUNDRY_PROJECT_* partially configured" in caplog.text


def test_returns_client_when_all_env_set(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://ai-example.services.ai.azure.com")
    monkeypatch.setenv("FOUNDRY_PROJECT_NAME", "proj-1")
    model = appmod._build_chat_model()
    assert model is not None
    assert model.complete.__self__ is model
