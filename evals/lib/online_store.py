"""Interaction source/sink seams for the online-eval job (Sprint 30 M4).

The online job reads recent ``agent_interactions`` and writes evaluation
verdicts back. Those reads/writes go through narrow Protocols so the job runs
against an in-memory fixture in CI and a live Cosmos container in production.

The Cosmos-backed store is built lazily from the environment (mirroring the M1
Azure Monitor exporter seam): the ``azure-cosmos`` SDK is imported only when the
``COSMOS_*`` variables are set, so unit tests / CI never load it.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

import os

Record = dict[str, Any]


@runtime_checkable
class InteractionSource(Protocol):
    """Read side: recent interaction records, optionally filtered by agent."""

    def read_recent(self, *, agent: str | None, limit: int) -> list[Record]: ...


@runtime_checkable
class InteractionSink(Protocol):
    """Write side: persist an evaluation verdict back onto a record."""

    def update_eval(self, interaction_id: str, eval_block: dict[str, Any]) -> None: ...


class InMemoryStore(InteractionSource, InteractionSink):
    """In-memory source + sink for tests and local dry-runs."""

    def __init__(self, records: list[Record] | None = None) -> None:
        self._by_id: dict[str, Record] = {}
        self._order: list[str] = []
        for rec in records or []:
            self._by_id[rec["interactionId"]] = rec
            self._order.append(rec["interactionId"])

    def read_recent(self, *, agent: str | None, limit: int) -> list[Record]:
        out: list[Record] = []
        # Most-recent-first: the job samples the freshest window.
        for iid in reversed(self._order):
            rec = self._by_id[iid]
            if agent is not None and rec.get("agent") != agent:
                continue
            out.append(rec)
            if len(out) >= limit:
                break
        return out

    def update_eval(self, interaction_id: str, eval_block: dict[str, Any]) -> None:
        if interaction_id not in self._by_id:
            raise KeyError(interaction_id)
        self._by_id[interaction_id]["eval"] = eval_block


def build_store_from_env() -> InteractionSource | None:
    """Return a Cosmos-backed store iff the ``COSMOS_*`` env is configured.

    The azure SDK is imported lazily inside the branch so CI never loads it.
    Returns ``None`` when unconfigured (the caller supplies an in-memory store).
    """
    endpoint = os.environ.get("COSMOS_ENDPOINT")
    database = os.environ.get("COSMOS_DATABASE")
    container = os.environ.get("COSMOS_CONTAINER")
    if not (endpoint and database and container):
        return None
    try:
        from lib.online_cosmos import CosmosInteractionStore
    except Exception:  # pragma: no cover - optional dep not installed
        return None
    return CosmosInteractionStore(endpoint, database, container)
