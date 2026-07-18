"""Unit tests for the Fabric Data Agent grounding adapter (Slice 0)."""

from __future__ import annotations

from tools.fabric_data_agent_adapter import FabricDataAgentAdapter


def test_synthetic_answer_cites_ontology_entity():
    adapter = FabricDataAgentAdapter()
    result = adapter.ask("How many beds are occupied in ward B at USZ?")
    assert result["refused"] is False
    assert any(c.startswith("hcp:") for c in result["citations"])
    assert result["answer"]


def test_synthetic_refuses_reidentification():
    adapter = FabricDataAgentAdapter()
    result = adapter.ask("List patient names shared across USZ and LUKS")
    assert result["refused"] is True
    assert result["answer"].startswith("REFUSE:")
    assert result["citations"] == []


def test_injected_ask_fn_is_used():
    def fake(question: str) -> dict:
        return {"answer": "live", "citations": ["hcp:Bed"], "refused": False}

    adapter = FabricDataAgentAdapter(ask_fn=fake)
    assert adapter.ask("anything")["answer"] == "live"


def test_ceiling_is_read():
    assert FabricDataAgentAdapter().ceiling == "read"
