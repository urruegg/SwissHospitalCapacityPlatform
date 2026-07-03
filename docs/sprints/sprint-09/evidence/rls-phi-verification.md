# RLS PHI Gate Verification — Sprint 09 v2.0.0 Evidence

| Field | Value |
| ----- | ----- |
| Version | 0.1.0 |
| Date | 2026-07-03 |
| Author | Urs Rüegg |
| Status | Pending portal round-trip |
| Previous Version | n/a |

## Purpose

ADR-0016 **gate 4** — the Direct Lake semantic model must return **zero rows** for any PHI-tagged column when queried under any of the 4 defined RLS roles (BedOps, ORPlanner, Analyst, SemanticOwner).

## Status

**Pending portal round-trip** — the TMDL semantic model is a skeleton (T4.1) awaiting portal authoring per [`data-platform/reports/capacity-dashboard.SemanticModel/README.md`](../../../../data-platform/reports/capacity-dashboard.SemanticModel/README.md). RLS roles are pre-authored in [`data-platform/reports/capacity-dashboard.SemanticModel/definition/model.tmdl`](../../../../data-platform/reports/capacity-dashboard.SemanticModel/definition/model.tmdl) and will be carried through the portal export.

## Roles authored

| Role | Purpose limitation | Table filter |
| ---- | ------------------ | ------------ |
| `BedOps` | Bed operations — no PHI exposure per ADR-0016 gate 4 | `IF([_data_quality]="phi", FALSE, TRUE)` on `encounter`, `fact_encounter` |
| `ORPlanner` | OR planning — no PHI exposure per ADR-0016 gate 4 | `IF([_data_quality]="phi", FALSE, TRUE)` on `or_case`, `or_schedule`, `encounter` |
| `Analyst` | Broad analytics — no PHI exposure per ADR-0016 gate 4 | `IF([_data_quality]="phi", FALSE, TRUE)` on all `fact_*` + `encounter` tables |
| `SemanticOwner` | Semantic model steward — no PHI exposure per ADR-0016 gate 4 | `IF([_data_quality]="phi", FALSE, TRUE)` on `encounter` |

## Design note

The row-level `_data_quality="phi"` filter is a **proxy** placeholder. The portal-authored TMDL export must additionally add column-level PHI tagging (annotation `[phi]="true"`) and adjust the role filters accordingly. See the "Manual step for portal-authored model" comment block at the bottom of [`model.tmdl`](../../../../data-platform/reports/capacity-dashboard.SemanticModel/definition/model.tmdl).

## Manual verification procedure (post-portal round-trip)

For each role:

1. In Power BI Desktop → **Manage roles** → select role
2. Use **View as role** on a PHI-tagged column (once portal author adds `[phi]="true"` annotations)
3. Confirm 0 rows returned
4. Record the DAX query used, the row count, and the timestamp in the log below

## Verification log

| Date | Role | PHI column tested | Query | Rows returned | Reviewer | Result |
| ---- | ---- | ----------------- | ----- | ------------: | -------- | ------ |
| _pending portal auth_ | BedOps | (tbd) | | | | |
| _pending portal auth_ | ORPlanner | (tbd) | | | | |
| _pending portal auth_ | Analyst | (tbd) | | | | |
| _pending portal auth_ | SemanticOwner | (tbd) | | | | |

## Fixture inputs

Test data currently in gold layer has `_data_quality ∈ {explicit, inferred, missing}`. **No `phi`-tagged rows exist yet** — the demo scope explicitly avoids ingesting PHI-shaped data. The verification test therefore also requires a **synthetic PHI fixture row** to be injected into a test lakehouse before the RLS filter can be exercised end-to-end. This is deferred to the Sprint 10 test harness.

## References

- ADR-0016 gate 4 — [`docs/adr/0016-no-phi-in-mvp-demo-scope.md`](../../../adr/0016-no-phi-in-mvp-demo-scope.md)
- TMDL skeleton README — [`data-platform/reports/capacity-dashboard.SemanticModel/README.md`](../../../../data-platform/reports/capacity-dashboard.SemanticModel/README.md)
- Design spec §6.5 — [`docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md`](../../../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md)
- `docs/TEST.md` §Sprint 09 evidence — [`docs/TEST.md`](../../../TEST.md)
