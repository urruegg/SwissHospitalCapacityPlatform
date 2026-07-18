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

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from manifests.loader import AgentManifest, load_agent_host_manifests
from orchestrator.dispatch import Orchestrator
from orchestrator.mock_model import MockChatModel
from tools.fabric_data_agent_adapter import FabricDataAgentAdapter
from hitl.gate_enforcer import enforce_gates


def _agents_root() -> Path:
    override = os.environ.get("AGENTS_ROOT")
    if override:
        return Path(override)
    # apps/hcc-agent-host/src/api/app.py → repo root is parents[4].
    return Path(__file__).resolve().parents[4] / "agents"


def _build_live_data_agent():
    """Return a live FabricDataAgentClient when env is configured, else None."""
    endpoint = os.environ.get("FABRIC_DATA_AGENT_ENDPOINT")
    workspace = os.environ.get("FABRIC_WORKSPACE_ID")
    agent_id = os.environ.get("FABRIC_DATA_AGENT_ID")
    if not (endpoint and workspace and agent_id):
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


class ToolRequest(BaseModel):
    params: dict[str, Any] = {}
    hitlEvidence: dict[str, dict[str, Any]] = {}


def create_app() -> FastAPI:
    app = FastAPI(title="hcc-agent-host", version="0.1.0")

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

    @app.post("/agents/{name}/chat")
    def chat(name: str, req: ChatRequest) -> dict[str, Any]:
        state = get_state()
        manifest = state.require(name)
        system_prompt = _system_prompt_for(manifest, state.agents_root)
        reply = state.orchestrator.dispatch(
            manifest,
            system_prompt,
            req.prompt,
            conversation_id=req.conversationId,
            caller_oid=req.callerObjectId,
        )
        return {
            "answer": reply.answer,
            "citations": list(reply.citations),
            "refused": reply.refused,
            "correlationId": reply.correlation_id,
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

    return app


app = create_app()
