"""Cosmos-backed interaction store (Sprint 30 M4 runtime seam).

The "real in prod" side of :mod:`lib.online_store`. Imported lazily by
``build_store_from_env`` only when the ``COSMOS_*`` environment is configured, so
unit tests / CI never load the optional ``azure-cosmos`` + ``azure-identity``
dependencies. Uses Managed Identity (Workload Identity Federation) — no keys.
"""

from __future__ import annotations

from typing import Any

Record = dict[str, Any]


class CosmosInteractionStore:  # pragma: no cover - requires azure SDK + network
    """Read recent interactions and write eval verdicts back to Cosmos."""

    def __init__(self, endpoint: str, database: str, container: str) -> None:
        from azure.cosmos import CosmosClient
        from azure.identity import DefaultAzureCredential

        self._client = CosmosClient(endpoint, credential=DefaultAzureCredential())
        self._container = self._client.get_database_client(database).get_container_client(container)

    def read_recent(self, *, agent: str | None, limit: int) -> list[Record]:
        if agent is None:
            query = "SELECT * FROM c ORDER BY c.ts DESC OFFSET 0 LIMIT @limit"
            params = [{"name": "@limit", "value": limit}]
        else:
            query = (
                "SELECT * FROM c WHERE c.agent = @agent "
                "ORDER BY c.ts DESC OFFSET 0 LIMIT @limit"
            )
            params = [{"name": "@agent", "value": agent}, {"name": "@limit", "value": limit}]
        return list(
            self._container.query_items(
                query=query, parameters=params, enable_cross_partition_query=True
            )
        )

    def update_eval(self, interaction_id: str, eval_block: dict[str, Any]) -> None:
        # Patch only the eval block; leaves the redacted record untouched.
        self._container.patch_item(
            item=interaction_id,
            partition_key=interaction_id,
            patch_operations=[{"op": "set", "path": "/eval", "value": eval_block}],
        )
