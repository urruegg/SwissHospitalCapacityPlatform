"""Unit tests — #424 M4 RlsProvider seam (evidence-grounded capability ladder).

Row-level security on the structured golden read is enforced through a swappable
``RlsProvider``:

- ``SimulatedRlsProvider`` (default, Rung 0) filters synthetic rows in the
  agent-host; provenance ``simulated``. It is honest about being a demonstration
  of the RLS *shape*, not live Fabric enforcement.
- ``FabricDataAgentRlsProvider`` (Rung 1) reuses the **proven, live** Fabric Data
  Agent client (``da_hospital_capacity``) — the surface that already enforces the
  Direct-Lake semantic model's RLS + ADR-0016 PHI gate. Per-user structured row
  scope additionally requires an OBO token (M5) plus a dynamic-RLS TMDL predicate
  (data-lane follow-up), so without an OBO token it refuses the structured read
  rather than serve MI-scoped rows as if they were per-user.

Deny-by-default: an ungrounded read (no scope or no oid) is refused everywhere.
Synthetic-only, no PHI (ADR-0016).
"""

from __future__ import annotations

import pytest

from golden.rls import (
    FabricDataAgentRlsProvider,
    RlsProviderError,
    SimulatedRlsProvider,
    build_rls_provider,
)

ROWS = [
    {"id": "a", "hospital": "hospital-usz", "v": 1},
    {"id": "b", "hospital": "hospital-ksa", "v": 2},
    {"id": "c", "v": 3},  # site-agnostic
]


class _FakeDataAgentClient:
    """Stand-in for the proven FabricDataAgentClient (no cloud in unit tests)."""

    def __init__(self):
        self.asked: list[str] = []

    def ask(self, question: str):
        self.asked.append(question)
        return {"answer": "hcp:Ward", "citations": ["hcp:Ward"], "refused": False}


# --- Rung 0: SimulatedRlsProvider -------------------------------------------


def test_simulated_aggregated_returns_all_rows():
    provider = SimulatedRlsProvider()
    decision = provider.scope(ROWS, hospital_scope="aggregated", user_oid="u-1")
    assert [r["id"] for r in decision.rows] == ["a", "b", "c"]
    assert decision.scope == "aggregated"
    assert decision.provider == "simulated"
    assert decision.provenance == "simulated"


def test_simulated_site_scope_filters_to_that_site_plus_untagged():
    provider = SimulatedRlsProvider()
    decision = provider.scope(ROWS, hospital_scope="hospital-usz", user_oid="u-1")
    assert [r["id"] for r in decision.rows] == ["a", "c"]
    assert decision.scope == "hospital-usz"


def test_simulated_deny_by_default_without_scope():
    with pytest.raises(RlsProviderError):
        SimulatedRlsProvider().scope(ROWS, hospital_scope="", user_oid="u-1")


def test_simulated_deny_by_default_without_oid():
    with pytest.raises(RlsProviderError):
        SimulatedRlsProvider().scope(ROWS, hospital_scope="aggregated", user_oid="")


# --- Rung 1: FabricDataAgentRlsProvider -------------------------------------


def test_fabric_data_agent_provider_holds_the_proven_client():
    client = _FakeDataAgentClient()
    provider = FabricDataAgentRlsProvider(client=client)
    assert provider.client is client
    assert provider.provider == "fabric-data-agent"
    assert provider.provenance == "live"


def test_fabric_data_agent_refuses_structured_scope_without_obo():
    # Model RLS + PHI are live on the /chat grounding path, but per-user
    # *structured* row scope needs OBO (M5); without it, refuse rather than serve
    # MI-scoped rows as if they were the caller's.
    provider = FabricDataAgentRlsProvider(client=_FakeDataAgentClient(), obo_token=None)
    with pytest.raises(RlsProviderError):
        provider.scope(ROWS, hospital_scope="aggregated", user_oid="u-1")


def test_fabric_data_agent_deny_by_default_without_scope():
    provider = FabricDataAgentRlsProvider(client=_FakeDataAgentClient(), obo_token="obo-x")
    with pytest.raises(RlsProviderError):
        provider.scope(ROWS, hospital_scope="", user_oid="u-1")


# --- Factory ----------------------------------------------------------------


def test_factory_defaults_to_simulated(monkeypatch):
    monkeypatch.delenv("RLS_PROVIDER", raising=False)
    provider = build_rls_provider()
    assert isinstance(provider, SimulatedRlsProvider)
    assert provider.provider == "simulated"


def test_factory_simulated_explicit(monkeypatch):
    monkeypatch.setenv("RLS_PROVIDER", "simulated")
    assert isinstance(build_rls_provider(), SimulatedRlsProvider)


def test_factory_fabric_data_agent_without_client_raises(monkeypatch):
    # Selecting the live provider without the proven client is a misconfiguration.
    monkeypatch.setenv("RLS_PROVIDER", "fabric-data-agent")
    with pytest.raises(RlsProviderError):
        build_rls_provider(data_agent_client=None)


def test_factory_fabric_data_agent_with_client_builds(monkeypatch):
    monkeypatch.setenv("RLS_PROVIDER", "fabric-data-agent")
    client = _FakeDataAgentClient()
    provider = build_rls_provider(data_agent_client=client, obo_token="obo-x")
    assert isinstance(provider, FabricDataAgentRlsProvider)
    assert provider.client is client
    assert provider.provider == "fabric-data-agent"
