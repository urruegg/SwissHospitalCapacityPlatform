"""Sprint 43 WS-6 -- Orchestrator.dispatch accepts a per-request
`fabric_override`, used instead of the startup `self.fabric` for grounding.
Also verifies the grounding cache is namespaced per-user when an override is
supplied, so one user's OBO-scoped rows never leak into another's reply."""

from __future__ import annotations

from manifests.loader import AgentManifest
from orchestrator.dispatch import Orchestrator
from tools.fabric_adapter import FabricAdapter


class _StubModel:
    def complete(self, system_prompt, user_prompt, grounding, *, agent_name=""):
        return f"answer using {len(grounding)} grounding item(s)"


def _manifest() -> AgentManifest:
    return AgentManifest(
        agent="bmca-agent",
        version="1.0.0",
        runtime="agent-host",
        model_deployment_ref="gpt-5",
        system_prompt_ref="AGENT.md",
        grounding_tables=("gold.bed_assignment",),
    )


def test_dispatch_uses_fabric_override_when_supplied():
    default_fabric = FabricAdapter(query_fn=lambda table: [])
    override_fabric = FabricAdapter(query_fn=lambda table: [{"ward": "B", "occupied": 46}])
    orch = Orchestrator(chat_model=_StubModel(), fabric=default_fabric)

    reply = orch.dispatch(
        _manifest(), "sys", "question",
        conversation_id="c1", caller_oid="user-a",
        fabric_override=override_fabric,
    )

    assert "gold.bed_assignment" in reply.citations
    assert "1 grounding item" in reply.answer


def test_dispatch_falls_back_to_startup_fabric_when_no_override():
    default_fabric = FabricAdapter(query_fn=lambda table: [{"ward": "B"}])
    orch = Orchestrator(chat_model=_StubModel(), fabric=default_fabric)

    reply = orch.dispatch(
        _manifest(), "sys", "question",
        conversation_id="c1", caller_oid="user-a",
    )

    assert "gold.bed_assignment" in reply.citations


def test_two_users_with_different_obo_overrides_do_not_share_cached_rows():
    orch = Orchestrator(chat_model=_StubModel())
    fabric_a = FabricAdapter(query_fn=lambda table: [{"ward": "A-only"}])
    fabric_b = FabricAdapter(query_fn=lambda table: [{"ward": "B-only"}])

    reply_a = orch.dispatch(
        _manifest(), "sys", "q1", conversation_id="c1", caller_oid="user-a",
        fabric_override=fabric_a,
    )
    reply_b = orch.dispatch(
        _manifest(), "sys", "q2", conversation_id="c2", caller_oid="user-b",
        fabric_override=fabric_b,
    )

    assert "1 grounding item" in reply_a.answer
    assert "1 grounding item" in reply_b.answer
    # If the cache key collided across users, user B's second call would
    # silently reuse user A's cached rows instead of querying fabric_b.
    assert orch.cache.get_grounding("user-a:gold.bed_assignment") == [{"ward": "A-only"}]
    assert orch.cache.get_grounding("user-b:gold.bed_assignment") == [{"ward": "B-only"}]
