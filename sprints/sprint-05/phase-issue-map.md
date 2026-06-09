# Sprint 05 Phase Issue Map and Dependency Model

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | N/A |

## Purpose

Provide the authoritative, validated issue decomposition and dependency model
for Sprint 05 execution. This map is the Phase 0 control artifact that makes the
sprint issue tree traceable, satisfying Phase 0 task 1 of
[`sprints/sprint-05-caf-waf-mvp-sit-prod.md`](../sprint-05-caf-waf-mvp-sit-prod.md)
and aligning with the dependency model in
[`docs/runbooks/sprint-05-copilot-delegation-runbook.md`](../../docs/runbooks/sprint-05-copilot-delegation-runbook.md).

## Baseline References

1. `sprints/sprint-05-caf-waf-mvp-sit-prod.md` (phase plan and Definition of Done)
2. `docs/adr/0007-0011-hardening-delta-summary.md` (consolidated hardening delta)
3. `docs/runbooks/sprint-05-copilot-delegation-runbook.md` (issue set, labels, kickoff templates)

## Issue Tree

| Issue | Title | Role | Primary Work Package | Labels |
| ----- | ----- | ----- | ----- | ----- |
| #32 | Sprint 05 - CAF/WAF MVP SIT PROD Execution | Umbrella / orchestration anchor | All | `sprint-05` |
| #33 | Sprint 05 Phase 0 - Control and Traceability Bootstrap | Phase 0 (this issue) | Governance bootstrap | `sprint-05`, `phase-0`, `governance`, `evidence-required` |
| #34 | Sprint 05 Phase 1 - Documentation Baseline Upgrade | Phase 1 | WP-01, WP-02, WP-03 | `sprint-05`, `phase-1`, `compliance`, `adr-alignment` |
| #35 | Sprint 05 Phase 2 - Policy as Code and Governance Gates | Phase 2 | WP-04 | `sprint-05`, `phase-2`, `policy-as-code`, `security` |
| #36 | Sprint 05 Phase 3 - Reliability and DR Operationalization | Phase 3 | WP-05 | `sprint-05`, `phase-3`, `reliability` |
| #37 | Sprint 05 Phase 4 - Autonomous Agent Execution Hardening | Phase 4 | WP-06 | `sprint-05`, `phase-4`, `runtime-governance` |

> Issue numbers reflect the Sprint 05 issue set declared in issue #33:
> `Depends on: #32`, `Blocks: #34 #35 #36 #37`.

## Dependency Model

The dependency model is the same one declared in the delegation runbook,
restated here as the validated control baseline:

1. #32 (umbrella) is the parent of Phase 0..4.
2. Phase 0 (#33) blocks all phases (#34, #35, #36, #37).
3. Phase 1 (#34) depends on Phase 0 (#33) and blocks Phase 2 (#35) and Phase 3 (#36).
4. Phase 2 (#35) depends on Phase 0 (#33) and Phase 1 (#34).
5. Phase 3 (#36) depends on Phase 0 (#33) and Phase 1 (#34).
6. Phase 4 (#37) depends on Phase 2 (#35) and Phase 3 (#36).

### Dependency Edges (machine-checkable)

| From (blocked) | Depends on (blocker) | Reason |
| ----- | ----- | ----- |
| #33 Phase 0 | #32 Umbrella | Umbrella authorizes sprint start |
| #34 Phase 1 | #33 Phase 0 | Controls, templates, register must exist first |
| #35 Phase 2 | #33 Phase 0, #34 Phase 1 | Policy enforces documented baseline controls |
| #36 Phase 3 | #33 Phase 0, #34 Phase 1 | DR profile defined in docs before operationalization |
| #37 Phase 4 | #35 Phase 2, #36 Phase 3 | Agent hardening locks gates proven in Phase 2 and 3 |

### Dependency Diagram

```text
              #32 Umbrella
                   |
              #33 Phase 0  (blocks all)
                   |
              #34 Phase 1
                 /     \
        #35 Phase 2   #36 Phase 3
                 \     /
              #37 Phase 4
```

## Critical Path

`#32 -> #33 -> #34 -> (#35 and #36) -> #37`

Phase 2 (#35) and Phase 3 (#36) can run in parallel once Phase 1 (#34) is merged,
but both must complete before Phase 4 (#37) starts.

## Validation

1. No cyclic dependencies: edges form a directed acyclic graph (verified by the
   diagram and the dependency-edge table above).
2. Every phase issue has exactly one upstream gate to Phase 0, preserving the
   "Phase 0 blocks all phases" control.
3. Phase 4 has no direct edge to Phase 1, because its dependencies (#35, #36)
   already transitively require Phase 1.
4. Each issue carries the labels required by the delegation runbook so that gate
   and evidence automation can filter on `sit-gate`, `prod-gate`, and
   `evidence-required`.

## Change Control

Any change to the issue tree or dependency edges requires a bump to this
document's version per `.github/copilot-instructions.md` §9 and must remain
consistent with the delegation runbook dependency model.
