"""Sprint 30 M0/M2 — agent_interactions container + user-event append."""

from __future__ import annotations

import pytest

from persistence.cosmos_client import CosmosPersistence


def test_agent_interactions_container_writes_by_conversation_key():
    p = CosmosPersistence()
    rec = p.write("agent_interactions", {
        "interactionId": "AIX-abc",
        "conversationKey": "user-oid:ooa-agent",
        "agent": "ooa-agent",
    })
    assert rec["conversationKey"] == "user-oid:ooa-agent"
    assert p.read_all("agent_interactions")[0]["interactionId"] == "AIX-abc"


def test_agent_interactions_requires_partition_key():
    p = CosmosPersistence()
    with pytest.raises(ValueError):
        p.write("agent_interactions", {"interactionId": "AIX-x"})  # no conversationKey


def test_append_user_event_adds_to_record():
    p = CosmosPersistence()
    p.write("agent_interactions", {
        "interactionId": "AIX-abc",
        "conversationKey": "user-oid:ooa-agent",
        "userEvents": [],
    })
    updated = p.append_user_event("AIX-abc", {"type": "thumbs", "value": "up", "ts": "2026-07-27T09:00:00Z"})
    assert updated["userEvents"][-1]["type"] == "thumbs"
    assert p.read_all("agent_interactions")[0]["userEvents"][-1]["value"] == "up"


def test_append_user_event_unknown_id_raises():
    p = CosmosPersistence()
    with pytest.raises(KeyError):
        p.append_user_event("AIX-missing", {"type": "thumbs", "value": "up"})
