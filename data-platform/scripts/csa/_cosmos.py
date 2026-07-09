"""Lazy, credential-optional Azure Cosmos client helper for CSA seed scripts.

Returns ``None`` when Cosmos credentials are not configured (or the azure-cosmos
SDK is not installed), so seed scripts and tests degrade to a dry run instead of
failing. Auth is RBAC-only (managed identity / az login) per the T1 Bicep
(``disableLocalAuth = true``) — no account keys.
"""
from __future__ import annotations

import os
from typing import Any, Optional

COSMOS_ENDPOINT_ENV = "CSA_COSMOS_ENDPOINT"
COSMOS_DATABASE_ENV = "CSA_COSMOS_DATABASE"


def cosmos_configured() -> bool:
    """True when the endpoint env var is set (credentials available)."""
    return bool(os.environ.get(COSMOS_ENDPOINT_ENV))


def get_database_client() -> Optional[Any]:
    """Return a Cosmos DatabaseProxy, or None when creds/SDK unavailable."""
    endpoint = os.environ.get(COSMOS_ENDPOINT_ENV)
    if not endpoint:
        return None
    try:
        from azure.cosmos import CosmosClient  # type: ignore
        from azure.identity import DefaultAzureCredential  # type: ignore
    except ImportError:
        return None

    database = os.environ.get(COSMOS_DATABASE_ENV, "csa")
    client = CosmosClient(endpoint, credential=DefaultAzureCredential())
    return client.get_database_client(database)


def upsert_all(container_name: str, documents: list[dict]) -> int:
    """Upsert documents into a container. Returns the count upserted.

    Raises RuntimeError when Cosmos is not configured — callers should check
    ``cosmos_configured()`` first and skip when running a dry run.
    """
    db = get_database_client()
    if db is None:
        raise RuntimeError(
            f"Cosmos not configured; set {COSMOS_ENDPOINT_ENV} to upsert."
        )
    container = db.get_container_client(container_name)
    count = 0
    for doc in documents:
        container.upsert_item(doc)
        count += 1
    return count
