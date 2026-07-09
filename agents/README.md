# Superpowers Execution Playbook

| Field | Value |
| ----- | ----- |
| **Version** | 2.4.0 |
| **Date** | 2026-07-09 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | 2.3.0 (updated Cutover Status narrative for the 2.0.0 `agents-archive/` → `agents/` restructure) |

## Purpose

This guide explains how to run development using GitHub Copilot CLI with the
Superpowers plugin as the default execution method, while preserving repository
governance controls for safety, traceability, and compliance.

Use this as the operating how-to for issue creation, planning, execution,
verification, and approval gates.

## Operating Model

### Human role

1. Set goals, priority, and acceptance criteria.
2. Approve deploy-gated steps.
3. Resolve scope, compliance, and tradeoff decisions.
4. Accept or reject final PRs.

### Copilot + Superpowers role

1. Execute scoped work from issue inputs.
2. Produce auditable draft PRs with traceability.
3. Refuse out-of-scope or unsafe actions.
4. Follow workflow discipline: design -> plan -> execute -> review -> verify.

## Superpowers Skills System (Mandatory)

Before starting any task:

1. Check if a Superpowers skill applies.
2. If yes, read the relevant `SKILL.md` and follow it.

When a skill applies:

1. It is mandatory to use it.
2. Do not skip steps.
3. If multiple skills apply, execute them in a documented sequence.

Core skills to always consider:

1. `test-driven-development`
2. `systematic-debugging`
3. `writing-plans`
4. `verification-before-completion`

## Cutover Status

1. Default mode is Superpowers-driven execution.
2. All agent packs (prompts, runtime manifests, golden tasks) live under
	`agents/<name>/` as the **single source of truth**. The `agents-archive/`
	folder was retired in the 2.0.0 restructure — see
	[`LEGACY-STATUS.md`](LEGACY-STATUS.md) for the changelog and `git log` for
	historical Sprint 09 bodies (`bm-copilot`, `csa-agent` Sprint 09 v2 body).
3. Governance controls remain source-of-truth in:
	- [AGENTS.md](../AGENTS.md)
	- [.github/copilot/mcp.json](../.github/copilot/mcp.json)
	- [docs/TEST.md](../docs/TEST.md)
	- [.github/PULL_REQUEST_TEMPLATE.md](../.github/PULL_REQUEST_TEMPLATE.md)

## Superpowers Workflow Mapping

Use this sequence as mandatory baseline unless a higher-priority repository safety or compliance rule requires an additional step.

1. brainstorming: refine scope, alternatives, and acceptance criteria.
2. writing-plans: create a small-step implementation plan with explicit files.
3. execution: implement in small batches, preferring TDD where applicable.
4. requesting-code-review: run self-review and policy checks before PR ready.
5. verification-before-completion: execute required validation commands and
	compare outcomes to the plan.

## Work Readiness Checklist

Before execution:

1. Issue includes explicit FR or NFR IDs from [docs/PRD.md](../docs/PRD.md).
2. Scope is bounded to one clear outcome.
3. Target files or lane are stated.
4. Definition of done is included.
5. Dependencies and blockers are listed.
6. Execution mode is set to `superpowers` unless legacy compatibility is required.

## Issue Authoring Pattern (Copy/Paste)

Use this issue body pattern for concrete delegation.

```text
Title: [MVP:<lane>] <outcome>

@copilot please execute this scope using Superpowers workflow.

Execution mode:
- superpowers

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

## Concrete Execution Examples

### Example 1: Architecture slice

- Goal: Define MVP app/API boundary for React command center
- Requirements: FR-CX-001, FR-CX-002, NFR-PERF-005, NFR-SEC-001
- Output: Updated section in [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) with lane-level decisions and open risks

### Example 2: Data contract pack

- Goal: Add first contract pack for ingest, AI outputs, and integration events
- Requirements: FR-DATA-001 to FR-DATA-008, NFR-DQ-001 to NFR-DQ-004
- Output: Contract sections and traceability update in [docs/DATA.md](../docs/DATA.md)

### Example 3: Compliance evidence hardening

- Goal: Add evidence ownership and cadence mapping for CH-C controls
- Requirements: NFR-COMP-005 to NFR-COMP-010
- Output: Control-to-evidence matrix update in [docs/COMPLIANCE.md](../docs/COMPLIANCE.md)

### Example 4: Landing zone implementation

- Goal: Produce IaC plan and what-if evidence for MVP baseline resources
- Requirements: FR-GOV-003, FR-GOV-004, NFR-SEC-001 to NFR-SEC-004
- Output: infra changes + what-if summary in draft PR
- Gate: deploy apply requires approved-to-apply comment

### Example 5: Final verification

- Goal: Validate release readiness of merged MVP slices
- Requirements: FR-GOV-001, FR-GOV-004, NFR-MAINT-002, NFR-MAINT-003
- Output: gate evidence and residual gaps in [docs/TEST.md](../docs/TEST.md)

## Handoff Contract Between Iterations

Each execution iteration should provide these items for next-step reuse:

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
3. Triage PRs and decide: accept, revise, or defer.

### Weekly cadence

1. Run readiness checks against [docs/TEST.md](../docs/TEST.md).
2. Run drift checks for selected scope when relevant.
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
| Validation debt | PRs without evidence | Run mandatory gate checklist from [docs/TEST.md](../docs/TEST.md) |

## Kick-Start Backlog (Suggested)

1. MVP-001: Solution slice hardening for React/API operational path
2. MVP-002: First data contract pack and lineage evidence anchors
3. MVP-003: Compliance evidence ownership and review cadence matrix
4. MVP-004: Landing zone what-if pack for MVP baseline resources
5. MVP-005: App/integration implementation slice for command-center and partner loop
6. MVP-006: Release readiness evidence and residual risk report
7. MVP-007: Post-merge drift baseline report

## References

1. [AGENTS.md](../AGENTS.md)
2. [docs/PRD.md](../docs/PRD.md)
3. [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
4. [docs/ALM_PLAN.md](../docs/ALM_PLAN.md)
5. [docs/TEST.md](../docs/TEST.md)
6. [docs/OPERATIONS.md](../docs/OPERATIONS.md)
7. [docs/runbooks/superpowers-cutover.md](../docs/runbooks/superpowers-cutover.md)
8. [LEGACY-STATUS.md](LEGACY-STATUS.md)
