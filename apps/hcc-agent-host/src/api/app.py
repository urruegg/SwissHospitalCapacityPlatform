"""Sprint 13 T5 — FastAPI entrypoint for the Container Apps agent-host.

Endpoints:
- ``GET  /healthz``                       — liveness.
- ``GET  /agents``                        — deployed agent list (name, ceiling).
- ``POST /agents/{name}/chat``            — dispatch a prompt to one agent.
- ``POST /agents/{name}/tools/{tool}``    — invoke one agent tool (HITL-gated).

The host loads all ``runtime: agent-host`` manifests at startup. The chat model
defaults to the deterministic mock (dev/CI) and is replaced by a live Foundry
client at deploy time. Tool invocation is gated deny-by-default by the HITL
enforcer for the manifest's declared gates (ADR-0007).
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from manifests.loader import AgentManifest, load_agent_host_manifests
from orchestrator.dispatch import Orchestrator
from orchestrator.mock_model import MockChatModel
from tools.fabric_data_agent_adapter import FabricDataAgentAdapter
from golden.rls import build_rls_provider
from golden.service import GoldenScopeError, UnknownResourceError, load_golden
from threads.provider import ThreadProviderError, build_thread_provider
from hitl.gate_enforcer import enforce_gates
from observability import tracing

logger = logging.getLogger(__name__)


def _agents_root() -> Path:
    override = os.environ.get("AGENTS_ROOT")
    if override:
        return Path(override)
    # apps/hcc-agent-host/src/api/app.py → repo root is parents[4].
    return Path(__file__).resolve().parents[4] / "agents"


# Default browser origins for the hcc-app-fluent Copilot Drawer (ADR-0013 westus2
# SIT + ADR-0030 custom domains). Overridable via AGENT_HOST_ALLOWED_ORIGINS
# (comma-separated) so the same image lifts westus2 → eastus2 without a rebuild.
_DEFAULT_ALLOWED_ORIGINS = (
    "https://appsit.curavias.ch",
    "https://app.curavias.ch",
    "https://ca-app-fluent-ihzhhpf-sit.ashysky-8f51a689.westus2.azurecontainerapps.io",
)


def _allowed_origins() -> list[str]:
    raw = os.environ.get("AGENT_HOST_ALLOWED_ORIGINS")
    if raw:
        return [o.strip() for o in raw.split(",") if o.strip()]
    return list(_DEFAULT_ALLOWED_ORIGINS)


def _build_live_data_agent():
    """Return a live FabricDataAgentClient when env is fully configured, else None."""
    endpoint = os.environ.get("FABRIC_DATA_AGENT_ENDPOINT")
    workspace = os.environ.get("FABRIC_WORKSPACE_ID")
    agent_id = os.environ.get("FABRIC_DATA_AGENT_ID")
    provided = [bool(endpoint), bool(workspace), bool(agent_id)]
    if not all(provided):
        if any(provided):
            logger.warning(
                "FABRIC_DATA_AGENT_* partially configured (%d/3 set); using synthetic grounding",
                sum(provided),
            )
        return None
    from tools.fabric_data_agent_client import FabricDataAgentClient

    return FabricDataAgentClient(endpoint=endpoint, workspace_id=workspace, data_agent_id=agent_id)


def _system_prompt_for(manifest: AgentManifest, agents_root: Path) -> str:
    ref = manifest.system_prompt_ref.split("#", 1)[0].lstrip("./")
    prompt_path = agents_root / manifest.agent / ref
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return f"You are {manifest.agent}."


class HostState:
    def __init__(self, agents_root: Path):
        self.agents_root = agents_root
        self.manifests: dict[str, AgentManifest] = load_agent_host_manifests(agents_root)
        # Slice 0: inject the read-only Fabric Data Agent adapter so manifests that
        # bind `groundingAgent: precedence: primary` (e.g. ooa-agent) ground via the
        # MVO ontology (hcp:* citations) and propagate its PHI refusals. Without a
        # live client the adapter answers synthetically (no PHI, ADR-0016); a live
        # Fabric Data Agent client is injected here once the endpoint is provisioned.
        live = _build_live_data_agent()
        adapter = FabricDataAgentAdapter(ask_fn=(live.ask if live is not None else None))
        self.orchestrator = Orchestrator(
            chat_model=MockChatModel(),
            data_agent=adapter,
        )
        # #424 M3 — server-side (userOid x agent) -> threadId map. Shares the
        # orchestrator's persistence so a minted thread and its turns co-locate in
        # the same conversations container. Native by default (ADR-0013 scope);
        # THREAD_PROVIDER=foundry flips to real Foundry threads at M5 (OBO).
        self.thread_provider = build_thread_provider(self.orchestrator.persistence)
        # #424 M4 — RLS provider seam for the structured golden read (capability
        # ladder, see the M4 design spec). Rung 0 `SimulatedRlsProvider` is the SIT
        # default (provenance `simulated`, honest demonstration of the RLS shape).
        # Rung 1 `FabricDataAgentRlsProvider` reuses the *proven* live Data Agent
        # client (`da_hospital_capacity`) — selected via RLS_PROVIDER=fabric-data-
        # agent — but per-user structured scope still needs OBO (M5) + a dynamic-RLS
        # TMDL predicate, so it refuses the structured read until then. No OBO token
        # is available in the current MI flow, hence obo_token stays None.
        self.rls_provider = build_rls_provider(data_agent_client=live)

    def require(self, name: str) -> AgentManifest:
        manifest = self.manifests.get(name)
        if manifest is None:
            raise HTTPException(status_code=404, detail=f"unknown agent '{name}'")
        return manifest


@lru_cache(maxsize=1)
def get_state() -> HostState:
    return HostState(_agents_root())


class ChatRequest(BaseModel):
    prompt: str
    conversationId: str = "demo-conversation"
    callerObjectId: str = "demo.guest"
    # #424 M3 — when present, the (userOid x agent) thread minted via
    # POST /agents/{name}/threads; used as the conversation id so turns thread
    # server-side. Falls back to the legacy conversationId default when absent.
    threadId: str | None = None


class ToolRequest(BaseModel):
    params: dict[str, Any] = {}
    hitlEvidence: dict[str, dict[str, Any]] = {}


class UserEventRequest(BaseModel):
    type: str
    value: str | None = None
    ts: str | None = None


def create_app() -> FastAPI:
    app = FastAPI(title="hcc-agent-host", version="0.1.0")

    # Sprint 30 M1-observe: wire the agent-turn trace exporter. Defaults to the
    # dependency-free NullExporter; a real Azure Monitor exporter is built only
    # when APPLICATIONINSIGHTS_CONNECTION_STRING is set (no azure import in CI).
    tracing.configure(tracing.build_exporter_from_env())

    # Browser cross-origin access for the hcc-app-fluent Copilot Drawer. Only the
    # POST /chat + GET /agents verbs and content-type header are needed; scoped to
    # the configured app origins (not "*") to keep the surface least-privilege.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_allowed_origins(),
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=[
            "content-type",
            "authorization",
            # #424 M2 — OBO/RLS scope headers the app attaches on live golden reads.
            "x-user-oid",
            "x-hospital-scope",
            "x-active-role",
        ],
        max_age=600,
    )

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/agents")
    def list_agents() -> list[dict[str, str]]:
        state = get_state()
        return [
            {
                "name": m.agent,
                "displayName": m.agent.replace("-agent", "").upper(),
                "ceiling": m.max_ceiling,
            }
            for m in state.manifests.values()
        ]

    @app.get("/golden/{resource}")
    def golden(
        resource: str,
        response: Response,
        hospital: str = "aggregated",
        window: int = 72,
        x_user_oid: str = Header(default=""),
        x_hospital_scope: str = Header(default=""),
        x_active_role: str = Header(default=""),
    ) -> dict[str, Any]:
        # #424 M2 — live golden-source read. The scope is the caller's proven
        # ContextEnvelope, propagated as headers by the app's IQ gateway; the
        # `hospital` query param is advisory and never widens the header scope.
        # #424 M4 — the row-scope decision is made by the RLS provider seam.
        state = get_state()
        try:
            payload = load_golden(
                resource,
                hospital_scope=x_hospital_scope,
                user_oid=x_user_oid,
                provider=state.rls_provider,
            )
        except UnknownResourceError:
            raise HTTPException(status_code=404, detail=f"unknown golden resource '{resource}'")
        except GoldenScopeError as exc:
            # Deny-by-default: an ungrounded read is refused, not served wide.
            raise HTTPException(status_code=401, detail=str(exc))
        rls = payload.get("_rls", {})
        response.headers["X-Data-Provenance"] = "live"
        response.headers["X-Applied-Scope"] = rls.get("scope", x_hospital_scope)
        response.headers["X-Rls-Provider"] = rls.get("provider", "simulated")
        response.headers["X-Rls-Provenance"] = rls.get("provenance", "simulated")
        return payload

    @app.post("/agents/{name}/threads")
    def mint_thread(
        name: str,
        x_user_oid: str = Header(default=""),
        x_active_role: str = Header(default=""),
    ) -> dict[str, Any]:
        # #424 M3 — mint (or reuse) the (userOid x agent) thread. Deny-by-default:
        # an identity-less mint is refused, mirroring the /golden read path.
        state = get_state()
        state.require(name)  # 404 on unknown agent
        if not x_user_oid:
            raise HTTPException(status_code=401, detail="thread mint requires X-User-Oid")
        try:
            ref = state.thread_provider.mint(x_user_oid, name)
        except ThreadProviderError as exc:
            # e.g. FoundryThreadProvider selected before OBO lands (M5).
            raise HTTPException(status_code=503, detail=str(exc))
        return {"threadId": ref.thread_id, "provenance": ref.provenance}

    @app.post("/agents/{name}/chat")
    def chat(name: str, req: ChatRequest, x_user_oid: str = Header(default="")) -> dict[str, Any]:
        state = get_state()
        manifest = state.require(name)
        system_prompt = _system_prompt_for(manifest, state.agents_root)
        # #424 M3 — thread-scoped when a threadId is supplied; identity header
        # (OBO oid) overrides the demo caller default when present.
        conversation_id = req.threadId or req.conversationId
        caller_oid = x_user_oid or req.callerObjectId
        reply = state.orchestrator.dispatch(
            manifest,
            system_prompt,
            req.prompt,
            conversation_id=conversation_id,
            caller_oid=caller_oid,
        )
        return {
            "answer": reply.answer,
            "citations": list(reply.citations),
            "refused": reply.refused,
            "correlationId": reply.correlation_id,
            "interactionId": reply.interaction_id,
        }

    @app.post("/agents/{name}/tools/{tool}")
    def invoke_tool(name: str, tool: str, req: ToolRequest) -> dict[str, Any]:
        state = get_state()
        manifest = state.require(name)
        # Deny-by-default HITL gate check before any side effect (ADR-0007 §7).
        gate = enforce_gates(manifest.hitl_gates, req.hitlEvidence)
        if not gate.allowed:
            raise HTTPException(
                status_code=403,
                detail={
                    "decision": "deny",
                    "gateId": gate.gate_id,
                    "reason": gate.reason.value if gate.reason else None,
                },
            )
        # Positive-path tool execution wiring lands per agent in follow-up sprints.
        return {"decision": "allow", "gateId": gate.gate_id, "tool": tool}

    @app.post("/agents/{name}/interactions/{interaction_id}/events")
    def append_event(name: str, interaction_id: str, req: UserEventRequest) -> dict[str, Any]:
        state = get_state()
        state.require(name)  # 404 on unknown agent
        event = {k: v for k, v in req.model_dump().items() if v is not None}
        try:
            state.orchestrator.persistence.append_user_event(interaction_id, event)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"unknown interactionId '{interaction_id}'")
        return {"ok": True, "interactionId": interaction_id}

    return app


app = create_app()
