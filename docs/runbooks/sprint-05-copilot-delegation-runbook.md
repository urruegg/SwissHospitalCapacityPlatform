# Sprint 05 Copilot Delegation Runbook

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | N/A |

## Purpose

Provide one operational runbook to kick off Sprint 05 with GitHub issues and `@copilot` delegation, aligned to ADR-0007..0011 and the sprint phase model.

## Baseline References

1. `docs/sprints/sprint-05-caf-waf-mvp-sit-prod.md`
2. `docs/adr/0007-0011-hardening-delta-summary.md`
3. `docs/adr/0007-mvp-agent-runtime-and-hitl-release-gates.md`
4. `docs/adr/0008-agent-runtime-pattern-scope-and-selection.md`
5. `docs/adr/0009-reliability-and-dr-baseline-for-sit-prod.md`
6. `docs/adr/0010-policy-as-code-and-release-evidence-gates.md`
7. `docs/adr/0011-cantonal-legal-applicability-gate.md`
8. `docs/reviews/2026-06-09-ama-caf-waf-review session.md`
9. `docs/reviews/2026-06-08-ama-review-session-csa-sd-challanger.md`
10. `docs/reviews/2026-06-08-ama-review-session-csa-cantonal-full.md`

## Required Label Set

1. `sprint-05`
2. `phase-0`
3. `phase-1`
4. `phase-2`
5. `phase-3`
6. `phase-4`
7. `governance`
8. `compliance`
9. `security`
10. `reliability`
11. `policy-as-code`
12. `runtime-governance`
13. `adr-alignment`
14. `sit-gate`
15. `prod-gate`
16. `evidence-required`
17. `blocked`
18. `ready-for-review`

## Issue Set

1. Sprint 05 - CAF/WAF MVP SIT PROD Execution (umbrella)
2. Sprint 05 Phase 0 - Control and Traceability Bootstrap
3. Sprint 05 Phase 1 - Documentation Baseline Upgrade
4. Sprint 05 Phase 2 - Policy as Code and Governance Gates
5. Sprint 05 Phase 3 - Reliability and DR Operationalization
6. Sprint 05 Phase 4 - Autonomous Agent Execution Hardening

## Dependency Model

1. Umbrella is parent of Phase 0..4.
2. Phase 0 blocks all phases.
3. Phase 1 depends on Phase 0 and blocks Phase 2 and Phase 3.
4. Phase 2 depends on Phase 0 and Phase 1.
5. Phase 3 depends on Phase 0 and Phase 1.
6. Phase 4 depends on Phase 2 and Phase 3.

## Kickoff Comment Templates

### Umbrella

`@copilot Execute Sprint 05 from this umbrella issue by orchestrating Phase 0 to Phase 4 in order, using mandatory baselines in docs/sprints/sprint-05-caf-waf-mvp-sit-prod.md and docs/adr/0007-0011-hardening-delta-summary.md. Use draft PR first per phase, enforce SIT before PROD gates, block promotion on critical failures or expired exceptions, and maintain FR/NFR/CH traceability in every PR.`

### Phase 0

`@copilot Execute Phase 0 now. Build dependency map, create requires-validation register, and create PR evidence checklist template with FR/NFR/CH mappings and gate outcomes. Open draft PR and post evidence links.`

### Phase 1

`@copilot Execute Phase 1 document-first baseline upgrade now. Update baseline docs per sprint and ADR controls, add cantonal annex and reliability profile artifacts, run markdown/link checks, open draft PR, and post traceability evidence.`

### Phase 2

`@copilot Execute Phase 2 now. Implement policy-as-code checks, enforce zero critical-failure promotion threshold, implement evidence schema and exception expiry blocker behavior, integrate cantonal annex checks, open draft PR, and post SIT gate evidence.`

### Phase 3

`@copilot Execute Phase 3 now. Operationalize reliability and DR controls with R1/R2/R3 targets, run SIT rehearsal, attach restore proof and risk ownership, open draft PR, and post SIT pass/fail with PROD readiness recommendation.`

### Phase 4

`@copilot Execute Phase 4 now. Update golden tasks, validate positive and negative gate paths, enforce deny-by-default for missing HITL evidence, validate runtime boundary enforcement, open draft PR, and post final autonomous readiness statement.`

## Close Criteria

1. Every issue has labels, dependencies, and kickoff comment posted.
2. Every phase starts with draft PR and evidence-first reporting.
3. Umbrella tracks all phase links and final closure state.
