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
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Protocol

from manifests.loader import AgentManifest
from tools.fabric_adapter import FabricAdapter
from tools.fabric_data_agent_adapter import FabricDataAgentAdapter
from cache.redis_client import RedisCache
from persistence.cosmos_client import CosmosPersistence
from orchestrator.redaction import redact, contains_sensitive

logger = logging.getLogger(__name__)


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
    data_agent: FabricDataAgentAdapter | None = None
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

    def _primary_grounding(
        self, manifest: AgentManifest, user_prompt: str
    ) -> tuple[list[dict[str, Any]], list[str], str | None, bool]:
        """Return (grounding_rows, citations, refusal_answer, degraded).

        Uses the Fabric Data Agent when the manifest binds one and an adapter is
        available. On adapter failure, degrades LOUDLY to table grounding.
        """
        binding = manifest.grounding_agent
        if binding is None or self.data_agent is None or binding.precedence != "primary":
            rows, citations = self._grounding(manifest)
            return rows, citations, None, False
        try:
            result = self.data_agent.ask(user_prompt)
        except Exception:
            logger.exception(
                "Fabric Data Agent grounding failed; degrading to table grounding"
            )
            rows, citations = self._grounding(manifest)
            return rows, citations, None, True
        if result.get("refused"):
            return [], list(result.get("citations", [])), result["answer"], False
        rows = [{"dataAgentAnswer": result["answer"]}]
        return rows, list(result.get("citations", [])), None, False

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

        grounding, citations, refusal_answer, degraded = self._primary_grounding(
            manifest, user_prompt
        )

        if refusal_answer is not None:
            # Data Agent refusal propagates verbatim; the model is not consulted.
            self.persistence.write(
                "conversations",
                {
                    "conversationId": conversation_id,
                    "agent": manifest.agent,
                    "userPrompt": redact(user_prompt),
                    "answer": refusal_answer,
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
                    "refused": True,
                    "timestampUtc": time.time(),
                },
            )
            return GroundedReply(
                answer=refusal_answer,
                citations=tuple(citations),
                refused=True,
                correlation_id=correlation_id,
            )

        raw_answer = self.chat_model.complete(system_prompt, user_prompt, grounding)
        if degraded:
            raw_answer = (
                "[grounding degraded: Fabric Data Agent unavailable, answered from "
                "table grounding] " + raw_answer
            )
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
