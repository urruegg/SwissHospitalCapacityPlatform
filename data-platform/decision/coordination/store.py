"""Persistence abstraction for the coordination runtime (Sprint 26 WS-C).

Mirrors the two Cosmos containers added in T5 (``9d59999``): ``plans``
(partition key ``/episode_key``) and ``proposed_actions`` (partition key
``/plan_id``). :class:`PlanStore` is an abstract protocol so a future
``CosmosStore`` (backed by the ``cosmos-mcp`` allow-listed server, per
``AGENTS.md`` Sec 2) can implement the same surface. **This module contains no
live Cosmos/network calls** — per governance, any live deploy of a
``CosmosStore`` is HITL-gated (``AGENTS.md`` Sec 4) and out of scope for this
task. The only implementation here is :class:`InMemoryStore`, a deterministic,
dict-backed store used by tests and the Slice 1 seed script.
"""
from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class PlanStore(ABC):
    """Abstract persistence surface for ``plans`` and ``proposed_actions``.

    Implementations must be side-effect isolated per call: callers may mutate
    the dicts they pass in or receive back without corrupting store state
    (see :class:`InMemoryStore`, which deep-copies on every read/write).
    """

    @abstractmethod
    def create_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new plan. Raise ``ValueError`` if ``plan['id']`` already exists."""

    @abstractmethod
    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Return the plan for ``plan_id``, or ``None`` if not found."""

    @abstractmethod
    def upsert_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or replace the plan keyed by ``plan['id']``."""

    @abstractmethod
    def create_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new proposed action. Raise ``ValueError`` if ``action['id']`` exists."""

    @abstractmethod
    def get_action(self, action_id: str) -> Optional[Dict[str, Any]]:
        """Return the action for ``action_id``, or ``None`` if not found."""

    @abstractmethod
    def upsert_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or replace the action keyed by ``action['id']``."""

    @abstractmethod
    def list_actions(self, plan_id: str) -> List[Dict[str, Any]]:
        """Return all actions for ``plan_id``, in insertion order."""


class InMemoryStore(PlanStore):
    """Deterministic, dict-backed :class:`PlanStore`. NOT for production use —
    there is no persistence beyond the process, and no concurrency control.
    Intended for tests and the Slice 1 seed script only."""

    def __init__(self) -> None:
        self._plans: Dict[str, Dict[str, Any]] = {}
        self._actions: Dict[str, Dict[str, Any]] = {}
        # Preserve insertion order for list_actions() determinism.
        self._action_order: List[str] = []

    def create_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        plan_id = plan["id"]
        if plan_id in self._plans:
            raise ValueError(f"plan already exists: {plan_id!r}")
        self._plans[plan_id] = copy.deepcopy(plan)
        return copy.deepcopy(plan)

    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        plan = self._plans.get(plan_id)
        return copy.deepcopy(plan) if plan is not None else None

    def upsert_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        self._plans[plan["id"]] = copy.deepcopy(plan)
        return copy.deepcopy(plan)

    def create_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        action_id = action["id"]
        if action_id in self._actions:
            raise ValueError(f"action already exists: {action_id!r}")
        self._actions[action_id] = copy.deepcopy(action)
        self._action_order.append(action_id)
        return copy.deepcopy(action)

    def get_action(self, action_id: str) -> Optional[Dict[str, Any]]:
        action = self._actions.get(action_id)
        return copy.deepcopy(action) if action is not None else None

    def upsert_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        action_id = action["id"]
        if action_id not in self._actions:
            self._action_order.append(action_id)
        self._actions[action_id] = copy.deepcopy(action)
        return copy.deepcopy(action)

    def list_actions(self, plan_id: str) -> List[Dict[str, Any]]:
        return [
            copy.deepcopy(self._actions[action_id])
            for action_id in self._action_order
            if self._actions[action_id]["plan_id"] == plan_id
        ]
