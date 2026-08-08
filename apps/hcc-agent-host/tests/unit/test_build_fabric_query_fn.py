"""Unit tests for the env-gated live Fabric Delta query factory (Sprint 43 WS-2)."""

from __future__ import annotations

import api.app as appmod


def _clear_env(monkeypatch):
    for k in ("FABRIC_WORKSPACE_ID", "FABRIC_LAKEHOUSE_ID"):
        monkeypatch.delenv(k, raising=False)


def test_returns_none_when_no_env(monkeypatch):
    _clear_env(monkeypatch)
    assert appmod._build_fabric_query_fn() is None


def test_returns_none_on_partial_env(monkeypatch, caplog):
    _clear_env(monkeypatch)
    monkeypatch.setenv("FABRIC_WORKSPACE_ID", "ws-1")
    assert appmod._build_fabric_query_fn() is None
    assert "FABRIC_LAKEHOUSE_ID" in caplog.text or "partially configured" in caplog.text


def test_returns_callable_when_all_env_set(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("FABRIC_WORKSPACE_ID", "ws-1")
    monkeypatch.setenv("FABRIC_LAKEHOUSE_ID", "lh-1")
    query_fn = appmod._build_fabric_query_fn()
    assert query_fn is not None
    assert callable(query_fn)
