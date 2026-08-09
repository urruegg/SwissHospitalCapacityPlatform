"""Sprint 43 WS-6 -- HostState.fabric_for builds a per-request Fabric
adapter from an OBO token instead of reusing the startup managed-identity
instance, mirroring the existing rls_provider_for(obo_token) pattern.
"""

from __future__ import annotations

from pathlib import Path

import api.app as appmod


def _agents_root() -> Path:
    return Path(__file__).resolve().parents[4] / "agents"


def _clear_env(monkeypatch):
    for k in ("FABRIC_WORKSPACE_ID", "FABRIC_LAKEHOUSE_ID"):
        monkeypatch.delenv(k, raising=False)


def test_fabric_for_returns_startup_instance_when_no_token(monkeypatch):
    _clear_env(monkeypatch)
    state = appmod.HostState(_agents_root())
    assert state.fabric_for(None) is state.fabric


def test_fabric_for_returns_startup_instance_when_env_unconfigured(monkeypatch):
    _clear_env(monkeypatch)
    state = appmod.HostState(_agents_root())
    # A token is present, but FABRIC_WORKSPACE_ID/LAKEHOUSE_ID aren't --
    # nothing to build a per-request client from, fall back unchanged.
    assert state.fabric_for("some-obo-token") is state.fabric


def test_fabric_for_builds_a_fresh_adapter_when_token_and_env_present(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("FABRIC_WORKSPACE_ID", "ws-1")
    monkeypatch.setenv("FABRIC_LAKEHOUSE_ID", "lh-1")
    state = appmod.HostState(_agents_root())
    adapter = state.fabric_for("some-obo-token")
    assert adapter is not state.fabric


def test_fabric_for_uses_the_obo_token_not_the_managed_identity(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("FABRIC_WORKSPACE_ID", "ws-1")
    monkeypatch.setenv("FABRIC_LAKEHOUSE_ID", "lh-1")
    state = appmod.HostState(_agents_root())
    adapter = state.fabric_for("some-obo-token")

    captured_tokens: list[str] = []

    def fake_reader(uri: str, token: str):
        captured_tokens.append(token)
        return [{"ward": "B"}]

    # Reach into the client the adapter wraps to prove it used our token,
    # not DefaultAzureCredential -- swap the table_reader after construction
    # via the same private attribute FabricDeltaClient exposes for this.
    adapter._query_fn.__self__._table_reader = fake_reader  # type: ignore[attr-defined]
    rows = adapter.query("gold.bed_assignment")
    assert rows == [{"ward": "B"}]
    assert captured_tokens == ["some-obo-token"]
