"""WS-D Class D ontology: read-only query surface over the Fabric Data Agent.

Implements the frozen Class D tool signature::

    ontologyQuery(question: str) -> GroundedChunk[]

Wraps the read-only ``da_hospital_capacity`` Fabric Data Agent
(ADR-0034 demo artefact). Every emitted ``GroundedChunk`` (classId
``D``) is **required** to carry ``citation.conceptRef`` AND
``citation.goldBinding``; any data-agent row missing either binding is
dropped (grounded refusal, never an ungrounded answer).

The Preview per-capacity gate (issue #270) is feature-flagged via
``preview_enabled``: when the capacity has not opted into the Fabric
Data Agent Preview, the surface returns ``[]``. Rows the agent marks
``stale`` degrade to ``liveness="snapshot"`` while still carrying their
concept + gold binding.

Read-only: the injected client exposes only ``ask(question)``; no
mutation is performed. The live client is injected so CI supplies a
fake and no network call is made.
"""

from __future__ import annotations

import datetime as _dt
import re
from typing import Any, Optional

CLASS_ID = "D"

DATA_AGENT_NAME = "da_hospital_capacity"
DATA_AGENT_ID = "b2e53c23-182a-452d-9321-e63f6009e80b"
SOURCE_REF = f"fabric-data-agent:{DATA_AGENT_NAME} ({DATA_AGENT_ID})"


def _as_datetime(value: str) -> str:
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return f"{value}T00:00:00Z"
    return value


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _clamp_confidence(value: Any) -> float:
    try:
        c = float(value)
    except (TypeError, ValueError):
        return 0.7
    return max(0.0, min(1.0, c))


def _to_grounded_chunk(row: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Map one data-agent row to a Class D GroundedChunk, or None if ungrounded."""

    concept = str(row.get("conceptRef") or "").strip()
    gold = str(row.get("goldBinding") or "").strip()
    text = str(row.get("answer") or "").strip()
    # Class D grounding rule: concept + gold binding + text are mandatory.
    if not concept or not gold or not text:
        return None

    stale = bool(row.get("stale", False))
    return {
        "classId": CLASS_ID,
        "text": text,
        "citation": {
            "sourceRef": str(row.get("sourceRef") or SOURCE_REF),
            "conceptRef": concept,
            "goldBinding": gold,
        },
        "asOf": _as_datetime(str(row.get("asOf") or _now())),
        "liveness": "snapshot" if stale else "live",
        "status": "partial" if stale else str(row.get("status") or "verified"),
        "confidence": _clamp_confidence(row.get("confidence", 0.8)),
        "language": str(row.get("language") or "en"),
    }


def ontologyQuery(
    question: str,
    data_agent_client: Any = None,
    preview_enabled: bool = True,
) -> list[dict[str, Any]]:
    """Answer a data/ontology question read-only via the Fabric Data Agent.

    Returns Class D GroundedChunks each carrying concept + gold-binding
    citations. Returns ``[]`` when the Preview gate is disabled, the
    client is absent, the agent errors, or no row is fully grounded.
    """

    # Preview per-capacity gate (#270).
    if not preview_enabled or data_agent_client is None:
        return []

    try:
        rows = data_agent_client.ask(question)
    except Exception:
        # Cannot ground without a concept binding -> grounded refusal.
        return []

    if isinstance(rows, dict):
        rows = [rows]

    chunks = []
    for row in rows or []:
        chunk = _to_grounded_chunk(row)
        if chunk is not None:
            chunks.append(chunk)
    return chunks


# ---------------------------------------------------------------------------
# WS-RET Task RET.2: real client wiring for the shared da_hospital_capacity
# Fabric Data Agent connection (ADR-0034/ADR-0033).
#
# Reuses the EXACT connection values ``ooa-agent`` already proves work
# (apps/hcc-agent-host/src/tools/fabric_data_agent_client.py):
#   * env vars FABRIC_DATA_AGENT_ENDPOINT / FABRIC_WORKSPACE_ID /
#     FABRIC_DATA_AGENT_ID (agent-host's ``_build_live_data_agent``)
#   * api-version "2024-05-01-preview" (that client's ``_API_VERSION``)
#   * bearer-token scope "https://api.fabric.microsoft.com/.default" via
#     DefaultAzureCredential (that client's ``_default_token_provider``)
#
# NOT the openai SDK / AzureOpenAI, and NOT api-version 2025-05-15-preview -
# that version string belongs to the unrelated Foundry Agent Service
# control-plane API (data-platform/decision/foundry/live_factory.py),
# a different surface entirely. The published Fabric Data Agent consumption
# endpoint speaks the OpenAI *Assistants* protocol over a raw HTTP client,
# which is reimplemented here (not imported) because the PO agent service
# and agent-host are separately deployed containers with no shared source
# tree.
# ---------------------------------------------------------------------------

_FABRIC_SCOPE = "https://api.fabric.microsoft.com/.default"
_API_VERSION = "2024-05-01-preview"
_TERMINAL_OK = "completed"
_TERMINAL_BAD = {"failed", "cancelled", "canceled", "expired"}
_CITATION_RE = re.compile(
    r"(?:hcp:[A-Za-z_][\w/]*|dim_[A-Za-z0-9_]+|fact_[A-Za-z0-9_]+|gold\.[A-Za-z0-9_.]+)"
)


def _default_token_provider() -> str:
    from azure.identity import DefaultAzureCredential

    return DefaultAzureCredential().get_token(_FABRIC_SCOPE).token


def _default_http_request(method: str, url: str, headers=None, json=None, timeout=None):
    import requests

    return requests.request(method, url, headers=headers, json=json, timeout=timeout)


def _extract_citations(answer: str) -> list[str]:
    seen: list[str] = []
    for match in _CITATION_RE.findall(answer):
        if match not in seen:
            seen.append(match)
    return seen


class _RawFabricDataAgentClient:
    """Real Fabric Data Agent HTTP client (OpenAI Assistants protocol).

    Reimplements (does not import)
    ``apps/hcc-agent-host/src/tools/fabric_data_agent_client.py``'s proven
    create-assistant -> thread -> message -> run -> poll -> messages
    sequence: same endpoint/workspace/data-agent-id wiring, api-version,
    and Fabric bearer-token scope as ``ooa-agent``'s live connection.
    """

    def __init__(
        self,
        endpoint: str,
        workspace_id: str,
        data_agent_id: str,
        token_provider: Any,
        http_request: Any = None,
        timeout: int = 60,
        poll_interval: float = 1.0,
        max_polls: int = 120,
        api_version: str = _API_VERSION,
    ) -> None:
        self._endpoint = (endpoint or "").rstrip("/")
        self._workspace_id = workspace_id
        self._data_agent_id = data_agent_id
        self._token_provider = token_provider
        self._http_request = http_request or _default_http_request
        self._timeout = timeout
        self._poll_interval = poll_interval
        self._max_polls = max_polls
        self._api_version = api_version

    def _url(self, path: str) -> str:
        return f"{self._endpoint}{path}?api-version={self._api_version}"

    def _call(self, method: str, path: str, headers: dict, body: Any = None) -> dict:
        resp = self._http_request(
            method, self._url(path), headers=headers, json=body, timeout=self._timeout
        )
        resp.raise_for_status()
        return resp.json()

    def ask(self, question: str) -> dict[str, Any]:
        import time as _time

        headers = {
            "Authorization": f"Bearer {self._token_provider()}",
            "Content-Type": "application/json",
        }
        assistant_id = self._call("POST", "/assistants", headers, {}).get("id")
        thread_id = self._call("POST", "/threads", headers, {}).get("id")
        self._call(
            "POST",
            f"/threads/{thread_id}/messages",
            headers,
            {"role": "user", "content": question},
        )
        run_id = self._call(
            "POST", f"/threads/{thread_id}/runs", headers, {"assistant_id": assistant_id}
        ).get("id")

        status = ""
        for _ in range(self._max_polls):
            run = self._call("GET", f"/threads/{thread_id}/runs/{run_id}", headers)
            status = str(run.get("status", "")).lower()
            if status == _TERMINAL_OK:
                break
            if status in _TERMINAL_BAD:
                raise RuntimeError(f"Fabric Data Agent run {run_id} {status}")
            if self._poll_interval:
                _time.sleep(self._poll_interval)
        else:
            raise RuntimeError(f"Fabric Data Agent run {run_id} did not complete (last={status})")

        messages = self._call("GET", f"/threads/{thread_id}/messages", headers)
        answer = self._first_assistant_text(messages)
        refused = "REFUSE:" in answer.upper()
        citations: list[str] = [] if refused else _extract_citations(answer)
        return {"answer": answer, "citations": citations, "refused": refused}

    @staticmethod
    def _first_assistant_text(messages: dict[str, Any]) -> str:
        for message in messages.get("data") or []:
            if message.get("role") != "assistant":
                continue
            parts = [
                (part.get("text") or {}).get("value", "")
                for part in (message.get("content") or [])
                if part.get("type") == "text"
            ]
            text = "".join(p for p in parts if p).strip()
            if text:
                return text
        return ""


def _openai_assistants_client(**kwargs: Any) -> Any:
    """Factory name mirrors the OpenAI Assistants protocol the published
    Fabric Data Agent endpoint speaks - the real ooa-agent connection is a
    raw HTTP client (:class:`_RawFabricDataAgentClient`), not the ``openai``
    SDK."""
    return _RawFabricDataAgentClient(**kwargs)


class _OntologyGroundedClient:
    """Adapt the raw Fabric Data Agent free-text answer into the Class D row
    shape :func:`ontologyQuery` requires.

    The real Fabric Data Agent connection returns
    ``{"answer", "citations", "refused"}`` (agent-host's proven contract),
    not structured ``conceptRef``/``goldBinding`` fields. This adapter takes
    the first ``hcp:*`` citation as the concept binding and the first
    ``dim_*``/``fact_*``/``gold.*`` citation as the gold binding; a row
    missing either is dropped here (before :func:`ontologyQuery` even sees
    it), same grounded-refusal outcome as the pure-logic drop rule.
    """

    def __init__(self, raw_client: Any) -> None:
        self._raw = raw_client

    def ask(self, question: str) -> list[dict[str, Any]]:
        result = self._raw.ask(question)
        if result.get("refused") or not result.get("answer"):
            return []
        citations = result.get("citations", [])
        concept = next((c for c in citations if c.startswith("hcp:")), "")
        gold = next(
            (c for c in citations if c.startswith(("dim_", "fact_", "gold."))), ""
        )
        if not concept or not gold:
            return []
        return [
            {
                "conceptRef": concept,
                "goldBinding": gold,
                "answer": result["answer"],
                "sourceRef": SOURCE_REF,
            }
        ]


def build_production_client() -> Any:
    """Build the real Class D client for the shared ``da_hospital_capacity``
    Fabric Data Agent (ADR-0034), reusing the exact env vars, api-version,
    and auth scope ``ooa-agent`` already proves work in
    ``apps/hcc-agent-host/src/tools/fabric_data_agent_client.py``.
    """
    import os

    raw_client = _openai_assistants_client(
        endpoint=os.environ.get("FABRIC_DATA_AGENT_ENDPOINT", ""),
        workspace_id=os.environ.get("FABRIC_WORKSPACE_ID", ""),
        data_agent_id=os.environ.get("FABRIC_DATA_AGENT_ID", DATA_AGENT_ID),
        token_provider=_default_token_provider,
    )
    return _OntologyGroundedClient(raw_client)
