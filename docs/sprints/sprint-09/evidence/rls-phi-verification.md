# RLS PHI Gate Verification — Sprint 09 v2.0.0 Evidence

| Field | Value |
| ----- | ----- |
| Version | 1.0.0 |
| Date | 2026-07-06 |
| Author | Urs Rüegg |
| Status | **Carry-over → Sprint 10** — gate cannot be exercised in Sprint 09 scope |
| Previous Version | 0.1.0 (pending portal round-trip) |

## Purpose

ADR-0016 **gate 4** — the Direct Lake semantic model must return **zero rows** for any PHI-tagged column when queried under any of the 4 defined RLS roles (BedOps, ORPlanner, Analyst, SemanticOwner).

## Result

> **CARRY-OVER to Sprint 10** — the gate cannot be verified in Sprint 09 v2.0.0 scope. Three independent blockers exist; the design of Sprint 09 v2 (no PHI ingestion, portal-first TMDL) makes each unresolvable in-sprint. All three are Sprint 10 scope. Sprint 09 ships a **row-level `_data_quality="phi"` proxy scaffold** as the T5.6 deliverable; the scaffold is authoritative pattern documentation but cannot be executed against real data.

### Blocker 1 — 4 RLS roles lost during Fabric web-modeling round-trip

The T5.6 skeleton TMDL at [`data-platform/reports/capacity-dashboard.SemanticModel/definition/model.tmdl`](../../../../data-platform/reports/capacity-dashboard.SemanticModel/definition/model.tmdl) originally carried 4 pre-authored `role` blocks (BedOps, ORPlanner, Analyst, SemanticOwner). The 2026-07-06 session authored the model via the **Fabric web modeling editor** (portal-first), then round-tripped TMDL via [`export_semantic_model_tmdl.ps1`](../../../../data-platform/scripts/export_semantic_model_tmdl.ps1). **Grep of the round-tripped TMDL shows zero `role` blocks** — the portal flow created a fresh model without carrying the skeleton's role scaffolds. Sprint 10 must **re-author the 4 roles in the Fabric web modeling editor** using the Roles pane, then re-run `export_semantic_model_tmdl.ps1` to persist them.

### Blocker 2 — column-level `[phi]="true"` annotations not present

The skeleton's role filter (`IF([_data_quality]="phi", FALSE, TRUE)`) is a **row-level proxy**. ADR-0016 gate 4 is defined at the **column** level (annotation `[phi]="true"` on individual PHI-shaped columns). The portal-first workflow needs a manual annotation pass per column, then role filters adjusted to reference the annotation. Sprint 10 scope.

### Blocker 3 — no synthetic PHI fixture to verify against

Sprint 09 v2 gold-layer test data has `_data_quality ∈ {explicit, inferred, missing}`. **No `phi`-tagged rows exist by design** — [ADR-0016](../../../adr/0016-no-phi-in-mvp-demo-scope.md) explicitly forbids PHI ingestion in demo scope. To exercise the RLS filter end-to-end, a **synthetic PHI fixture row** must be injected into an isolated test lakehouse (not `lh_ihzhhpf_sit`). Fixture design + injection procedure = Sprint 10 T-scope.

## Roles authored (skeleton scaffold — to be re-added in portal)

| Role | Purpose limitation | Table filter (skeleton syntax) |
| ---- | ------------------ | ----------------------------- |
| `BedOps` | Bed operations — no PHI exposure per ADR-0016 gate 4 | `IF([_data_quality]="phi", FALSE, TRUE)` on `encounter`, `fact_encounter` |
| `ORPlanner` | OR planning — no PHI exposure per ADR-0016 gate 4 | `IF([_data_quality]="phi", FALSE, TRUE)` on `or_case`, `or_schedule`, `encounter` |
| `Analyst` | Broad analytics — no PHI exposure per ADR-0016 gate 4 | `IF([_data_quality]="phi", FALSE, TRUE)` on all `fact_*` + `encounter` tables |
| `SemanticOwner` | Semantic model steward — no PHI exposure per ADR-0016 gate 4 | `IF([_data_quality]="phi", FALSE, TRUE)` on `encounter` |

## Sprint 10 verification procedure (post-blocker-resolution)

1. **In Fabric web modeling editor** → **Manage roles** → create the 4 roles per the table above (adjust filters to reference column-level `[phi]="true"` annotations rather than row-level `_data_quality="phi"`).
2. Run [`export_semantic_model_tmdl.ps1`](../../../../data-platform/scripts/export_semantic_model_tmdl.ps1) — verify the exported TMDL contains 4 `role` blocks.
3. Inject synthetic PHI fixture into isolated test lakehouse (Sprint 10 fixture-design deliverable).
4. For each role: **View as role** on a PHI-tagged column, confirm 0 rows returned, record DAX query + row count + timestamp in the log below.

## Verification log

| Date | Role | PHI column tested | Query | Rows returned | Reviewer | Result |
| ---- | ---- | ----------------- | ----- | ------------: | -------- | ------ |
| _pending Sprint 10 unblock_ | BedOps | (tbd) | | | | |
| _pending Sprint 10 unblock_ | ORPlanner | (tbd) | | | | |
| _pending Sprint 10 unblock_ | Analyst | (tbd) | | | | |
| _pending Sprint 10 unblock_ | SemanticOwner | (tbd) | | | | |

## References

- ADR-0016 gate 4 — [`docs/adr/0016-no-phi-in-mvp-demo-scope.md`](../../../adr/0016-no-phi-in-mvp-demo-scope.md)
- Round-tripped TMDL — [`data-platform/reports/capacity-dashboard.SemanticModel/definition/`](../../../../data-platform/reports/capacity-dashboard.SemanticModel/definition/)
- Semantic-model README — [`data-platform/reports/capacity-dashboard.SemanticModel/README.md`](../../../../data-platform/reports/capacity-dashboard.SemanticModel/README.md)
- Design spec §6.5 — [`docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md`](../../../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md)
- Sprint 09 retrospective §5 (Sprint 10 follow-ups) — [`retrospective.md`](../retrospective.md#5-follow-ups-sprint-10)
- `docs/TEST.md` §Sprint 09 evidence — [`docs/TEST.md`](../../../TEST.md)
