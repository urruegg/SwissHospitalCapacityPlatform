# Sprint 23 — Unified Curavias Organisation Spine + Org/Skills Ontology (P1b)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-19 |
| **Author** | @urruegg |
| **Status** | Planned (blocked on Sprint 22) |
| **Previous Version** | n/a (new document) |

> **Sprint theme.** Fold `dim_hospital` into a unified Curavias organisation hierarchy (three Curavias tenants **replace** today's hospital rows), add the Curavias organisation + skills master-data domain as first-class `gold.*` tables, and extend the semantic model, ontology, crosswalk, and Fabric IQ Data Agent grounding. This is **Part 1b** of the Curavias shared-master-data design.

---

## 1. Sprint goal

Reconcile the operational capacity model with the real (synthetic) Curavias organisation: retire `dim_hospital`, introduce the `dim_tenant` / `dim_org_unit` / `dim_department` spine, add the workforce skills domain (supply / demand / gap / eligibility), and extend every downstream contract — semantic model, ontology, crosswalk, conformance gate, and the Fabric IQ ontology + Data Agent grounding — so both the operational agents and the Foundry IQ agents reason over one unified organisation spine.

**Success shape:**

* The 20 Curavias org/skills CSVs + generator are git-owned under `data/master-data/curavias-org-skills/`, validator-gated (GLN mod-10, enum domains, FK integrity).
* An org/skills medallion produces the 19 `gold.*` tables.
* `dim_hospital` is replaced by the three Curavias tenants (CuraNova / Curalp / Vialta) via `_hospital_to_org_crosswalk.csv`; `fact_capacity_baseline`, `encounter`, `bed_assignment`, `or_case`, and `or_schedule` are re-keyed; the semantic model, report visuals, and `sim-capacity` generators are re-pointed. **BVA keeps its separate `bva_dim_hospital`.**
* The ontology + crosswalk + conformance gate and the Fabric IQ ontology `ont_hospital_capacity` + Data Agent grounding cover the organisation + skills domain.

---

## 2. Source baseline

1. [Design Spec — Curavias shared master data + ontology](../superpowers/specs/2026-07-19-curavias-shared-master-data-and-ontology-design.md) — §4.5 (unified spine + org/skills), §5 (Part 2 agent design-only), §6 (governance)
2. [Curavias idea package](../superpowers/ideas/curavias-organisation-skills-ontology-work-id/) — Step 1 (ontology extension), Step 2 (Swiss competency sources), Step 3 (Work-ID / Skills-Manager), Step 4 (master-data schema) + 20 CSVs + `generate_master_data.py`
3. [Sprint 22 — Golden-source + reproducible medallion (P1a)](sprint-22-curavias-golden-source-reproducible-medallion.md) — **prerequisite** (provides the modernized `gold.*` notebooks this sprint extends)
4. [`docs/ontology/`](../ontology/) — reference ontology, crosswalk, and conformance design this sprint extends
5. `data-platform/scripts/export_semantic_model_tmdl.ps1` + `.github/workflows/verify-semantic-model.yml` — the exact-count CI gate to re-baseline

> **Implementation plan:** authored **after** Sprint 22 lands, because the P1b tasks depend on the modernized `gold.*` notebooks and the re-keying crosswalk produced there.

---

## 3. Sprint scope

| # | Task | Deliverable | DoD |
|---|------|-------------|-----|
| T1 | Relocate org/skills master data | 20 CSVs + generator under `data/master-data/curavias-org-skills/` + README | Git-moved; provenance recorded |
| T2 | Extend validator | GLN mod-10, enum domains, cross-CSV FK integrity + tests | Tests fail then pass; real data valid |
| T3 | Org/skills medallion | bronze/silver/gold notebooks -> 19 `gold.*` tables | Managed tables; parity check extended |
| T4 | Replace `dim_hospital` | `_hospital_to_org_crosswalk.csv` + re-key facts to `dim_tenant` | No `dim_hospital`; facts re-keyed |
| T5 | Re-point consumers | Semantic model, report visuals, `sim-capacity` generators | Visuals render; generators emit org keys |
| T6 | Skills measures | supply / demand / gap + eligibility measures | Measures validate in the model |
| T7 | Re-baseline CI gate | Bump `verify-semantic-model.yml` exact counts | Gate green with new counts |
| T8 | Extend ontology | `docs/ontology/` + `crosswalk.md` + conformance gate | Conformance green |
| T9 | Extend Fabric IQ | `ont_hospital_capacity` + Data Agent grounding cover org/skills | Data Agent cites org/skills concepts |
| T10 | Governance | New ADR (unified spine) + PRD FR/NFR + §7 matrix | Doc gates green; ADR Accepted |

---

## 4. Key decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | The three Curavias tenants **replace** `dim_hospital` rows (no back-compat alias) | User-confirmed (Q1): one unified organisation spine, not a parallel dimension. |
| D2 | Facts re-keyed via a one-time `_hospital_to_org_crosswalk.csv` | Deterministic, reviewable mapping from legacy `hospital_id` to `tenant_id` / `org_unit_id`. |
| D3 | **BVA stays a separate `bva_*` domain** with its own `bva_dim_hospital` | User-confirmed (Q2): BVA's cost/value model must not be entangled with the operational spine. |
| D4 | Part 2 (agent extension) is **design-only** this sprint | Land the data + ontology spine first; wire the operational + Foundry agents to the extended ontology in a follow-up build sprint. |
| D5 | Skills competency sourced from the Step-2 Swiss references, synthetic only | ADR-0013 / ADR-0016 — demo scope, no PHI, no real workforce records. |

---

## 5. Definition of Done

* [ ] Sprint 22 (P1a) landed — modernized `gold.*` notebooks available
* [ ] P1b implementation plan authored and approved
* [ ] Org/skills CSVs + generator under `data/master-data/curavias-org-skills/`; validator green
* [ ] Org/skills medallion produces the 19 `gold.*` tables; parity check extended
* [ ] `dim_hospital` replaced by `dim_tenant` / `dim_org_unit` / `dim_department`; all references re-pointed; facts re-keyed
* [ ] Semantic model extended (skills measures); `verify-semantic-model.yml` re-baselined + green
* [ ] Ontology + crosswalk + conformance gate extended and green
* [ ] Fabric IQ `ont_hospital_capacity` + Data Agent grounding cover the org/skills domain
* [ ] New ADR (unified org spine) Accepted; PRD FR/NFR rows + §7 matrix updated
* [ ] SIT + PROD deployed identically; live applies gated by `approved-to-apply`; PR merges human-performed
* [ ] All CI checks pass

---

## 6. References

* Design: [`2026-07-19-curavias-shared-master-data-and-ontology-design.md`](../superpowers/specs/2026-07-19-curavias-shared-master-data-and-ontology-design.md)
* Idea package: [`curavias-organisation-skills-ontology-work-id/`](../superpowers/ideas/curavias-organisation-skills-ontology-work-id/)
* Prerequisite sprint: [Sprint 22 — Golden-source + reproducible medallion (P1a)](sprint-22-curavias-golden-source-reproducible-medallion.md)
* Ontology: [`docs/ontology/`](../ontology/)
* Issue: [#255 — Sprint 23: Unified Curavias organisation spine + org/skills ontology (P1b)](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/255)
* Depends on: [#254 — Sprint 22 (P1a)](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/254)
