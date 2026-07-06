# Sprint 09 v2.0.0 Evidence Index

| Field | Value |
| ----- | ----- |
| Version | 1.1.0 |
| Date | 2026-07-06 |
| Author | Urs Rüegg |
| Status | Reviewed — Sprint 09 closed with 3 formal carry-over items |
| Previous Version | 1.0.0 (initial evidence pack; RLS + agent-eval marked pending) |

Companion evidence pack for Sprint 09 v2.0.0 sprint-close review. Each report validates one of the 5 test artefacts documented in [`docs/TEST.md`](../../../TEST.md) §Sprint 09 evidence.

## Reports

| # | Artefact | Report | Status |
| - | -------- | ------ | ------ |
| 1 | HCC utilization pattern conformance (MAPE < 15%) | [`hcc-conformance-report.md`](hcc-conformance-report.md) | **PASS** (MAPE 2.44%) |
| 2 | PHI regex sweep (ADR-0016 gate 1) | [`phi-sweep-report.md`](phi-sweep-report.md) | **PASS** (0 hits, 20 tests) |
| 3 | Ontology conformance CI STRICT | [`ontology-conformance.md`](ontology-conformance.md) | **PASS** (STRICT green on merge base) |
| 4 | 9 agent eval fixtures (design spec §5.5) | [`agent-eval-replay.md`](agent-eval-replay.md) | **CARRY-OVER → Sprint 10** (agent runtimes not deployed + automation not built) |
| 5 | RLS PHI gate (ADR-0016 gate 4) | [`rls-phi-verification.md`](rls-phi-verification.md) | **CARRY-OVER → Sprint 10** (round-trip lost roles + column-level tagging + no PHI fixture) |
| 6 | Semantic model relationship contract (2026-07-06 session) | verified by [`export_semantic_model_tmdl.ps1`](../../../../data-platform/scripts/export_semantic_model_tmdl.ps1) | **PASS** (14 total, 12 Active, 2 Inactive Option B) |

## Sprint close checklist status

Per [`docs/sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md`](../../sprint-09-master-data-simulation-and-capacity-dashboard.md) §7:

- [x] Full CI pipeline green on Sprint 09 v2.0.0 PRs
- [x] HCC pattern conformance test locally (MAPE 2.44% < 15%)
- [x] PHI regex sweep (0 hits over ≥ 10k events)
- [ ] **CARRY-OVER → Sprint 10:** 9 agent eval fixtures replay green (agent runtimes not deployed + automation harness not built — see [`agent-eval-replay.md`](agent-eval-replay.md))
- [ ] **CARRY-OVER → Sprint 10:** RLS PHI gate returns 0 rows for all 4 roles on PHI columns (portal round-trip dropped roles + column-level tagging + no PHI fixture by design per ADR-0016 — see [`rls-phi-verification.md`](rls-phi-verification.md))
- [ ] **Pending user action:** Suspend Fabric F2 SIT via `Suspend-FabricCapacity.ps1 -Environment sit`

## Carry-over to Sprint 10

Full backlog inherited from Sprint 09 (15 items) is in the [Sprint 09 retrospective §5](../retrospective.md#5-follow-ups-sprint-10). Highlights:

- Automated agent-eval harness (`evals/` workflow) → unblocks evidence report 4.
- Portal re-authoring of 4 RLS roles + column-level PHI tagging + synthetic PHI fixture → unblocks evidence report 5.
- 4 missing fact tables (`fact_encounter`, `fact_bed_state`, `fact_bed_assignment`, `fact_forecast_output`) via Fabric Eventstream + simulator wiring → unblocks 5 of the 8 Option D catch-up measures.
- Extend silver→gold OR loader with `isFirstCase`, `actualStart`, `plannedStart`, `cancellationLeadTimeHours`, `turnoverMinutes`; align `or_schedule.status` vocabulary → unblocks remaining 3 Option D catch-up measures.
- Portal-authored PBIP visuals for Page 1 + Page 2 per layout READMEs.
