# Curavias Shared Golden-Source Master Data + Extended Organisation & Skills Ontology — Design Spec

| Field | Value |
|-------|-------|
| **Version** | 1.1.0 |
| **Date** | 2026-07-19 |
| **Author** | Urs Rüegg |
| **Status** | Draft for review |
| **Previous Version** | 1.0.0 (resolved Q1: the three Curavias tenants **replace** today's `dim_hospital` rows; resolved Q2: BVA stays a separate `bva_*` domain, but every remaining `dim_hospital` / `hospital_id` reference is re-pointed to the Curavias org spine) |
| **Supersedes** | [issue #253](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/253) (operational medallion notebook modernization is folded in as P1a below) |
| **Builds on** | The Curavias idea package under [`docs/superpowers/ideas/curavias-organisation-skills-ontology-work-id/`](../ideas/curavias-organisation-skills-ontology-work-id/README-Curavias-Skills-Ontology-Deliverables.md) (Steps 1-4 + 20 CSVs + generator); the [Fabric IQ to Foundry readiness design](2026-07-17-fabric-iq-foundry-readiness-design.md) (Phase 2 was paused on the stale-notebook blocker) |
| **Runtime posture** | GitHub Copilot coding agent + Superpowers-first execution; git = single source of truth for master data; Fabric Git integration + `fabric-cicd` for Fabric assets; every Azure apply gated by `approved-to-apply`; human-performed PR merges |
| **Related ADRs** | [ADR-0013 (US demo scope)](../../adr/0013-temporary-us-region-demo-scope.md); [ADR-0014 (Fabric IQ ontology backbone, GA-gated)](../../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md); [ADR-0016 (no PHI in demo)](../../adr/0016-no-phi-in-mvp-demo-scope.md); [ADR-0035 (PROD Fabric IQ in westus2)](../../adr/0035-fabric-iq-layer-region-westus2.md); a new ADR (unified organisation spine) is a deliverable of this spec |

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Context and problem statement](#2-context-and-problem-statement)
3. [Decisions taken (brainstorm outcomes)](#3-decisions-taken-brainstorm-outcomes)
4. [Part 1 — Golden-source master data + unified medallion](#4-part-1--golden-source-master-data--unified-medallion)
5. [Part 2 — Target architecture: agent extension (design-only)](#5-part-2--target-architecture-agent-extension-design-only)
6. [Governance, versioning, traceability](#6-governance-versioning-traceability)
7. [Risks and open questions](#7-risks-and-open-questions)
8. [Sequencing summary](#8-sequencing-summary)

---

## 1. Goal and desired end state

Establish a **single, git-owned source of truth** for the platform's master data — the existing
operational capacity master data **plus** the Curavias Organisation and Skills master data — and load
it **identically** into the SIT and PROD Fabric IQ lakehouses through a reproducible
bronze -> silver -> gold medallion, a Direct Lake semantic model, and an **extended ontology**. On top
of that unified data product, produce a **target architecture** (design-only) for extending the
platform's operational agents with skills-based, evidence-gated capacity reasoning.

Desired end state:

- One canonical master-data tree in the repo (`data/master-data/`), validated and CI-gated, that both
  environments consume with no per-environment data drift.
- A reproducible medallion: running the notebooks against an empty schemas-enabled lakehouse yields the
  same `gold.*` table set in SIT and PROD (closes the readiness-design Phase 2 blocker).
- A **unified organisation spine** — `dim_hospital` reconciled into the Curavias
  `dim_tenant` / `dim_org_unit` / `dim_department` hierarchy — with the Skills layer
  (`dim_skill`, `dim_employee`, `fact_skill_assertion`, `fact_skill_demand`, `fact_skill_gap`,
  `bridge_worker_unit_eligibility`, ...) as first-class gold tables.
- The Fabric IQ ontology (`ont_hospital_capacity`), semantic model, and Data Agent grounding extended to
  cover the Organisation and Skills product domain.
- A documented, later-sprint target architecture for the operational agents to consume it.

Non-goals (this effort):

- No agent code changes (Part 2 is design-only).
- No real / PHI data — the Curavias set is synthetic and anonymized (see 3.6).
- No change to the Foundry control plane or region posture (ADR-0032, ADR-0035 unchanged).

## 2. Context and problem statement

The readiness-design Phase 2 (reproducible PROD Fabric IQ build) is **paused**: the committed operational
medallion notebooks write the **old path-based** gold layout
(`Tables/gold/reference/*`, `Tables/gold/patient-flow/*`, `Files/gold/*`), whereas the as-built SIT gold
is **flat schemas-enabled** `gold.*`. The `capacity-dashboard` Direct Lake model binds to `[gold].[*]`,
so a fresh workspace cannot be rebuilt faithfully from the committed notebooks. That was captured as
issue #253.

Separately, the Curavias idea package delivered a complete, load-ready **Organisation + Skills** extension:
an ontology model (Step 1), a Swiss competency-source catalogue and 66-skill list (Step 2), a
Work-ID / Skills-Manager solution design (Step 3), and 20 master-data CSVs + a deterministic generator
(Step 4). Today that master data lives only under `docs/superpowers/ideas/` and is not wired into the
platform. The current operational master data lives in a review folder
(`docs/reviews/2026-06-29-ama-capacity-metadata-review/*.csv`) rather than a canonical home.

This spec fixes both: it makes git the single source of truth for **all** master data, modernizes the
medallion for reproducibility, and integrates the Curavias organisation and skills layer into the
existing ontology and semantic model.

## 3. Decisions taken (brainstorm outcomes)

| # | Decision | Rationale |
|---|----------|-----------|
| 3.1 | **Supersede #253** — fold the notebook modernization into this broader design as **P1a**. | One coherent design; #253 was a subset. |
| 3.2 | **Git is the single source of truth** for master data — version-controlled CSVs, validated, CI-gated, deployed identically to each environment. | Reproducibility, review, no cross-env drift. |
| 3.3 | **Canonical home = `data/master-data/`**, following the `data/entra/` pattern (validator + CI gate). | Reuses an established, working repo pattern. |
| 3.4 | **Reconcile into one unified organisation spine** — the three Curavias tenants **replace** today's `dim_hospital` rows; every remaining `dim_hospital` / `hospital_id` reference is re-pointed to `dim_tenant` / `dim_org_unit` / `dim_department`. | One unified organisation model; cleaner ontology; accepted higher rework. |
| 3.5 | **Phased build (Approach B)** — P1a reproducibility-first on today's schema, then P1b unify + org/skills. | Incremental validation; unblocks PROD fast; isolates the risky semantic-model change. |
| 3.6 | **Synthetic Curavias set = canonical demo master data** — no PHI, modelled on real Swiss archetypes. | Platform is demo / proof-of-technology scope (ADR-0013, ADR-0016). |
| 3.7 | **Part 1 builds now; Part 2 is design-only** target architecture for the operational agents. | Ship the data product; agent extension is a later sprint. |

## 4. Part 1 — Golden-source master data + unified medallion

### 4.1 Repo layout (single source of truth)

```text
data/master-data/
  README.md                    # golden-source contract, load order, provenance, PHI statement
  validate_master_data.py      # data/entra-style validator: FK integrity, GLN mod-10, enum domains, load order
  tests/
    test_validate_master_data.py
  capacity/                    # the 9 existing operational CSVs, relocated from docs/reviews/2026-06-29-...
    01_dim_hospital.csv ... 09_map_disease_treatment_specialty_service.csv
  curavias-org-skills/         # the 20 Curavias CSVs + the deterministic generator
    generate_master_data.py
    dim_tenant.csv ... fact_skills_manager_sync_log.csv
```

- New CI gate `.github/workflows/master-data.yml` (mirrors `entra-master-data.yml`) runs
  `validate_master_data.py` + unittests on any PR touching `data/master-data/**`.
- The `docs/reviews/2026-06-29-ama-capacity-metadata-review/*.csv` copies become **provenance-only**; a
  short pointer note is added there directing to the canonical `data/master-data/capacity/`.
- The `docs/superpowers/ideas/curavias-organisation-skills-ontology-work-id/master-data/` copies remain as
  the **idea provenance**; `data/master-data/curavias-org-skills/` is canonical. The generator is
  relocated (not duplicated) and its output path points at the canonical folder.

### 4.2 Validator (git gate before any load)

`validate_master_data.py` asserts, for both `capacity/` and `curavias-org-skills/`:

- **Referential integrity** — every FK resolves to a PK in its parent table (per the Step 4 load-order DAG).
- **GLN check digit** — every person / org GLN passes the GS1 mod-10 check.
- **Closed value sets** — enum columns (`entity_type`, `assurance_level`, `spec_type`, `skill_category`, ...)
  contain only declared members.
- **Load order** — the dependency DAG has no cycle and dimensions precede facts/bridges.
- **No PHI markers** — a lightweight scan asserting the "synthetic / anonymized" contract holds.

### 4.3 Parameterized loader (removes the #253 hard-coded GUIDs)

`data-platform/scripts/upload_to_onelake.py` is refactored from hard-coded SIT GUIDs to explicit
parameters:

```text
upload_to_onelake.py \
  --workspace-id <ws> --lakehouse-id <lh> \
  --source-root data/master-data \
  --target Files/master-data
```

- SIT and PROD invoke it **identically**; only the workspace/lakehouse IDs differ, sourced from
  `data-platform/fabric/environments.yml`.
- Uploads `capacity/*.csv` -> `Files/master-data/capacity/` and
  `curavias-org-skills/*.csv` -> `Files/master-data/curavias-org-skills/`.
- The same parameterized entry point is reused by BVA (`bva_upload_bronze.py` currently uploads generated
  parquet); BVA stays generated but shares the upload path — no CSV curation for BVA.

### 4.4 P1a — reproducibility-first medallion (today's schema, `gold.*`)

Goal: prove a byte-reproducible rebuild on the **current** table contract before adding the org/skills
layer.

- Modernize the operational notebooks to schema-qualified writes:
  - `reference/01_bronze_master_data` -> `saveAsTable('bronze.<table>')` (reads `Files/master-data/capacity/`).
  - `reference/02_silver_master_data` -> `saveAsTable('silver.<table>')`.
  - `reference/03_gold_master_data` -> `saveAsTable('gold.<table>')` (drop `Tables/gold/reference/*`).
  - `eventstream/03_gold_eventstream` -> `saveAsTable('gold.<entity>')`; add a documented **batch seed**
    for `bronze_eventstream_raw` so the chain runs with `use_streaming=False` and no live Eventstream.
  - `reference/04_load_or_samples` -> read OR JSON fixtures from `Files/` (uploaded via the parameterized
    loader) instead of a repo-relative path; write `saveAsTable('gold.or_case')` / `saveAsTable('gold.or_schedule')`.
- Add a **gold-schema parity check** (new verify step + CI) asserting the produced gold table set matches
  the `capacity-dashboard` semantic-model table contract.
- Acceptance: running the modernized notebooks against an **empty schemas-enabled** lakehouse produces the
  flat `gold.*` set the `capacity-dashboard` model binds to; verified against an empty SIT clone **and**
  the empty PROD lakehouse `lh_ihzhhpf_prod` (`4f73c480-6c85-4823-bb98-4e66780c527f`). This closes the
  original #253 acceptance criteria and unblocks the readiness-design Phase 2 PROD load.

### 4.5 P1b — unify spine + org/skills domain + ontology

- **New org/skills medallion notebooks** (`reference/1x_bronze_org_skills`, `_silver_`, `_gold_`) reading
  `Files/master-data/curavias-org-skills/` and writing `saveAsTable('{bronze,silver,gold}.*')`.
- **Reconciliation (the unified spine) — replace, not alias:**
  - The three Curavias tenants (CuraNova / Curalp / Vialta) and their org units **replace** today's
    `dim_hospital` rows. `dim_hospital` is **retired** as a canonical table; the Curavias org hierarchy
    (`dim_tenant` / `dim_org_unit` / `dim_department`) becomes the single organisation spine.
  - A one-time **migration crosswalk** (`data/master-data/capacity/_hospital_to_org_crosswalk.csv`,
    checked into git and validated) maps each old `hospital_id` to its replacement tenant / org-unit so
    downstream facts can be re-keyed deterministically.
  - Re-key downstream facts — `fact_capacity_baseline`, `encounter`, `bed_assignment`, `or_case`,
    `or_schedule` — to `org_unit_id` / `department_id` via the crosswalk. `hospital_id` is dropped (no
    back-compat alias — Q1 chose replace).
  - **Reference-replacement surface** (all re-pointed to the Curavias org keys in the same cutover):
    the semantic-model tables (`dim_hospital.tmdl`, `relationships.tmdl`, roles, dependent measures), the
    `capacity-dashboard` report visuals that bind `dim_hospital` / `hospital_id`, and the `sim-capacity`
    generators / calibration presets that emit `hospital_id`. **Out of scope (Q2):** BVA keeps its own
    separate `bva_dim_hospital` (`bva_*` product domain) unchanged.
- **Gold additions (org/skills product domain):** `dim_tenant`, `dim_org_unit`, `dim_department`,
  `dim_specialisation`, `dim_occupation_role`, `dim_skill`, `dim_issuing_authority`, `dim_assurance_level`,
  `dim_proficiency_level`, `dim_workforce_position`, `dim_employee`, `fact_skill_assertion`,
  `bridge_role_skill_demand_template`, `fact_skill_demand`, `fact_skill_gap`,
  `bridge_worker_unit_eligibility`, `dim_work_id_profile`, `map_skill_crosswalk`,
  `fact_skills_manager_sync_log`.
- **Skill supply view + gap logic:** a `view_skill_supply` (valid, assurance-gated assertions per
  worker/skill) feeding `fact_skill_gap = demand - valid supply`, deny-by-default (only L2+ valid counts
  as safety-critical supply; L4 where legally required).
- **Semantic model:** add the org/skills tables, relationships (GLN / org-unit / department joins), and
  measures (skill supply, demand, gap, eligibility, currency). **Bump the exact-count constants** in
  `export_semantic_model_tmdl.ps1` and the `verify-semantic-model.yml` gate to match the new
  relationship / measure / role totals.
- **Ontology + crosswalk:** extend `docs/ontology/README.md` + `docs/ontology/crosswalk.md` with the
  Organisation and Skills classes (`Department`, `Specialisation`, `WorkforcePosition`, `Employee`,
  `Skill`, `SkillAssertion`, `AssuranceLevel`, `IssuingAuthority`) and their ESCO / FHIR R5 / ISCO-08 /
  SNOMED / GLN crosswalk rows. Extend `scripts/ontology/check_crosswalk_conformance.py` + the
  `ontology-conformance.yml` gate to cover the new contract rows.
- **Fabric IQ:** extend the ontology `ont_hospital_capacity`, the semantic model, and the read-only Data
  Agent grounding to include the Organisation and Skills product domain.

### 4.6 Deployment (SIT + PROD identical)

- Both environments: parameterized uploader -> notebook runs (`import_notebooks.py` + `run_notebooks.py`)
  -> `deploy_fabric_cicd.py` for the semantic model + report.
- Every Azure apply is gated by an `approved-to-apply` comment; PR merges are human-performed.
- The OIDC SP `gh-oidc-ihzhhpf` must be granted **Member** on the PROD Fabric workspace before CI publish
  (already flagged in the fabric-cicd runbook).

## 5. Part 2 — Target architecture: agent extension (design-only)

This section is **design-only**; no agent code changes in this effort. It defines how the eight
operational agents consume the unified Organisation + Skills data product in a later sprint.

| Agent | How the extended ontology extends it | Priority |
|-------|--------------------------------------|----------|
| `sba-agent` (staffing balance) | Primary consumer: reads `fact_skill_demand`, `view_skill_supply`, `fact_skill_gap`, `bridge_worker_unit_eligibility` for skills-based, currency-aware staffing recommendations. | High |
| `csa-agent` (crisis / scenario) | Surge suitability by **proficiency** (case complexity) and **assurance** (eligibility gate); response levers gated on valid skill supply, not headcount. | High |
| `bmca-agent` / `ooa-agent` / `dca-agent` | Capacity / occupancy / discharge signals enriched by a deny-by-default "is a qualified, currency-valid person available" gate over the skills layer. | Medium |
| `data-quality-agent` | New bronze/silver/gold contract checks + drift alerts for the org/skills tables, GLN integrity, and the assurance-gate invariant (nothing self-declared becomes safety-critical supply). | Medium |

Design principles carried from the idea package:

- **Two orthogonal axes never collapse** — proficiency (1-5, how capable) and assurance (L0-L4, how proven);
  demand gates on both.
- **GLN golden thread** — one identifier joins HR, federal registers, and FHIR `Practitioner`; every match
  is deterministic.
- **Gold is deny-by-default** — Work-ID / Skills-Manager are **source systems** feeding Bronze at L0-L1;
  they provide breadth and discovery and **never override** the federal L2-L4 safety floor.
- **Grounding** — agents reach the data product via the read-only Fabric Data Agent over the extended
  semantic model; consent-first for the Work-ID / Skills-Manager sources.
- **HITL** — all agent output remains advisory; every downstream action is human-in-the-loop.

Deliverable of Part 2: a follow-up sprint design + issues; the agent `AGENT.md` and golden-task changes
are scoped there, not here.

## 6. Governance, versioning, traceability

- **New ADR** — "Unified organisation spine + Curavias golden-source master data." Records that folding
  `dim_hospital` into the Curavias org hierarchy is a **breaking contract change** (a consumer that
  referenced `gold.dim_hospital` keys must migrate to org-unit / department keys) and that this spec
  **supersedes and closes #253**.
- **PRD** — add FR/NFR rows for (a) git golden-source master data with CI validation, (b) the unified
  organisation spine, (c) the Skills product domain + ontology extension, and (d) the agent-extension
  target architecture; update the PRD Section 7 traceability matrix in the same edit.
- **Doc versioning** — this spec starts at 1.0.0. The readiness design gets a MINOR bump noting that its
  paused Phase 2 is now driven by this spec. The PRD and any edited ontology docs bump per the versioning
  rules.
- **`verify-semantic-model.yml`** — the P1b semantic-model change requires bumping the expected
  relationship / measure / role counts in `export_semantic_model_tmdl.ps1`.

## 7. Risks and open questions

| # | Risk / question | Mitigation |
|---|-----------------|------------|
| R1 | Replacing `dim_hospital` breaks the `capacity-dashboard` model, its exact-count CI gate, report visuals, and the `sim-capacity` generators. | Isolate in P1b; do the full reference-replacement (semantic model + visuals + generators) in one cutover PR; bump gate constants in the same PR; validate `what-if` on a SIT clone first. |
| R2 | Re-keying facts to org units mis-maps historical rows once `hospital_id` is dropped. | Explicit, reviewed `_hospital_to_org_crosswalk.csv` checked into `data/master-data/capacity/`; validator asserts every old `hospital_id` maps and every re-keyed fact key resolves. |
| R3 | ESCO / SIWF / SNOMED references in the CSVs are demo slugs, not canonical URIs. | Keep as demo slugs for the demo; record a "replace at real load" note in the README; crosswalk conformance treats them as demo-tier. |
| R4 | The org/skills gold enlarges the semantic model beyond what Direct Lake demoably handles. | Scope the demo semantic model to the tables the dashboard + agents actually use; keep the rest queryable via the Data Agent only. |
| Q1 | ~~Should the three Curavias tenants replace or map onto today's `dim_hospital` rows?~~ **Resolved: replace.** The Curavias org hierarchy is canonical; `dim_hospital` is retired and all references re-pointed. | — |
| Q2 | ~~Does BVA gold need re-keying to the org spine?~~ **Resolved: no.** BVA keeps its separate `bva_dim_hospital` (`bva_*` domain); only the operational `dim_hospital` / `hospital_id` references are re-pointed. | — |

## 8. Sequencing summary

1. **P1a — reproducibility-first** (supersedes #253): relocate the 9 capacity CSVs to
   `data/master-data/capacity/`; add the validator + `master-data.yml` CI gate; parameterize
   `upload_to_onelake.py`; modernize the operational notebooks to `gold.*`; add the gold-schema parity
   check; prove reproducible parity on empty SIT clone + empty PROD lakehouse.
2. **P1b — unify + org/skills**: relocate the 20 Curavias CSVs + generator to
   `data/master-data/curavias-org-skills/`; build the org/skills medallion; reconcile `dim_hospital` into
   the org spine + re-key facts; extend the semantic model + bump its CI gate; extend the ontology +
   crosswalk + conformance gate; extend the Fabric IQ ontology + Data Agent grounding.
3. **Deploy** to SIT then PROD (identical path, `approved-to-apply`-gated).
4. **Part 2** — write the agent-extension target-architecture follow-up (design-only) + its issues.
5. **Governance** — new ADR; PRD FR/NFR + Section 7 matrix; readiness-design MINOR bump; close #253.

> After this spec is approved, the next step is the **writing-plans** skill to produce the P1a / P1b
> implementation plan.
