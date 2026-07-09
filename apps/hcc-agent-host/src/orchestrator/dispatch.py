"""Sprint 13 T5 — agent orchestrator.

Composes the system prompt + grounding + tool contracts per an
:class:`~manifests.loader.AgentManifest`, dispatches to a Microsoft Foundry chat
model (ADR-0008: Foundry = model provider only), redacts the output, persists the
conversation + audit records (ADR-0007), and returns a grounded reply.

The chat model is injected as a :class:`ChatModel` so the host can run against a
live Foundry deployment in production and a deterministic mock in dev/CI.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Protocol

from manifests.loader import AgentManifest
from tools.fabric_adapter import FabricAdapter
from cache.redis_client import RedisCache
from persistence.cosmos_client import CosmosPersistence
from orchestrator.redaction import redact, contains_sensitive


class ChatModel(Protocol):
    """Foundry chat-completion surface (ADR-0008)."""

    def complete(self, system_prompt: str, user_prompt: str, grounding: list[dict[str, Any]]) -> str:
        ...


@dataclass(frozen=True)
class GroundedReply:
    answer: str
    citations: tuple[str, ...]
    refused: bool
    correlation_id: str


@dataclass
class Orchestrator:
    chat_model: ChatModel
    fabric: FabricAdapter = field(default_factory=FabricAdapter)
    cache: RedisCache = field(default_factory=RedisCache)
    persistence: CosmosPersistence = field(default_factory=CosmosPersistence)

    def _grounding(self, manifest: AgentManifest) -> tuple[list[dict[str, Any]], list[str]]:
        rows: list[dict[str, Any]] = []
        citations: list[str] = []
        for table in manifest.grounding_tables:
            cached = self.cache.get_grounding(table)
            if cached is None:
                cached = self.fabric.query(table)
                self.cache.cache_grounding(table, cached)
            rows.extend(cached)
            citations.append(table)
        return rows, citations

    def dispatch(
        self,
        manifest: AgentManifest,
        system_prompt: str,
        user_prompt: str,
        *,
        conversation_id: str,
        caller_oid: str,
    ) -> GroundedReply:
        correlation_id = hashlib.sha256(
            f"{manifest.agent}:{conversation_id}:{time.time_ns()}".encode()
        ).hexdigest()[:16]

        grounding, citations = self._grounding(manifest)

        raw_answer = self.chat_model.complete(system_prompt, user_prompt, grounding)
        # Defence-in-depth: refuse if the model leaked a secret/PHI token.
        refused = contains_sensitive(raw_answer)
        answer = redact(raw_answer)

        # Persist conversation turn + audit event (ADR-0007 §2).
        self.persistence.write(
            "conversations",
            {
                "conversationId": conversation_id,
                "agent": manifest.agent,
                "userPrompt": redact(user_prompt),
                "answer": answer,
                "citations": citations,
                "correlationId": correlation_id,
            },
        )
        self.persistence.write(
            "audit",
            {
                "correlationId": correlation_id,
                "agent": manifest.agent,
                "callerObjectId": caller_oid,
                "event": "agent_dispatch",
                "refused": refused,
                "timestampUtc": time.time(),
            },
        )

        return GroundedReply(
            answer=answer,
            citations=tuple(citations),
            refused=refused,
            correlation_id=correlation_id,
        )
