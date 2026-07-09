"""Sprint 13 T5 — grounding + session cache (ADR-0007 §1).

Azure Cache for Redis holds grounding and session entries. This module provides a
tiny get/set/TTL surface with an **in-memory** implementation for dev/CI; the
live implementation is wired via ``redis`` (optional ``runtime`` extra) at deploy
time. Keys are namespaced so grounding and session entries never collide.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

GROUNDING_NS = "grounding"
SESSION_NS = "session"


def _key(namespace: str, key: str) -> str:
    return f"{namespace}:{key}"


@dataclass
class _Entry:
    value: Any
    expires_at: float | None


@dataclass
class RedisCache:
    """In-memory Redis stand-in with TTL semantics."""

    _store: dict[str, _Entry] = field(default_factory=dict)

    def set(self, namespace: str, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        expires_at = time.monotonic() + ttl_seconds if ttl_seconds else None
        self._store[_key(namespace, key)] = _Entry(value, expires_at)

    def get(self, namespace: str, key: str) -> Any | None:
        entry = self._store.get(_key(namespace, key))
        if entry is None:
            return None
        if entry.expires_at is not None and time.monotonic() >= entry.expires_at:
            del self._store[_key(namespace, key)]
            return None
        return entry.value

    # Convenience wrappers for the two namespaces the host uses.
    def cache_grounding(self, key: str, rows: Any, ttl_seconds: int = 300) -> None:
        self.set(GROUNDING_NS, key, rows, ttl_seconds)

    def get_grounding(self, key: str) -> Any | None:
        return self.get(GROUNDING_NS, key)
