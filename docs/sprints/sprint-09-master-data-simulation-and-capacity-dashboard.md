# Sprint 09 — Master Data Foundation, Simulation Enhancement & Capacity Dashboard

| Field | Value |
| ----- | ----- |
| **Version** | 1.2.0 |
| **Date** | 2026-07-02 |
| **Author** | Urs Rüegg (recovery from GitHub Copilot v1.0.0 draft) |
| **Status** | Draft — pre-refresh (recovered from unmerged branch) |
| **Previous Version** | 1.1.3 (RB-06 resolved by PRD v1.4.0 §H) |

> **⚠️ Recovery banner — read before execution.**
> This document was authored on 2026-06-29 and lay unmerged on branch
> `hotfix/sit-disable-placeholder-modules` (commit `6424eff`). Recovered onto
> `main` on 2026-07-02 without further semantic changes. **It has NOT been
> refreshed against the two events that landed after it was written:**
>
> 1. **Sprint 00 tenant migration** — new tenant `MngEnvMCAP164444`
>    (`1337187a-4c41-4da9-8fca-731bba7a4329`), solution short name `ihzhhpf`,
>    subscription `66a9953a-df37-4c51-856c-9971b9bf3e03`, Fabric F2 running in
>    `westus2` per [ADR-0013](../adr/0013-temporary-us-region-demo-scope.md).
>    Sprint 08 blockers are resolved.
> 2. **AMA HCC / North Star review** (2026-07-01) — see [Section 11
>    handoff](../reviews/2026-07-01-ama-hcc-northstar-review.md#11-sprint-09-implementation-handoff)
>    for 7 additional handoff items (H-01…H-07: ADR-0005 supersession, MVO via
>    Fabric IQ, `FR-ONT-*` PRD family, semantic owner in OPERATIONS.md,
>    reference↔operational crosswalk + CI conformance check, Fabric IQ
>    Switzerland-GA tracker, `DC-OR-SCHEDULE-v1` + `DC-OR-CASE-v1` contracts).
>
> **Before starting execution:** run the Refresh Backlog in §0 below,
> optionally through the Superpowers `brainstorming` → `writing-plans` flow.

---

## §0 — Refresh Backlog (must-do before execution)

| ID | Topic | Action | Owner | Source |
| --- | ----- | ------ | ----- | ------ |
| RB-01 | Residency tags | **Resolved 2026-07-02** — dual-mode residency now documented in §1.2 schema table: `CH-North` (target GA) + `US-West` (demo carve-out per [ADR-0013](../adr/0013-temporary-us-region-demo-scope.md), exception `EX-2026-07-02-westus2-demo`, expires 2026-09-30). No PHI in either mode. Silver validation gate (§2.2 Notebook 02) updated to match. | Governance | [ADR-0013](../adr/0013-temporary-us-region-demo-scope.md); [`policy/exceptions.json`](../../policy/exceptions.json) |
| RB-02 | Sprint 08 dependency | **Resolved 2026-07-02** — § Dependency on Sprint 08 rewritten to reflect Sprint 00 delivery: Fabric F2 `fabricihzhhpfsit` + workspace `ws-ihzhhpf-sit-data` + lakehouse `lh_ihzhhpf_sit` + `gold.demand_encounter` (3 rows loaded, G2.2 spirit-met). Sprint 08 bronze/silver/gold notebook pipeline still deferred; interim path is lakehouse-direct CSV load per RB-12. Old risk register row "Sprint 08 Fabric admin blocker" replaced with "Sprint 08 bronze/silver notebook pipeline deferred". | Data platform | [sprint-00 report §Slice 1+2](sprint-00-new-tenantprovisioning.md); [G2.2 close-out narrative](sprint-00-new-tenantprovisioning.md) |
| RB-03 | Fabric capacity SKU | **Resolved 2026-07-02** — F2 (`fabricihzhhpfsit`) confirmed via Sprint 00 lakehouse-direct load; Direct Lake support in `westus2` demo scope verified end-to-end for `gold.demand_encounter`. Capacity is currently **Paused** for cost hygiene (~USD 260/month saved) — resume via `az resource invoke-action ... --action resume` before dashboard smoke test. Note added to §4.1 semantic-model section + risk register row updated. | Data platform | Sprint 00 evidence: `fabricihzhhpfsit` Paused state |
| RB-04 | AMA HCC/North Star H-01 | **Resolved 2026-07-02** by [ADR-0014](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md) *(Proposed)* — supersedes ADR-0002; establishes Fabric IQ Ontology as target semantic backbone, GA-gated, with portable reference layer, two-layer conformance CI, and gates G-A/G-B/G-C. AMA §9.1 H-01 proposed ADR-0005 as placeholder path; renumbered to 0014 because 0005 was already taken. | Governance / ADR track | [AMA §11.1 H-01](../reviews/2026-07-01-ama-hcc-northstar-review.md#11-sprint-09-implementation-handoff); [ADR-0014](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md) |
| RB-05 | AMA HCC/North Star H-02 | **Stand up the Minimum Viable Ontology (MVO)** in the Sprint-09 Power BI semantic model + Fabric IQ ontology generation, bounded to bed + OR slot + encounter + facility hierarchy. Adds a new track / deliverable. | Data platform | [AMA §11.1 H-02, §11.2](../reviews/2026-07-01-ama-hcc-northstar-review.md#11-sprint-09-implementation-handoff) |
| RB-06 | AMA HCC/North Star H-03 | **Resolved 2026-07-02** — [PRD.md v1.4.0](../PRD.md) adds **§H Semantic Ontology** (`FR-ONT-001..007`, `FR-GOV-ONT-001..003`) under Functional Requirements and **§H Semantic Ontology** (`NFR-ONT-001`) under Non-Functional Requirements. Traceability matrix extended with 4 new rows anchoring the family to ADR-0014, AMA review, OPERATIONS.md and this sprint doc. | Product / PRD track | [AMA §11.1 H-03](../reviews/2026-07-01-ama-hcc-northstar-review.md#11-sprint-09-implementation-handoff); [PRD §H](../PRD.md#h-semantic-ontology); [ADR-0014](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md) |
| RB-07 | AMA HCC/North Star H-04 | **Resolved 2026-07-02** — [OPERATIONS.md v1.4.0 RACI baseline](../OPERATIONS.md#roles-and-accountability-raci-baseline) adds *Semantic / ontology stewardship* row; new subsection *Semantic / Ontology Owner (new role per ADR-0014)* defines remit, change discipline, principles, deliverables and escalation. Incumbent nomination is Sprint 09 acceptance evidence. | Governance | [AMA §11.1 H-04](../reviews/2026-07-01-ama-hcc-northstar-review.md#11-sprint-09-implementation-handoff); [ADR-0014 §4](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md#4-governance-model-obo-inspired) |
| RB-08 | AMA HCC/North Star H-05 | Design the **reference↔operational crosswalk** artefact (`docs/ontology/crosswalk.md`) + CI conformance check (design in Sprint 09; enforcement may slip to Sprint 10). | Governance + Data Platform | [AMA §11.1 H-05](../reviews/2026-07-01-ama-hcc-northstar-review.md#11-sprint-09-implementation-handoff) |
| RB-09 | AMA HCC/North Star H-06 | **Resolved 2026-07-02** — [OPERATIONS.md v1.4.0 Live Risk Register](../OPERATIONS.md#live-risk-register-new) adds `OPS-RISK-01` (Fabric IQ Switzerland-region GA + DPA equivalence). Monthly review cadence; owner = semantic / ontology owner; fallback = property-graph on GA per [ADR-0014 §3](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md#3-sprint-09-delivers-the-minimum-viable-ontology-mvo). | Product | [AMA §11.1 H-06](../reviews/2026-07-01-ama-hcc-northstar-review.md#11-sprint-09-implementation-handoff); [OPERATIONS.md `OPS-RISK-01`](../OPERATIONS.md#live-risk-register-new) |
| RB-10 | AMA HCC/North Star H-07 | Draft `DC-OR-SCHEDULE-v1` + `DC-OR-CASE-v1` **contract schemas only** (ingestion in Sprint 10). Adds to the 9 DC-MASTER-* contracts. | Data contracts | [AMA §11.1 H-07](../reviews/2026-07-01-ama-hcc-northstar-review.md#11-sprint-09-implementation-handoff) |
| RB-11 | Reference-layer skeleton | Create `docs/ontology/` folder + OWL/RDF skeleton importing BFO / OMRSE / OGMS / OOSTT + `CapacityUnit` abstraction. | Governance | [AMA §11.2 "Reference-layer skeleton"](../reviews/2026-07-01-ama-hcc-northstar-review.md#11-sprint-09-implementation-handoff) |
| RB-12 | Source-of-record for master data | **Resolved 2026-07-02** — §2.2 Track 2 now documents the ingestion decision: **lakehouse-direct CSV upload is the accepted interim path** (validated in Sprint 00 for `gold.demand_encounter`). Full bronze→silver→gold notebook pipeline stays in scope for volume/complexity but is not gated on Sprint 08 delivery. Source SQL remains disabled per MCAPS regional restriction ([sprint-00 v1.1.0 follow-up #2](sprint-00-new-tenantprovisioning.md)); Bicep is ready — flip when unblocked. | Data platform | [sprint-00 v1.1.0](sprint-00-new-tenantprovisioning.md) |
| RB-13 | TMDL semantic model creation | **Resolved 2026-07-02** — §4.1 semantic-model section now specifies **Approach A** (portal-authored TMDL export as reference, then REST-based `getDefinition` → `updateDefinition` for automation). REST-only creation via handwritten `dataSources.tmdl` deferred until the Direct Lake TMDL grammar reference is available. Aligns with Sprint 00 follow-up #1. | Data platform | [sprint-00 v1.1.0 follow-up #1](sprint-00-new-tenantprovisioning.md) |
| RB-14 | Naming | Verified on recovery (2026-07-02): no legacy `chhealthpf` references in this doc or the design spec. Item closed on recovery, kept for traceability. | Data platform | [.github/copilot-instructions.md §8](../../.github/copilot-instructions.md) |

**Refresh discipline:** each RB-* item resolved either updates this doc
in-place (bump to 1.2.0 for MINOR additions, 2.0.0 for MAJOR — e.g. adding
the MVO track) or spins off into its own ADR / PRD change. Do not start
Sprint 09 execution while §0 has open rows.

---

## Sprint Goal

Integrate the AMA-reviewed 4-layer hospital master data model into the Microsoft
Fabric data platform, extend the real-time capacity simulation to generate
DRG- and specialty-weighted episode streams, and deliver an end-to-end Power BI
Capacity Dashboard connecting master data dimensions to live capacity metrics.

Sprint 09 starts after Sprint 08 is fully completed (Fabric SIT pipeline green,
OneLake bronze/silver/gold zones operational).

---

## Source Baseline

1. [docs/PRD.md](../PRD.md)
2. [docs/DATA.md](../DATA.md)
3. [docs/ARCHITECTURE.md](../ARCHITECTURE.md)
4. [docs/COMPLIANCE.md](../COMPLIANCE.md)
5. [docs/SECURITY.md](../SECURITY.md)
6. [docs/sprints/sprint-08-data-platform-resources-and-ingestion-pipeline.md](sprint-08-data-platform-resources-and-ingestion-pipeline.md)
7. [docs/superpowers/specs/2026-06-29-sprint09-master-data-capacity-dashboard-design.md](../superpowers/specs/2026-06-29-sprint09-master-data-capacity-dashboard-design.md)
8. [docs/reviews/2026-06-29-ama-capacity-metadata-review.md](../reviews/2026-06-29-ama-capacity-metadata-review.md)
9. [docs/reviews/2026-06-29-ama-capacity-metadata-review/](../reviews/2026-06-29-ama-capacity-metadata-review/) (9 CSV files + master Excel)
10. [docs/adr/0003-swiss-regional-inference-for-phi.md](../adr/0003-swiss-regional-inference-for-phi.md)
11. [docs/adr/0004-block-global-and-data-zone-for-phi.md](../adr/0004-block-global-and-data-zone-for-phi.md)

---

## Dependency on Sprint 08

Sprint 09 requires Sprint 08 to be complete and verified:

| Sprint 08 Deliverable | Required by Sprint 09 |
| ----------------------- | ----------------------- |
| Fabric capacity + OneLake workspace provisioned | Master data loading notebooks |
| Bronze/silver/gold lakehouse zones operational | New `gold/reference/` schema |
| SQL → OneLake ingestion pipeline green in SIT | End-to-end data path validation |
| Sprint 08 SIT pipeline passes all gates | Sprint 09 SIT baseline |

Do **not** start Sprint 09 execution until `sprint-08` status changes from
`Blocked` to `Completed`.

---

## Sprint Scope

### Track 1 — Data Model Extensions

Extend the platform data model to incorporate the 9-table master data structure
defined in the AMA review session.

#### 1.1 New data tier: `gold/reference/`

Add a **reference (slow-changing) tier** within the existing gold lakehouse.
This tier holds dimension tables and the capacity baseline fact. It is separate
from the transactional `gold/patient-flow/` data.

```text
gold/
├── patient-flow/   (existing — episodes, throughput, LOS)
└── reference/      (new — master data dimensions + capacity fact)
    ├── dim_hospital
    ├── dim_specialty
    ├── dim_hospital_service
    ├── dim_disease
    ├── dim_treatment
    ├── dim_drg
    ├── dim_ward_capacityunit
    ├── fact_capacity_baseline
    └── map_disease_treatment_specialty_service
```

#### 1.2 Schema definitions

All `gold/reference/` tables carry these mandatory cross-cutting columns
(consistent with `docs/DATA.md` governance contract):

| Column | Type | Values |
| -------- | ------ | -------- |
| `_classification` | string | `Operational confidential` |
| `_residency_tag` | string | Dual-mode: **`CH-North`** (target GA) or **`US-West`** (demo carve-out per [ADR-0013](../adr/0013-temporary-us-region-demo-scope.md), exception `EX-2026-07-02-westus2-demo`, expires 2026-09-30). No PHI in either mode. |
| `_legal_basis` | string | `nDSG/KVG` |
| `_retention_class` | string | `R3` (7 years operational) |
| `_data_quality` | string | `explicit` / `inferred` / `missing` |
| `_lineage_ref` | string | source CSV filename + load timestamp |
| `_pseudonymisation_flag` | boolean | `false` (no PII in reference data) |

#### 1.3 Data contracts

Nine new data contracts are added to `docs/DATA.md`:

| Contract ID | Table | Producer | Consumers |
| ------------- | ------- | ---------- | ----------- |
| DC-MASTER-01 | dim_hospital | Master data loader | Semantic model, simulation |
| DC-MASTER-02 | dim_specialty | Master data loader | Semantic model, simulation |
| DC-MASTER-03 | dim_hospital_service | Master data loader | Semantic model |
| DC-MASTER-04 | dim_disease | Master data loader | Semantic model, simulation |
| DC-MASTER-05 | dim_treatment | Master data loader | Semantic model |
| DC-MASTER-06 | dim_drg | Master data loader | Simulation, semantic model |
| DC-MASTER-07 | dim_ward_capacityunit | Master data loader | Simulation, semantic model |
| DC-MASTER-08 | fact_capacity_baseline | Master data loader | Dashboard, semantic model |
| DC-MASTER-09 | map_disease_treatment_specialty_service | Master data loader | Semantic model |

#### 1.4 docs/DATA.md update

Add §X Master Data Domain section covering:
- Domain purpose (reference/slow-changing classification and clinical dimensions)
- Domain ownership (Data platform lead)
- All 9 contracts above

---

### Track 2 — Master Data Loading Pipeline

Load the 9 reference CSV files from `docs/reviews/2026-06-29-ama-capacity-metadata-review/`
into the `gold/reference/` schema via a validated Fabric Spark notebook pipeline.

#### 2.1 Source files

| Source file | Target table | FK dependencies |
| ------------- | ------------- | ----------------- |
| `01_dim_hospital.csv` | `dim_hospital` | — (root) |
| `02_dim_specialty.csv` | `dim_specialty` | `dim_hospital` |
| `03_dim_hospital_service.csv` | `dim_hospital_service` | `dim_hospital`, `dim_specialty` |
| `04_dim_disease.csv` | `dim_disease` | — |
| `05_dim_treatment.csv` | `dim_treatment` | `dim_disease` |
| `06_dim_drg.csv` | `dim_drg` | `dim_disease` |
| `07_dim_ward_capacityunit.csv` | `dim_ward_capacityunit` | `dim_hospital`, `dim_specialty` |
| `08_fact_capacity_baseline.csv` | `fact_capacity_baseline` | `dim_hospital` |
| `09_map_disease_treatment_specialty_service.csv` | `map_disease_treatment_specialty_service` | all dims |
| `SwissHospital_MasterData.xlsx` | Reference only | — (source of truth for any manual gap-fill) |

#### 2.2 Loading notebooks (Fabric Spark, PySpark)

Create the following notebook pipeline under `data-platform/notebooks/`:

```text
data-platform/notebooks/
└── reference/
    ├── 01_load_master_data_bronze.ipynb   # CSV → bronze/master-data/
    ├── 02_validate_master_data_silver.ipynb # bronze → silver (type, quality, FK checks)
    └── 03_publish_master_data_gold.ipynb   # silver → gold/reference/ (add governance cols)
```

**Notebook 01 — Bronze ingestion:**
- Source: CSV files from OneLake landing zone (uploaded from `docs/reviews/…/*.csv`)
- Action: ingest as-is into `bronze/master-data/<table>/` in Delta format
- Governance column: `_lineage_ref` = `<filename>:<load_timestamp>`

**Notebook 02 — Silver validation (fail-fast gates):**

| Gate | Check | Fail action |
| ------ | ------- | ------------- |
| Row count | `count > 0` per table | Abort run, log error |
| No null keys | Primary key columns not null | Abort run |
| FK integrity | All FK values exist in parent dim | Log missing FK rows, abort if > 5% |
| Data quality | `data_quality` in {explicit, inferred, missing} | Abort run |
| Residency | `residency_tag` in {`CH-North`, `US-West`} — dual-mode per [ADR-0013](../adr/0013-temporary-us-region-demo-scope.md) | Abort run |
| No PII | No columns matching PII pattern (email, phone, DOB) | Abort run |

**Notebook 03 — Gold publication:**
- Append mandatory governance columns (`_classification`, `_residency_tag`, etc.)
- Write to `gold/reference/<table>/` in Delta format with `overwrite` mode (idempotent)
- Update `_lineage_ref` with silver-to-gold transformation timestamp
- Emit load summary (row counts, quality distribution) to Log Analytics

#### 2.3 Validation CLI

Add a standalone Python script `data-platform/scripts/validate_reference_load.py`
that reads from `gold/reference/` and asserts:
- All 9 tables present
- Row counts match expected minimums (from design spec)
- FK graph is consistent across all tables
- `_data_quality` distribution reported (explicit %, inferred %, missing %)

Run as part of SIT gate before semantic model publication.

---

### Track 3 — Simulation Extensions

Extend the real-time capacity simulation service in `apps/sim-capacity/` to
generate DRG- and specialty-weighted episode streams based on the reference
dimension tables loaded in Track 2.

#### 3.1 Current simulation state

The Sprint 08 simulation generates `HospitalisationEpisode` records with:
- Random specialty (uniform distribution)
- Fixed LOS distribution (single Gaussian, not DRG-aware)
- No hospital-specific calibration

#### 3.2 Target simulation state

The extended simulation generates episodes where:
- **Hospital selection** is weighted by `dim_hospital.stationary_cases_yr`
- **Disease/specialty** is sampled from `dim_specialty` × `dim_ward_capacityunit.bed_count`
  (proportional to capacity allocation)
- **DRG assignment** uses `map_disease_treatment_specialty_service.drg_code`
  (each disease has a mapped DRG)
- **LOS** is sampled from `Poisson(λ = dim_drg.mean_los_norm)` (realistic
  length-of-stay distribution)
- **Ward routing** assigns the episode to the correct `dim_ward_capacityunit`
  based on `specialty_id` match

#### 3.3 New simulation components

```text
apps/sim-capacity/src/
├── reference/
│   ├── loader.py           # Loads dims from gold/reference/ via OneLake SDK
│   ├── probability_tables.py # Builds weighted sampling tables at startup
│   └── hospital_presets.py   # USZ, LUKS, SZB preset configurations
├── generators/
│   ├── demand_generator.py   # Extended: uses probability_tables
│   └── drg_los_sampler.py    # New: Poisson sampler over dim_drg.mean_los_norm
└── tests/
    ├── test_reference_loader.py    # Unit tests for dim table loading
    ├── test_probability_tables.py  # Tests for weighted sampling distribution
    └── test_drg_los_sampler.py     # Tests for LOS distribution shape
```

#### 3.4 Hospital presets

| Preset | Hospital | Daily admission rate | ED arrival rate/hr | Specialties |
| -------- | ---------- | --------------------- | ------------------- | ------------- |
| `USZ` | Universitätsspital Zürich | ~113/day | ~5.1/hr | ~27 |
| `LUKS` | Luzerner Kantonsspital | ~137/day | not published (use proxy) | ~27 |
| `SZB` | Spital Zollikerberg | ~30/day | not published | ~25 |

Hirslanden (`HSL`) is excluded from simulation presets in Sprint 09 due to
insufficient bed/OR data (all 🔴 missing). Add as Sprint 10 item when
provider data becomes available.

#### 3.5 Simulation test requirements

- Unit tests must cover DRG LOS sampler: `mean(samples) ≈ mean_los_norm ± 5%`
- Integration test: run 100 episodes per hospital preset, assert specialty
  distribution is within ±15% of expected weights
- No test should require live Fabric connectivity (mock the reference loader)

---

### Track 4 — Microsoft Fabric Data Platform + Power BI Dashboard

Publish the `gold/reference/` star schema as a Power BI semantic model and
build the 4-page Capacity Dashboard.

#### 4.1 Fabric semantic model

Create a Power BI semantic model (`CapacityPlatform.SemanticModel`) from the
`gold/reference/` Delta tables using Fabric's Direct Lake connection mode.

> **Sprint 00 environment note (2026-07-02):** F2 SKU (`fabricihzhhpfsit`) in `westus2` supports Direct Lake and is proven end-to-end via the Sprint 00 `gold.demand_encounter` lakehouse-direct load. **Capacity is currently Paused** for cost hygiene; resume with `az resource invoke-action ... --action resume` before running any dashboard smoke test. **Semantic model creation path:** follow **Approach A** — author the semantic model in Power BI Desktop / Fabric portal first, export TMDL via REST `getDefinition`, then automate future updates via REST `updateDefinition`. Do **not** hand-author `dataSources.tmdl` for Direct Lake until the TMDL grammar reference is available (Sprint 00 follow-up #1).

**Star schema:**

```text
fact_capacity_baseline (central fact)
├── dim_hospital         (hospital_id)
├── dim_specialty        (specialty_id)  [via dim_hospital_service bridge]
├── dim_ward_capacityunit (ward_id)
└── [via map table]
    ├── dim_disease      (disease_id)
    ├── dim_treatment    (treatment_id)
    └── dim_drg          (drg_code)
```

**Calculated DAX measures:**

| Measure | Formula |
| --------- | --------- |
| `Occupancy %` | `DIVIDE([Census], [Total Beds]) * 100` |
| `Beds Free` | `[Total Beds] - [Census]` |
| `LOS Efficiency` | `DIVIDE([Actual LOS], [DRG Norm LOS])` |
| `ED Arrivals/hr` | `DIVIDE([ED Visits/Day], 24)` |
| `Daily Discharge Rate` | `[Discharges/Day]` |
| `Data Quality Score` | `% explicit rows out of total` |

**Governance:** All measures include a `Data Quality` tooltip sourced from
`_data_quality` column — visuals must display "⚠ Inferred" or "⛔ Missing"
badges for non-explicit data points.

#### 4.2 Power BI report — 4-page Capacity Dashboard

##### Page 1 — Hospital Overview

| Visual | Fields | Purpose |
| -------- | -------- | --------- |
| KPI cards (4×) | Occupancy % per hospital | At-a-glance current state |
| Bar chart | Beds Free by hospital | Capacity availability |
| Line chart | Daily admissions + discharges (7-day trend) | Throughput trend |
| Treemap | ED arrivals by hospital | Emergency load distribution |
| Slicer | Care level (tertiary / regional / specialised) | Filter by hospital type |
| Data quality badge | % explicit per hospital | Transparency |

##### Page 2 — Specialty Drilldown

| Visual | Fields | Purpose |
| -------- | -------- | --------- |
| Matrix | Specialty × Hospital → Occupancy % | Cross-hospital specialty comparison |
| Heat map | Specialty occupancy (colour-coded) | Identify overloaded specialties |
| Bar chart | Avg LOS vs DRG norm LOS | LOS efficiency by specialty |
| Donut | Case-mix by DRG cost weight band | Revenue/complexity mix |
| Slicer | Hospital selector | Focus on single provider |

##### Page 3 — Ward & Bed State

| Visual | Fields | Purpose |
| -------- | -------- | --------- |
| Bar chart (stacked) | Bed count by unit type (ICU/IMC/normal/ED/OR) | Structural capacity |
| Gauge | Ward occupancy % per ward | Individual ward load |
| Table | Ward, specialty, bed count, quality flag | Operational detail |
| Conditional formatting | Red > 90%, amber 75–90%, green < 75% | Visual alert |
| Data quality flag | Inferred/missing bed counts highlighted | Transparency |

##### Page 4 — LOS & Discharge Readiness

| Visual | Fields | Purpose |
| -------- | -------- | --------- |
| Box plot / violin | LOS distribution vs DRG norm by specialty | Discharge efficiency |
| Bar chart | Avg LOS gap (actual − norm) by specialty | Delay hotspots |
| Table | DRG, mean norm LOS, simulation avg LOS, deviation | Reference table |
| KPI | % episodes within DRG norm LOS | Discharge performance |
| Placeholder | Discharge blocker categories (Sprint 10) | Roadmap indicator |

#### 4.3 Report deployment

The Power BI report is deployed to the Fabric workspace provisioned in Sprint 08.

| Artefact | Location |
| ---------- | ---------- |
| Semantic model | Fabric workspace → `CapacityPlatform.SemanticModel` |
| Report file | `data-platform/reports/capacity-dashboard.pbix` |
| Deployment script | `data-platform/scripts/deploy_report.ps1` |

Access model: Hospital operations staff (read-only viewer role on Fabric workspace).
No PII exposure — all visuals use aggregated operational data only.

---

## Deliverables

| # | Deliverable | Track | Definition of Done |
| --- | ------------- | ------- | -------------------- |
| D1 | `gold/reference/` schema with 9 Delta tables populated | T2 | All validation gates pass; row counts match minimums |
| D2 | 3 Fabric Spark notebooks (`01_bronze`, `02_silver`, `03_gold`) | T2 | Notebooks run end-to-end in SIT; no errors; load summary emitted |
| D3 | `validate_reference_load.py` validation script | T2 | Script passes against live `gold/reference/` data |
| D4 | `docs/DATA.md` updated with 9 new data contracts | T1 | PR approved; version bumped to 0.6.0 |
| D5 | Simulation `reference/` module (loader + probability tables + presets) | T3 | Unit tests pass; integration test passes for USZ, LUKS, SZB presets |
| D6 | Simulation `drg_los_sampler.py` | T3 | LOS distribution mean within ±5% of DRG norm for each preset |
| D7 | `CapacityPlatform.SemanticModel` published to Fabric | T4 | Direct Lake connected; all measures calculable |
| D8 | 4-page Power BI Capacity Dashboard | T4 | All 4 pages render with real data; data quality badges visible |
| D9 | Sprint 09 SIT pipeline green | All | SIT run passes all gates including reference load and report smoke test |

---

## Success Criteria

1. The 9 master data dimension tables are loaded in `gold/reference/` with correct
   FK relationships and governance tags, and the validation script exits 0.
2. The simulation generates episode streams where the LOS distribution per DRG
   matches the mean LOS norm within ±5% over 1,000 episodes.
3. The Power BI dashboard renders Hospital Overview and Specialty Drilldown pages
   with live data from the semantic model, including data quality badges.
4. All 9 data contracts are registered in `docs/DATA.md`.
5. No PII is present in any `gold/reference/` table (validated by pipeline gate).
6. All CI checks pass: markdown lint, Bicep validate, Python unit tests.

---

## Out of Scope for Sprint 09

The following items are intentionally deferred:

| Item | Reason | Target sprint |
| ------ | -------- | --------------- |
| Hirslanden (HSL) simulation preset | Missing bed/OR data | Sprint 10 (after provider data) |
| Discharge blocker categories in dashboard | Requires operational feed | Sprint 10 |
| Real-time ward state streaming on Power BI dashboard | Sprint 08 streaming path must first stabilise | Sprint 10 |
| AI/ML demand forecasting integration | Separate model training sprint | Sprint 11 |
| Multi-provider data pooling | Out of MVP scope per ADR-0001 | Post-MVP |
| DRG data from KIS/provider source | Public data only in Sprint 09 | Sprint 10+ |

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
| ------ | ------------ | -------- | ------------ |
| Fabric Direct Lake mode not available on F2 SKU in `westus2` | Low | High | **Resolved 2026-07-02 (RB-03)**: F2 verified end-to-end via Sprint 00 `gold.demand_encounter` load. Fall-back to Import mode remains available if performance regresses. |
| Some ward bed counts are inferred (not explicit) | High | Medium | Expose `_data_quality` badge; use `beds_quality` flag in Power BI tooltips; document limitation |
| Simulation LOS distribution diverges from norm for small specialties | Medium | Low | Increase minimum episode count per specialty to 30 in integration test |
| Sprint 08 bronze/silver notebook pipeline still deferred | Medium | Medium | **Updated 2026-07-02 (RB-02, RB-12)**: interim path is Sprint 00 lakehouse-direct CSV load; Track 1 (contracts) and Track 3 (simulation unit tests) proceed independently; Track 2 notebook pipeline is best-effort until Sprint 08 restart. |
| TMDL grammar for Direct Lake `dataSources` not yet documented | Medium | Medium | **Added 2026-07-02 (RB-13)**: use Approach A (portal-authored TMDL export as reference) per Sprint 00 follow-up #1; REST-based automation only for updates, not creation. |
| Fabric F2 capacity billing while paused-only-when-remembered | Medium | Low | **Added 2026-07-02**: cost-hygiene runbook step — pause via `az resource invoke-action ... --action suspend` when idle; resume before smoke test. Currently Paused. |

---

## Dependencies and Prerequisites

| Prerequisite | Owner | Status |
| ------------- | ------- | -------- |
| Sprint 08 bronze/silver notebook pipeline in SIT | Platform lead | **Deferred (2026-07-02)**: interim path is Sprint 00 lakehouse-direct CSV load; sprint may proceed against `gold/reference/` via lakehouse-direct if notebook pipeline is not delivered in time. |
| Fabric F2 capacity (`fabricihzhhpfsit`) available (unpaused) | Platform lead | **Available on demand (2026-07-02)**: currently Paused for cost hygiene; resume via `az resource invoke-action` before dashboard smoke test. |
| Fabric workspace + lakehouse provisioned | Platform lead | ✅ delivered by Sprint 00: `ws-ihzhhpf-sit-data` + `lh_ihzhhpf_sit` |
| `gold.demand_encounter` populated | Data platform | ✅ delivered by Sprint 00: 3 rows via lakehouse-direct load (G2.2 spirit-met) |
| Source SQL for master-data loader | Data platform | **Blocked (2026-07-02)**: MCAPS regional restriction on Azure SQL in `westus2`; Bicep ready — flip `enableSourceSqlModule=true` when unblocked. |
| Review CSV files committed to repo | Done | ✅ recovered onto `main` 2026-07-02 (PR #81) |
| `gold/reference/` schema design approved | Solution owner | ✅ per this sprint plan |

---

## Definition of Done (Sprint)

- [ ] All 9 deliverables (D1–D9) completed and verified
- [ ] `docs/DATA.md` updated with 9 new data contracts (version 0.6.0)
- [ ] Simulation unit + integration tests pass in CI (`python -m pytest apps/sim-capacity/tests/ -q`)
- [ ] Power BI dashboard deployed to Fabric workspace and accessible to viewer role
- [ ] Validation script `validate_reference_load.py` exits 0 against SIT data
- [ ] SIT pipeline run passes all gates (markdown lint, Bicep validate, reference load gate, simulation smoke test)
- [ ] Sprint 09 document version updated to reflect completion status
- [ ] PR merged to `main` with full PR output contract fields populated

---

## Sprint Execution Model

Sprint 09 follows the **Superpowers Basic Workflow** (consistent with Sprints 07–08):

1. `brainstorming` → design spec (✅ complete: `2026-06-29-sprint09-master-data-capacity-dashboard-design.md`)
2. `writing-plans` → task breakdown per track (next step)
3. `test-driven-development` → tests written before implementation per track
4. `systematic-debugging` → applied to any failing gate or test
5. `verification-before-completion` → mandatory before marking sprint complete

Work packages are executed track-by-track. Recommended execution order:
1. Track 1 (DATA.md contracts) — no Fabric dependency, can start immediately
2. Track 3 (Simulation unit tests + code) — no Fabric dependency, can start immediately
3. Track 2 (Master data loading notebooks) — requires Fabric access (Sprint 08 prerequisite)
4. Track 4 (Semantic model + dashboard) — requires Track 2 complete

---

## Traceability

| Sprint 09 Item | Requirement ID |
| ---------------- | --------------- |
| 4-layer master data model | FR-DAT-001, FR-DAT-002 |
| DRG-weighted simulation | FR-SIM-001 |
| Power BI capacity dashboard | FR-VIZ-001, FR-VIZ-002 |
| Data quality transparency | NFR-GOV-003, NFR-GOV-006 |
| nDSG compliance (no PII) | NFR-SEC-002, NFR-COMP-001 |
| Data contracts | NFR-DAT-001 |
