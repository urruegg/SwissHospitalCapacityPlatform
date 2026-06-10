# Sprint 06 Phase Issue Map and Dependency Model

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | N/A |

## Purpose

Provide the authoritative, validated issue decomposition and dependency model
for Sprint 06 execution. This map is the Phase 0 control artifact that makes the
sprint issue tree traceable, satisfying Phase 0 task 1 of
[`docs/sprints/sprint-06-minimal-data-onboarding-and-capacity-specialty.md`](../sprint-06-minimal-data-onboarding-and-capacity-specialty.md)
and aligning with the dependency model in
[`docs/runbooks/sprint-06-copilot-delegation-runbook.md`](../../runbooks/sprint-06-copilot-delegation-runbook.md).

## Baseline References

1. `docs/sprints/sprint-06-minimal-data-onboarding-and-capacity-specialty.md` (phase plan and Definition of Done)
2. `docs/runbooks/sprint-06-copilot-delegation-runbook.md` (issue set, labels, dependency model, kickoff templates)
3. `docs/reviews/2026-06-09-ama-cto-mentor-Review.md` (onboarding review baseline)
4. `docs/reviews/2026-06-09-ama-sd-review.md` (solution-design review baseline)

## Issue Tree

| Issue | Title | Role | Primary Scope | Labels |
| ----- | ----- | ----- | ----- | ----- |
| #43 | Sprint 6 - Minimal-Data Onboarding and Specialty-Driven Capacity Onboarding | Umbrella / orchestration anchor | All | `sprint-06` |
| #44 | Sprint 6 Phase 0 - Control and Traceability Bootstrap | Phase 0 (this issue) | Control + traceability bootstrap | `sprint-06`, `phase-0`, `evidence-required` |
| #45 | Sprint 6 Phase 1 - IaC Data Platform Kickoff and MVP Agents (OOA DCA BMCA) | Phase 1 | Doc deltas, IaC, synthesized data, MVP agents | `sprint-06`, `phase-1`, `synthetic-data`, `data-platform`, `iac`, `mvp-phase-1`, `evidence-required` |
| #46 | Sprint 6 Phase 2 - Onboarding Policy and Schema Enforcement | Phase 2 | Minimum-data policy + specialty schema gates | `sprint-06`, `phase-2`, `onboarding`, `specialty-metadata`, `sit-gate`, `evidence-required` |
| #47 | Sprint 6 Phase 3 - Provider SIT Evidence and Optional Agent Wave | Phase 3 | Provider SIT evidence + optional agents | `sprint-06`, `phase-3`, `optional-phase-3`, `sit-gate`, `evidence-required` |
| #48 | Sprint 6 Phase 4 - Hardening and Sprint Closure | Phase 4 | Hardening + closeout | `sprint-06`, `phase-4`, `prod-gate`, `evidence-required` |

> Issue numbers reflect the Sprint 06 issue set: umbrella `#43` is parent of
> `#44`, `#45`, `#46`, `#47`, `#48`. Phase 0 (`#44`) declares
> `Depends on: #43` and `Blocks: #45 #46 #47 #48`.

## Dependency Model

The dependency model is the same one declared in the delegation runbook,
restated here as the validated control baseline:

1. #43 (umbrella) is the parent of Phase 0..4.
2. Phase 0 (#44) blocks all phases (#45, #46, #47, #48).
3. Phase 1 (#45) depends on Phase 0 (#44) and blocks Phase 2 (#46) and Phase 3 (#47).
4. Phase 2 (#46) depends on Phase 0 (#44) and Phase 1 (#45).
5. Phase 3 (#47) depends on Phase 0 (#44) and Phase 1 (#45).
6. Phase 4 (#48) depends on Phase 2 (#46) and Phase 3 (#47).

### Dependency Edges (machine-checkable)

| From (blocked) | Depends on (blocker) | Reason |
| ----- | ----- | ----- |
| #44 Phase 0 | #43 Umbrella | Umbrella authorizes sprint start |
| #45 Phase 1 | #44 Phase 0 | Controls, register, and evidence checklist must exist first |
| #46 Phase 2 | #44 Phase 0, #45 Phase 1 | Policy/schema enforces documented onboarding baseline contracts |
| #47 Phase 3 | #44 Phase 0, #45 Phase 1 | Provider SIT evidence needs IaC + synthesized datasets from Phase 1 |
| #48 Phase 4 | #46 Phase 2, #47 Phase 3 | Hardening locks gates proven in Phase 2 and Phase 3 |

### Dependency Diagram

```text
              #43 Umbrella
                   |
              #44 Phase 0  (blocks all)
                   |
              #45 Phase 1
                 /     \
        #46 Phase 2   #47 Phase 3
                 \     /
              #48 Phase 4
```

## Critical Path

`#43 -> #44 -> #45 -> (#46 and #47) -> #48`

Phase 2 (#46) and Phase 3 (#47) can run in parallel once Phase 1 (#45) is merged,
but both must complete before Phase 4 (#48) starts.

## Gating Checklist (Phase 0 control)

| Gate question | Control answer |
| ----- | ----- |
| Are all phase issues created and linked to umbrella #43? | Yes — #44..#48 declare parent #43 |
| Is Phase 0 a hard predecessor for every later phase? | Yes — #44 blocks #45..#48 |
| Are MVP Phase 1 agents locked to OOA/DCA/BMCA? | Yes — optional DFA/IWA/DQSA/CSA/EAA deferred to Phase 3 (#47) |
| Is draft-PR-first enforced per phase? | Yes — see [`pr-evidence-checklist.md`](pr-evidence-checklist.md) "How to Use" |
| Are FR/NFR/CH traceability anchors explicit? | Yes — see [`requires-validation-register.md`](requires-validation-register.md) |
| Is the SIT-before-PROD gate order confirmed? | Yes — see [`gate-sequence.md`](gate-sequence.md) |

## Validation

1. No cyclic dependencies: edges form a directed acyclic graph (verified by the
   diagram and the dependency-edge table above).
2. Every phase issue has exactly one upstream gate to Phase 0, preserving the
   "Phase 0 blocks all phases" control.
3. Phase 4 has no direct edge to Phase 1, because its dependencies (#46, #47)
   already transitively require Phase 1.
4. Each issue carries the labels required by the delegation runbook so that gate
   and evidence automation can filter on `sit-gate`, `prod-gate`, and
   `evidence-required`.

## Change Control

Any change to the issue tree or dependency edges requires a bump to this
document's version per `.github/copilot-instructions.md` §9 and must remain
consistent with the delegation runbook dependency model.

