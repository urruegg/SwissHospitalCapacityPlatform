# ADR 0007-0011 Hardening Delta Summary

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Reviewed |
| **Previous Version** | N/A |
| **Scope** | Consolidated changes and implementation actions from ADR-0007 to ADR-0011 |

## Purpose

This document consolidates the design hardening updates applied to:

1. `docs/adr/0007-mvp-agent-runtime-and-hitl-release-gates.md`
2. `docs/adr/0008-agent-runtime-pattern-scope-and-selection.md`
3. `docs/adr/0009-reliability-and-dr-baseline-for-sit-prod.md`
4. `docs/adr/0010-policy-as-code-and-release-evidence-gates.md`
5. `docs/adr/0011-cantonal-legal-applicability-gate.md`

It is intended as a Sprint 5 kickoff reference for autonomous issue/PR execution.

## Executive Delta

### What changed materially

1. Runtime persistence and HITL evidence rules are now explicit and enforceable.
2. Runtime pattern choice (application-hosted vs Foundry-hosted vs hybrid) now has hard go/no-go and approval gates.
3. Reliability and DR moved from intent to measurable baseline target values.
4. Policy-as-code now includes quantifiable promotion thresholds, canonical evidence schema, and exception expiry behavior.
5. Cantonal legal applicability now has mandatory annex schema, approval ownership, and promotion blockers.

### Why this matters

1. Reduces implementation ambiguity across SIT and PROD.
2. Converts governance intent into verifiable release controls.
3. Improves auditability and public-sector compliance readiness.
4. Enables consistent autonomous execution by repository agents.

## ADR-by-ADR Delta Matrix

| ADR | Before hardening | After hardening | Implementation effect |
| ----- | ----- | ----- | ----- |
| `0007` | HITL and runtime direction defined, but persistence and evidence semantics partially open | Cosmos DB selected as default persistence target; mandatory HITL evidence schema; deterministic deny behavior; multi-layer enforcement added | Runtime and approval-event implementation can be standardized without team-specific interpretation |
| `0008` | Runtime pattern scope defined, but exception criteria and owners not explicit | GA-in-region go/no-go for Foundry paths; hybrid boundary contract template; enforcement gates; owner approvals; monthly revalidation | Runtime selection becomes reviewable and repeatable at promotion gates |
| `0009` | DR and reliability gates present, but target values and cadence not explicit | Recovery classes (R1/R2/R3) with baseline RTO/RPO values; rehearsal evidence schema; restore proof recency; exception limits; cadence checker | Reliability readiness can be objectively measured before PROD promotion |
| `0010` | Policy-as-code and evidence gate intent defined, but thresholds and schema not explicit | Zero critical-failure promotion target; mandatory control coverage target; canonical evidence schema; expiry-blocking exceptions; ownership model; monthly review | CI/CD policy checks become enforceable with audit-grade evidence outputs |
| `0011` | Cantonal applicability gate defined, but annex schema and severity thresholds not explicit | Mandatory annex field schema; zero unresolved high-severity gap threshold; owner approvals; exception max validity; monthly legal applicability revalidation | Cantonal legal readiness is explicitly testable and promotion-blocking when incomplete |

## New Baseline Control Targets

### Runtime and HITL controls

1. Cosmos DB is the default MVP/PROD persistence for conversation and approval-event state.
2. HITL evidence requires canonical minimum fields.
3. Missing or invalid HITL evidence is deny-by-default for side-effecting actions.

### Runtime pattern controls

1. Foundry path is no-go if required capability is not GA in selected region.
2. Hybrid runtime requires explicit boundary contract and fallback path.
3. Monthly runtime revalidation is mandatory.

### Reliability controls

1. R1 target: RTO <= 60m, RPO <= 15m.
2. R2 target: RTO <= 4h, RPO <= 1h.
3. R3 target: RTO <= 24h, RPO <= 24h.
4. Stateful restore proof must be fresh (<= 90 days) for promotion.

### Policy and evidence controls

1. Zero critical policy failures for SIT to PROD promotion.
2. 100 percent coverage for mandatory controls in changed scope.
3. Canonical policy evidence artifact fields are required.
4. Expired exceptions are hard blockers.

### Cantonal applicability controls

1. Canton annex entries require canonical fields.
2. Zero unresolved high-severity legal gaps for target canton promotion.
3. Monthly legal applicability revalidation is mandatory.

## Enforcement Gate Model (Consolidated)

1. CI gate:
   - runtime matrix and policy checks execute for affected scope.
   - evidence artifacts generated and attached to pipeline outputs.
2. SIT gate:
   - boundary contracts, DR evidence, and policy evidence validated.
   - unresolved high-severity compliance/reliability blockers stop progression.
3. PROD gate:
   - all SIT evidence plus owner approvals and residual-risk statement.
   - expired exceptions block promotion.
4. Runtime gate:
   - side-effecting operations enforce boundary contracts and HITL evidence at execution time.

## Approval Ownership Baseline

1. Architecture Owner:
   - runtime pattern decisions
   - boundary contracts
   - policy-pack scope approvals
2. Security and Compliance Owner:
   - data class, residency, control mapping
   - exception risk acceptance recommendation
3. Operations and Release Owner:
   - production readiness
   - fallback/recovery supportability
   - release evidence completeness
4. Legal and Compliance Owner (cantonal gate specific):
   - canton-specific legal applicability sign-off

## Exception Management Baseline

1. Every exception must include:
   - rationale
   - compensating controls
   - owner
   - explicit expiry
   - mitigation plan
   - follow-up validation date
2. Maximum baseline validity for critical governance exceptions: 90 days.
3. Expired exceptions are promotion blockers until renewed or remediated.

## Sprint 5 Operational Action Set

### Immediate (Phase 0 to Phase 1)

1. Create and populate runtime decision matrix and hybrid boundary contract register.
2. Create `docs/compliance/cantonal-annex.md` with baseline schema.
3. Create `docs/operations/reliability-dr-profile.md` with R1/R2/R3 targets.
4. Update `docs/TEST.md` and `docs/ALM_PLAN.md` with new evidence gate fields.

### Near-term (Phase 2 to Phase 3)

1. Implement CI checks for mandatory control coverage and critical failure blocking.
2. Implement SIT rehearsal evidence pipeline for DR and policy controls.
3. Add monthly cadence checker issues/workflow for runtime, policy, and legal applicability reviews.

### Stabilization (Phase 4)

1. Align impacted agent golden tasks to enforce updated gates.
2. Validate deny-by-default runtime behavior on missing HITL evidence.
3. Confirm PR output contracts include all evidence schema references.

## Traceability References

1. Sprint plan: `sprints/sprint-05-caf-waf-mvp-sit-prod.md`
2. Review baseline priority: `docs/reviews/2026-06-09-ama-caf-waf-review session.md`
3. Additional review inputs:
   - `docs/reviews/2026-06-08-ama-review-session-csa-sd-challanger.md`
   - `docs/reviews/2026-06-08-ama-review-session-csa-cantonal-full.md`
4. ADR set:
   - `docs/adr/0007-mvp-agent-runtime-and-hitl-release-gates.md`
   - `docs/adr/0008-agent-runtime-pattern-scope-and-selection.md`
   - `docs/adr/0009-reliability-and-dr-baseline-for-sit-prod.md`
   - `docs/adr/0010-policy-as-code-and-release-evidence-gates.md`
   - `docs/adr/0011-cantonal-legal-applicability-gate.md`

## Exit Condition for This Summary

This summary remains valid as Sprint 5 kickoff baseline until one of the following occurs:

1. a superseding ADR changes governance targets,
2. a legal applicability change alters canton controls,
3. reliability target classes are revised by architecture decision.
