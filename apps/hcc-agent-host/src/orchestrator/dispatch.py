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
from orchestrator.interaction_record import build_interaction_record
from observability import tracing
from observability.tracing import TraceRecorder

logger = logging.getLogger(__name__)


class ChatModel(Protocol):
    """Foundry chat-completion surface (ADR-0008).

    ``agent_name`` (Sprint 43 WS-1) identifies which registered Foundry Agent
    to invoke -- always ``manifest.agent`` (AGENTS.md naming convention: the
    manifest's ``agent`` field is identical to the registered Foundry Agent
    name). A single ``ChatModel`` instance serves every agent-host manifest;
    routing happens per-call, not per-instance.
    """

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        grounding: list[dict[str, Any]],
        *,
        agent_name: str = "",
    ) -> str:
        ...


@dataclass(frozen=True)
class GroundedReply:
    answer: str
    citations: tuple[str, ...]
    refused: bool
    correlation_id: str
    interaction_id: str = ""


@dataclass
class Orchestrator:
    chat_model: ChatModel
    fabric: FabricAdapter = field(default_factory=FabricAdapter)
    data_agent: FabricDataAgentAdapter | None = None
    cache: RedisCache = field(default_factory=RedisCache)
    persistence: CosmosPersistence = field(default_factory=CosmosPersistence)
    tracer: TraceRecorder = field(default_factory=tracing.get_recorder)

    def _grounding(self, manifest: AgentManifest) -> tuple[list[dict[str, Any]], list[str]]:
        rows: list[dict[str, Any]] = []
        citations: list[str] = []
        for table in manifest.grounding_tables:
            cached = self.cache.get_grounding(table)
            if cached is None:
                cached = self.fabric.query(table)
                self.cache.cache_grounding(table, cached)
            rows.extend(cached)
            # Sprint 43 WS-5 -- a citation asserts "this answer used this
            # source". A table that returned zero rows (e.g. WS-2's Fabric
            # read blocked upstream) contributed nothing, so citing it would
            # mislead the reader into believing the answer is grounded when
            # it is not (found via live UI verification, 2026-08-09).
            if cached:
                citations.append(table)
        return rows, citations

    def _primary_grounding(
        self, manifest: AgentManifest, user_prompt: str
    ) -> tuple[list[dict[str, Any]], list[str], str | None, bool, str]:
        """Return (grounding_rows, citations, refusal_answer, degraded, mode).

        ``mode`` is the grounding source actually used (``"agent"`` or
        ``"table"``). Uses the Fabric Data Agent when the manifest binds one and
        an adapter is available. On adapter failure, degrades LOUDLY to table
        grounding.
        """
        binding = manifest.grounding_agent
        if binding is None or self.data_agent is None or binding.precedence != "primary":
            rows, citations = self._grounding(manifest)
            return rows, citations, None, False, "table"
        try:
            result = self.data_agent.ask(user_prompt)
        except Exception:
            logger.exception(
                "Fabric Data Agent grounding failed; degrading to table grounding"
            )
            rows, citations = self._grounding(manifest)
            return rows, citations, None, True, "table"
        if result.get("refused"):
            return [], list(result.get("citations", [])), result["answer"], False, "agent"
        rows = [{"dataAgentAnswer": result["answer"]}]
        return rows, list(result.get("citations", [])), None, False, "agent"

    def dispatch(
        self,
        manifest: AgentManifest,
        system_prompt: str,
        user_prompt: str,
        *,
        conversation_id: str,
        caller_oid: str,
    ) -> GroundedReply:
        started = time.perf_counter()
        correlation_id = hashlib.sha256(
            f"{manifest.agent}:{conversation_id}:{time.time_ns()}".encode()
        ).hexdigest()[:16]

        with self.tracer.span("agent.turn", agent=manifest.agent) as root:
            with self.tracer.span("agent.retrieve", agent=manifest.agent) as rspan:
                grounding, citations, refusal_answer, degraded, mode = self._primary_grounding(
                    manifest, user_prompt
                )
                rspan.set_attribute("grounding.mode", mode)
                rspan.set_attribute("grounding.degraded", degraded)
                rspan.set_attribute("citationCount", len(citations))

            if refusal_answer is not None:
                # Data Agent refusal propagates verbatim; the model is not consulted.
                with self.tracer.span("agent.assemble", agent=manifest.agent, refused=True):
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
                    interaction_id = self._capture(
                        agent=manifest.agent, caller_oid=caller_oid, prompt=user_prompt,
                        answer=refusal_answer, citations=citations, refused=True,
                        degraded=False, started=started,
                    )
                root.set_attribute("refused", True)
                self._emit_turn_event(
                    agent=manifest.agent, interaction_id=interaction_id,
                    correlation_id=correlation_id, refused=True, degraded=False,
                    provenance="live", citations=citations, started=started,
                )
                return GroundedReply(
                    answer=refusal_answer,
                    citations=tuple(citations),
                    refused=True,
                    correlation_id=correlation_id,
                    interaction_id=interaction_id,
                )

            with self.tracer.span(
                "agent.model", agent=manifest.agent, model=type(self.chat_model).__name__
            ):
                raw_answer = self.chat_model.complete(
                    system_prompt, user_prompt, grounding, agent_name=manifest.agent
                )
            if degraded:
                raw_answer = (
                    "[grounding degraded: Fabric Data Agent unavailable, answered from "
                    "table grounding] " + raw_answer
                )
            # Defence-in-depth: refuse if the model leaked a secret/PHI token.
            refused = contains_sensitive(raw_answer)
            answer = redact(raw_answer)

            with self.tracer.span("agent.assemble", agent=manifest.agent, refused=refused):
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
                interaction_id = self._capture(
                    agent=manifest.agent, caller_oid=caller_oid, prompt=user_prompt,
                    answer=answer, citations=citations, refused=refused,
                    degraded=degraded, started=started,
                )
            root.set_attribute("refused", refused)
            self._emit_turn_event(
                agent=manifest.agent, interaction_id=interaction_id,
                correlation_id=correlation_id, refused=refused, degraded=degraded,
                provenance="live" if not degraded else "simulated",
                citations=citations, started=started,
            )
            return GroundedReply(
                answer=answer,
                citations=tuple(citations),
                refused=refused,
                correlation_id=correlation_id,
                interaction_id=interaction_id,
            )

    def _emit_turn_event(
        self,
        *,
        agent: str,
        interaction_id: str,
        correlation_id: str,
        refused: bool,
        degraded: bool,
        provenance: str,
        citations: list[str],
        started: float,
    ) -> None:
        """Emit one PHI-free ``AgentTurn`` customEvent (ids / counts / flags only)."""
        self.tracer.emit_event(
            "AgentTurn",
            properties={
                "agent": agent,
                "interactionId": interaction_id,
                "correlationId": correlation_id,
                "refused": "true" if refused else "false",
                "degraded": "true" if degraded else "false",
                "provenance": provenance,
            },
            measurements={
                "latencyMs": (time.perf_counter() - started) * 1000,
                "citationCount": float(len(citations)),
            },
        )

    def _capture(
        self,
        *,
        agent: str,
        caller_oid: str,
        prompt: str,
        answer: str,
        citations: list[str],
        refused: bool,
        degraded: bool,
        started: float,
    ) -> str:
        """Build + persist a DC-AGENT-INTERACTION-v1 record; return its id."""
        record = build_interaction_record(
            agent=agent,
            conversation_key=f"{caller_oid}:{agent}",
            prompt=prompt,
            answer=answer,
            citations=citations,
            refused=refused,
            reco=None,
            model={"name": type(self.chat_model).__name__},
            provenance="live" if not degraded else "simulated",
            total_ms=int((time.perf_counter() - started) * 1000),
        )
        self.persistence.write("agent_interactions", record)
        return record["interactionId"]
