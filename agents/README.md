# Agents Delegation Playbook

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-06-08 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | 1.0.0 (initial delegation playbook baseline) |

## Purpose

This guide explains how to use repository-defined GitHub Copilot agents in a
high-delegation model to implement MVP scope safely, traceably, and quickly.

Use this as the operating how-to for issue creation, delegation sequencing,
agent handoff quality, and approval gates.

## Delegation Operating Model

### Human role (you)

1. Set goals, priority, and acceptance criteria.
2. Approve deploy-gated steps.
3. Resolve scope, compliance, and tradeoff decisions.
4. Accept or reject final PRs.

### Agent role

1. Execute scoped work from issue inputs.
2. Produce auditable draft PRs with traceability.
3. Refuse out-of-scope or unsafe actions.
4. Hand off to downstream agents through artefact quality and issue linkage.

## Agent Map and Best Use

| Agent | Best use | Inputs required | Primary outputs |
| ----- | ----- | ----- | ----- |
| orchestrator | Cross-cutting triage and routing | Issue summary, requirement IDs, requested outcome | Routing comment, label, or small cross-cutting PR |
| spec-parser-agent | Requirement extraction from specs | Source docs under docs/specs | PRD updates in [docs/PRD.md](../docs/PRD.md) |
| solution-design-agent | Architecture and MVP slicing | PRD baseline | Architecture updates in [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) |
| data-design-agent | Data model/contracts/governance shape | PRD + architecture | Data design updates in [docs/DATA.md](../docs/DATA.md) |
| compliance-agent | Compliance control mapping and evidence coverage | PRD + architecture + data/security docs | Compliance updates in [docs/COMPLIANCE.md](../docs/COMPLIANCE.md) |
| landing-zone-agent | IaC and Azure landing-zone outputs | PRD + architecture + approved infra scope | Infrastructure artifacts and what-if evidence |
| app-builder-agent | App and integration slices | PRD requirement IDs + architecture decisions | App/integration changes under apps/integrations |
| test-verifier-agent | Readiness and validation evidence | All changed artefacts + acceptance criteria | Validation matrix and gate evidence in [docs/TEST.md](../docs/TEST.md) |
| review-session-agent | Evaluate review-session transcripts against repository artefacts | Transcript source under `docs/reviews/raw/` + target artefact set | Dedicated review report under `docs/reviews/` |
| drift-analyzer | Post-merge drift detection and reporting | Target subscription + reference artefacts | Drift reports and severity-labelled findings |

## Recommended MVP Delegation Sequence

Use this sequence as default unless a specific sprint objective requires reordering.

1. spec-parser-agent: confirm requirement completeness and IDs.
2. solution-design-agent: lock architecture and MVP implementation slices.
3. data-design-agent and compliance-agent in parallel.
4. landing-zone-agent and app-builder-agent in parallel after data/compliance baseline is accepted.
5. test-verifier-agent: run final readiness gate.
6. drift-analyzer: run baseline drift scan after merge and after first deployment wave.

## Delegation Readiness Checklist

Before delegating to any agent:

1. Issue includes explicit FR or NFR IDs from [docs/PRD.md](../docs/PRD.md).
2. Scope is bounded to one clear outcome.
3. Target files or lane are stated.
4. Definition of done is included.
5. Dependencies and blockers are listed.

## Issue Authoring Pattern (Copy/Paste)

Use this issue body pattern for concrete delegation.

```text
Title: [MVP:<lane>] <outcome>

@copilot please run <agent-name> for this scope.

Requirements:
- FR-...
- NFR-...

Scope:
- In scope: ...
- Out of scope: ...

Target artefacts:
- docs/... or infra/... or apps/...

Definition of done:
1) ...
2) ...
3) ...

Constraints:
- Swiss region / PHI / policy constraints
- No deploy/delete unless explicitly approved

Dependencies:
- Linked issues/PRs
```

## Concrete Delegation Examples

### Example 1: Architecture slice

- Agent: solution-design-agent
- Goal: Define MVP app/API boundary for React command center
- Requirements: FR-CX-001, FR-CX-002, NFR-PERF-005, NFR-SEC-001
- Output: Updated section in [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) with lane-level decisions and open risks

### Example 2: Data contract pack

- Agent: data-design-agent
- Goal: Add first contract pack for ingest, AI outputs, and integration events
- Requirements: FR-DATA-001 to FR-DATA-008, NFR-DQ-001 to NFR-DQ-004
- Output: Contract sections and traceability update in [docs/DATA.md](../docs/DATA.md)

### Example 3: Compliance evidence hardening

- Agent: compliance-agent
- Goal: Add evidence ownership and cadence mapping for CH-C controls
- Requirements: NFR-COMP-005 to NFR-COMP-010
- Output: Control-to-evidence matrix update in [docs/COMPLIANCE.md](../docs/COMPLIANCE.md)

### Example 4: Landing zone implementation

- Agent: landing-zone-agent
- Goal: Produce IaC plan and what-if evidence for MVP baseline resources
- Requirements: FR-GOV-003, FR-GOV-004, NFR-SEC-001 to NFR-SEC-004
- Output: infra changes + what-if summary in draft PR
- Gate: deploy apply requires approved-to-apply comment

### Example 5: Final verification

- Agent: test-verifier-agent
- Goal: Validate release readiness of merged MVP slices
- Requirements: FR-GOV-001, FR-GOV-004, NFR-MAINT-002, NFR-MAINT-003
- Output: gate evidence and residual gaps in [docs/TEST.md](../docs/TEST.md)

## Handoff Contract Between Agents

Each upstream agent should provide these items for downstream reuse:

1. Requirement IDs implemented.
2. Changed file list with purpose.
3. Assumptions and unresolved questions.
4. Validation evidence executed.
5. Residual risks and proposed owner.

## Approval and Safety Gates

### Mandatory gates

1. No deploy/delete actions without explicit human approval.
2. No edits to governance-sensitive files without explicit issue scope.
3. PR must include requirement traceability and evidence summary.
4. Security/compliance-impact statement must be explicit.

### Deploy gate

For deploy-capable work, require the exact approval phrase:

- approved-to-apply

Do not approve until the what-if/plan evidence is reviewed.

## Delegation Cadence

### Daily cadence

1. Open or reprioritize 1-3 issues for active slices.
2. Ensure each issue has FR/NFR IDs and done criteria.
3. Triage PRs produced by agents and decide: accept, revise, or defer.

### Weekly cadence

1. Run test-verifier-agent readiness check.
2. Run drift-analyzer against selected scope.
3. Update risk and blocker log.
4. Rebaseline next week delegation queue.

## Common Failure Modes and Fixes

| Failure mode | Symptom | Fast fix |
| ----- | ----- | ----- |
| Scope too broad | Large unfocused PR | Split into smaller issue slices |
| Missing requirements | Refusal or weak traceability | Add FR/NFR IDs in issue body |
| Premature deploy request | Agent refuses apply | Run plan-first and approve explicitly |
| Cross-lane inconsistency | Conflicting docs/artefacts | Insert explicit handoff issue between agents |
| Validation debt | PRs without evidence | Trigger test-verifier-agent before merge |

## Kick-Start Delegation Backlog (Suggested)

1. MVP-001: Solution slice hardening for React/API operational path (solution-design-agent)
2. MVP-002: First data contract pack and lineage evidence anchors (data-design-agent)
3. MVP-003: Compliance evidence ownership and review cadence matrix (compliance-agent)
4. MVP-004: Landing zone what-if pack for MVP baseline resources (landing-zone-agent)
5. MVP-005: App/integration implementation slice for command-center and partner loop (app-builder-agent)
6. MVP-006: Release readiness evidence and residual risk report (test-verifier-agent)
7. MVP-007: Post-merge drift baseline report (drift-analyzer)

## References

1. [AGENTS.md](../AGENTS.md)
2. [docs/PRD.md](../docs/PRD.md)
3. [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
4. [docs/ALM_PLAN.md](../docs/ALM_PLAN.md)
5. [docs/TEST.md](../docs/TEST.md)
6. [docs/OPERATIONS.md](../docs/OPERATIONS.md)
