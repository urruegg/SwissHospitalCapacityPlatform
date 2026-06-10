# Sprint 05 Control and Traceability Bootstrap

| Field | Value |
| ----- | ----- |
| **Version** | 1.3.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | 1.2.0 (Phase 3 reliability/DR evidence) |

## Purpose

This directory holds the Sprint 05 **Phase 0** control and traceability
artifacts: the execution controls, issue structure, and evidence templates that
govern the rest of the sprint. It is the deliverable set for Phase 0 of
[`docs/sprints/sprint-05-caf-waf-mvp-sit-prod.md`](../sprint-05-caf-waf-mvp-sit-prod.md),
built from the baselines in
[`docs/adr/0007-0011-hardening-delta-summary.md`](../../adr/0007-0011-hardening-delta-summary.md)
and the CAF/WAF review session.

## Artifacts

| Artifact | Phase 0 Task | Purpose |
| ----- | ----- | ----- |
| [`phase-issue-map.md`](phase-issue-map.md) | Task 1 | Validated phase issue map and dependency model |
| [`requires-validation-register.md`](requires-validation-register.md) | Task 2 | Requires-validation register sourced from review findings |
| [`pr-evidence-checklist.md`](pr-evidence-checklist.md) | Task 3 | PR evidence checklist with FR/NFR/CH controls, gate outcomes, residual risks |
| [`gate-sequence.md`](gate-sequence.md) | Task 4 | Confirmed SIT and PROD gate sequence for all remaining phases |
| [`phase-2-policy-gate.md`](phase-2-policy-gate.md) | Phase 2 (#35) | Policy-as-code gate implementation and SIT gate evidence (RV-03) |
| [`phase-3-reliability-dr.md`](phase-3-reliability-dr.md) | Phase 3 (#36) | DR rehearsal/restore-proof SIT evidence and PROD readiness recommendation (RV-02, RV-07, RV-11) |
| [`phase-4-agent-hardening.md`](phase-4-agent-hardening.md) | Phase 4 (#37) | Autonomous agent execution hardening: HITL deny-by-default, runtime boundary enforcement, ADR-IaC drift control, and SIT golden-replay evidence (RV-10, RV-12) |

## Baseline Inputs

1. `docs/sprints/sprint-05-caf-waf-mvp-sit-prod.md`
2. `docs/adr/0007-0011-hardening-delta-summary.md`
3. `docs/runbooks/sprint-05-copilot-delegation-runbook.md`
4. `docs/reviews/2026-06-09-ama-caf-waf-review session.md`
5. `docs/reviews/2026-06-08-ama-review-session-csa-cantonal-full.md`

## Phase 0 Definition of Done Mapping

| Definition of Done item | Satisfied by |
| ----- | ----- |
| Issue tree exists and is traceable | [`phase-issue-map.md`](phase-issue-map.md) |
| PR template coverage includes FR/NFR and CH control references | [`pr-evidence-checklist.md`](pr-evidence-checklist.md) |
| No unresolved scope ambiguity | [`requires-validation-register.md`](requires-validation-register.md) + [`gate-sequence.md`](gate-sequence.md) |

## Phase 0 Gate Status

| Gate | Criteria | Status |
| ----- | ----- | ----- |
| SIT | All phase issues created and linked; evidence template committed | Met on merge of this PR |
| PROD | Human review confirms sprint governance controls are complete | Pending human review |

## Scope Note

These artifacts are governance documentation only. They create no infrastructure
and change no runtime behavior, consistent with ADR-0002 (agents and controls are
realized as Markdown). Phase 1..4 implementation work is tracked in the
respective phase issues and must not start until Phase 0 PROD gate passes.

