"""Unit tests — #424 M3 server-side Foundry thread provider.

A ``ThreadProvider`` maps ``(userOid x agent) -> threadId`` so each board-agent
conversation threads its turns server-side. ``NativeThreadProvider`` is the SIT
default (agent-host-native persistence, provenance ``native``, within ADR-0013
synthetic scope); ``FoundryThreadProvider`` is dormant until #424 M5 (needs OBO)
and refuses rather than minting an app-identity thread. Synthetic-only, no PHI.
"""

from __future__ import annotations

import pytest

from persistence.cosmos_client import CosmosPersistence
from threads.provider import (
    FoundryThreadProvider,
    NativeThreadProvider,
    ThreadProviderError,
    ThreadRef,
    build_thread_provider,
)


def test_native_mint_is_idempotent_per_user_and_agent():
    provider = NativeThreadProvider()
    first = provider.mint("oid-1", "bmca-agent")
    second = provider.mint("oid-1", "bmca-agent")
    assert isinstance(first, ThreadRef)
    assert first.thread_id == second.thread_id
    assert first.provenance == "native"


def test_native_mint_distinct_per_agent_and_user():
    provider = NativeThreadProvider()
    a = provider.mint("oid-1", "bmca-agent")
    b = provider.mint("oid-1", "ooa-agent")
    c = provider.mint("oid-2", "bmca-agent")
    assert len({a.thread_id, b.thread_id, c.thread_id}) == 3


def test_native_mint_requires_user_oid():
    provider = NativeThreadProvider()
    with pytest.raises(ThreadProviderError):
        provider.mint("", "bmca-agent")


def test_native_mint_seeds_one_conversations_record():
    persistence = CosmosPersistence()
    provider = NativeThreadProvider(persistence=persistence)
    ref = provider.mint("oid-1", "bmca-agent")
    provider.mint("oid-1", "bmca-agent")  # idempotent: no second seed
    seeded = [
        r for r in persistence.read_all("conversations")
        if r.get("conversationId") == ref.thread_id
    ]
    assert len(seeded) == 1
    assert seeded[0]["provenance"] == "native"


def test_foundry_provider_refuses_without_obo_context():
    provider = FoundryThreadProvider()
    with pytest.raises(ThreadProviderError):
        provider.mint("oid-1", "bmca-agent")


def test_build_thread_provider_defaults_to_native(monkeypatch):
    monkeypatch.delenv("THREAD_PROVIDER", raising=False)
    assert isinstance(build_thread_provider(), NativeThreadProvider)


def test_build_thread_provider_selects_foundry(monkeypatch):
    monkeypatch.setenv("THREAD_PROVIDER", "foundry")
    assert isinstance(build_thread_provider(), FoundryThreadProvider)
