# Sprint 10 — End-to-End Pipeline + Dashboard Completion

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-06 |
| **Author** | @urruegg |
| **Status** | Planned |
| **Previous Version** | n/a (initial sprint charter) |

> **Sprint theme.** Sprint 09 v2 shipped 80% fully-complete with 3 formal DoD carry-overs. Sprint 10 unblocks those 3 items (E2E pipeline, agent eval, RLS PHI gate) and completes the capacity-dashboard (visuals + Option D measure catch-up). Scope is derived from the 15-item [Sprint 09 retrospective §5](sprint-09/retrospective.md#5-follow-ups-sprint-10) backlog.
>
> **Charter shape.** This is a **scoped follow-up sprint** — a full design-spec + implementation-plan pair (Sprint 09 v2 pattern) is optional per track. Add design + plan for tracks where scope grows beyond the enumerated items; skip for tracks where the retrospective backlog is self-contained.

## Table of Contents

1. [Sprint goal](#1-sprint-goal)
2. [Source baseline](#2-source-baseline)
3. [Sprint scope](#3-sprint-scope)
4. [Track structure](#4-track-structure)
5. [Deliverables (mapped from retrospective §5)](#5-deliverables-mapped-from-retrospective-5)
6. [Definition of Done](#6-definition-of-done)
7. [Risk register](#7-risk-register)
8. [Traceability](#8-traceability)
9. [Sprint close checklist](#9-sprint-close-checklist)
10. [References](#10-references)

---

## 1. Sprint goal

Close the 3 open Sprint 09 v2 DoD items (E2E pipeline, 9 agent eval fixtures, RLS PHI gate) and land the remaining T5 dashboard scope (Option D measure catch-up + PBIP Page 1 + Page 2 visuals), so that the capacity-dashboard is demo-ready end-to-end for the AMA session sequence and the ADR-0013 westus2 demo-scope expiry milestone (2026-09-30).

Success shape:

- Simulator → Event Hubs → Fabric Eventstream → bronze → silver → gold → Direct Lake semantic model → Page 1 + Page 2 visuals runs green end-to-end on Fabric F2 SIT.
- All 13 spec §6.3 measures authored and rendering on the correct dashboard cards.
- 4 RLS roles verified in portal against a synthetic PHI fixture.
- 9 agent golden-task fixtures replay green via automated harness.

---

## 2. Source baseline

Read these in order before touching Sprint 10 code or docs:

1. [Sprint 09 retrospective](sprint-09/retrospective.md) — authoritative Sprint 10 backlog (§5) + risk-register outcomes (§6)
2. [Sprint 09 v2 sprint doc](sprint-09-master-data-simulation-and-capacity-dashboard.md) v2.1.0 — DoD carry-over annotations
3. [Sprint 09 v2 design spec](../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md) — measure/relationship contract source
4. [Sprint 09 v2 implementation plan](../superpowers/plans/2026-07-02-sprint-09-v2-refinement-plan.md) — task breakdown patterns
5. [`docs/sprints/sprint-09/checkpoint-2026-07-06-fabric-and-model.md`](sprint-09/checkpoint-2026-07-06-fabric-and-model.md) §9.1 — Option D catch-up plan for measures
6. [`docs/sprints/sprint-09/evidence/rls-phi-verification.md`](sprint-09/evidence/rls-phi-verification.md) v1.0.0 — 3 concrete RLS blockers
7. [`docs/sprints/sprint-09/evidence/agent-eval-replay.md`](sprint-09/evidence/agent-eval-replay.md) v1.0.0 — 2 concrete agent-eval blockers
8. [`data-platform/reports/capacity-dashboard.SemanticModel/README.md`](../../data-platform/reports/capacity-dashboard.SemanticModel/README.md) — measure inventory (5 authored, 8 deferred)
9. [ADR-0013](../adr/0013-temporary-us-region-demo-scope.md) — westus2 demo scope expiry 2026-09-30 (sets Sprint 10 close deadline pressure)
10. [ADR-0016](../adr/0016-no-phi-in-mvp-demo-scope.md) — no PHI ingest constraint (drives Blocker 3 of RLS gate: needs synthetic PHI fixture)
11. [ADR-0017](../adr/0017-sprint-09-v2-track-restructure.md) — Sprint 09 v2 5-track structure precedent

---

## 3. Sprint scope

### In scope

1. **Fabric Eventstream + Event Hubs wiring** (retrospective §5 item 1) — provision Eventstream Bicep + execute post-deploy portal step ([`configure-eventstream.ps1`](../../infra/modules/data-platform/fabric-eventstream/post-deploy/configure-eventstream.ps1)) against SIT.
2. **Eventstream bronze/silver/gold notebooks** (item 2) — port the reference-data pattern to the streaming path.
3. **4 missing fact tables** (item 3) — `fact_encounter`, `fact_bed_state`, `fact_bed_assignment`, `fact_forecast_output` in `lh_ihzhhpf_sit/gold/`.
4. **8 Option D measures** (item 4) — author on the new fact tables per [checkpoint §9.1 table](sprint-09/checkpoint-2026-07-06-fabric-and-model.md#91-sprint-10-handoff--capacity-dashboard-measures-option-d).
5. **OR loader schema extension** (item 5) — derive `isFirstCase`, `actualStart`, `plannedStart`, `cancellationLeadTimeHours`, `turnoverMinutes` on `or_case`; align `or_schedule.status` vocabulary to include `available`; retire the Sprint 09 `Idle-Slot Minutes` proxy in favour of the spec-exact filter.
6. **Re-author 4 RLS roles + column-level PHI tagging** (item 6) — Fabric web modeling → **Manage roles** → BedOps, ORPlanner, Analyst, SemanticOwner; add column-level `[phi]="true"` annotations on PHI-shaped columns.
7. **Synthetic PHI fixture** (item 7) — design + inject procedure into an **isolated test lakehouse** (NOT `lh_ihzhhpf_sit`), then exercise the RLS filter for each of 4 roles per [rls-phi-verification.md](sprint-09/evidence/rls-phi-verification.md#sprint-10-verification-procedure-post-blocker-resolution).
8. **Automated agent-eval harness** (item 8) — extend [`.github/workflows/eval-goldens.yml`](../../.github/workflows/eval-goldens.yml) to drive the 9 fixtures against deployed agents.
9. **Deploy 3 agent runtime hosts** (item 9) — BM-Copilot (Foundry-hosted), Fabric Data Agent, CSA (Foundry-hosted). Executes the already-shipped D4.5 Foundry Bicep + D4.6 Fabric REST deploy against SIT.
10. **PBIP Page 1 + Page 2 visual authoring** (item 10) — implement the layout READMEs against the 13 measures.
11. **Verifier extension** (item 11) — [`export_semantic_model_tmdl.ps1`](../../data-platform/scripts/export_semantic_model_tmdl.ps1) asserts measure count (13 target) + RLS role count (4 target).
12. **CI verifier workflow** (item 12) — `.github/workflows/verify-semantic-model.yml` runs `-VerifyOnly` on every PR touching `data-platform/reports/capacity-dashboard.SemanticModel/**`.

### Out of scope (explicit)

1. **PHI ingestion into `lh_ihzhhpf_sit`** — ADR-0016 unchanged; RLS testing uses an isolated test lakehouse with a synthetic fixture only.
2. **`switzerlandnorth` lift-and-shift** (retrospective §5 item 15) — carry-forward to a governance-scoped sprint after Fabric IQ Swiss GA + DPA equivalence is confirmed. Only the `-Region` parameter flip on deploy scripts is validated in Sprint 10.
3. **Frozen `MngEnvMCAP228255` tenant teardown** (retrospective §5 item 14) — carry-forward to a governance-scoped sprint; blocker is management-plane approval, not technical.
4. **Nightly HCC MAPE re-validation harness** (retrospective §5 item 13) — carry-forward; the sprint-09 blocking test (MAPE 2.44%) is sufficient for Sprint 10 demo scope.
5. **PROD deployment** — Sprint 10 targets SIT only; PROD replication uses the [checkpoint §3 replication checklist](sprint-09/checkpoint-2026-07-06-fabric-and-model.md#3-fabric-f2-prod-replication-checklist) in a subsequent sprint.

---

## 4. Track structure

Six tracks, dependency order **T1 → T2 → (T3 ∥ T4 ∥ T5) → T6**:

```mermaid
flowchart LR
    T1[T1 Eventstream + facts<br/>items 1-3]
    T2[T2 OR loader + measures<br/>items 4-5]
    T3[T3 Dashboard closure<br/>items 6, 7, 10]
    T4[T4 Agent runtime + eval<br/>items 8, 9]
    T5[T5 Tooling<br/>items 11, 12]
    T6[T6 Close-out<br/>evidence + retro]

    T1 --> T2
    T2 --> T3
    T1 --> T4
    T1 --> T5
    T3 --> T6
    T4 --> T6
    T5 --> T6
```

| Track | Items (retrospective §5) | Owner | Notes |
| ----- | ------------------------ | ----- | ----- |
| **T1 Eventstream + facts** | 1, 2, 3 | @urruegg | Unblocks all Page-1 measures. Fabric-managed EH connection is a portal step — cost budget for F2 SIT stays on. |
| **T2 OR loader + measures** | 4, 5 | @urruegg | Unblocks all 8 Option D measures + retires Sprint 09 `Idle-Slot Minutes` proxy. Depends on T1 for `fact_*` context. |
| **T3 Dashboard closure** | 6, 7, 10 | @urruegg | RLS re-authoring + synthetic PHI fixture + PBIP visuals. Independent from T1 for RLS; visuals depend on T2 measures. |
| **T4 Agent runtime + eval** | 8, 9 | @urruegg | Deploy 3 agents + build automation harness. Independent from T1/T2/T3; may run in parallel. Cost budget for Foundry deployments. |
| **T5 Tooling** | 11, 12 | @urruegg | Verifier extension + CI workflow. Depends on T3 for role count assertion + T2 for measure count. |
| **T6 Close-out** | (evidence + retrospective) | @urruegg | Update Sprint 09 v2 evidence reports (rls-phi-verification.md, agent-eval-replay.md) from "carry-over" → "PASS"; author Sprint 10 retrospective. |

---

## 5. Deliverables (mapped from retrospective §5)

Total: 12 deliverables + evidence/retro close-out. Full retrospective §5 backlog has 15 items; items 13, 14, 15 are explicitly out of scope (see §3).

| Track | # | Deliverable | Retrospective item | Design/plan needed? |
| ----- | - | ----------- | ------------------ | ------------------- |
| T1 | S10.1 | Fabric Eventstream Bicep + post-deploy portal wiring | 1 | Design: brief; plan: yes |
| T1 | S10.2 | Eventstream bronze/silver/gold notebooks | 2 | Design: brief; plan: yes |
| T1 | S10.3 | 4 fact tables landed in `lh_ihzhhpf_sit/gold/` | 3 | Design: brief; plan: yes |
| T2 | S10.4 | 8 Option D measures authored on new fact tables | 4 | Design: n/a (spec §6.3 authoritative); plan: brief |
| T2 | S10.5 | OR loader schema extension + status vocabulary alignment | 5 | Design: brief; plan: brief |
| T3 | S10.6 | 4 RLS roles re-authored in Fabric web modeling + column-level `[phi]` annotations | 6 | Design: brief (fixture-injection contract); plan: brief |
| T3 | S10.7 | Synthetic PHI fixture design + injection procedure | 7 | Design: yes; plan: yes |
| T3 | S10.8 | PBIP Page 1 + Page 2 visual authoring | 10 | Design: reference layout READMEs; plan: brief |
| T4 | S10.9 | Automated agent-eval harness under `evals/` + workflow | 8 | Design: brief; plan: yes |
| T4 | S10.10 | 3 agent runtime hosts deployed to SIT | 9 | Design: n/a (D4.5/D4.6 authoritative); plan: brief |
| T5 | S10.11 | `export_semantic_model_tmdl.ps1` verifier extension (measure + role count) | 11 | Design: n/a; plan: brief |
| T5 | S10.12 | `.github/workflows/verify-semantic-model.yml` CI merge gate | 12 | Design: n/a; plan: brief |

**Total: 12 deliverables (S10.1..S10.12).** Compare to Sprint 09 v2 (35 deliverables) — this is a scoped follow-up sprint by design.

---

## 6. Definition of Done

Sprint 10 closes when all of the following are true:

- [ ] All 12 deliverables (S10.1..S10.12) completed and evidenced.
- [ ] Sprint 09 v2 DoD item 4 (E2E pipeline) verified: simulator → EH → Eventstream → bronze → silver → gold → semantic model → Page 1 + Page 2 renders real values.
- [ ] Sprint 09 v2 DoD item 6 (agent eval) verified: 9 golden-task fixtures replay green via automated harness (no manual runs).
- [ ] Sprint 09 v2 DoD item 8 (RLS PHI gate) verified: 4 roles return 0 rows on PHI-tagged columns against synthetic PHI fixture; verification log populated in [`rls-phi-verification.md`](sprint-09/evidence/rls-phi-verification.md).
- [ ] All 13 spec §6.3 measures rendering on the correct Page 1 / Page 2 visuals with no `BLANK`s (except intentional forecast-window truncation).
- [ ] `export_semantic_model_tmdl.ps1 -VerifyOnly` asserts `Total: 14, Active: 12, Inactive: 2, Measures: 13, Roles: 4` and passes on every PR touching `capacity-dashboard.SemanticModel/**`.
- [ ] Sprint 10 evidence pack under `docs/sprints/sprint-10/evidence/` mirrors Sprint 09 pattern (one report per DoD gate).
- [ ] Sprint 10 retrospective committed in [`docs/sprints/sprint-10/retrospective.md`](sprint-10/retrospective.md) *(create at sprint kick-off)*.
- [ ] Fabric F2 SIT operational-cost hygiene reviewed at sprint close: user decision on suspend vs keep-active for AMA demo window.

---

## 7. Risk register

Inherits Sprint 09 v2 OPS-RISK-01..05 (see [`docs/OPERATIONS.md`](../OPERATIONS.md)). Sprint-10-scoped additions:

- **OPS-RISK-06** *(new)* — **Fabric web-modeling round-trip drops RLS role scaffolds** (Sprint 09 finding). Mitigation: Sprint 10 S10.6 re-authors roles in the portal; verifier extension S10.11 asserts role count in CI so future round-trips can't silently drop them again.
- **OPS-RISK-07** *(new)* — **Foundry-hosted agent deployment cost overrun**. Deploying 3 agents (BM-Copilot + CSA + FDA) may exceed Sprint 09 v2 F2 SIT cost baseline. Mitigation: rehearse in a scratch deployment first, budget explicit cap in track kick-off.
- **ADR-0013 westus2 exception expiry (2026-09-30)** — 3 months runway at Sprint 10 start. If Sprint 10 slips beyond 2026-09, the westus2 demo scope needs an ADR-0013 extension decision.

---

## 8. Traceability

Per-track FR/NFR anchors from [`docs/PRD.md`](../PRD.md):

| Track | Requirement anchors |
| ----- | ------------------- |
| T1 Eventstream + facts | `FR-DATA-001`, `FR-DATA-003`, `FR-DATA-005`, `FR-DATA-008`, `NFR-DQ-001..004`, `NFR-PERF-001` |
| T2 OR loader + measures | `FR-DATA-005`, `FR-DATA-008`, `FR-CX-005`, `NFR-DQ-001..004` |
| T3 Dashboard closure | `FR-CX-005`, `FR-GOV-001`, `FR-GOV-002`, ADR-0016 gate 4 |
| T4 Agent runtime + eval | `FR-CX-001..006`, `FR-ONT-004`, `FR-ONT-006`, `NFR-AI-001..005`, ADR-0016 gate 3 |
| T5 Tooling | `FR-GOV-001`, `FR-GOV-004`, `NFR-MAINT-001..005` |
| T6 Close-out | `FR-GOV-004`, `NFR-MAINT-002` |

**Design-spec drift carry-forward from Sprint 09:** the Sprint 09 v2 design spec §7.7 references non-existent PRD IDs (`FR-VIZ-001..002`, `NFR-GOV-003`, `NFR-GOV-006`). Sprint 10 either adds these to PRD.md §7 or fixes the design-spec references. Add to sprint-open issue as a scope-clarification task.

---

## 9. Sprint close checklist

- [ ] Full CI pipeline green on all Sprint 10 PRs (markdown lint, link check, Bicep build, actionlint, semantic-model verifier from S10.12).
- [ ] End-to-end demo dry-run: launch simulator → observe live update on Page 1 + Page 2 within Direct Lake refresh window.
- [ ] All 9 agent eval fixtures replay green via automated workflow.
- [ ] 4 RLS roles verified against synthetic PHI fixture; 0 rows returned per role; verification log populated.
- [ ] Sprint 09 v2 evidence pack updated: [`rls-phi-verification.md`](sprint-09/evidence/rls-phi-verification.md) + [`agent-eval-replay.md`](sprint-09/evidence/agent-eval-replay.md) transition Status from "Carry-over → Sprint 10" to "PASS".
- [ ] Sprint 09 v2 sprint-doc DoD items 4, 6, 8 flipped from "CARRY-OVER" to "[x]".
- [ ] Sprint 10 retrospective committed under [`docs/sprints/sprint-10/retrospective.md`](sprint-10/retrospective.md).
- [ ] Sprint 10 PR merged to `main` with full PR output contract fields populated.

---

## 10. References

- [Sprint 09 retrospective §5 (Sprint 10 backlog)](sprint-09/retrospective.md#5-follow-ups-sprint-10) — authoritative scope source
- [Sprint 09 v2 sprint doc](sprint-09-master-data-simulation-and-capacity-dashboard.md) — DoD carry-over annotations
- [Sprint 09 v2 design spec](../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md) §6.3 (measures) + §6.5 (RLS access model)
- [Sprint 09 v2 implementation plan](../superpowers/plans/2026-07-02-sprint-09-v2-refinement-plan.md) — Sprint 09 pattern for track/task structure
- [`docs/sprints/sprint-09/checkpoint-2026-07-06-fabric-and-model.md`](sprint-09/checkpoint-2026-07-06-fabric-and-model.md) §9.1 — Option D unblock plan
- [`docs/sprints/sprint-09/evidence/rls-phi-verification.md`](sprint-09/evidence/rls-phi-verification.md) — 3 concrete RLS blockers
- [`docs/sprints/sprint-09/evidence/agent-eval-replay.md`](sprint-09/evidence/agent-eval-replay.md) — 2 concrete agent-eval blockers
- [`data-platform/reports/capacity-dashboard.SemanticModel/README.md`](../../data-platform/reports/capacity-dashboard.SemanticModel/README.md) — measure inventory
- [`data-platform/scripts/export_semantic_model_tmdl.ps1`](../../data-platform/scripts/export_semantic_model_tmdl.ps1) — TMDL round-trip + contract verifier
- [ADR-0013](../adr/0013-temporary-us-region-demo-scope.md) — westus2 demo expiry 2026-09-30
- [ADR-0016](../adr/0016-no-phi-in-mvp-demo-scope.md) — no PHI ingest → drives synthetic-fixture design
- [ADR-0017](../adr/0017-sprint-09-v2-track-restructure.md) — track/deliverable pattern precedent
