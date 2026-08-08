"""Unit tests for MockChatModel's agent_name kwarg (Sprint 43 WS-1 prep)."""

from __future__ import annotations

from orchestrator.mock_model import MockChatModel


def test_complete_accepts_agent_name_kwarg():
    model = MockChatModel()
    answer = model.complete(
        "sys", "Wie ist die Auslastung?", [{"ward": "B", "occupied": 46, "capacity": 50}],
        agent_name="bmca-agent",
    )
    assert "92%" in answer


def test_complete_agent_name_is_optional():
    model = MockChatModel()
    # Existing call sites that omit agent_name must keep working (default "").
    answer = model.complete("sys", "q", [])
    assert "Keine Auslastungsdaten" in answer
