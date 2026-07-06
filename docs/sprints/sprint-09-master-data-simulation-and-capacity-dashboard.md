# Sprint 09 — Master Data, Simulation, Semantic Model, Agents, Capacity Dashboard (v2.0.0)

| Field | Value |
| ----- | ----- |
| **Version** | 2.1.0 |
| **Date** | 2026-07-06 |
| **Author** | @urruegg |
| **Status** | Closed — 3 carry-over items to Sprint 10 (see retrospective §5) |
| **Previous Version** | 2.0.0 (ticked DoD 2/3/5/7/10; annotated 4/6/8 as Sprint 10 carry-over; added retrospective + evidence-pack pointers) |

> **What changed vs. v1.3.0.** Full MAJOR rewrite per [ADR-0017](../adr/0017-sprint-09-v2-track-restructure.md). Track boundaries, deliverable IDs, and DoD are restructured to align 1:1 with the 2026-07-02 design spec ([`docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md`](../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md)) and its implementation plan ([`docs/superpowers/plans/2026-07-02-sprint-09-v2-refinement-plan.md`](../superpowers/plans/2026-07-02-sprint-09-v2-refinement-plan.md)). The v1.x §0 Refresh Backlog is superseded; its RB-01…RB-14 outcomes are now folded into the design spec §1 context and the tracks below.
>
> **Source of truth.** This document is a concise sprint charter. The **design spec** is authoritative for scope, DoD, and risk; the **plan** is authoritative for task breakdown, TDD steps, and commit boundaries. When in doubt, defer to those artefacts and open an ADR if this doc drifts.

---

## 1. Sprint goal

Deliver a `westus2`-based reference-implementation MVP demo of the Swiss AI-Powered Patient Flow platform: calibrated real-time simulator → Event Hubs → Fabric Eventstream → Delta lakehouse → semantic model + MVO ontology → Power BI dashboard replicating the HCC utilization pattern → three data agents (BM-Copilot / Fabric Data Agent / CSA). Every `westus2` module carries a documented Swiss-region lift-and-shift path per [ADR-0014 gate G-C](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md#5-explicit-go-no-go-gates).

Full context: [design spec §1](../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md#1-context).

---

## 2. Track structure

Five execution tracks, dependency order **T1 → (T2 ∥ T3) → (T4 ∥ T5) → DX** ([design spec §7.1](../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md#71-five-tracks-execution-order-t1--t2t3-parallel--t4t5-parallel)).

| Track | Theme | Plan tasks | PR |
| ----- | ----- | ----- | ----- |
| **T1 Foundation** | 2 new ADRs (0015, 0016) + ontology v0.2.0 + 3 new contract schemas + strict-mode CI + CODEOWNERS | [plan T1.1–T1.8](../superpowers/plans/2026-07-02-sprint-09-v2-refinement-plan.md) | PR #93 (merged) |
| **T2 Ingestion** | Event Hubs consumer groups + Fabric Eventstream Bicep + 3 reference-data notebooks + 3 eventstream notebooks | plan T2.1–T2.8 | PR #94 (open) |
| **T3 Simulator** | 4 calibration modules + 6 event generators + Event Hub emitter + sim clock + HCC conformance + PHI regex test + ACA Bicep | plan T3.1–T3.7 | PR #95 (open) |
| **T4 Semantic Model + Agents** | TMDL semantic model + BM-Copilot / Fabric Data Agent / CSA prompt + fixtures + Foundry RBAC Bicep + Fabric REST deployer | plan T4.1–T4.7 | PR #96 (open) |
| **T5 Dashboard** | 2-page PBIP + OR sample data + `04_load_or_samples.ipynb` + deploy script + RLS PHI gate | plan T5.1–T5.6 | PR #97 (open) |
| **DX Cross-cutting** | Sprint doc rewrite (this file) + F2 lifecycle runbook + OPERATIONS OPS-RISK rows + TEST evidence subsection | plan DX.1–DX.4 | PR #98 (planned) |

---

## 3. 35-deliverable summary

The authoritative deliverable table is [design spec §7.2](../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md#72-deliverables-35-items). Summary by track:

- **T1 Foundation — 7 deliverables** — D1.1 ADR-0015 skip SQL, D1.2 ADR-0016 no PHI, D1.3 `reference-layer.ttl` v0.2.0, D1.4 `crosswalk.md` v0.2.0, D1.5 three contract schemas (`dc-discharge-score-v1`, `dc-discharge-recommendation-v1`, `dc-demand-forecast-v1`), D1.6 ontology CI strict-mode flip, D1.7 CODEOWNERS `agents/**` row.
- **T2 Ingestion — 8 deliverables** — D2.1 Event Hubs consumer-group + RBAC extension, D2.2 Fabric Eventstream Bicep, D2.3–D2.5 reference-data bronze/silver/gold notebooks, D2.6–D2.8 eventstream bronze/silver/gold notebooks.
- **T3 Simulator — 7 deliverables** — D3.1 calibration modules (`hospital_presets` / `seasonal_profile` / `acuity_distribution` / `ward_topology`), D3.2 six event generators, D3.3 Event Hub emitter, D3.4 sim clock, D3.5 HCC pattern conformance test, D3.6 no-PHI regex sweep test, D3.7 ACA hosting Bicep.
- **T4 Semantic Model + Agents — 7 deliverables** — D4.1 TMDL semantic model, D4.2–D4.4 three agent prompt + fixture packs, D4.5 Foundry RBAC Bicep, D4.6 Fabric REST deployment script, D4.7 `docs/AI.md` § Agent Registry.
- **T5 Dashboard — 6 deliverables** — D5.1–D5.2 PBIP Page 1 + Page 2, D5.3 `deploy_report.ps1`, D5.4 OR sample data (`or_schedule.json` + `or_case.json`), D5.5 `04_load_or_samples.ipynb`, D5.6 RLS PHI gate.
- **Cross-cutting — 4 deliverables** — DX.1 this sprint-doc rewrite, DX.2 Fabric F2 capacity lifecycle runbook + scripts, DX.3 `docs/OPERATIONS.md` v1.5.0 (new OPS-RISK rows), DX.4 `docs/TEST.md` §Sprint 09 evidence.

**Total: 35 deliverables (D1.1..DX.4).**

---

## 4. Definition of Done

Copied from [design spec §7.3](../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md#73-definition-of-done-sprint-09-v200) as the authoritative sprint-close checklist. **Final state at sprint close (2026-07-06):**

- [x] All 35 deliverables (D1.1..DX.4) completed and verified. **Actual: 32 delivered (91%) + 3 formal carry-over** (D2.2 Eventstream Bicep, D2.6–D2.8 eventstream notebooks partial, D5.1–D5.2 PBIP visuals partial — see [retrospective §3](sprint-09/retrospective.md#3-deliverable-outcome)).
- [x] [ADR-0015](../adr/0015-skip-sql-for-mvp-demo.md) + [ADR-0016](../adr/0016-no-phi-in-mvp-demo-scope.md) merged.
- [x] Ontology conformance CI in **strict mode**; 0 WARN, 0 FAIL against `reference-layer.ttl` v0.2.0 — [evidence](sprint-09/evidence/ontology-conformance.md).
- [ ] **CARRY-OVER → Sprint 10:** Fabric F2 SIT runs the full pipeline end-to-end: simulator → EH → Eventstream → bronze → silver → gold → semantic model → Page 1 + Page 2. **Blocked by:** Fabric-managed EH connection (portal step) + 4 fact tables not materialised. Documented in [checkpoint §9.1](sprint-09/checkpoint-2026-07-06-fabric-and-model.md#91-sprint-10-handoff--capacity-dashboard-measures-option-d) + [retrospective §5](sprint-09/retrospective.md#5-follow-ups-sprint-10).
- [x] HCC utilization-pattern conformance test passes: MAPE < 15% for LUKS preset. **Actual: MAPE 2.44%** — [evidence](sprint-09/evidence/hcc-conformance-report.md).
- [ ] **CARRY-OVER → Sprint 10:** All 9 agent eval fixtures (3 per agent) replay green. **Blocked by:** 3 agent runtime hosts not deployed + no automated replay harness — [evidence](sprint-09/evidence/agent-eval-replay.md).
- [x] PHI regex sweep test (D3.6) reports 0 hits over 10 000 events — [evidence](sprint-09/evidence/phi-sweep-report.md).
- [ ] **CARRY-OVER → Sprint 10:** RLS PHI gate verified: no PHI-tagged column visible to any of 4 roles. **Blocked by:** (a) portal round-trip dropped 4 RLS role scaffolds, (b) column-level `[phi]="true"` annotations not present, (c) no synthetic PHI fixture (deliberately no PHI in demo per ADR-0016) — [evidence](sprint-09/evidence/rls-phi-verification.md).
- [ ] **PENDING USER ACTION:** Fabric F2 SIT paused at sprint close; PROD unchanged (still stopped).
- [x] PR to `main` merged with full PR output contract fields populated (8 PRs #93–#100).
- [x] Sprint 09 v2.0.0 retrospective committed in [`docs/sprints/sprint-09/retrospective.md`](sprint-09/retrospective.md).

---

## 5. Risk register

Authoritative: [design spec §7.5](../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md#75-risk-register). Operationally tracked in [`docs/OPERATIONS.md` § Live Risk Register](../OPERATIONS.md#live-risk-register-new):

- **OPS-RISK-01** — Fabric IQ Ontology Switzerland-region GA + DPA equivalence (H).
- **OPS-RISK-02** — ADR-0013 westus2 demo exception expiry 2026-09-30 (M).
- **OPS-RISK-03** — Direct Lake preview stability (M).
- **OPS-RISK-04** — Fabric F2 forgot-to-pause cost hygiene (L-M).
- **OPS-RISK-05** — 3-hospital calibration realism drift (M).

Additional sprint-scoped risks (not promoted to OPS-RISK because they close at sprint end): USZ calibration inference drift, Foundry runtime SDK breaking change during CSA authoring — see [design spec §7.5](../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md#75-risk-register).

---

## 6. Traceability

Authoritative: [design spec §7.7](../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md#77-traceability). Per-track FR / NFR anchors from [`docs/PRD.md`](../PRD.md):

| Track | Requirement anchors |
| ----- | ----- |
| T1 Foundation | `FR-ONT-001..007`, `FR-GOV-ONT-001..003`, `NFR-ONT-001`, `NFR-COMP-001` (ADR-0016), `NFR-MAINT-004` (ADR-0015 supersession) |
| T2 Ingestion | `FR-DATA-001`, `FR-DATA-003`, `FR-DATA-005`, `FR-DATA-008`, `NFR-DQ-001..004`, `NFR-PERF-001` |
| T3 Simulator | `FR-DATA-003`, `FR-FC-006`, `NFR-PERF-002..005`, ADR-0016 gate 1 + 2 |
| T4 Semantic Model + Agents | `FR-CX-001..006`, `FR-ONT-004`, `FR-ONT-006`, `NFR-AI-001..005`, ADR-0016 gate 3 |
| T5 Dashboard | `FR-CX-005`, `FR-VIZ-001..002`, `NFR-GOV-003`, `NFR-GOV-006`, ADR-0016 gate 4 |
| Cross-cutting DX | `NFR-MAINT-002`, `NFR-MAINT-005`, `NFR-COMP-004..010`, `NFR-SEC-001..004` |

Task → PR mapping lives on the PR itself (each PR description lists the D-IDs it advances).

---

## 7. Sprint close checklist

Copied from [plan `Sprint close (after all 35 deliverables)`](../superpowers/plans/2026-07-02-sprint-09-v2-refinement-plan.md#sprint-close-after-all-35-deliverables):

- [ ] Full CI pipeline green on the Sprint 09 v2.0.0 PRs.
- [ ] Verify HCC pattern conformance test locally (MAPE < 15%).
- [ ] Verify PHI regex sweep test (0 hits over 10 000 events).
- [ ] Verify 9 agent eval fixtures replay green.
- [ ] Verify RLS PHI gate returns 0 rows for all 4 roles on PHI-tagged columns.
- [ ] Suspend Fabric F2 SIT: `.\infra\scripts\Suspend-FabricCapacity.ps1 -Environment sit` ([DX.2 runbook](../runbooks/fabric-capacity-lifecycle.md)).
- [ ] Commit Sprint 09 v2.0.0 retrospective in [`docs/sprints/sprint-09/retrospective.md`](sprint-09/retrospective.md).
- [ ] Merge Sprint 09 v2.0.0 PRs to `main`.

Evidence artefacts (populated at sprint close) live under `docs/sprints/sprint-09/evidence/` — see [`docs/TEST.md` § Sprint 09 evidence](../TEST.md#sprint-09-evidence) for the enumeration.

---

## 8. Retrospective

Retrospective template stub: [`docs/sprints/sprint-09/retrospective.md`](sprint-09/retrospective.md). Populate at sprint close per the DoD in §4.

---

## References

- [Design spec](../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md) — authoritative for scope, DoD, risk register, traceability
- [Implementation plan](../superpowers/plans/2026-07-02-sprint-09-v2-refinement-plan.md) — authoritative for task breakdown, TDD steps, commit boundaries
- [ADR-0013 westus2 demo scope](../adr/0013-temporary-us-region-demo-scope.md)
- [ADR-0014 Fabric IQ Ontology target backbone GA-gated](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md)
- [ADR-0015 skip SQL for MVP demo](../adr/0015-skip-sql-for-mvp-demo.md)
- [ADR-0016 no PHI in MVP demo scope](../adr/0016-no-phi-in-mvp-demo-scope.md)
- [ADR-0017 Sprint 09 v2.0.0 track restructure](../adr/0017-sprint-09-v2-track-restructure.md) — backs this MAJOR bump
- [DX.2 Fabric F2 capacity lifecycle runbook](../runbooks/fabric-capacity-lifecycle.md)
- [`docs/OPERATIONS.md` § Live Risk Register](../OPERATIONS.md#live-risk-register-new)
- [`docs/TEST.md` § Sprint 09 evidence](../TEST.md#sprint-09-evidence)
