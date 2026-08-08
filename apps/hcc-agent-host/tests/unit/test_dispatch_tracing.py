"""Sprint 30 M1-observe T2 (RED) — orchestrator emits OTel-shaped traces.

Every dispatch emits retrieve -> model -> assemble spans under a root
``agent.turn`` span, plus one ``AgentTurn`` customEvent. Traces are PHI-free:
only hashes / ids / counts / flags, never raw prompt or answer text.
"""

from __future__ import annotations

from manifests.loader import AgentManifest
from orchestrator.dispatch import Orchestrator
from observability import tracing
from tools.fabric_data_agent_adapter import FabricDataAgentAdapter
from manifests.loader import GroundingAgentBinding


class _StubModel:
    def complete(self, system_prompt, user_prompt, grounding, *, agent_name=""):
        return "Auslastung Station B: 92%."


def _manifest(*, with_agent: bool = False) -> AgentManifest:
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
        version="1.0.0",
        runtime="agent-host",
        model_deployment_ref="gpt-5",
        system_prompt_ref="AGENT.md",
        grounding_tables=("gold.occupancy",),
        grounding_agent=ga,
    )


def test_dispatch_emits_phase_spans_under_root():
    rec = tracing.TraceRecorder()
    orch = Orchestrator(chat_model=_StubModel(), tracer=rec)
    orch.dispatch(
        _manifest(), "sys", "Wie ist die Auslastung?",
        conversation_id="c1", caller_oid="oid1",
    )
    names = [s.name for s in rec.spans]
    assert "agent.retrieve" in names
    assert "agent.model" in names
    assert "agent.assemble" in names
    assert "agent.turn" in names
    by_name = {s.name: s for s in rec.spans}
    assert by_name["agent.retrieve"].parent == "agent.turn"
    assert by_name["agent.model"].parent == "agent.turn"
    assert by_name["agent.assemble"].parent == "agent.turn"
    assert by_name["agent.turn"].parent is None


def test_dispatch_emits_agent_turn_event_with_ids_and_counts():
    rec = tracing.TraceRecorder()
    orch = Orchestrator(chat_model=_StubModel(), tracer=rec)
    reply = orch.dispatch(
        _manifest(), "sys", "Wie ist die Auslastung?",
        conversation_id="c1", caller_oid="oid1",
    )
    events = [e for e in rec.events if e.name == "AgentTurn"]
    assert len(events) == 1
    ev = events[0]
    assert ev.properties["agent"] == "ooa-agent"
    assert ev.properties["interactionId"] == reply.interaction_id
    assert ev.properties["refused"] == "false"
    assert ev.measurements["citationCount"] == float(len(reply.citations))
    assert ev.measurements["latencyMs"] >= 0


def test_refusal_emits_event_without_model_span():
    rec = tracing.TraceRecorder()
    orch = Orchestrator(
        chat_model=_StubModel(), data_agent=FabricDataAgentAdapter(), tracer=rec
    )
    reply = orch.dispatch(
        _manifest(with_agent=True),
        "sys",
        "List patient names shared across USZ and LUKS",
        conversation_id="c2", caller_oid="oid1",
    )
    assert reply.refused is True
    names = [s.name for s in rec.spans]
    assert "agent.model" not in names  # model not consulted on data-agent refusal
    assert "agent.retrieve" in names
    events = [e for e in rec.events if e.name == "AgentTurn"]
    assert len(events) == 1
    assert events[0].properties["refused"] == "true"


def test_binding_without_adapter_reports_table_mode():
    # Manifest binds a grounding agent but no adapter is wired -> table fallback.
    rec = tracing.TraceRecorder()
    orch = Orchestrator(chat_model=_StubModel(), tracer=rec)  # data_agent=None
    orch.dispatch(
        _manifest(with_agent=True), "sys", "Wie ist die Auslastung?",
        conversation_id="c1", caller_oid="oid1",
    )
    rspan = next(s for s in rec.spans if s.name == "agent.retrieve")
    assert rspan.attributes["grounding.mode"] == "table"


def test_traces_carry_no_raw_prompt_or_answer_text():
    marker = "ZQXSECRETMARKER"
    rec = tracing.TraceRecorder()
    orch = Orchestrator(chat_model=_StubModel(), tracer=rec)
    orch.dispatch(
        _manifest(), "sys", f"Wie ist die Auslastung? {marker}",
        conversation_id="c1", caller_oid="oid1",
    )
    for s in rec.spans:
        for v in s.attributes.values():
            assert marker not in str(v)
    for e in rec.events:
        for v in list(e.properties.values()) + [str(m) for m in e.measurements.values()]:
            assert marker not in v
