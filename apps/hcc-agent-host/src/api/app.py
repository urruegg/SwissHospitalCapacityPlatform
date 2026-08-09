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

import json
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
from tools.fabric_adapter import FabricAdapter
from tools.fabric_data_agent_adapter import FabricDataAgentAdapter
from golden.rls import build_rls_provider
from golden.service import GoldenScopeError, UnknownResourceError, load_golden
from threads.provider import ThreadProviderError, build_thread_provider
from auth.obo_context import build_obo_context
from auth.token_validator import TokenValidationError
from hitl.gate_enforcer import enforce_gates
from loop.sim_registry import SimRegistry
from observability import tracing

logger = logging.getLogger(__name__)


def _agents_root() -> Path:
    override = os.environ.get("AGENTS_ROOT")
    if override:
        return Path(override)
    # apps/hcc-agent-host/src/api/app.py → repo root is parents[4].
    return Path(__file__).resolve().parents[4] / "agents"


def _default_gold_path() -> Path:
    # The simulated-MVP default gold source: the USZ snapshot bundled in the
    # agent-host image at src/loop/, so it resolves in the container (/app/src/
    # loop) AND locally without reaching into another app's test fixtures and
    # without a fixed parents[N] depth (which IndexErrors in the container).
    return Path(__file__).resolve().parent.parent / "loop" / "gold-snapshot-usz.json"


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


def _build_chat_model():
    """Return a live FoundryResponsesChatModel when env is configured, else None.

    A single instance serves every agent-host manifest -- the Foundry Agent
    name is supplied per-call as ``agent_name`` (manifest.agent), not bound at
    construction (Sprint 43 WS-1).
    """
    endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT")
    project = os.environ.get("FOUNDRY_PROJECT_NAME")
    provided = [bool(endpoint), bool(project)]
    if not all(provided):
        if any(provided):
            logger.warning(
                "FOUNDRY_PROJECT_* partially configured (%d/2 set); using MockChatModel",
                sum(provided),
            )
        return None
    from orchestrator.foundry_chat_model import FoundryResponsesChatModel

    return FoundryResponsesChatModel(project_endpoint=endpoint, project_name=project)


def _build_fabric_query_fn():
    """Return a live FabricDeltaClient.query callable when env is configured, else None.

    Sprint 43 WS-2 -- reuses FABRIC_WORKSPACE_ID (already set for the Fabric
    Data Agent binding, same workspace) plus the new FABRIC_LAKEHOUSE_ID.
    """
    workspace = os.environ.get("FABRIC_WORKSPACE_ID")
    lakehouse = os.environ.get("FABRIC_LAKEHOUSE_ID")
    provided = [bool(workspace), bool(lakehouse)]
    if not all(provided):
        if any(provided):
            logger.warning(
                "FABRIC_WORKSPACE_ID/FABRIC_LAKEHOUSE_ID partially configured "
                "(%d/2 set); FabricAdapter stays on synthetic fallback",
                sum(provided),
            )
        return None
    from tools.fabric_delta_client import FabricDeltaClient

    return FabricDeltaClient(workspace_id=workspace, lakehouse_id=lakehouse).query


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
        # Sprint 43 WS-2 -- live Fabric Gold table reads (replaces
        # FabricAdapter's hardcoded 3-row dict). Unset env keeps the
        # synthetic fallback (dev/CI default).
        fabric_query_fn = _build_fabric_query_fn()
        self.fabric = FabricAdapter(query_fn=fabric_query_fn)

        live = _build_live_data_agent()
        self._live_data_agent = live
        adapter = FabricDataAgentAdapter(ask_fn=(live.ask if live is not None else None))
        # Sprint 43 WS-1 -- live Foundry Agent Service chat model (Option A).
        # FOUNDRY_PROJECT_ENDPOINT/FOUNDRY_PROJECT_NAME unset (dev/CI default)
        # keeps the deterministic MockChatModel; both set (SIT/PROD) invokes
        # the real registered agents via FoundryResponsesChatModel.
        live_chat_model = _build_chat_model()
        self.orchestrator = Orchestrator(
            chat_model=live_chat_model if live_chat_model is not None else MockChatModel(),
            fabric=self.fabric,
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
        # Sprint 39 P2 — one stateful in-host SimState per hospital, seeded from a
        # materialized gold snapshot via the Plan 1 gold_seed (no deploy, no live
        # write-back). Backs GET /agents/{role}/worklist + POST /decisions.
        self.sim_registry = SimRegistry()

    def load_gold_snapshot(self, hospital: str) -> dict[str, Any]:
        # Sprint 39 P2 simulated-MVP seam: read a materialized gold snapshot from
        # GOLD_SNAPSHOT_PATH (default = the committed Plan 1 USZ fixture). The live
        # golden-source read (golden.service.load_golden) is the follow-on.
        path = Path(os.environ.get("GOLD_SNAPSHOT_PATH", str(_default_gold_path())))
        return json.loads(path.read_text(encoding="utf-8"))

    def rls_provider_for(self, obo_token: str | None):
        """#424 M5 — the per-request RLS provider.

        When an OBO context is present (``OBO_ENABLED`` + a valid bearer), build a
        provider carrying the user's token so the read runs on-behalf-of the user
        (config-selected via ``RLS_PROVIDER``). Otherwise reuse the startup
        provider (SIT default: simulated). Config, not code (ADR-0057).
        """
        if not obo_token:
            return self.rls_provider
        return build_rls_provider(
            data_agent_client=self._live_data_agent, obo_token=obo_token
        )

    def fabric_for(self, obo_token: str | None) -> FabricAdapter:
        """Sprint 43 WS-6 -- the per-request chat-grounding Fabric adapter.

        Mirrors ``rls_provider_for``: an OBO token builds a fresh
        ``FabricDeltaClient`` scoped to the signed-in user's own delegated
        Fabric permissions, bypassing the service-principal restriction the
        startup ``self.fabric`` (managed identity) hits (see
        docs/superpowers/specs/2026-08-09-obo-self-service-fabric-grounding-design.md).
        No token, or the Fabric env unconfigured, reuses the startup instance
        unchanged (byte-parity with today when OBO is off).
        """
        if not obo_token:
            return self.fabric
        workspace = os.environ.get("FABRIC_WORKSPACE_ID")
        lakehouse = os.environ.get("FABRIC_LAKEHOUSE_ID")
        if not (workspace and lakehouse):
            return self.fabric
        from tools.fabric_delta_client import FabricDeltaClient

        client = FabricDeltaClient(
            workspace_id=workspace,
            lakehouse_id=lakehouse,
            token_provider=lambda: obo_token,
        )
        return FabricAdapter(query_fn=client.query)

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


class DecisionRequest(BaseModel):
    # Sprint 39 P2 — a single human accept/deny on a role's recommendation.
    decision: str  # "accept" | "deny"
    hospital: str = "USZ"
    params: dict[str, Any] = {}


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
        authorization: str = Header(default=""),
        x_user_oid: str = Header(default=""),
        x_hospital_scope: str = Header(default=""),
        x_active_role: str = Header(default=""),
    ) -> dict[str, Any]:
        # #424 M2 — live golden-source read. The scope is the caller's proven
        # ContextEnvelope, propagated as headers by the app's IQ gateway; the
        # `hospital` query param is advisory and never widens the header scope.
        # #424 M4 — the row-scope decision is made by the RLS provider seam.
        # #424 M5 — when OBO is enabled and a valid bearer is presented, the read
        # runs on-behalf-of the user; otherwise it stays on the simulated provider
        # (SIT default). Deny-by-default: an invalid bearer under OBO is a 401.
        state = get_state()
        try:
            obo = build_obo_context(authorization)
        except TokenValidationError as exc:
            raise HTTPException(status_code=401, detail=str(exc))
        try:
            provider = state.rls_provider_for(obo.obo_token if obo else None)
            payload = load_golden(
                resource,
                hospital_scope=x_hospital_scope,
                user_oid=(obo.user_oid if obo else x_user_oid),
                provider=provider,
            )
        except UnknownResourceError:
            raise HTTPException(status_code=404, detail=f"unknown golden resource '{resource}'")
        except GoldenScopeError as exc:
            # Deny-by-default: an ungrounded read (or a provider that cannot yet
            # enforce per-user scope, or a fabric provider misconfigured without a
            # live client) is refused, not served wide.
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

    @app.get("/agents/{name}/worklist")
    def worklist(name: str, hospital: str = "USZ", x_user_oid: str = Header(default="")) -> dict[str, Any]:
        # Sprint 39 P2 — the role's live observations + one grounded recommendation
        # on real seeded gold. Simulated-MVP: gold comes from the Plan 1 fixture via
        # load_gold_snapshot; the live golden-source read is the follow-on.
        state = get_state()
        gold = state.load_gold_snapshot(hospital)
        sim = state.sim_registry.get_or_seed(hospital, gold)
        from loop.worklist import build_worklist

        try:
            return build_worklist(name, sim, provenance=gold.get("provenance", "simulated"))
        except ValueError as exc:
            # e.g. a multi-ward snapshot is out of the single-ward MVP scope: a
            # loud 400, not a silent mis-grounding.
            raise HTTPException(status_code=400, detail=str(exc))

    @app.post("/agents/{name}/decisions")
    def decisions(name: str, req: DecisionRequest, x_user_oid: str = Header(default="")) -> dict[str, Any]:
        # Sprint 39 P2 — a human accept/deny drives the REAL HITL apply->outcome on
        # the in-host SimState. NFR-UXL-001: only a human oid may act; the bot/self
        # refusal is enforced by plan_runtime.approve_action (surfaced as 403).
        if not x_user_oid:
            raise HTTPException(status_code=401, detail="human approver (x-user-oid) required")
        state = get_state()
        gold = state.load_gold_snapshot(req.hospital)
        sim = state.sim_registry.get_or_seed(req.hospital, gold)
        from loop.decisions import decide

        try:
            return decide(
                name, req.decision, approver=x_user_oid, state=state, sim=sim,
                params=req.params, provenance=gold.get("provenance", "simulated"),
            )
        except PermissionError as exc:
            # NFR-UXL-001: a bot/self approver is refused by approve_action.
            raise HTTPException(status_code=403, detail=str(exc))
        except (ValueError, KeyError) as exc:
            # Unvalidated params (e.g. unknown ward) or a multi-ward snapshot -> 400.
            raise HTTPException(status_code=400, detail=str(exc))

    @app.get("/agents/{name}/evidence")
    def evidence(name: str, branch: str = "accept", hospital: str = "USZ") -> dict[str, Any]:
        # Sprint 39 P2 B3/B4 - the DC-EVIDENCE-TRACE-v1 five-part proof for a role,
        # built by the Plan 1 harness on the SAME seeded gold the loop uses. This
        # is the validation==UX unification (FR-UXL-004): the evidence steps carry
        # the same DC-SIM-OUTCOME-v1 contract the /decisions endpoint produces.
        # Read-only (no oid); branch in {accept, deny}. Provenance is the gold's.
        state = get_state()
        gold = state.load_gold_snapshot(hospital)
        from closedloop.evidence import build_evidence_trace

        try:
            return build_evidence_trace(gold, branch)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    return app


app = create_app()
