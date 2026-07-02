# Design Spec — Sprint 09: Master Data Foundation, Simulation Enhancement & Capacity Dashboard

| Field | Value |
| ------- | ------- |
| **Version** | 1.0.1 |
| **Date** | 2026-07-02 |
| **Author** | GitHub Copilot (Brainstorming + Design), recovered by Urs Rüegg |
| **Status** | Historical draft — superseded by Sprint 09 §0 Refresh Backlog |
| **Previous Version** | 1.0.0 (2026-06-29 initial draft, unmerged on `hotfix/sit-disable-placeholder-modules` at commit `6424eff`) |
| **Source Review** | [docs/reviews/2026-06-29-ama-capacity-metadata-review.md](../../reviews/2026-06-29-ama-capacity-metadata-review.md) |
| **Depends on** | Sprint 08 completed; Fabric SIT pipeline green *(context stale — see banner)* |

> **⚠️ Recovery banner.** This spec was authored on 2026-06-29 and recovered
> onto `main` on 2026-07-02 without semantic changes. Two later events must be
> reconciled before this spec is used as a live design input:
>
> 1. **Sprint 00 tenant migration** — new tenant, `ihzhhpf` short name,
>    `westus2` demo carve-out per [ADR-0013](../../adr/0013-temporary-us-region-demo-scope.md).
> 2. **AMA HCC / North Star review** (2026-07-01) — adds MVO / Fabric IQ /
>    reference-layer OWL/RDF / crosswalk requirements; see
>    [§11 handoff](../../reviews/2026-07-01-ama-hcc-northstar-review.md#11-sprint-09-implementation-handoff).
>
> **Do not treat this spec as authoritative.** The authoritative refresh backlog
> lives in the sprint doc [§0](../../sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md#0--refresh-backlog-must-do-before-execution).

---

## 1. Problem Statement

Sprint 08 established the data pipeline skeleton (bronze/silver/gold in Fabric/OneLake) and the real-time simulation service. The 2026-06-29 AMA review session produced a concrete **9-table master data model** (4 reference hospitals, disease/DRG/specialty/ward dimensions, a capacity baseline fact) that is materially richer than what was available when Sprint 07–08 were designed.

Sprint 09 must integrate this model into the existing platform so that:
1. The simulation generates realistic, specialty- and DRG-weighted episode streams.
2. The Fabric gold layer exposes a proper star-schema semantic model for Power BI.
3. Hospital operations staff can view capacity state end-to-end in a Power BI dashboard.

---

## 2. Key Insights from AMA Review

### 2.1 Master Data Structure (9 tables)

| # | Table | Role | Row count (seed) |
| --- | ------- | ------ | ----------------- |
| 01 | `dim_hospital` | Reference hospital registry with org axis, care level, capacity proxies | 4 |
| 02 | `dim_specialty` | FMH-mapped specialties per hospital (hospital×specialty combinations) | ~100 |
| 03 | `dim_hospital_service` | Centre/institute-level services (Hirslanden-primary) | ~33+ |
| 04 | `dim_disease` | ICD-10-GM coded diseases with synonyms, acuity, body system | ~15+ |
| 05 | `dim_treatment` | CHOP-coded procedures with modality and care setting | ~15+ |
| 06 | `dim_drg` | SwissDRG codes with cost weight and mean LOS norms | ~15+ |
| 07 | `dim_ward_capacityunit` | Physical wards with specialty and bed count (some inferred) | ~20+ |
| 08 | `fact_capacity_baseline` | Derived capacity metrics per hospital (daily/hourly rates) | ~40+ |
| 09 | `map_disease_treatment_specialty_service` | Cross-mapping: disease → treatment → DRG → specialty → service → ward | ~30+ |

### 2.2 Hospital Axis Mismatch

Each hospital organises its data along a different primary axis:

| Hospital | Primary axis | Maps natively to |
| ---------- | ------------- | ----------------- |
| USZ | Disease-led | `Disease → Treatment` |
| LUKS | Disease-led (with synonym layer) | `Disease (+ synonyms[])` |
| Hirslanden | Centre/Institute-led | `Specialty/Center → HospitalService` |
| Zollikerberg | Specialty-led | `Specialty` |

**Design consequence:** `Disease`, `Specialty`, and `Center/Service` must be treated as separate linked entities. The `map_disease_treatment_specialty_service` table is the bridge.

### 2.3 Data Quality Tiering

Every row in the reference data carries an explicit quality flag:
- `explicit` — published on hospital website or in official statistics
- `inferred` — derived from published annual totals
- `missing` — not available from public sources; requires KIS/ADT feed

Sprint 09 preserves these flags as non-nullable metadata columns in the gold-ref schema. Missing data uses sentinel values, never NULLs in dimension keys.

---

## 3. Approach — Recommended Design (Option B)

### 3.1 Data Layer Architecture

```text
OneLake
├── bronze/       (raw CSVs ingested from source)
│   └── master-data/   ← NEW: 9 CSV files land here on first load
├── silver/       (validated, typed, deduped)
│   └── master-data/   ← NEW: cleaned dimension rows
└── gold/
    ├── patient-flow/  (existing: episodes, throughput, LOS)
    └── reference/     ← NEW: star-schema dims + capacity baseline fact
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

The `gold/reference/` schema is a **slow-changing reference tier** — loaded once, refreshed when master data is updated (not streamed). It is read by the semantic model and the simulation service.

### 3.2 Master Data Loading Pipeline

**Pattern:** Fabric Spark notebooks, reusing Sprint 08 bronze→silver→gold pipeline conventions.

**Load order** (respects foreign key dependencies):
1. `dim_hospital`
2. `dim_specialty` (FK → dim_hospital)
3. `dim_hospital_service` (FK → dim_hospital, dim_specialty)
4. `dim_disease`
5. `dim_treatment` (FK → dim_disease)
6. `dim_drg` (FK → dim_disease)
7. `dim_ward_capacityunit` (FK → dim_hospital, dim_specialty)
8. `fact_capacity_baseline` (FK → dim_hospital)
9. `map_disease_treatment_specialty_service` (FK → all dims)

**Validation gates** (fail-fast per table):
- Row count > 0
- No null values in key columns
- All FK values exist in parent dimension
- `data_quality` column present and in {explicit, inferred, missing}
- `residency_tag` = CH-North for all rows (nDSG compliance check)

### 3.3 Simulation Extension Design

**Current state:** `apps/sim-capacity/` generates generic `HospitalisationEpisode` records with random specialty and fixed LOS distributions.

**Extended design:**

```text
SimulationEngine (extends existing)
├── ReferenceDataLoader
│   ├── loads dim_hospital, dim_disease, dim_drg, dim_ward from gold/reference
│   └── builds weighted probability tables at startup
├── DemandGenerator (extended)
│   ├── hospital_weights: based on stationary_cases_yr
│   ├── disease_weights: based on historical case-mix per specialty
│   ├── drg_los_sampler: Poisson(mean_los_norm) per drg_code
│   └── ward_router: assigns episode to ward by specialty_id match
└── EpisodeEmitter (unchanged interface)
```

**New simulation parameters (per hospital preset):**

| Parameter | Source | Example (LUKS) |
| ----------- | -------- | --------------- |
| `daily_admission_rate` | `fact_capacity_baseline.stationary_discharges_yr / 365` | ~137/day |
| `ed_arrival_rate_hr` | `fact_capacity_baseline.ed_visits_hr` | derived |
| `specialty_distribution` | dim_specialty × dim_ward bed counts | weighted |
| `drg_los_mean` | `dim_drg.mean_los_norm` | per drg_code |

**Hospital presets:** `USZ`, `LUKS`, `SZB` (Hirslanden excluded — missing bed/OR data).

### 3.4 Power BI Star Schema & Dashboard Design

**Semantic model (published from gold/reference):**

```text
fact_capacity_baseline
    ├── dim_hospital        (hospital_id)
    ├── dim_specialty       (specialty_id)
    ├── dim_ward_capacityunit (ward_id)
    └── [bridge via map]   → dim_disease, dim_drg, dim_treatment
```

**Calculated measures:**
- `Occupancy %` = census / total_beds × 100
- `Beds Free` = total_beds − census
- `Avg LOS (actual vs norm)` = actual_LOS / dim_drg.mean_los_norm
- `ED Arrivals/hr` = ed_visits_day / 24
- `Discharge Rate` = discharges_day / total_beds

**Dashboard pages (4-page report):**

| Page | Scope | Key visuals |
| ------ | ------- | ------------- |
| Hospital Overview | All 4 hospitals | Bed occupancy % by hospital, admission/discharge rates, ED arrivals treemap |
| Specialty Drilldown | Per specialty per hospital | Specialty occupancy heat-map, LOS vs DRG norm, case-mix donut |
| Ward & Bed State | Ward level | Ward occupancy bar chart, bed-class breakdown (ICU/normal/ED), ward utilisation gauge |
| LOS & Discharge Readiness | Discharge planning | LOS distribution vs DRG norm, discharge delay reasons (from simulation), blocker categories |

---

## 4. Approach Comparison (for record)

| Track | Option A | Option B (chosen) | Option C |
| ------- | ---------- | ------------------- | ---------- |
| Master data loading | Python scripts, flat load | Spark notebooks, bronze→gold-ref (reuses Sprint 08 pattern) | Fabric Dataflow Gen2 visual ETL |
| Simulation | Hardcoded profiles | Loads dims from gold at runtime, DRG-weighted | Separate config files per hospital |
| Power BI schema | Flat reports on gold | Star schema semantic model from gold-ref | Composite DirectQuery+Import |
| Fabric layer | Add dims to existing gold | New `gold/reference/` schema, same lakehouse | New dedicated reference lakehouse |

**Rationale for Option B:** Reuses Sprint 08 notebook patterns (lower ramp-up cost), keeps the simulation as a genuine data consumer of the gold layer (validates the end-to-end data path), and avoids a new lakehouse resource (cost efficiency).

---

## 5. Data Contracts Added by Sprint 09

| Contract ID | Producer | Consumer | Table | Breaking change? |
| ------------- | ---------- | ---------- | ------- | ----------------- |
| DC-MASTER-01 | Master data loader | Semantic model, simulation | dim_hospital | No |
| DC-MASTER-02 | Master data loader | Semantic model, simulation | dim_specialty | No |
| DC-MASTER-03 | Master data loader | Semantic model | dim_hospital_service | No |
| DC-MASTER-04 | Master data loader | Semantic model, simulation | dim_disease | No |
| DC-MASTER-05 | Master data loader | Semantic model | dim_treatment | No |
| DC-MASTER-06 | Master data loader | Simulation, semantic model | dim_drg | No |
| DC-MASTER-07 | Master data loader | Simulation, semantic model | dim_ward_capacityunit | No |
| DC-MASTER-08 | Master data loader | Semantic model, dashboard | fact_capacity_baseline | No |
| DC-MASTER-09 | Master data loader | Semantic model | map_disease_treatment_specialty_service | No |

---

## 6. Governance & Compliance Notes

- All master data is `classification: Operational confidential` (no PHI).
- `residency_tag: CH-North` applies to all rows (data stays in Switzerland North region).
- `legal_basis: nDSG/KVG` applies — no special consent required for aggregated operational data.
- `data_quality` flags must be exposed in Power BI tooltips so consumers know when values are inferred.
- Missing data (🔴) must never be presented as real values in the dashboard — use a "Data pending" indicator.

---

## 7. Spec Self-Review

| Check | Result |
| ------- | -------- |
| No placeholders or TODOs | ✅ |
| No contradictions with Sprint 08 design | ✅ (extends, not replaces) |
| All FK dependencies captured in load order | ✅ |
| Governance attributes defined | ✅ |
| Scope clearly bounded (no PHI, no new Fabric resources) | ✅ |
| Simulation interface unchanged (existing tests remain valid) | ✅ |
| Power BI measures defined and derivable from available data | ✅ |

---

## 8. Transition

This spec transitions to the `writing-plans` skill for Sprint 09 task breakdown.
See: `docs/sprints/sprint-09-master-data-simulation-and-capacity-dashboard.md`
