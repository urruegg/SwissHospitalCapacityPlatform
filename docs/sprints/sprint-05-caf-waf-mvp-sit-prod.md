# Sprint 5 - CAF/WAF Baseline Hardening and MVP SIT/PROD Implementation

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-06-09 |
| **Author** | Urs Rueegg |
| **Status** | Completed |
| **Previous Version** | 1.0.0 (initial sprint plan baseline) |

## Sprint Goal

Convert AMA review outcomes into an implementation-ready and governance-auditable baseline, then execute phased SIT and PROD implementation with strict release gates and explicit Definition of Done per phase.

This sprint is designed to be delegated to repository agents for autonomous execution under GitHub issue and PR controls.

## Completion Summary

Sprint 5 was executed end-to-end using the canonical issue chain and phase PRs.

Canonical issue chain:
1. `#32` Sprint umbrella (closed)
2. `#33` Phase 0 (closed)
3. `#34` Phase 1 (closed)
4. `#35` Phase 2 (closed)
5. `#36` Phase 3 (closed)
6. `#37` Phase 4 (closed)

Phase PR outcomes:
1. `#38` Phase 0 — merged
2. `#39` Phase 1 — merged
3. `#40` Phase 2 — merged
4. `#41` Phase 3 — merged
5. `#42` Phase 4 — merged

Primary evidence bundle:
1. `docs/sprints/sprint-05/README.md`
2. `docs/sprints/sprint-05/gate-sequence.md`
3. `docs/sprints/sprint-05/phase-issue-map.md`
4. `docs/sprints/sprint-05/pr-evidence-checklist.md`
5. `docs/sprints/sprint-05/requires-validation-register.md`

## Review Baseline and Priority

Primary review baseline:
1. `docs/reviews/2026-06-09-ama-caf-waf-review session.md`

Additional review baselines:
1. `docs/reviews/2026-06-08-ama-review-session-csa-sd-challanger.md`
2. `docs/reviews/2026-06-08-ama-review-session-csa-cantonal-full.md`

## Trigger Model

This sprint runs as a GitHub issue-driven, agent-executed workflow.

1. Sprint issue is the orchestration anchor.
2. Work is split into phase issues and linked draft PRs.
3. `@copilot` mention is used to trigger autonomous agent execution for each phase issue.
4. All deploy/delete-ceiling actions remain gated by explicit human approval and repository confirmation rules.

## Scope

### In scope

1. Refine and extend solution documentation to establish a new baseline requirement and design set aligned to CAF/WAF findings.
2. Define domain-specific phased implementation plan with SIT and PROD gates and phase-level Definition of Done.
3. Implement phases using repository agents with traceable evidence and release-gate compliance.
4. Close high-priority gaps from review baseline, especially:
   - cantonal legal applicability and control mapping
   - reliability and DR readiness definition
   - policy-as-code and evidence automation
   - runtime pattern consistency decisioning

### Out of scope

1. Destructive production operations.
2. Non-Azure cloud migration patterns.
3. Scope expansion beyond reviewed baseline requirements unless approved in sprint issue.

## Step Plan (Mandatory)

### Step 1: Documentation Baseline First

Refine and extend documentation to create Sprint 5 baseline versions before implementation changes.

Target documents:
1. `docs/PRD.md`
2. `docs/SD.md`
3. `docs/ARCHITECTURE.md`
4. `docs/COMPLIANCE.md`
5. `docs/SECURITY.md`
6. `docs/AI.md`
7. `docs/INFRASTRUCTURE.md`
8. `docs/ALM_PLAN.md`
9. `docs/TEST.md`
10. `docs/OPERATIONS.md`
11. `docs/adr/0007-mvp-agent-runtime-and-hitl-release-gates.md` (only if required by change impact)

New documents expected in this sprint:
1. `docs/compliance/cantonal-annex.md` (cantonal control deltas and legal applicability map)
2. `docs/architecture/caf-waf-alignment-matrix.md` (CAF/WAF delta and closure tracking)
3. `docs/operations/reliability-dr-profile.md` (RTO/RPO, failover boundaries, DR evidence model)

### Step 2: Domain-Specific Phased Plan

Define phase plan by domain with SIT and PROD gates and explicit Definition of Done.

Domains:
1. Governance and compliance
2. Security and policy-as-code
3. Architecture and runtime alignment
4. Reliability and operations evidence
5. Delivery and test automation

### Step 3: Implement Phases

Implement each phase through issue-driven agent execution with evidence-first PR output contract and mandatory gate validation.

## Phase Plan and Definition of Done

### Phase 0 - Sprint Control and Traceability Bootstrap

Objective:
Establish sprint execution controls, issue decomposition, and evidence templates.

Implementation tasks:
1. Create sprint umbrella issue and linked phase issues.
2. Create per-phase PR checklist with requirement and control mapping.
3. Create `Requires validation` register sourced from review findings.

SIT gate:
1. All phase issues created and linked.
2. Evidence template committed.

PROD gate:
1. Human review confirms sprint governance controls are complete.

Definition of Done:
1. Issue tree exists and is traceable.
2. PR template coverage includes FR/NFR and CH control references.
3. No unresolved scope ambiguity.

### Phase 1 - Documentation Baseline Upgrade (Document First)

Objective:
Upgrade baseline docs according to review priorities and formalize open decisions.

Implementation tasks:
1. Integrate high-priority findings from 2026-06-09 CAF/WAF review.
2. Add cantonal compliance annex and legal applicability workflow.
3. Add architecture pattern decision matrix for runtime modes.
4. Add reliability/DR profile and acceptance model.
5. Update test and ALM docs to include evidence automation checkpoints.

SIT gate:
1. Draft PR with all baseline doc changes.
2. Markdown lint and link checks pass.
3. Traceability matrix updated for changed requirements and controls.

PROD gate:
1. Approved documentation PR merged to main.
2. Versioning headers updated for every changed document.

Definition of Done:
1. All target baseline docs updated and internally consistent.
2. All review high-priority findings are either closed or explicitly deferred with owner and due phase.
3. No unresolved contradictions between `docs/AI.md` and `docs/ARCHITECTURE.md` runtime pattern decisions.

### Phase 2 - Policy and Governance Implementation

Objective:
Convert documented controls into enforceable, testable governance and policy gates.

Implementation tasks:
1. Add policy-as-code checks for residency and deployment-type restrictions.
2. Add control-owner and evidence cadence for CH-C03, CH-C05, CH-C10.
3. Add release checklist sections for DSR, incident, and transfer-risk validation.

SIT gate:
1. CI checks enforce policy baseline on SIT validation path.
2. Evidence artifacts generated for at least one SIT validation run.

PROD gate:
1. Policy checks required on production promotion path.
2. Human-approved sign-off on legal and compliance controls.

Definition of Done:
1. Control checks are automated in CI/CD where technically feasible.
2. Manual controls have explicit runbooks and owners.
3. Evidence artifacts are attached to release records.

### Phase 3 - Reliability and DR Operationalization

Objective:
Define and validate reliability posture for MVP under CAF/WAF reliability expectations.

Implementation tasks:
1. Implement reliability profile checks (zone redundancy posture, backup/restore controls, dependency isolation).
2. Add DR runbook and SIT rehearsal checklist.
3. Capture recovery test evidence model and cadence.

SIT gate:
1. At least one SIT DR rehearsal or tabletop run completed and documented.
2. Restore/failover assumptions validated or marked with bounded risk acceptance.

PROD gate:
1. PROD readiness statement includes RTO/RPO commitments and unresolved risk register.
2. Approval to promote includes documented business acceptance of residual risk.

Definition of Done:
1. DR and reliability controls are documented, testable, and reviewed.
2. Residual risks are explicit with mitigation owners.
3. Reliability section in architecture docs has no open high-severity ambiguity.

### Phase 4 - Autonomous Agent Execution Hardening

Objective:
Ensure autonomous GitHub agent execution is safe, repeatable, and reviewable for ongoing implementation.

Implementation tasks:
1. Add phase-specific golden-task updates for impacted agents.
2. Align agent prompts and output contracts with new sprint baseline requirements.
3. Validate deploy/delete confirmation rule enforcement in affected flows.

SIT gate:
1. Golden-task fixtures pass for impacted agents.
2. Agent output contract fields validated on sprint PRs.

PROD gate:
1. Governance reviewers confirm autonomous execution controls are sufficient for subsequent sprints.

Definition of Done:
1. Agent behavior remains aligned to side-effect ceilings and approval rules.
2. Golden-task coverage includes happy path and failure/refusal path for changed controls.
3. No critical agent governance regressions remain open.

## Domain Work Packages for Agent Delegation

| Work Package | Primary Agent | Supporting Agents | Deliverables |
| ----- | ----- | ----- | ----- |
| WP-01 Baseline documentation upgrade | `solution-design-agent` | `spec-parser-agent`, `compliance-agent` | Updated docs baseline, traceability updates |
| WP-02 Cantonal compliance annex and legal mapping | `compliance-agent` | `review-session-agent`, `solution-design-agent` | `docs/compliance/cantonal-annex.md`, control-owner mapping |
| WP-03 Runtime pattern alignment and ADR consistency | `solution-design-agent` | `orchestrator`, `test-verifier-agent` | Runtime decision matrix, ADR impact proposal |
| WP-04 Policy-as-code and release-gate integration | `landing-zone-agent` | `test-verifier-agent`, `compliance-agent` | CI/CD policy checks, evidence pack flow |
| WP-05 Reliability and DR evidence model | `test-verifier-agent` | `landing-zone-agent`, `compliance-agent` | DR profile doc, rehearsal checklist, validation evidence |
| WP-06 Agent governance hardening | `orchestrator` | `test-verifier-agent`, `review-session-agent` | Updated golden tasks, autonomous execution guardrails |

## Delivery Workflow for Autonomous Execution

1. Open Sprint 5 umbrella issue with links to this sprint file and three review baselines.
2. Open one issue per phase and assign matching work package labels.
3. Trigger agent execution with `@copilot` in each phase issue.
4. Require draft PR first for every phase.
5. Enforce gate order:
   - docs lint and traceability
   - policy and test checks
   - SIT validation evidence
   - approval
   - PROD promotion evidence
6. Merge only when phase Definition of Done is fully satisfied.

## Acceptance Criteria

1. Documentation-first baseline is complete and versioned before implementation PRs start.
2. Phase plan is executed with SIT then PROD gating for each applicable phase.
3. All high-priority findings from `docs/reviews/2026-06-09-ama-caf-waf-review session.md` are either:
   - closed with evidence, or
   - explicitly deferred with owner, due sprint, and risk rationale.
4. Additional findings from the two 2026-06-08 review sessions are incorporated or explicitly dispositioned.
5. Autonomous agent execution artifacts are complete and auditable in issues/PRs.

## Risks and Dependencies

1. Cantonal legal interpretation and sign-off timing can delay compliance closure.
2. Policy automation depth may be constrained by available enforcement surfaces.
3. DR validation in SIT might require coordinated test windows and environment readiness.
4. Runtime alignment decisions might require ADR updates and wider stakeholder review.

## Evidence Requirements

Per phase PR must include:
1. Requirement IDs and CH control IDs impacted.
2. Commands/checks executed and outcome summary.
3. SIT validation evidence links.
4. PROD promotion approval and evidence links where applicable.
5. Residual risks and mitigation ownership.

## Exit Criteria

Sprint 5 is complete when:
1. New documentation baseline is merged and published.
2. Phase implementation artifacts are merged with gates passed.
3. Open high-priority review risks are reduced to accepted residual risk with explicit owner and next action.
4. Repository is ready for next autonomous implementation sprint without unresolved governance blockers.
