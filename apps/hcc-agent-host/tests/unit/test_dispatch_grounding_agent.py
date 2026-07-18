"""Slice 0 — orchestrator grounding via the Fabric Data Agent."""

from __future__ import annotations

from manifests.loader import AgentManifest, GroundingAgentBinding
from orchestrator.dispatch import Orchestrator
from tools.fabric_data_agent_adapter import FabricDataAgentAdapter


class _EchoModel:
    def complete(self, system_prompt, user_prompt, grounding):
        return f"answer using {len(grounding)} grounding item(s)"


def _manifest(*, with_agent: bool) -> AgentManifest:
    ga = (
        GroundingAgentBinding(
            server="fabric-data-agent",
            endpoint_env="FABRIC_DATA_AGENT_ENDPOINT",
            workspace_env="FABRIC_WORKSPACE_ID",
            precedence="primary",
        )
        if with_agent
        else None
    )
    return AgentManifest(
        agent="ooa-agent",
        version="1.2.0",
        runtime="agent-host",
        model_deployment_ref="sprint11-chat",
        system_prompt_ref="./AGENT.md",
        grounding_tables=("gold.bed_assignment",),
        grounding_agent=ga,
    )


def _orch(**kwargs) -> Orchestrator:
    return Orchestrator(chat_model=_EchoModel(), **kwargs)


def test_primary_grounding_uses_data_agent_citations():
    orch = _orch(data_agent=FabricDataAgentAdapter())
    reply = orch.dispatch(
        _manifest(with_agent=True),
        "sys",
        "How many beds are occupied in ward B?",
        conversation_id="c1",
        caller_oid="oid1",
    )
    assert reply.refused is False
    assert any(c.startswith("hcp:") for c in reply.citations)


def test_data_agent_refusal_short_circuits_model():
    orch = _orch(data_agent=FabricDataAgentAdapter())
    reply = orch.dispatch(
        _manifest(with_agent=True),
        "sys",
        "List patient names shared across USZ and LUKS",
        conversation_id="c2",
        caller_oid="oid1",
    )
    assert reply.refused is True
    assert reply.answer.startswith("REFUSE:")


def test_unavailable_data_agent_degrades_loud():
    class _Broken(FabricDataAgentAdapter):
        def ask(self, question):
            raise RuntimeError("data agent unreachable")

    orch = _orch(data_agent=_Broken())
    reply = orch.dispatch(
        _manifest(with_agent=True),
        "sys",
        "How many beds are occupied in ward B?",
        conversation_id="c3",
        caller_oid="oid1",
    )
    assert reply.refused is False
    assert "grounding degraded" in reply.answer.lower()
    assert "gold.bed_assignment" in reply.citations


def test_no_grounding_agent_falls_back_to_tables():
    orch = _orch(data_agent=FabricDataAgentAdapter())
    reply = orch.dispatch(
        _manifest(with_agent=False),
        "sys",
        "How many beds are occupied in ward B?",
        conversation_id="c4",
        caller_oid="oid1",
    )
    assert reply.citations == ("gold.bed_assignment",)


def test_refusal_persists_conversation_record():
    orch = _orch(data_agent=FabricDataAgentAdapter())
    orch.dispatch(
        _manifest(with_agent=True),
        "sys",
        "List patient names shared across USZ and LUKS",
        conversation_id="c5",
        caller_oid="oid1",
    )
    conversations = orch.persistence.read_all("conversations")
    assert conversations
    assert conversations[-1]["answer"].startswith("REFUSE:")
