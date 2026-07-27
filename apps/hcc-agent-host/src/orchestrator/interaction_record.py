"""Sprint 30 M0 — build a DC-AGENT-INTERACTION-v1 record for one agent turn.

Pure + deterministic (apart from id/timestamp). PHI-free by construction: the raw
prompt is hashed (never stored) and prompt/answer text pass through the existing
redaction gate before persistence (design §6; ADR-0016).
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any

from orchestrator.redaction import redact

CONTRACT_ID = "DC-AGENT-INTERACTION-v1"


def prompt_hash(prompt: str) -> str:
    """Return ``sha256:<hex>`` for dedup / regression matching without retaining text."""
    return "sha256:" + hashlib.sha256((prompt or "").encode("utf-8")).hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_interaction_record(
    *,
    agent: str,
    conversation_key: str,
    prompt: str,
    answer: str,
    citations: list[str],
    refused: bool,
    reco: dict[str, Any] | None = None,
    lang: str | None = None,
    scope: dict[str, Any] | None = None,
    model: dict[str, Any] | None = None,
    tools: list[dict[str, Any]] | None = None,
    total_ms: int = 0,
    provenance: str = "simulated",
    env: str = "sit",
    region: str = "eastus2",
    ts: str | None = None,
) -> dict[str, Any]:
    """Assemble one contract-shaped, redacted interaction record."""
    return {
        "contractId": CONTRACT_ID,
        "interactionId": f"AIX-{uuid.uuid4().hex}",
        "conversationKey": conversation_key,
        "agent": agent,
        "ts": ts or _now_iso(),
        "env": env,
        "region": region,
        "scope": scope or {},
        "request": {
            "promptHash": prompt_hash(prompt),
            "promptRedacted": redact(prompt),
            "lang": lang,
        },
        "response": {
            "answerRedacted": redact(answer),
            "citations": list(citations),
            "refused": refused,
            "reco": reco,
        },
        "model": model or {},
        "tools": tools or [],
        "timing": {"totalMs": total_ms},
        "provenance": provenance,
        "userEvents": [],
        "eval": {"scored": False},
    }
