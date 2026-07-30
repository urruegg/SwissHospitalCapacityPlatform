"""#424 M3 — server-side Foundry thread provider.

A :class:`ThreadProvider` maps ``(userOid x agent) -> threadId`` so each
board-agent conversation threads its turns server-side (design §3.1). Two
implementations sit behind the same interface so Option 2 slots in at M5 as a
config flip, not a rebuild:

- :class:`NativeThreadProvider` — agent-host-native persistence via the existing
  :class:`~persistence.cosmos_client.CosmosPersistence` ``conversations`` seam
  (in-memory now, live Cosmos later). Provenance ``native``. Stays within the
  ADR-0013 synthetic-demo scope (no OBO, no new infrastructure). **SIT default.**
- :class:`FoundryThreadProvider` — real Foundry Assistants threads (eastus2,
  pattern in ``tools/fabric_data_agent_client.py``). Requires a per-user **OBO**
  token, so it is dormant until #424 M5 and **refuses** rather than minting an
  app-identity thread (that would violate the OBO-per-user rule in ADR-0052 and
  be a throwaway).

The provider is selected by the ``THREAD_PROVIDER`` env var (default ``native``)
so one image lifts westus2 -> live without a code edit (config, not code).
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from persistence.cosmos_client import CosmosPersistence


class ThreadProviderError(RuntimeError):
    """Raised when a provider cannot mint a thread (e.g. missing user/OBO context)."""


@dataclass(frozen=True)
class ThreadRef:
    """A resolved thread handle + where it is persisted."""

    thread_id: str
    provenance: str  # "native" | "foundry"


@runtime_checkable
class ThreadProvider(Protocol):
    provenance: str

    def mint(self, user_oid: str, agent: str) -> ThreadRef:
        ...


def _stable_thread_id(user_oid: str, agent: str) -> str:
    """Deterministic id from ``(userOid x agent)`` — inherently idempotent, so a
    thread survives an in-memory restart and never collides across users/agents."""
    digest = hashlib.sha256(f"{user_oid}:{agent}".encode()).hexdigest()[:24]
    return f"thr-{digest}"


@dataclass
class NativeThreadProvider:
    """Agent-host-native threads keyed by ``(userOid x agent)``. Idempotent, and
    seeded once into the ``conversations`` container so the thread is auditable
    from turn 0."""

    persistence: CosmosPersistence = field(default_factory=CosmosPersistence)
    provenance: str = "native"
    _threads: dict[str, str] = field(default_factory=dict)

    def mint(self, user_oid: str, agent: str) -> ThreadRef:
        if not user_oid:
            raise ThreadProviderError("thread mint requires a user oid (deny-by-default)")
        key = f"{user_oid}:{agent}"
        thread_id = self._threads.get(key)
        if thread_id is None:
            thread_id = _stable_thread_id(user_oid, agent)
            self._threads[key] = thread_id
            # Seed a conversations record so the thread is auditable from turn 0.
            self.persistence.write(
                "conversations",
                {
                    "conversationId": thread_id,
                    "agent": agent,
                    "event": "thread_minted",
                    "provenance": self.provenance,
                },
            )
        return ThreadRef(thread_id=thread_id, provenance=self.provenance)


@dataclass
class FoundryThreadProvider:
    """Real Foundry Assistants threads (eastus2). Dormant until #424 M5 (OBO)."""

    provenance: str = "foundry"

    def mint(self, user_oid: str, agent: str) -> ThreadRef:
        # M5 lights this up using the signed-in user's OBO token + the Foundry
        # Assistants threads API. Until then it refuses rather than minting an
        # app-identity thread.
        raise ThreadProviderError(
            "FoundryThreadProvider requires per-user OBO context (arrives in #424 M5)"
        )


def build_thread_provider(persistence: CosmosPersistence | None = None) -> ThreadProvider:
    """Select the provider from ``THREAD_PROVIDER`` (default ``native``)."""
    kind = os.environ.get("THREAD_PROVIDER", "native").strip().lower()
    if kind == "foundry":
        return FoundryThreadProvider()
    return NativeThreadProvider(persistence=persistence or CosmosPersistence())
