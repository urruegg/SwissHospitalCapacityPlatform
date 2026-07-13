# ADR-0026 — Evidence readiness measure ownership: separate `evidence.SemanticModel`

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-07-10 |
| **Deciders** | @urruegg |
| **Superseded by** | — |

> Sprint 14.1 mini-sprint T4 decision ADR. Resolves the open question raised in
> the Sprint 14.1 kickoff issue: where do the Showcase Evidence readiness
> measures live? Referenced by the Sprint 14 design spec
> [`2026-07-09-sprint-14-evidence-design.md`](../superpowers/specs/2026-07-09-sprint-14-evidence-design.md)
> §3–§6 and the plan [`2026-07-09-sprint-14-evidence-plan.md`](../superpowers/plans/2026-07-09-sprint-14-evidence-plan.md)
> Task 4.

## Context

Sprint 14 delivered the evidence data product's parsers, seed catalogs, and
medallion notebooks (T1–T3, PR #165). The readiness scoring rules
(`data-platform/notebooks/evidence/readiness_rules.py`, ADR-0021) materialise
`gold.fact_readiness_snapshot` (`bomId × track × region × status`) and
`gold.fact_readiness_summary` (`% Ready` per track). T4 must expose those Gold
tables through a Direct Lake semantic model so the presenter whiteboard (T5/T6)
can read readiness scores.

Two options were considered:

- **Option A** — add the readiness fact + measures to the existing
  `capacity-dashboard.SemanticModel` (readiness cards sit alongside the
  operational capacity/OR/BVA content).
- **Option B** — a **separate** `evidence.SemanticModel` under
  `data-platform/reports/evidence.SemanticModel/`, dedicated to the Showcase
  Evidence consumer.

## Decision

**Adopt Option B — a separate `evidence.SemanticModel`.** The readiness measures
own their own Direct Lake model over the `gold.fact_readiness_*` tables. The
`capacity-dashboard.SemanticModel` is left untouched.

## Rationale

| # | Criterion | Option A (shared) | Option B (separate) |
| --- | --- | --- | --- |
| 1 | Consumer boundary | Mixes two audiences (Ops teams vs. presenter/board) in one model. | Clean 1:1 with the Backstage Evidence tab — evidence data has exactly one consumer surface. |
| 2 | RLS story | Would inherit the capacity model's PHI/hospital RLS roles, which are irrelevant to synthetic non-PHI evidence data. | Evidence data is synthetic non-PHI (ADR-0016); RLS is trivial (see below). |
| 3 | Change blast-radius | Every evidence change re-triggers the capacity-dashboard contract gate (`verify-semantic-model.yml`, exact measure/relationship/role counts). | Evidence changes are isolated; no risk to the operational dashboard contract. |
| 4 | Deploy cadence | Coupled to capacity-dashboard publishes. | Independent `deploy` cadence, gated separately by `approved-to-apply`. |
| 5 | Model size / Direct Lake | Adds 2 unrelated Gold tables + 5 measures to an already 55-measure model. | Small, focused model — easier to reason about and optimise. |

Evidence + capacity are **different consumers** (operational Ops teams vs. the
presenter/board demo audience). A cleaner boundary and an isolated change
blast-radius outweigh the minor duplication of the Direct Lake connection
expression.

## RLS decision (T4 sub-decision)

Showcase Evidence data is **synthetic and non-PHI** (ADR-0006 scoping, ADR-0016
no-PHI-in-MVP). There are therefore **no row-level restrictions** required on the
evidence tables. To keep least-privilege posture explicit, the model ships a
single read-only role (`EvidenceReadOnly`, `modelPermission: read`, no row
filter) assignable to the presenter audience
(`HCC.Presenter`, `HCC.PlatformAdmin`, `HCC.OntologySteward`, `HCC.Auditor`,
`HCC.GuestReadOnly`). Row-scoped RLS is **deferred** — it can be added if a
future evidence source ever carries restricted data.

## Consequences

- New PBIP semantic model `data-platform/reports/evidence.SemanticModel/`
  (Direct Lake over `lh_ihzhhpf_sit`), tables `fact_readiness_snapshot` +
  `fact_readiness_summary`, measures `Readiness % (T-SHOW)`,
  `Readiness % (T-PROD)`, `GA-Parity Gap`, `BOM count`,
  `Blocked requirements count`.
- The presenter whiteboard (T5) and Backstage Evidence tab (T6) read from this
  model (or its committed demo dataset in dev/CI where no Fabric endpoint is
  wired).
- `verify-semantic-model.yml` remains scoped to `capacity-dashboard` only; the
  evidence model has its own lightweight structure check
  (`data-platform/reports/tests/test_evidence_semantic_model.py`).
- Semantic-model publish is `deploy`-ceiling and stays gated by
  `approved-to-apply` (AGENTS.md §4).

## Rollback path

If the separation proves to add more maintenance overhead than value, the two
`gold.fact_readiness_*` tables and their 5 measures can be folded into
`capacity-dashboard.SemanticModel` in a follow-up PR (bumping that model's
contract constants in `export_semantic_model_tmdl.ps1`). The Gold tables and the
`readiness_rules.py` scoring logic are unaffected either way.
