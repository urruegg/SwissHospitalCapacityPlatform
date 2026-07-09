"""Integration test — BMCA end-to-end through the agent-host (T5, T6 contract).

Loads the real ``bmca-agent`` manifest, dispatches the canonical Copilot Drawer
prompt through the orchestrator with the deterministic mock Foundry model, and
asserts the grounded-reply contract the Fluent Copilot Drawer expects:
``{answer, citations[], refused}`` — citations reference the manifest grounding
tables, no PHI leaks, and the conversation + audit records are persisted
(ADR-0007).
"""

from __future__ import annotations

from pathlib import Path

from manifests.loader import load_agent_host_manifests
from orchestrator.dispatch import Orchestrator
from orchestrator.mock_model import MockChatModel
from orchestrator.redaction import contains_sensitive


CANONICAL_PROMPT = "Station B ist fast voll — was sollen wir tun?"


def _bmca():
    repo_root = Path(__file__).resolve().parents[4]
    manifests = load_agent_host_manifests(repo_root / "agents")
    return manifests["bmca-agent"]


def test_bmca_grounded_reply_contract():
    manifest = _bmca()
    orchestrator = Orchestrator(chat_model=MockChatModel())

    reply = orchestrator.dispatch(
        manifest,
        system_prompt="You are the bed-management copilot.",
        user_prompt=CANONICAL_PROMPT,
        conversation_id="conv-1",
        caller_oid="user-oid",
    )

    # Grounded: citations are the manifest's gold tables, in order.
    assert reply.citations == manifest.grounding_tables
    assert "gold.bed_assignment" in reply.citations
    # PHI-free answer (design spec §6 / T6 contract).
    assert not contains_sensitive(reply.answer)
    assert not reply.refused
    assert "HITL-02" in reply.answer  # recommends the gated action

    # Conversation + audit persisted (ADR-0007 §2).
    conversations = orchestrator.persistence.read_all("conversations")
    audit = orchestrator.persistence.query_by_correlation("audit", reply.correlation_id)
    assert conversations and conversations[0]["agent"] == "bmca-agent"
    assert audit and audit[0]["event"] == "agent_dispatch"


def test_grounding_is_cached_second_call():
    manifest = _bmca()
    orchestrator = Orchestrator(chat_model=MockChatModel())
    orchestrator.dispatch(
        manifest, "sys", CANONICAL_PROMPT, conversation_id="c1", caller_oid="u"
    )
    # After first dispatch the grounding tables are cached.
    for table in manifest.grounding_tables:
        assert orchestrator.cache.get_grounding(table) is not None
