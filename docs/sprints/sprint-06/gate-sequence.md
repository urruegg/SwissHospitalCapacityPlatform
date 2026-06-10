# Sprint 06 SIT and PROD Gate Sequence

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | 1.0.0 (initial Sprint 6 gate sequence) |

## Purpose

Confirm the SIT then PROD release-gate sequence for all Sprint 06 phases. This is
the Phase 0 gating checklist for
[`docs/sprints/sprint-06-minimal-data-onboarding-and-capacity-specialty.md`](../sprint-06-minimal-data-onboarding-and-capacity-specialty.md),
consolidating the SIT-before-PROD gate model used across the platform and the
phase plan of that sprint file.

## Canonical Gate Order

Every phase that promotes follows the same ordered gate chain. A later gate may
not pass until every earlier gate for the same change has passed.

```text
CI gate  ->  SIT gate  ->  approval  ->  PROD gate  ->  (Runtime gate at execution)
```

1. **CI gate** — markdown/link checks and (Phase 1+) synthesized-data contract and
   schema checks execute for affected scope; evidence artifacts generated.
2. **SIT gate** — onboarding contracts, specialty-metadata schemas, and synthesized
   datasets validated; unresolved high-severity onboarding blockers stop progression
   for the affected phase's SIT evidence.
3. **Approval** — required owner roles sign off (ARCH / SEC / OPS / LEGAL as
   applicable); `approved-to-apply` recorded for any deploy/delete action.
4. **PROD gate** — all SIT evidence plus owner approvals and residual-risk
   statement; expired exceptions block promotion.
5. **Runtime gate** — side-effecting onboarding operations enforce minimum-data and
   tenant-boundary contracts at execution time.

## Per-Phase Gate Sequence

### Phase 0 — Control and Traceability Bootstrap (#44)

| Gate | Entry criteria | Exit evidence |
| ----- | ----- | ----- |
| SIT | All phase issues created and linked; control artifacts committed | Issue tree traceable; artifacts in `docs/sprints/sprint-06/`; markdown lint + link check pass |
| PROD | SIT passed | Human review confirms sprint governance controls are complete |

### Phase 1 — IaC Data Platform Kickoff and MVP Agents (#45)

| Gate | Entry criteria | Exit evidence |
| ----- | ----- | ----- |
| SIT | Draft PR with onboarding contract deltas, IaC modules, and synthesized datasets | Markdown/link checks pass; synthesized dataset contract/schema validation passes; FR/NFR/CH traceability updated; MVP scope locked to OOA/DCA/BMCA |
| PROD | SIT passed; approvals collected | Doc + IaC PR merged; version headers bumped for every changed document |

### Phase 2 — Onboarding Policy and Schema Enforcement (#46)

| Gate | Entry criteria | Exit evidence |
| ----- | ----- | ----- |
| SIT | CI enforces onboarding minimum-data, specialty-schema, and tenant-boundary checks on SIT path | Evidence artifacts generated for at least one SIT run; zero critical onboarding policy failures |
| PROD | SIT passed; legal/compliance sign-off | Policy checks required on production promotion path; re-identification (`RV-06-04`) control accepted |

### Phase 3 — Provider SIT Evidence and Optional Agent Wave (#47)

| Gate | Entry criteria | Exit evidence |
| ----- | ----- | ----- |
| SIT | Synthesized Hirslanden and Zollikerberg specialty-capacity datasets validated in SIT | Provider onboarding contract/schema evidence captured; degraded-mode (`RV-06-05`) assumptions validated or bounded-risk accepted |
| PROD | SIT passed; business acceptance of residual risk | PROD readiness statement includes provider assumptions and residual-risk register; optional agent wave decision recorded |

### Phase 4 — Hardening and Sprint Closure (#48)

| Gate | Entry criteria | Exit evidence |
| ----- | ----- | ----- |
| SIT | Deterministic-classification (`RV-06-02`) coverage and Sprint 6 onboarding control-path checks are consolidated | Classification coverage validated; closeout evidence and control-path checks linked |
| PROD | SIT passed | Governance reviewers confirm Sprint 06 closeout and next-increment recommendation |

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

1. Phase 0 SIT gate must pass before any Phase 1..4 SIT evidence is entered.
2. Phase 1 SIT gate must pass before Phase 2 and Phase 3 SIT evidence is entered.
3. Phase 2 and Phase 3 SIT evidence must both pass before the Phase 4 closeout
   SIT evidence is entered.
4. A later phase may collect SIT evidence while an earlier phase's PROD gate is
   still pending, but no later phase may claim **PROD pass** or trigger
   promotion until the prerequisite phases' PROD blockers are cleared.

## Change Control

Any change to the gate sequence bumps this document's version per
`.github/copilot-instructions.md` §9 and must stay consistent with the phase
plan in the sprint file.
