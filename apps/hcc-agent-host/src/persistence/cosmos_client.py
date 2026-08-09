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

import os
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable

CONTAINERS = ("conversations", "audit", "approval-events", "agent_interactions")

# Partition key per container (ADR-0007 §Implementation Notes: correlationId
# indexing; conversations partition by conversationId; Sprint 30 agent_interactions
# partition by conversationKey = <userOid>:<agent>).
PARTITION_KEYS = {
    "conversations": "conversationId",
    "audit": "correlationId",
    "approval-events": "correlationId",
    "agent_interactions": "conversationKey",
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

    def append_user_event(self, interaction_id: str, event: dict[str, Any]) -> dict[str, Any]:
        """Append a user-interaction event to a stored agent_interactions record."""
        for record in self._store["agent_interactions"]:
            if record.get("interactionId") == interaction_id:
                record.setdefault("userEvents", []).append(dict(event))
                return record
        raise KeyError(f"no agent_interactions record with interactionId '{interaction_id}'")


@dataclass
class LiveCosmosPersistence:
    """azure-cosmos-backed persistence. Same interface as CosmosPersistence.

    The container-client lookup is injected (``_container_for``) so this class
    is unit-tested without a live account -- mirrors the existing
    ``acquire_obo_token``/``credential_factory`` injection pattern used
    elsewhere in this app.
    """

    _container_for: Callable[[str], Any]

    def write(self, container: str, item: dict[str, Any]) -> dict[str, Any]:
        if container not in CONTAINERS:
            raise ValueError(f"unknown container '{container}'")
        record = dict(item)
        record.setdefault("id", str(uuid.uuid4()))
        pk = PARTITION_KEYS[container]
        if pk not in record:
            raise ValueError(f"item for '{container}' missing partition key '{pk}'")
        self._container_for(container).upsert_item(record)
        return record

    def read_all(self, container: str) -> list[dict[str, Any]]:
        if container not in CONTAINERS:
            raise ValueError(f"unknown container '{container}'")
        return list(self._container_for(container).read_all_items())

    def query_by_correlation(self, container: str, correlation_id: str) -> list[dict[str, Any]]:
        return list(
            self._container_for(container).query_items(
                query="SELECT * FROM c WHERE c.correlationId = @cid",
                parameters=[{"name": "@cid", "value": correlation_id}],
                enable_cross_partition_query=True,
            )
        )

    def append_user_event(self, interaction_id: str, event: dict[str, Any]) -> dict[str, Any]:
        container = self._container_for("agent_interactions")
        matches = list(
            container.query_items(
                query="SELECT * FROM c WHERE c.interactionId = @iid",
                parameters=[{"name": "@iid", "value": interaction_id}],
                enable_cross_partition_query=True,
            )
        )
        if not matches:
            raise KeyError(f"no agent_interactions record with interactionId '{interaction_id}'")
        record = dict(matches[0])
        record.setdefault("userEvents", []).append(dict(event))
        container.upsert_item(record)
        return record


def build_cosmos_persistence(
    *, container_client_factory: Callable[[str], Any] | None = None
) -> "CosmosPersistence | LiveCosmosPersistence":
    """Return a live Cosmos-backed persistence when ``COSMOS_ENDPOINT`` is
    configured, else the in-memory stand-in (unchanged dev/CI default).

    Mirrors ``api/app.py``'s ``_build_chat_model``/``_build_live_data_agent``
    guarded-optional pattern. The Cosmos account, ``agenthost`` database, and
    every container in ``CONTAINERS`` (including ``approval-events``) are
    already deployed live in SIT with ``Cosmos DB Built-in Data Contributor``
    already granted to this app's managed identity -- this function is the
    only missing piece.
    """
    endpoint = os.environ.get("COSMOS_ENDPOINT")
    if not endpoint:
        return CosmosPersistence()
    if container_client_factory is not None:
        return LiveCosmosPersistence(_container_for=container_client_factory)
    from azure.cosmos import CosmosClient
    from azure.identity import DefaultAzureCredential

    client = CosmosClient(endpoint, credential=DefaultAzureCredential())
    database = client.get_database_client("agenthost")
    return LiveCosmosPersistence(_container_for=database.get_container_client)
