"""Sprint 13 T5 — Cosmos DB persistence (ADR-0007 §2, §Implementation Notes).

Persists conversation, audit, and approval-event records. Cosmos DB is the
required persistence engine for MVP/PROD (ADR-0007). This module provides a
container-abstracted write/read surface with an **in-memory** implementation used
in dev/CI; the live implementation is wired via ``azure-cosmos`` (optional
``runtime`` extra) at deploy time.

Container schema (ADR-0007 §Implementation Notes):
- ``conversations`` — per-conversation turns, partitioned by conversationId.
- ``audit`` — audit events, correlationId-indexed.
- ``approval-events`` — HITL approval evidence records (schema from §6).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

CONTAINERS = ("conversations", "audit", "approval-events")

# Partition key per container (ADR-0007 §Implementation Notes: correlationId
# indexing; conversations partition by conversationId).
PARTITION_KEYS = {
    "conversations": "conversationId",
    "audit": "correlationId",
    "approval-events": "correlationId",
}


@dataclass
class CosmosPersistence:
    """In-memory Cosmos stand-in. Swap for a live client at deploy time."""

    _store: dict[str, list[dict[str, Any]]] = field(
        default_factory=lambda: {c: [] for c in CONTAINERS}
    )

    def write(self, container: str, item: dict[str, Any]) -> dict[str, Any]:
        if container not in CONTAINERS:
            raise ValueError(f"unknown container '{container}'")
        record = dict(item)
        record.setdefault("id", str(uuid.uuid4()))
        pk = PARTITION_KEYS[container]
        if pk not in record:
            raise ValueError(f"item for '{container}' missing partition key '{pk}'")
        self._store[container].append(record)
        return record

    def read_all(self, container: str) -> list[dict[str, Any]]:
        if container not in CONTAINERS:
            raise ValueError(f"unknown container '{container}'")
        return list(self._store[container])

    def query_by_correlation(self, container: str, correlation_id: str) -> list[dict[str, Any]]:
        return [
            r for r in self.read_all(container) if r.get("correlationId") == correlation_id
        ]
