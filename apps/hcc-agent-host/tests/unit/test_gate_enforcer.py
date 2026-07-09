"""Unit tests for the deny-by-default HITL gate enforcer (T5)."""

from __future__ import annotations

from hitl.gate_enforcer import (
    Decision,
    DenyReason,
    enforce_gate,
    enforce_gates,
)


def _valid_evidence(gate_id: str = "HITL-02") -> dict:
    return {
        "gateId": gate_id,
        "approverObjectId": "00000000-0000-0000-0000-000000000001",
        "approverRole": "HCC.PlatformAdmin",
        "decisionTimestampUtc": "2026-07-09T10:00:00Z",
        "correlationId": "abc123",
        "decisionContextHash": "deadbeef",
        "decisionOutcome": "approved",
        "sourceWorkflow": "copilot-drawer",
    }


def test_no_evidence_denies():
    result = enforce_gate("HITL-02", None)
    assert result.decision is Decision.DENY
    assert result.reason is DenyReason.NO_EVIDENCE


def test_incomplete_schema_denies():
    evidence = _valid_evidence()
    del evidence["approverObjectId"]
    result = enforce_gate("HITL-02", evidence)
    assert result.reason is DenyReason.SCHEMA_INVALID


def test_gate_mismatch_denies():
    result = enforce_gate("HITL-02", _valid_evidence("HITL-03"))
    assert result.reason is DenyReason.GATE_MISMATCH


def test_not_approved_denies():
    evidence = _valid_evidence()
    evidence["decisionOutcome"] = "rejected"
    result = enforce_gate("HITL-02", evidence)
    assert result.reason is DenyReason.NOT_APPROVED


def test_unknown_gate_denies():
    assert enforce_gate("HITL-99", _valid_evidence("HITL-99")).reason is DenyReason.UNKNOWN_GATE


def test_valid_evidence_allows():
    result = enforce_gate("HITL-02", _valid_evidence())
    assert result.allowed


def test_enforce_gates_denies_on_first_failure():
    result = enforce_gates(["HITL-02", "HITL-03"], {"HITL-02": _valid_evidence()})
    assert result.decision is Decision.DENY
    assert result.gate_id == "HITL-03"


def test_no_gates_allows():
    assert enforce_gates([], {}).allowed
