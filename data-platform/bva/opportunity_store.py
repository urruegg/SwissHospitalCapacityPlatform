"""Env-driven Cosmos DB store for BVA Opportunity records.

Mirrors the CSA Cosmos helper posture: Azure SDK imports are lazy and optional;
when the endpoint is unset or SDK/client setup is unavailable, writes degrade to a
local dry run and return the document that would have been upserted.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import os
import re
from typing import Any, Callable, Optional

from bva.opportunity import make_opportunity_id, validate_opportunity

COSMOS_ENDPOINT_ENV = "BVA_COSMOS_ENDPOINT"
COSMOS_DATABASE_ENV = "BVA_COSMOS_DATABASE"
DEFAULT_DATABASE = "bva"
OPPORTUNITIES_CONTAINER = "opportunities"
PARTITION_KEY = "/hospitalName"

_HUMAN_ONLY_STATUSES = {"onboarding", "won", "lost"}
_AGENT_EXACT_IDENTITIES = {
    "bva-agent",
    "app-copilot",
    "product-owner-agent",
    "copilot",
    "orchestrator",
    "system",
}
# A standalone 'bot' token or common bot/app suffixes (e.g. GitHub app "name[bot]",
# "handoff-bot"), matched at word boundaries so human names like "Talbot"/"Abbott"
# are NOT misclassified.
_BOT_TOKEN = re.compile(r"(?:^|[^a-z])bot(?:[^a-z]|$)")
_ALLOWED_TRANSITIONS = {
    "new": {"evaluating", "disqualified"},
    "evaluating": {"qualified", "disqualified"},
    "qualified": {"onboarding", "disqualified"},
    "disqualified": set(),
    "onboarding": {"won", "lost"},
    "won": set(),
    "lost": set(),
}

DatabaseClientFactory = Callable[[], Optional[Any]]


def cosmos_configured() -> bool:
    """True when the BVA Cosmos endpoint env var is set."""
    return bool(os.environ.get(COSMOS_ENDPOINT_ENV))


def get_database_client() -> Optional[Any]:
    """Return a Cosmos DatabaseProxy, or None when creds/SDK are unavailable."""
    endpoint = os.environ.get(COSMOS_ENDPOINT_ENV)
    if not endpoint:
        return None
    try:
        from azure.cosmos import CosmosClient  # type: ignore[import-not-found]
        from azure.identity import DefaultAzureCredential  # type: ignore[import-not-found]
    except ImportError:
        return None

    database = os.environ.get(COSMOS_DATABASE_ENV, DEFAULT_DATABASE)
    client = CosmosClient(endpoint, credential=DefaultAzureCredential())
    return client.get_database_client(database)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def append_history(doc: dict[str, Any], event: str, at: str, by: str | None = None) -> dict[str, Any]:
    """Return a copy of ``doc`` with one history event appended."""
    updated = deepcopy(doc)
    history = list(updated.get("history", []))
    entry: dict[str, Any] = {"at": at, "event": event}
    if by is not None:
        entry["by"] = by
    history.append(entry)
    updated["history"] = history
    return updated


def is_agent_identity(by: str | None) -> bool:
    """Return True for known agent/bot identity naming patterns.

    Safety-net heuristic only: the authoritative control is the authenticated
    principal (WIF / OBO identity) enforced at the MCP boundary. This classifier
    is deliberately conservative on both sides — it must not misclassify human
    names that merely contain ``bot`` (e.g. ``Talbot``, ``Abbott``), and it
    treats standalone ``bot`` tokens, an ``[bot]`` suffix, and any ``-agent``
    suffix as agent identities.
    """
    if by is None:
        return False
    identity = by.strip().lower()
    return (
        identity in _AGENT_EXACT_IDENTITIES
        or identity.endswith("-agent")
        or identity.endswith("-bot")
        or identity.endswith("[bot]")
        or bool(_BOT_TOKEN.search(identity))
    )


def is_agent_advance_forbidden(current: str, target: str, by: str | None) -> bool:
    """True when an agent/bot tries to set a human-owned terminal/onboarding status."""
    return target in _HUMAN_ONLY_STATUSES and is_agent_identity(by)


def _ensure_valid_transition(current: str, target: str) -> None:
    if current == target:
        return
    allowed = _ALLOWED_TRANSITIONS.get(current)
    if allowed is None or target not in allowed:
        raise ValueError(f"invalid Opportunity status transition: {current!r} -> {target!r}")


def set_status(doc: dict[str, Any], new_status: str, at: str, by: str) -> dict[str, Any]:
    """Return a copy of ``doc`` with a guarded status transition and audit event."""
    current = str(doc.get("status", ""))
    _ensure_valid_transition(current, new_status)
    if is_agent_advance_forbidden(current, new_status, by):
        raise ValueError(
            f"human-only Opportunity status transition refused for agent identity {by!r}: "
            f"{current!r} -> {new_status!r}"
        )
    updated = append_history(doc, f"status changed from {current} to {new_status}", at, by=by)
    updated["status"] = new_status
    return updated


def _validate_for_upsert(doc: dict[str, Any]) -> None:
    errors = validate_opportunity(doc)
    if errors:
        raise ValueError("invalid BVA Opportunity document: " + "; ".join(errors))


class OpportunityStore:
    """Thin Cosmos-backed Opportunity store with an offline dry-run fallback."""

    def __init__(
        self,
        *,
        container: Any | None = None,
        database_client_factory: DatabaseClientFactory = get_database_client,
    ) -> None:
        self._database_client_factory = database_client_factory
        self._container = container
        self._dry_run_docs: dict[str, dict[str, Any]] = {}
        self.dry_run = container is None and not cosmos_configured()

    def _get_container(self) -> Any | None:
        if self._container is not None:
            return self._container
        if not cosmos_configured():
            self.dry_run = True
            return None
        db = self._database_client_factory()
        if db is None:
            self.dry_run = True
            return None
        self._container = db.get_container_client(OPPORTUNITIES_CONTAINER)
        self.dry_run = False
        return self._container

    def _read_existing(self, opportunity_id: str, hospital_name: str) -> dict[str, Any] | None:
        if self.dry_run:
            existing = self._dry_run_docs.get(opportunity_id)
            return deepcopy(existing) if existing is not None else None
        container = self._get_container()
        if container is None:
            existing = self._dry_run_docs.get(opportunity_id)
            return deepcopy(existing) if existing is not None else None
        try:
            return dict(container.read_item(item=opportunity_id, partition_key=hospital_name))
        except Exception:
            return None

    def upsert(self, doc: dict[str, Any]) -> dict[str, Any]:
        """Validate and upsert one Opportunity, or return the dry-run document."""
        candidate = deepcopy(doc)
        _validate_for_upsert(candidate)
        container = self._get_container()
        if container is None:
            self.dry_run = True
            self._dry_run_docs[candidate["id"]] = deepcopy(candidate)
            return candidate
        result = container.upsert_item(candidate)
        return dict(result) if isinstance(result, dict) else candidate

    def record_ask(
        self,
        hospitalName: str,
        archetype: str,
        askText: str,
        language: str,
        createdBy: str,
        *,
        at: str | None = None,
        status: str = "new",
        bvaResult: dict[str, Any] | None = None,
        poVerdict: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
        historyEvent: str | None = None,
    ) -> dict[str, Any]:
        """Create or update the deterministic Opportunity lineage for a hospital ask."""
        timestamp = at or _utc_now()
        opportunity_id = make_opportunity_id(hospitalName)
        existing = self._read_existing(opportunity_id, hospitalName)

        if existing is None:
            if is_agent_advance_forbidden("new", status, createdBy):
                raise ValueError(
                    "human-only initial Opportunity status refused for agent identity "
                    f"{createdBy!r}: {status!r} (agents may create only up to 'qualified')"
                )
            doc: dict[str, Any] = {
                "id": opportunity_id,
                "hospitalName": hospitalName,
                "archetype": archetype,
                "createdAt": timestamp,
                "createdBy": createdBy,
                "status": status,
                "askText": askText,
                "language": language,
                "bvaResult": bvaResult,
                "poVerdict": poVerdict,
                "inputs": inputs,
                "history": [],
            }
            doc = append_history(doc, historyEvent or "created from BVA ask", timestamp, by=createdBy)
            return self.upsert(doc)

        updated = deepcopy(existing)
        updated["archetype"] = archetype
        updated["askText"] = askText
        updated["language"] = language
        if bvaResult is not None:
            updated["bvaResult"] = bvaResult
        if poVerdict is not None:
            updated["poVerdict"] = poVerdict
        if inputs is not None:
            updated["inputs"] = inputs
        updated = append_history(updated, historyEvent or "updated from BVA re-ask", timestamp, by=createdBy)
        return self.upsert(updated)


__all__ = [
    "COSMOS_DATABASE_ENV",
    "COSMOS_ENDPOINT_ENV",
    "DEFAULT_DATABASE",
    "OPPORTUNITIES_CONTAINER",
    "PARTITION_KEY",
    "OpportunityStore",
    "append_history",
    "cosmos_configured",
    "get_database_client",
    "is_agent_advance_forbidden",
    "is_agent_identity",
    "set_status",
]
