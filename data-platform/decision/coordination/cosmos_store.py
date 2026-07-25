"""Cosmos-backed :class:`~coordination.store.PlanStore` (Sprint 26 WS-C).

Thin, RBAC-only implementation of the abstract plan store over the two Cosmos
containers defined in ``infra/modules/cosmos/csa.bicep``:

* ``plans``            partition key ``/episode_key``  (item id = ``plan['id']``)
* ``proposed_actions`` partition key ``/plan_id``      (item id = ``action['id']``)

The runtime never depends on this class directly — it takes any
:class:`PlanStore`. Live use is HITL-gated (``AGENTS.md`` §4) and, per ADR-0029,
only reachable from inside the SIT VNet (the account has
``publicNetworkAccess = Disabled`` + a private endpoint), so this store is
exercised in CI purely through injected fake container clients. Auth is
RBAC/managed-identity only (``disableLocalAuth = true`` in the T1 Bicep) — no
account keys.

Construct either by injecting container clients (tests) or, in a live in-VNet
context, via :meth:`CosmosStore.from_env`, which returns ``None`` when Cosmos is
unconfigured or the ``azure-cosmos`` SDK is absent so callers degrade to a dry
run rather than failing.
"""
from __future__ import annotations

import copy
import os
import re
from typing import Any, Dict, List, Optional

from coordination.store import PlanStore

PLANS_CONTAINER = "plans"
ACTIONS_CONTAINER = "proposed_actions"

COSMOS_ENDPOINT_ENV = "CSA_COSMOS_ENDPOINT"
COSMOS_DATABASE_ENV = "CSA_COSMOS_DATABASE"

#: Trailing integer of a deterministic action id (``{plan_id}-action-{n}``),
#: used to restore insertion order from an unordered Cosmos partition query.
_ACTION_SEQ_RE = re.compile(r"-action-(\d+)$")


def _status_code(exc: Exception) -> Optional[int]:
    """Best-effort extraction of an HTTP status from a Cosmos SDK error.

    ``azure.cosmos`` errors expose ``status_code``; the fake container used in
    tests mirrors that attribute. Returns ``None`` when absent.
    """
    return getattr(exc, "status_code", None)


def _action_seq(action_id: str) -> int:
    match = _ACTION_SEQ_RE.search(action_id)
    return int(match.group(1)) if match else 0


class CosmosStore(PlanStore):
    """:class:`PlanStore` backed by two partition-keyed Cosmos containers.

    Documents are stored verbatim: ``plan``/``action`` dicts already carry both
    their ``id`` and their partition-key field (``episode_key`` / ``plan_id``),
    so no shape translation is needed. Every read returns a deep copy for the
    same caller-isolation guarantee :class:`InMemoryStore` provides.
    """

    def __init__(self, plans_container: Any, actions_container: Any) -> None:
        self._plans = plans_container
        self._actions = actions_container

    # -- construction ------------------------------------------------------

    @classmethod
    def from_env(cls) -> Optional["CosmosStore"]:
        """Build from ``CSA_COSMOS_ENDPOINT`` using RBAC creds, or ``None``.

        Returns ``None`` when the endpoint env var is unset or the
        ``azure-cosmos`` / ``azure-identity`` SDKs are not installed, so callers
        can fall back to a dry run. Never uses account keys.
        """
        endpoint = os.environ.get(COSMOS_ENDPOINT_ENV)
        if not endpoint:
            return None
        try:
            from azure.cosmos import CosmosClient  # type: ignore
            from azure.identity import DefaultAzureCredential  # type: ignore
        except ImportError:
            return None

        database_name = os.environ.get(COSMOS_DATABASE_ENV, "csa")
        client = CosmosClient(endpoint, credential=DefaultAzureCredential())
        database = client.get_database_client(database_name)
        return cls(
            plans_container=database.get_container_client(PLANS_CONTAINER),
            actions_container=database.get_container_client(ACTIONS_CONTAINER),
        )

    # -- plans -------------------------------------------------------------

    def create_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self._plans.create_item(body=plan)
        except Exception as exc:  # noqa: BLE001 - re-raised unless it is a 409
            if _status_code(exc) == 409:
                raise ValueError(f"plan already exists: {plan['id']!r}")
            raise
        return copy.deepcopy(plan)

    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        return self._query_one(self._plans, plan_id)

    def upsert_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        self._plans.upsert_item(body=plan)
        return copy.deepcopy(plan)

    # -- actions -----------------------------------------------------------

    def create_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self._actions.create_item(body=action)
        except Exception as exc:  # noqa: BLE001 - re-raised unless it is a 409
            if _status_code(exc) == 409:
                raise ValueError(f"action already exists: {action['id']!r}")
            raise
        return copy.deepcopy(action)

    def get_action(self, action_id: str) -> Optional[Dict[str, Any]]:
        return self._query_one(self._actions, action_id)

    def upsert_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        self._actions.upsert_item(body=action)
        return copy.deepcopy(action)

    def list_actions(self, plan_id: str) -> List[Dict[str, Any]]:
        rows = list(
            self._actions.query_items(
                query="SELECT * FROM c WHERE c.plan_id = @pid",
                parameters=[{"name": "@pid", "value": plan_id}],
                partition_key=plan_id,
            )
        )
        rows.sort(key=lambda a: _action_seq(a["id"]))
        return [copy.deepcopy(row) for row in rows]

    # -- internals ---------------------------------------------------------

    @staticmethod
    def _query_one(container: Any, item_id: str) -> Optional[Dict[str, Any]]:
        """Return a single document by ``id`` (cross-partition), or ``None``.

        A cross-partition ``id`` query is used rather than ``read_item`` so the
        caller need not know the partition-key value for a lookup keyed only by
        ``id`` (the runtime looks plans up by ``plan_id`` and actions by
        ``action_id``).
        """
        rows = list(
            container.query_items(
                query="SELECT * FROM c WHERE c.id = @id",
                parameters=[{"name": "@id", "value": item_id}],
                enable_cross_partition_query=True,
            )
        )
        return copy.deepcopy(rows[0]) if rows else None
