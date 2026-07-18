"""Unit tests for the env-gated live-client factory (M5)."""

from __future__ import annotations

import api.app as appmod


def _clear_env(monkeypatch):
    for k in ("FABRIC_DATA_AGENT_ENDPOINT", "FABRIC_WORKSPACE_ID", "FABRIC_DATA_AGENT_ID"):
        monkeypatch.delenv(k, raising=False)


def test_returns_none_when_no_env(monkeypatch):
    _clear_env(monkeypatch)
    assert appmod._build_live_data_agent() is None


def test_returns_none_on_partial_env(monkeypatch, caplog):
    _clear_env(monkeypatch)
    monkeypatch.setenv("FABRIC_DATA_AGENT_ENDPOINT", "https://da.example/query")
    # workspace + id missing → synthetic fallback
    assert appmod._build_live_data_agent() is None
    assert "FABRIC_DATA_AGENT_* partially configured (1/3 set)" in caplog.text


def test_returns_client_when_all_env_set(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("FABRIC_DATA_AGENT_ENDPOINT", "https://da.example/query")
    monkeypatch.setenv("FABRIC_WORKSPACE_ID", "ws-1")
    monkeypatch.setenv("FABRIC_DATA_AGENT_ID", "da-1")
    client = appmod._build_live_data_agent()
    assert client is not None
    assert client.ask.__self__ is client  # it's a FabricDataAgentClient with .ask
