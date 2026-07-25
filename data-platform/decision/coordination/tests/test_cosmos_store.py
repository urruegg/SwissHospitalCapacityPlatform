"""Unit tests for the Cosmos-backed :class:`PlanStore` (Sprint 26 WS-C).

Runs without the ``azure-cosmos`` SDK or any network: a
:class:`FakeContainer` implements the tiny slice of the Cosmos container API the
store depends on (``create_item`` / ``read_item`` / ``upsert_item`` /
``query_items``) with the same not-found (404) / conflict (409) semantics. The
tests assert that :class:`CosmosStore` honours the abstract
:class:`~coordination.store.PlanStore` contract exercised by the runtime, that
it writes documents into the correct partition-keyed containers, and that
``list_actions`` preserves insertion order deterministically.
"""
from __future__ import annotations

import copy
import unittest
from typing import Any, Dict, List, Optional

from coordination.cosmos_store import CosmosStore
from coordination.store import InMemoryStore


class _FakeStatusError(Exception):
    """Mimics an ``azure.cosmos`` error carrying an HTTP ``status_code``."""

    def __init__(self, status_code: int) -> None:
        super().__init__(f"status {status_code}")
        self.status_code = status_code


class FakeContainer:
    """In-memory stand-in for a Cosmos container client.

    Stores items by ``id`` and enforces the create/read semantics the store
    relies on: ``create_item`` raises 409 on a duplicate id, ``read_item``
    raises 404 when absent, ``query_items`` filters on ``id`` or on the
    partition-key field.
    """

    def __init__(self, partition_key_field: str) -> None:
        self.partition_key_field = partition_key_field
        self._items: Dict[str, Dict[str, Any]] = {}

    def create_item(self, body: Dict[str, Any]) -> Dict[str, Any]:
        if body["id"] in self._items:
            raise _FakeStatusError(409)
        self._items[body["id"]] = copy.deepcopy(body)
        return copy.deepcopy(body)

    def read_item(self, item: str, partition_key: Any) -> Dict[str, Any]:
        stored = self._items.get(item)
        if stored is None or stored[self.partition_key_field] != partition_key:
            raise _FakeStatusError(404)
        return copy.deepcopy(stored)

    def upsert_item(self, body: Dict[str, Any]) -> Dict[str, Any]:
        self._items[body["id"]] = copy.deepcopy(body)
        return copy.deepcopy(body)

    def query_items(
        self,
        query: str,
        parameters: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        params = {p["name"]: p["value"] for p in (parameters or [])}
        results: List[Dict[str, Any]] = []
        for stored in self._items.values():
            if "@id" in params and stored["id"] == params["@id"]:
                results.append(copy.deepcopy(stored))
            elif "@pid" in params and stored.get("plan_id") == params["@pid"]:
                results.append(copy.deepcopy(stored))
        return results


def _make_store() -> CosmosStore:
    return CosmosStore(
        plans_container=FakeContainer("episode_key"),
        actions_container=FakeContainer("plan_id"),
    )


def _plan(plan_id: str = "plan-EP-1", episode_key: str = "EP-1") -> Dict[str, Any]:
    return {"id": plan_id, "episode_key": episode_key, "actions": [], "current_pct": 100}


def _action(action_id: str, plan_id: str = "plan-EP-1") -> Dict[str, Any]:
    return {"id": action_id, "plan_id": plan_id, "status": "proposed"}


class TestCosmosStorePlans(unittest.TestCase):
    def test_create_then_get_plan(self):
        store = _make_store()
        store.create_plan(_plan())
        got = store.get_plan("plan-EP-1")
        self.assertIsNotNone(got)
        self.assertEqual(got["episode_key"], "EP-1")

    def test_get_missing_plan_returns_none(self):
        self.assertIsNone(_make_store().get_plan("nope"))

    def test_create_duplicate_plan_raises_value_error(self):
        store = _make_store()
        store.create_plan(_plan())
        with self.assertRaises(ValueError):
            store.create_plan(_plan())

    def test_upsert_plan_inserts_and_replaces(self):
        store = _make_store()
        store.upsert_plan(_plan())
        updated = _plan()
        updated["current_pct"] = 88
        store.upsert_plan(updated)
        self.assertEqual(store.get_plan("plan-EP-1")["current_pct"], 88)

    def test_get_plan_returns_isolated_copy(self):
        store = _make_store()
        store.create_plan(_plan())
        got = store.get_plan("plan-EP-1")
        got["current_pct"] = -1
        self.assertEqual(store.get_plan("plan-EP-1")["current_pct"], 100)


class TestCosmosStoreActions(unittest.TestCase):
    def test_create_then_get_action(self):
        store = _make_store()
        store.create_action(_action("plan-EP-1-action-0"))
        self.assertEqual(store.get_action("plan-EP-1-action-0")["status"], "proposed")

    def test_create_duplicate_action_raises_value_error(self):
        store = _make_store()
        store.create_action(_action("plan-EP-1-action-0"))
        with self.assertRaises(ValueError):
            store.create_action(_action("plan-EP-1-action-0"))

    def test_get_missing_action_returns_none(self):
        self.assertIsNone(_make_store().get_action("nope"))

    def test_upsert_action_replaces(self):
        store = _make_store()
        store.create_action(_action("plan-EP-1-action-0"))
        updated = _action("plan-EP-1-action-0")
        updated["status"] = "applied"
        store.upsert_action(updated)
        self.assertEqual(store.get_action("plan-EP-1-action-0")["status"], "applied")

    def test_list_actions_preserves_insertion_order(self):
        store = _make_store()
        # Insert out of natural order to prove we sort by the id index suffix.
        for i in (0, 2, 1, 10):
            store.create_action(_action(f"plan-EP-1-action-{i}"))
        ids = [a["id"] for a in store.list_actions("plan-EP-1")]
        self.assertEqual(
            ids,
            [
                "plan-EP-1-action-0",
                "plan-EP-1-action-1",
                "plan-EP-1-action-2",
                "plan-EP-1-action-10",
            ],
        )

    def test_list_actions_scopes_by_plan(self):
        store = _make_store()
        store.create_action(_action("plan-EP-1-action-0", plan_id="plan-EP-1"))
        store.create_action(_action("plan-EP-2-action-0", plan_id="plan-EP-2"))
        self.assertEqual(len(store.list_actions("plan-EP-1")), 1)


class TestCosmosStoreMatchesInMemoryContract(unittest.TestCase):
    """The Cosmos store must be swap-compatible with the in-memory store the
    runtime tests use: identical observable behaviour on the same call sequence."""

    def _run_sequence(self, store):
        store.create_plan(_plan())
        store.create_action(_action("plan-EP-1-action-0"))
        store.create_action(_action("plan-EP-1-action-1"))
        return [a["id"] for a in store.list_actions("plan-EP-1")]

    def test_parity_with_in_memory_store(self):
        self.assertEqual(
            self._run_sequence(_make_store()),
            self._run_sequence(InMemoryStore()),
        )


if __name__ == "__main__":
    unittest.main()
