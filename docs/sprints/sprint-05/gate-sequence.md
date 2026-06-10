# Sprint 05 SIT and PROD Gate Sequence

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | N/A |

## Purpose

Confirm the SIT then PROD release-gate sequence for all remaining Sprint 05
phases. This is the Phase 0 control artifact for Phase 0 task 4 of
[`docs/sprints/sprint-05-caf-waf-mvp-sit-prod.md`](../sprint-05-caf-waf-mvp-sit-prod.md),
consolidating the gate definitions in each phase and the enforcement gate model
of [`docs/adr/0007-0011-hardening-delta-summary.md`](../../adr/0007-0011-hardening-delta-summary.md).

## Canonical Gate Order

Every phase that promotes follows the same ordered gate chain. A later gate may
not pass until every earlier gate for the same change has passed.

```text
CI gate  ->  SIT gate  ->  approval  ->  PROD gate  ->  (Runtime gate at execution)
```

1. **CI gate** — runtime matrix and policy checks execute for affected scope;
   evidence artifacts generated and attached to pipeline outputs.
2. **SIT gate** — boundary contracts, DR evidence, and policy evidence validated;
   unresolved high-severity compliance/reliability blockers stop progression.
3. **Approval** — required owner roles sign off (ARCH / SEC / OPS / LEGAL as
   applicable); `approved-to-apply` recorded for any deploy/delete action.
4. **PROD gate** — all SIT evidence plus owner approvals and residual-risk
   statement; expired exceptions block promotion.
5. **Runtime gate** — side-effecting operations enforce boundary contracts and
   HITL evidence at execution time.

## Per-Phase Gate Sequence

### Phase 0 — Control and Traceability Bootstrap (#33)

| Gate | Entry criteria | Exit evidence |
| ----- | ----- | ----- |
| SIT | All phase issues created and linked; evidence template committed | Issue tree traceable; control artifacts in `docs/sprints/sprint-05/`; markdown lint + link check pass |
| PROD | SIT passed | Human review confirms sprint governance controls are complete |

### Phase 1 — Documentation Baseline Upgrade (#34)

| Gate | Entry criteria | Exit evidence |
| ----- | ----- | ----- |
| SIT | Draft PR with all baseline doc changes | Markdown lint and link checks pass; traceability matrix updated for changed requirements and controls |
| PROD | SIT passed; approvals collected | Documentation PR merged to main; version headers bumped for every changed document |

### Phase 2 — Policy as Code and Governance Gates (#35)

| Gate | Entry criteria | Exit evidence |
| ----- | ----- | ----- |
| SIT | CI checks enforce policy baseline on SIT validation path | Evidence artifacts generated for at least one SIT validation run; zero critical policy failures |
| PROD | SIT passed; legal/compliance sign-off | Policy checks required on production promotion path; human-approved sign-off on legal and compliance controls |

### Phase 3 — Reliability and DR Operationalization (#36)

| Gate | Entry criteria | Exit evidence |
| ----- | ----- | ----- |
| SIT | At least one SIT DR rehearsal or tabletop run completed and documented | Restore/failover assumptions validated or marked with bounded risk acceptance; restore proof fresh (<= 90 days) |
| PROD | SIT passed; business acceptance of residual risk | PROD readiness statement includes RTO/RPO commitments and unresolved risk register; documented residual-risk acceptance |

### Phase 4 — Autonomous Agent Execution Hardening (#37)

| Gate | Entry criteria | Exit evidence |
| ----- | ----- | ----- |
| SIT | Golden-task fixtures pass for impacted agents | Agent output contract fields validated on sprint PRs; deny-by-default verified for missing HITL evidence |
| PROD | SIT passed | Governance reviewers confirm autonomous execution controls are sufficient for subsequent sprints |

## Promotion Blockers (all phases)

A PROD gate must read `fail` or `pending` whenever any of the following holds:

1. The phase SIT gate has not passed.
2. A high-severity item in
   [`requires-validation-register.md`](requires-validation-register.md) targeting
   this phase remains `open` or `in-validation`.
3. Any governance exception applicable to the change is expired
   (max 90-day validity for critical exceptions).
4. Required owner approvals are missing for a deploy/delete-ceiling action.

## Sequencing Across Phases

Gate sequencing across phases follows the dependency model in
[`phase-issue-map.md`](phase-issue-map.md):

1. Phase 0 PROD gate must pass before any Phase 1..4 SIT gate is entered.
2. Phase 1 PROD gate must pass before Phase 2 and Phase 3 SIT gates are entered.
3. Phase 2 and Phase 3 PROD gates must both pass before the Phase 4 SIT gate is
   entered.

## Change Control

Any change to the gate sequence bumps this document's version per
`.github/copilot-instructions.md` §9 and must stay consistent with the phase
gates in the sprint file and the enforcement gate model in the hardening delta
summary.

