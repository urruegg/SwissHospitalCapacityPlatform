"""Sprint 13 T5 — Cosmos persistence tool adapter (write ceiling).

Thin tool-flavoured wrapper over the Cosmos persistence client so the
orchestrator can record conversation / audit / approval-event items through the
same adapter surface as the other tools. Write ceiling. Delegates to the injected
:class:`persistence.cosmos_client.CosmosPersistence` (in-memory in dev/CI).
"""

from __future__ import annotations

from typing import Any

from persistence.cosmos_client import CosmosPersistence


class CosmosAdapter:
    server = "cosmos"
    ceiling = "write"

    _CONTAINERS = {"conversations", "audit", "approval-events"}

    def __init__(self, persistence: CosmosPersistence | None = None):
        self._persistence = persistence or CosmosPersistence()

    def invoke(self, tool: str, params: dict[str, Any]) -> Any:
        if tool != "write-item":
            raise ValueError(f"cosmos adapter does not expose tool '{tool}'")
        container = params.get("container")
        if container not in self._CONTAINERS:
            raise ValueError(f"unknown cosmos container '{container}'")
        return self._persistence.write(container, params.get("item", {}))
