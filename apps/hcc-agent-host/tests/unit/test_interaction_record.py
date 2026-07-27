"""Sprint 30 M0 — DC-AGENT-INTERACTION-v1 record builder tests."""

from __future__ import annotations

from orchestrator.interaction_record import prompt_hash, build_interaction_record


def test_prompt_hash_is_sha256_prefixed():
    h = prompt_hash("Wie ist die Auslastung auf Station B?")
    assert h.startswith("sha256:")
    assert len(h) == len("sha256:") + 64


def test_build_record_shape_and_redaction():
    rec = build_interaction_record(
        agent="ooa-agent",
        conversation_key="user-oid:ooa-agent",
        prompt="patient 756.1234.5678.90 fragt nach Station B",
        answer="Auslastung 92%. token ghp_abcdefghijklmnopqrstuvwxyz0123",
        citations=["hcp:Ward", "gold.occupancy"],
        refused=False,
        reco=None,
        env="sit",
        region="eastus2",
        provenance="simulated",
        total_ms=1234,
    )
    assert rec["contractId"] == "DC-AGENT-INTERACTION-v1"
    assert rec["interactionId"].startswith("AIX-")
    assert rec["conversationKey"] == "user-oid:ooa-agent"
    assert rec["agent"] == "ooa-agent"
    # redaction applied to prompt + answer
    assert "756.1234.5678.90" not in rec["request"]["promptRedacted"]
    assert "ghp_" not in rec["response"]["answerRedacted"]
    # raw prompt never stored, only a hash
    assert "prompt" not in rec["request"]
    assert rec["request"]["promptHash"].startswith("sha256:")
    # capture is cheap: eval unscored, no user events yet
    assert rec["eval"] == {"scored": False}
    assert rec["userEvents"] == []
    assert rec["response"]["citations"] == ["hcp:Ward", "gold.occupancy"]
    assert rec["timing"]["totalMs"] == 1234
