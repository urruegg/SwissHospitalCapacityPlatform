# Sprint 06 Copilot Delegation Runbook

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | N/A |

## Purpose

Provide one operational runbook to kick off Sprint 06 with GitHub issues and
@copilot delegation, aligned to the Sprint 06 objective:
minimal-data onboarding, specialty-driven capacity onboarding, and MVP Phase 1
implementation readiness for OOA, DCA, and BMCA.

## Baseline References

1. sprints/sprint-06-minimal-data-onboarding-and-capacity-specialty.md
2. docs/reviews/2026-06-09-ama-cto-mentor-Review.md
3. docs/reviews/2026-06-09-ama-sd-review.md
4. docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform analysis.md
5. docs/reviews/2022-06-09-agent-solution-design-review.md
6. docs/PRD.md
7. docs/SD.md
8. docs/ARCHITECTURE.md
9. docs/DATA.md
10. docs/COMPLIANCE.md
11. docs/TEST.md

## Required Label Set

1. sprint-06
2. phase-0
3. phase-1
4. phase-2
5. phase-3
6. phase-4
7. onboarding
8. specialty-metadata
9. synthetic-data
10. data-platform
11. iac
12. mvp-phase-1
13. optional-phase-3
14. sit-gate
15. prod-gate
16. evidence-required
17. blocked
18. ready-for-review

## Issue Set

1. Sprint 6 - Minimal-Data Onboarding and Specialty-Driven Capacity Onboarding (umbrella)
2. Sprint 6 Phase 0 - Control and Traceability Bootstrap
3. Sprint 6 Phase 1 - IaC Data Platform Kickoff and MVP Agents (OOA DCA BMCA)
4. Sprint 6 Phase 2 - Onboarding Policy and Schema Enforcement
5. Sprint 6 Phase 3 - Provider SIT Evidence and Optional Agent Wave
6. Sprint 6 Phase 4 - Hardening and Sprint Closure

## Dependency Model

1. Umbrella is parent of Phase 0 to Phase 4.
2. Phase 0 blocks all phases.
3. Phase 1 depends on Phase 0 and blocks Phase 2 and Phase 3.
4. Phase 2 depends on Phase 0 and Phase 1.
5. Phase 3 depends on Phase 0 and Phase 1.
6. Phase 4 depends on Phase 2 and Phase 3.

## Sprint 6 Scope Locks

1. Mandatory MVP Phase 1 agents:
   - Operations Orchestrator Agent (OOA)
   - Discharge Coordination Agent (DCA)
   - Bed Management Copilot Agent (BMCA)
2. Optional agents deferred to Phase 3:
   - Demand Forecasting Agent (DFA)
   - Integration Workflow Agent (IWA)
   - Data Quality and Semantics Agent (DQSA)
   - Compliance and Safety Agent (CSA)
   - Explainability and Audit Agent (EAA)

## Kickoff Comment Templates

### Umbrella

@copilot Execute Sprint 6 from this umbrella issue by orchestrating Phase 0 to Phase 4 in order, using mandatory baseline sprints/sprint-06-minimal-data-onboarding-and-capacity-specialty.md. Keep MVP Phase 1 scope locked to OOA DCA BMCA only, keep DFA IWA DQSA CSA EAA optional in Phase 3, enforce draft PR first, maintain FR/NFR/CH traceability, and post evidence links per phase.

### Phase 0

@copilot Execute Phase 0 now. Build phase dependency map, create Sprint 6 requires-validation register updates for onboarding and specialty-capacity deltas, align PR evidence checklist, open draft PR first, and post evidence links.

### Phase 1

@copilot Execute Phase 1 now. Implement IaC-first data-platform kickoff and synthesized SIT datasets, baseline OOA DCA BMCA MVP scope readiness, update PRD SD ARCHITECTURE DATA COMPLIANCE docs, run markdown/link checks, open draft PR first, and post traceability evidence.

### Phase 2

@copilot Execute Phase 2 now. Enforce onboarding minimum-data policy checks, specialty metadata schema validation, cross-tenant identity boundary checks, and synthesized-data SIT gate checks. Open draft PR first and post SIT evidence links.

### Phase 3

@copilot Execute Phase 3 now. Produce provider SIT evidence for Hirslanden and Spital Zollikerberg onboarding metadata contracts, validate degraded-mode and reliability controls, and only then onboard optional agents DFA IWA DQSA CSA EAA if gates are green. Open draft PR first and post evidence links.

### Phase 4

@copilot Execute Phase 4 now. Validate deterministic classification coverage (agent vs service), run golden-task checks for onboarding control paths, consolidate residual risks and ownership, open draft PR first, and post final Sprint 6 closeout readiness statement.

## Close Criteria

1. Every issue has labels, dependencies, and kickoff comment posted.
2. Every phase starts with draft PR and evidence-first reporting.
3. Umbrella tracks all phase links and final closure state.
