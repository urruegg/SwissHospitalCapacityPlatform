"""Sprint 13 T5 — HITL gate enforcement middleware (ADR-0007 §3, §6, §7).

Deny-by-default: a side-effecting action governed by a HITL gate is blocked
unless a valid approval evidence record is present. Missing or invalid evidence
yields a deterministic deny + an audit reason code (ADR-0007 §7).

Sprint 13 scope: the gate-check middleware and the deny-by-default posture are
operational. Positive-path enforcement wiring per agent lands in follow-up
sprints (design spec §11) — this module provides the check surface they build on.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

# Minimum approval-evidence schema (ADR-0007 §6). All keys are required.
REQUIRED_EVIDENCE_FIELDS = (
    "gateId",
    "approverObjectId",
    "approverRole",
    "decisionTimestampUtc",
    "correlationId",
    "decisionContextHash",
    "decisionOutcome",
    "sourceWorkflow",
)

VALID_GATES = {"HITL-01", "HITL-02", "HITL-03", "HITL-04", "HITL-05"}


class Decision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


class DenyReason(str, Enum):
    NO_EVIDENCE = "hitl_no_evidence"
    SCHEMA_INVALID = "hitl_schema_invalid"
    GATE_MISMATCH = "hitl_gate_mismatch"
    NOT_APPROVED = "hitl_not_approved"
    UNKNOWN_GATE = "hitl_unknown_gate"


@dataclass(frozen=True)
class GateResult:
    decision: Decision
    gate_id: str
    reason: DenyReason | None = None

    @property
    def allowed(self) -> bool:
        return self.decision is Decision.ALLOW


def _valid_schema(evidence: dict[str, Any]) -> bool:
    return all(
        field in evidence and evidence[field] not in (None, "")
        for field in REQUIRED_EVIDENCE_FIELDS
    )


def enforce_gate(gate_id: str, evidence: dict[str, Any] | None) -> GateResult:
    """Evaluate one HITL gate. Deny-by-default.

    Returns ALLOW only when: the gate is known, evidence is present, the schema
    is complete, the evidence targets this exact gate, and the recorded outcome
    is an explicit approval.
    """
    if gate_id not in VALID_GATES:
        return GateResult(Decision.DENY, gate_id, DenyReason.UNKNOWN_GATE)
    if not evidence:
        return GateResult(Decision.DENY, gate_id, DenyReason.NO_EVIDENCE)
    if not _valid_schema(evidence):
        return GateResult(Decision.DENY, gate_id, DenyReason.SCHEMA_INVALID)
    if evidence.get("gateId") != gate_id:
        return GateResult(Decision.DENY, gate_id, DenyReason.GATE_MISMATCH)
    if str(evidence.get("decisionOutcome", "")).lower() not in ("approved", "allow"):
        return GateResult(Decision.DENY, gate_id, DenyReason.NOT_APPROVED)
    return GateResult(Decision.ALLOW, gate_id)


def enforce_gates(
    gate_ids: list[str] | tuple[str, ...],
    evidence_by_gate: dict[str, dict[str, Any]] | None,
) -> GateResult:
    """Evaluate all required gates for an action; deny on the first failure.

    An action with no governing gates is allowed (nothing to gate). This is the
    middleware entry point the orchestrator calls before any side effect.
    """
    evidence_by_gate = evidence_by_gate or {}
    for gate_id in gate_ids:
        result = enforce_gate(gate_id, evidence_by_gate.get(gate_id))
        if not result.allowed:
            return result
    # No gates, or every gate approved.
    last_gate = gate_ids[-1] if gate_ids else ""
    return GateResult(Decision.ALLOW, last_gate)
