"""Sprint 13 T5 — Fabric tool adapter (read-only grounding queries).

Wraps the ``fabric-mcp`` ``query`` tool to read synthetic Gold Delta tables for
grounding (AGENTS.md §2). Read ceiling only. When no live Fabric client is
injected (dev/CI) it returns deterministic synthetic rows so the orchestrator
can be exercised end-to-end without a live workspace. Synthetic-only, no PHI
(ADR-0016).
"""

from __future__ import annotations

from typing import Any, Callable


class FabricAdapter:
    server = "fabric-mcp"
    ceiling = "read"

    def __init__(self, query_fn: Callable[[str], list[dict[str, Any]]] | None = None):
        # ``query_fn`` is the live client; absent → synthetic grounding rows.
        self._query_fn = query_fn

    def invoke(self, tool: str, params: dict[str, Any]) -> Any:
        if tool != "query":
            raise ValueError(f"fabric-mcp adapter does not expose tool '{tool}'")
        table = params.get("table", "")
        return self.query(table)

    def query(self, table: str) -> list[dict[str, Any]]:
        if self._query_fn is not None:
            return self._query_fn(table)
        # Deterministic synthetic grounding sample keyed by table name.
        samples: dict[str, list[dict[str, Any]]] = {
            "gold.bed_assignment": [
                {"ward": "B", "occupied": 46, "capacity": 50},
            ],
            "gold.fact_capacity_baseline": [
                {"ward": "B", "baseline_capacity": 50},
            ],
            "gold.discharge_score": [
                {"ward": "B", "ready_for_discharge": 4},
            ],
        }
        return samples.get(table, [])
