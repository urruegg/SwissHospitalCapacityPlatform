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
