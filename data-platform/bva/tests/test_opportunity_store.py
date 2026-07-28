"""Offline tests for the BVA Opportunity Cosmos store."""
from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_PLATFORM = REPO_ROOT / "data-platform"
if str(DATA_PLATFORM) not in sys.path:
    sys.path.insert(0, str(DATA_PLATFORM))


def test_record_ask_is_idempotent_by_hospital_lineage_and_appends_history(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BVA_COSMOS_ENDPOINT", raising=False)
    from bva.opportunity import make_opportunity_id
    from bva.opportunity_store import OpportunityStore

    store = OpportunityStore()

    first = store.record_ask(
        hospitalName="Hopital de Fribourg",
        archetype="acute",
        askText="Should we onboard Hopital de Fribourg?",
        language="en",
        createdBy="bva-agent",
        at="2026-07-28T09:15:00Z",
    )
    second = store.record_ask(
        hospitalName="Hopital de Fribourg",
        archetype="acute",
        askText="Can you recompute the onboarding case?",
        language="en",
        createdBy="bva-agent",
        at="2026-07-28T09:20:00Z",
    )

    assert first["id"] == make_opportunity_id("Hopital de Fribourg")
    assert second["id"] == first["id"]
    assert second["askText"] == "Can you recompute the onboarding case?"
    assert len(second["history"]) == len(first["history"]) + 1
    assert [entry["at"] for entry in second["history"]] == [
        "2026-07-28T09:15:00Z",
        "2026-07-28T09:20:00Z",
    ]


def test_append_history_is_append_only_and_preserves_order() -> None:
    from bva.opportunity_store import append_history

    original = {
        "id": "opp-test-0001",
        "history": [
            {"at": "2026-07-28T09:00:00Z", "event": "created", "by": "app-copilot"}
        ],
    }

    updated = append_history(original, "re-asked", "2026-07-28T09:05:00Z", by="bva-agent")

    assert updated is not original
    assert original["history"] == [
        {"at": "2026-07-28T09:00:00Z", "event": "created", "by": "app-copilot"}
    ]
    assert updated["history"] == [
        {"at": "2026-07-28T09:00:00Z", "event": "created", "by": "app-copilot"},
        {"at": "2026-07-28T09:05:00Z", "event": "re-asked", "by": "bva-agent"},
    ]


def test_lifecycle_guard_blocks_agent_human_only_advances_but_allows_human_and_agent_qualification() -> None:
    from bva.opportunity_store import is_agent_advance_forbidden, set_status

    qualified = {"status": "qualified", "history": []}

    with pytest.raises(ValueError, match="human-only"):
        set_status(qualified, "onboarding", "2026-07-28T10:00:00Z", by="bva-agent")

    onboarded = set_status(qualified, "onboarding", "2026-07-28T10:00:00Z", by="urs")
    assert onboarded["status"] == "onboarding"

    new_doc = {"status": "new", "history": []}
    evaluating = set_status(new_doc, "evaluating", "2026-07-28T10:01:00Z", by="app-copilot")
    qualified_by_agent = set_status(evaluating, "qualified", "2026-07-28T10:02:00Z", by="product-owner-agent")
    assert qualified_by_agent["status"] == "qualified"

    assert is_agent_advance_forbidden("onboarding", "won", "handoff-bot")
    assert is_agent_advance_forbidden("onboarding", "lost", "triage-agent")
    with pytest.raises(ValueError, match="human-only"):
        set_status({"status": "onboarding", "history": []}, "won", "2026-07-28T10:03:00Z", by="handoff-bot")
    with pytest.raises(ValueError, match="human-only"):
        set_status({"status": "onboarding", "history": []}, "lost", "2026-07-28T10:04:00Z", by="triage-agent")


def test_upsert_refuses_invalid_opportunity_doc(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BVA_COSMOS_ENDPOINT", raising=False)
    from bva.opportunity_store import OpportunityStore

    invalid = {
        "id": "opp-invalid-0001",
        "hospitalName": "Invalid Hospital",
        "archetype": "acute",
        "createdAt": "2026-07-28T09:15:00Z",
        "createdBy": "bva-agent",
        "status": "auto-approved",
        "askText": "Should we onboard?",
        "language": "en",
        "history": [],
    }

    with pytest.raises(ValueError) as exc:
        OpportunityStore().upsert(invalid)

    message = str(exc.value)
    assert "status" in message
    assert "enum" in message or "not in enum" in message


def test_record_ask_refuses_agent_creating_at_human_only_status(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BVA_COSMOS_ENDPOINT", raising=False)
    from bva.opportunity_store import OpportunityStore

    store = OpportunityStore()

    for forbidden in ("onboarding", "won", "lost"):
        with pytest.raises(ValueError, match="human-only"):
            store.record_ask(
                hospitalName=f"Bypass {forbidden} Hospital",
                archetype="acute",
                askText="Should we onboard?",
                language="en",
                createdBy="bva-agent",
                status=forbidden,
                at="2026-07-28T09:15:00Z",
            )

    # Agents may still create up to 'qualified'; humans may create at any status.
    agent_ok = store.record_ask(
        hospitalName="Agent Qualified Hospital",
        archetype="acute",
        askText="Should we onboard?",
        language="en",
        createdBy="bva-agent",
        status="qualified",
        at="2026-07-28T09:15:00Z",
    )
    assert agent_ok["status"] == "qualified"

    human_ok = store.record_ask(
        hospitalName="Human Onboarding Hospital",
        archetype="acute",
        askText="Should we onboard?",
        language="en",
        createdBy="urs",
        status="onboarding",
        at="2026-07-28T09:15:00Z",
    )
    assert human_ok["status"] == "onboarding"


def test_is_agent_identity_uses_bounded_bot_token(monkeypatch: pytest.MonkeyPatch) -> None:
    from bva.opportunity_store import is_agent_identity

    # Human names containing 'bot' as a substring must NOT be classified as agents.
    assert is_agent_identity("Talbot") is False
    assert is_agent_identity("Abbott") is False
    assert is_agent_identity("Robertson") is False

    # Known agent/bot identity patterns ARE classified as agents.
    assert is_agent_identity("bva-agent") is True
    assert is_agent_identity("copilot") is True
    assert is_agent_identity("dependabot[bot]") is True
    assert is_agent_identity("handoff-bot") is True
    assert is_agent_identity("bot") is True


def test_dry_run_with_env_unset_returns_doc_without_constructing_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BVA_COSMOS_ENDPOINT", raising=False)
    from bva.opportunity_store import OpportunityStore

    def fail_if_called() -> object:
        raise AssertionError("network client should not be constructed in dry-run mode")

    store = OpportunityStore(database_client_factory=fail_if_called)

    doc = store.record_ask(
        hospitalName="Reha Zentrum Zürich Süd",
        archetype="rehab",
        askText="Should we onboard Reha Zentrum Zürich Süd?",
        language="en",
        createdBy="app-copilot",
        at="2026-07-28T11:00:00Z",
    )
    upserted = store.upsert(deepcopy(doc))

    assert store.dry_run is True
    assert doc["id"] == "opp-reha-zentrum-zurich-sud-0001"
    assert upserted == doc
