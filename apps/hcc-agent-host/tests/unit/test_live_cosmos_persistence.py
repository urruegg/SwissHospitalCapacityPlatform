"""Unit tests for LiveCosmosPersistence + build_cosmos_persistence (config-gated,
mirrors _build_chat_model's guarded-optional pattern). No live Cosmos needed --
the container client is dependency-injected."""
from __future__ import annotations

import pytest

from persistence.cosmos_client import (
    CosmosPersistence,
    LiveCosmosPersistence,
    build_cosmos_persistence,
)


class _FakeContainer:
    def __init__(self):
        self.items: list[dict] = []

    def upsert_item(self, record: dict) -> None:
        self.items = [i for i in self.items if i.get("id") != record.get("id")]
        self.items.append(record)

    def read_all_items(self):
        return list(self.items)

    def query_items(self, query, parameters, enable_cross_partition_query=False, partition_key=None):
        # Minimal fake: only supports the two equality queries this module issues.
        field = "correlationId" if "correlationId" in query else "interactionId"
        value = parameters[0]["value"]
        return [i for i in self.items if i.get(field) == value]


def _factory(containers: dict[str, _FakeContainer]):
    return lambda name: containers[name]


def test_build_cosmos_persistence_without_endpoint_is_in_memory(monkeypatch):
    monkeypatch.delenv("COSMOS_ENDPOINT", raising=False)
    persistence = build_cosmos_persistence()
    assert isinstance(persistence, CosmosPersistence)


def test_build_cosmos_persistence_with_endpoint_is_live(monkeypatch):
    monkeypatch.setenv("COSMOS_ENDPOINT", "https://cosmos-ihzhhpf-sit.documents.azure.com:443/")
    containers = {"approval-events": _FakeContainer()}
    persistence = build_cosmos_persistence(container_client_factory=_factory(containers))
    assert isinstance(persistence, LiveCosmosPersistence)


def test_live_persistence_write_and_query_by_correlation():
    containers = {"approval-events": _FakeContainer()}
    persistence = LiveCosmosPersistence(_container_for=_factory(containers))
    record = persistence.write("approval-events", {"correlationId": "gt-1", "decision": "accept"})
    assert record["id"]
    found = persistence.query_by_correlation("approval-events", "gt-1")
    assert found == [record]


def test_live_persistence_write_missing_partition_key_raises():
    containers = {"approval-events": _FakeContainer()}
    persistence = LiveCosmosPersistence(_container_for=_factory(containers))
    with pytest.raises(ValueError):
        persistence.write("approval-events", {"decision": "accept"})


def test_live_persistence_append_user_event():
    containers = {"agent_interactions": _FakeContainer()}
    persistence = LiveCosmosPersistence(_container_for=_factory(containers))
    persistence.write("agent_interactions", {
        "conversationKey": "user1:bmca-agent", "interactionId": "i1",
    })
    updated = persistence.append_user_event("i1", {"type": "click"})
    assert updated["userEvents"] == [{"type": "click"}]


def test_live_persistence_append_user_event_unknown_id_raises():
    containers = {"agent_interactions": _FakeContainer()}
    persistence = LiveCosmosPersistence(_container_for=_factory(containers))
    with pytest.raises(KeyError):
        persistence.append_user_event("nope", {"type": "click"})
