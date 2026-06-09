# ADR-0007: MVP Agent Runtime Choices and HITL Release Gates

- Status: Accepted
- Date: 2026-06-08
- Deciders: Architecture Working Group
- Related Decision ID: AR-D-007
- Related Requirements: FR-GOV-001, FR-GOV-005, FR-GOV-006, NFR-AI-001, NFR-AI-004, NFR-REL-003, NFR-PERF-005

## Context

The MVP solution design requires implementation-grade decisions for agent runtime
components and auditable human-in-the-loop controls. Prior baseline documents
defined architecture direction but left runtime and release-gating details partially
open.

The CSA challenger review introduced explicit recommendations to:

1. Standardize cache and audit persistence runtime choices.
2. Standardize HITL gate IDs and approval controls.
3. Make these controls release-gating artifacts across design, operations, and test documents.

## Decision

For MVP and PROD baseline:

1. Agent runtime uses Azure Cache for Redis for grounding and session cache.
2. Agent runtime uses Azure Cosmos DB for conversation, audit, and
   approval-event persistence under a stable contract model.
   - Selection rationale: the Dynamic AI Agents at Scale reference pattern uses
     Cosmos DB for durable conversational and operational state in high-scale
     agent systems.
   - Exception rule: Azure SQL can be used only through an explicit exception
     decision in a superseding ADR that preserves the same evidence contract,
     correlation model, and release-gate behavior.
3. HITL-01 to HITL-05 are mandatory control gates:
   - HITL-01 patient-affecting workflow trigger approval
   - HITL-02 bed transfer/reprioritization approval
   - HITL-03 cross-organizational handoff initiation approval
   - HITL-04 policy exception approval
   - HITL-05 forecast-driven staffing/capacity approval
4. HITL controls are release-gated across:
   - docs/SD.md
   - docs/OPERATIONS.md
   - docs/TEST.md
5. Side-effecting actions are blocked when required HITL evidence is missing.
6. HITL approval evidence must conform to a mandatory minimum schema:
   - gateId
   - approverObjectId
   - approverRole
   - decisionTimestampUtc
   - correlationId
   - decisionContextHash
   - decisionOutcome
   - sourceWorkflow
7. Missing or invalid HITL evidence results in deterministic deny-by-default behavior:
   - deny side-effecting action
   - emit audit event with reason code
   - notify workflow owner and require new approval artifact
8. HITL control enforcement is mandatory across three layers:
   - runtime guard checks before side effects
   - CI/CD release gates for evidence presence and schema validation
   - test coverage in positive and negative gate scenarios

## Consequences

- Architecture and operations now share a single control taxonomy for human approvals.
- Release evidence must include HITL gate validation for affected workflows.
- Governance posture improves for CH-C03/CH-C10-aligned auditability.
- Runtime persistence is standardized on Cosmos DB for implementation consistency,
   traceability, and reduced cross-environment divergence.

## Implementation Notes

- Cosmos DB is the default and required persistence engine for MVP and PROD
   approval-event and audit records.
- Approval-event and audit containers must enforce a stable schema contract,
   correlation ID indexing, and retention settings aligned with compliance
   evidence requirements.
- Any change to HITL gate definitions requires synchronized updates in SD,
  OPERATIONS, and TEST documents.
- Future runtime replacement or HITL taxonomy changes require a superseding ADR.
