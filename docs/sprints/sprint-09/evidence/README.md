# Sprint 09 v2.0.0 Evidence Index

| Field | Value |
| ----- | ----- |
| Version | 1.0.0 |
| Date | 2026-07-03 |
| Author | Urs Rüegg |
| Status | Reviewed |
| Previous Version | n/a |

Companion evidence pack for Sprint 09 v2.0.0 sprint-close review. Each report validates one of the 5 test artefacts documented in [`docs/TEST.md`](../../../TEST.md) §Sprint 09 evidence.

## Reports

| # | Artefact | Report | Status |
| - | -------- | ------ | ------ |
| 1 | HCC utilization pattern conformance (MAPE < 15%) | [`hcc-conformance-report.md`](hcc-conformance-report.md) | **PASS** (MAPE 2.44%) |
| 2 | PHI regex sweep (ADR-0016 gate 1) | [`phi-sweep-report.md`](phi-sweep-report.md) | **PASS** (0 hits, 20 tests) |
| 3 | Ontology conformance CI STRICT | [`ontology-conformance.md`](ontology-conformance.md) | **PASS** (STRICT green on merge base) |
| 4 | 9 agent eval fixtures (design spec §5.5) | [`agent-eval-replay.md`](agent-eval-replay.md) | Pending manual replay (automation Sprint 10) |
| 5 | RLS PHI gate (ADR-0016 gate 4) | [`rls-phi-verification.md`](rls-phi-verification.md) | Pending portal round-trip on TMDL |

## Sprint close checklist status

Per [`docs/sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md`](../../sprint-09-master-data-simulation-and-capacity-dashboard.md) §7:

- [x] Full CI pipeline green on Sprint 09 v2.0.0 PRs
- [x] HCC pattern conformance test locally (MAPE 2.44% < 15%)
- [x] PHI regex sweep (0 hits over ≥ 10k events)
- [ ] 9 agent eval fixtures replay green (pending Sprint 10 harness)
- [ ] RLS PHI gate returns 0 rows for all 4 roles on PHI columns (pending portal TMDL export)
- [ ] Suspend Fabric F2 SIT via `Suspend-FabricCapacity.ps1 -Environment sit`

## Deferred to Sprint 10

- Automated agent eval harness (`evals/` workflow)
- Portal-authored TMDL semantic model export
- Portal-authored PBIP visuals
- Column-level PHI tagging in TMDL (currently row-level `_data_quality="phi"` proxy)
