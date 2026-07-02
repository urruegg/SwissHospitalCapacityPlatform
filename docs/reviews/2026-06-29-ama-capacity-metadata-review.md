<!-- markdownlint-disable MD060 MD033 -->
<!-- Recovered 2026-07-02 from hotfix/sit-disable-placeholder-modules (6424eff). -->
<!-- MD060 (compact table pipes) + MD033 (inline HTML for line breaks) are     -->
<!-- disabled file-locally: content preserved as authored on 2026-06-29.       -->

# Swiss Hospital Capacity Planning & Demand Forecasting — Metadata Framework

| Field | Value |
|---|---|
| Document | Structured metadata framework for hospital capacity planning & demand forecasting |
| Scope | Diseases & treatments · Specialties (Fachbereiche) · Capacity (stationary / ambulatory) |
| Platform | SwissHospitalCapacityPlatform (provider-internal, single-provider per deployment) |
| Reference hospitals | USZ, Hirslanden Klinik Hirslanden, Spital Zollikerberg, Luzerner Kantonsspital (LUKS) |
| Control unit | **Hospitalisation Episode** (not patient) — pseudonymised identifiers only, no PII |
| Aligns to | `docs/DATA.md` (v0.3.1), `docs/specs/…analysis.md`, `docs/PRD.md`, public-source sizing report |
| Author | Prepared for Urs Rüegg |
| Date | 2026-06-29 |

> **Reading convention used throughout**
> - 🟢 **Explicit** = published on the hospital website or in official statistics.
> - 🟡 **Inferred / derived** = computed from public annual totals or architectural assumption.
> - 🔴 **Missing** = not available from public sources; must be obtained from provider source systems (KIS/ADT/bed management).

---

## Section 1 — Metadata Framework (structured model)

The model is organised in **four metadata layers** plus a **forecasting feature layer**. Every entity carries governance tags consistent with `DATA.md` (classification, residency, legal basis, retention class) and uses **pseudonymised identifiers** — the planning layer never holds PII; the KIS identity layer stays separate.

### 1.1 Clinical metadata (the "what")
Describes *what is treated* and *how*, independent of any single hospital's site structure.

| Entity | Key attributes | Standard / code system | Class |
|---|---|---|---|
| `Disease` (Krankheitsbild) | disease_id, name, synonyms[], body_system, acuity (acute/chronic), is_emergency_relevant | ICD-10-GM | Operational confidential |
| `Treatment` (Behandlung) | treatment_id, name, modality (surgical/conservative/diagnostic/interventional), setting (inpatient/outpatient/day-case) | CHOP (Swiss procedure classification) | Operational confidential |
| `CarePathway` | pathway_id, disease_id→, ordered steps[], typical_LOS_band, expected_handoffs[] | IHE / local pathway | Operational confidential |
| `DRG` (case-mix) | drg_code, drg_description, cost_weight, mean_LOS_norm, inlier/outlier bounds | **SwissDRG** (acute) / TARPSY (psych) / ST Reha (rehab) | Operational confidential |
| `Specialty` (Fachbereich) | specialty_id, name, FMH discipline mapping, parent_division | FMH discipline taxonomy | Operational confidential |

### 1.2 Operational metadata (the "with what")
Describes the *physical and human capacity* that delivers treatments.

| Entity | Key attributes | Notes | Class |
|---|---|---|---|
| `Ward / Unit` (Station) | unit_id, name, specialty_id→, unit_type (normal/ICU/IMC/ED/OR/day-clinic) | maps beds to specialty | Operational confidential |
| `Bed` | bed_id, unit_id→, bed_class (acute/ICU/monitored), status (free/occupied/blocked/cleaning) | bed-state domain | Operational confidential |
| `StaffingPool` | pool_id, role (MD/RN/allied), shift_capacity, skill_tags[] | staffing & ops context | Operational confidential |
| `HospitalisationEpisode` | episode_id (pseudonymised), specialty_id→, drg_code→, admit_ts, discharge_ts, LOS, source (ED/elective/transfer) | **control unit** | PHI-sensitive |
| `Throughput` (derived) | admissions/day, discharges/day, ED arrivals/hr, occupancy %, census | aggregated metrics | Operational confidential |
| `LengthOfStay (LOS)` | actual_LOS, expected_LOS (DRG norm), delay_reason | feeds discharge AI | Operational confidential |

### 1.3 Planning metadata (the "when / why demand moves")

| Entity | Key attributes | Notes |
|---|---|---|
| `Seasonality` | season_profile_id, specialty_id→, weekly/monthly/annual index | e.g. winter respiratory, summer trauma |
| `DemandDriver` | driver_id, type (epidemic, weather, demographics, elective backlog, referral), elasticity | exogenous + endogenous |
| `ReferralPattern` | source_org, catchment, share_of_admissions, urgency_mix | inbound demand |
| `DischargeHandoff` | handoff_type (rehab/Spitex/nursing-home/transport), expected_lead_time, blocker_class | downstream constraint |
| `PlanningCheckpoint` | cadence (e.g. **daily by 10:30**, LUKS pattern), owner | operational rhythm |

### 1.4 Forecasting features (the "signals")

| Feature family | Example features | Source domain | Granularity |
|---|---|---|---|
| Time-series signals | ED arrivals (hourly), admissions, discharges, census, occupancy %, transfers | Patient flow / bed state | hour → 72h horizon |
| Calendar features | day-of-week, public holiday (cantonal), school holidays, weekend flag | external | hour/day |
| Seasonal/epidemic | influenza/RSV index, BAG Sentinella signals, heat-wave alerts | external (BAG/MeteoSwiss) | day/week |
| Capacity-state features | free beds by specialty, OR slot availability, staffing ratio | bed/staffing | hour |
| Lag/rolling features | lag-24h, lag-168h, 7-day rolling mean, trend, volatility | derived | hour |
| Discharge-readiness | expected-LOS gap, blocker flags, handoff lead-time | discharge coordination | per episode |
| External factors | demographics, weather, regional events, pandemic phase | external | day |

### 1.5 Cross-cutting governance attributes (every entity)
`classification` (PHI-sensitive / Operational confidential / Governance evidence) · `residency` (Switzerland North/West) · `legal_basis` (nDSG/KVG/EPDG tag) · `retention_class` (R1–R5) · `contract_id` (`DC-*`) · `lineage_ref` · `pseudonymisation_flag`.

---

## Section 2 — Per-hospital structure analysis (mapping site → model)

Each hospital exposes a **different primary organising axis**. Harmonising them is the core mapping challenge.

| Hospital | Primary axis (entry page) | Organising logic | Maps natively to | Granularity | Language |
|---|---|---|---|---|---|
| **USZ** | *Diseases & treatments* (Krankheitsbilder) | **Disease-led** — clinical pictures with symptoms + treatments; departments & centres behind | `Disease` → `Treatment` | High (disease level) | EN/DE |
| **LUKS** | *Was wir behandeln* | **Disease-led glossary** — alphabetical, rich **synonym lists** ("beinhaltet auch…") | `Disease` (+ `synonyms[]`) | High (disease + synonym) | DE |
| **Hirslanden (Klinik Hirslanden)** | *Centers and Institutes* | **Centre/Institute-led** — 33 centres at this clinic (group-wide 311) grouped by clinical theme | `Specialty`/`Center` → `HospitalService` | Medium (centre level) | EN/DE |
| **Spital Zollikerberg** | *Fachbereiche* | **Specialty-led** — ~25 specialist areas (department list) | `Specialty` directly | Medium (department level) | DE |

### 2.1 Detailed structure mapping

| Model entity | USZ | LUKS | Hirslanden | Zollikerberg |
|---|---|---|---|---|
| `Disease` | 🟢 explicit list of clinical pictures <cite>turn1search25</cite> | 🟢 explicit glossary + synonyms <cite>turn1search1</cite> | 🟡 implied via centre scope | 🟡 implied via Fachbereich |
| `Treatment` | 🟢 per disease page | 🟡 within disease page | 🟡 per centre | 🟡 per Fachbereich |
| `Specialty` (Fachbereich) | 🟢 departments/Kliniken <cite>turn1search30</cite> | 🟢 ~27 FMH disciplines (UZH catalogue) <cite>turn1search5</cite> | 🟢 centres/institutes <cite>turn1search11</cite> | 🟢 ~25 Fachbereiche <cite>turn1search17</cite> |
| `Center`/`Institute` | 🟢 e.g. Comprehensive Cancer Center <cite>turn1search24</cite> | 🟢 >100 Kliniken/Zentren <cite>turn1search3</cite> | 🟢 33 centres (clinic) <cite>turn1search11</cite> | 🟢 e.g. Brustzentrum, Augenzentrum <cite>turn1search17</cite> |
| `DRG`/case-mix | 🔴 not on web | 🔴 not on web | 🔴 not on web | 🔴 not on web |
| `Bed`/`Ward` count | 🟡 "additional beds" (no total) <cite>turn1search46</cite> | 🟢 **839–900 beds** <cite>turn1search3</cite><cite>turn1search2</cite> | 🟡 group-level only | 🟢 **174 beds** <cite>turn1search17</cite> |

### 2.2 Differences & gaps between hospitals

- **Axis mismatch:** USZ & LUKS are **disease-first**; Hirslanden is **centre-first**; Zollikerberg is **department-first**. A unified model must therefore treat *Disease*, *Specialty* and *Center* as **separate linked entities**, not interchangeable labels.
- **Synonym richness:** Only **LUKS** publishes a structured synonym layer ("Diese Seite beinhaltet auch…") — a ready-made gift for NLP entity-resolution and ICD mapping. <cite>turn1search1</cite>
- **Granularity:** USZ/LUKS expose **disease-level** detail; Hirslanden/Zollikerberg stop at **service/department** level → coarser demand cohorts.
- **Scale spread:** LUKS (839–900 beds, university tertiary) <cite>turn1search3</cite> vs Zollikerberg (174 beds, regional acute) <cite>turn1search17</cite> — two ends of the cohort-size spectrum, ideal for testing model transferability.
- **Bed transparency:** Only LUKS and Zollikerberg publish bed totals; USZ and Hirslanden do not (Hirslanden only group-level). <cite>turn1search13</cite>

---

## Section 3 — Capacity indicators (per hospital)

Capacity **proxies** are derived where explicit numbers are absent. Throughput/census figures use the public-source sizing report's method (`day = annual/365`, `census ≈ cases × ALOS/365`, acute ALOS ≈ 4.8–4.9). <cite>turn1search46</cite>

| Indicator | USZ | LUKS (Group) | Hirslanden (Klinik HSL) | Zollikerberg |
|---|---|---|---|---|
| Beds | 🔴 not published | 🟢 **839–900** <cite>turn1search3</cite><cite>turn1search2</cite> | 🟡 group ~ ; clinic n/a <cite>turn1search13</cite> | 🟢 **174** <cite>turn1search17</cite> |
| Specialties / Fachbereiche | 🟢 ~27 (UZH) <cite>turn1search30</cite> | 🟢 ~27; >100 Kliniken/Zentren <cite>turn1search5</cite><cite>turn1search3</cite> | 🟢 **33 centres** (clinic) <cite>turn1search11</cite> | 🟢 **~25** <cite>turn1search17</cite> |
| Stationary cases/yr | 🟢 **41,151** (≈41,138 discharges) <cite>turn1search46</cite> | 🟢 **>50,000** <cite>turn1search46</cite> | 🔴 clinic-level n/a | 🟢 **~11,000** <cite>turn1search19</cite> |
| Ambulatory/yr | 🟡 high (not exact) | 🟢 **>926,000** contacts <cite>turn1search46</cite> | 🔴 n/a | 🟢 **~60,000–70,000** <cite>turn1search19</cite> |
| ED visits/yr | 🟢 **45,000** <cite>turn1search46</cite> | 🔴 not published <cite>turn1search46</cite> | 🟡 24h A&E exists <cite>turn1search11</cite> | 🟡 24h Notfall <cite>turn1search22</cite> |
| Avg discharges/day | 🟡 **~113** <cite>turn1search46</cite> | 🟡 **>137** <cite>turn1search46</cite> | 🔴 | 🟡 **~30** (11k/365) |
| Avg active inpatient census | 🟡 **~541–553** <cite>turn1search46</cite> | 🟡 **>658** <cite>turn1search46</cite> | 🔴 | 🟡 **~145** (≈174 beds est.) |
| Staff | 🟡 large | 🟢 **~8,600** <cite>turn1search3</cite> | 🟡 group 13,796 <cite>turn1search15</cite> | 🟢 **~1,200** <cite>turn1search19</cite> |
| OR / birth rooms | 🔴 | 🟢 **55** <cite>turn1search3</cite> | 🔴 | 🟡 ICU+OR centre <cite>turn1search17</cite> |
| **Service-breadth proxy** | **Very high** (university, full spectrum) | **Very high** (tertiary, >100 units) | **High** (33 specialised centres) | **Medium** (regional acute, ~25 areas) |

### 3.1 Capacity-proxy ranking (service breadth)
**LUKS ≈ USZ (tertiary/university) > Hirslanden Klinik Hirslanden (33 specialised centres) > Spital Zollikerberg (regional acute, ~25 Fachbereiche).** Use **#specialties × #centres** as a service-breadth index, and **beds × ALOS-implied turnover** as a throughput-capacity index, until explicit bed/OR data is sourced.

### 3.2 Explicit capacity data that is missing → how to obtain it
| Missing item | Hospitals affected | How to obtain |
|---|---|---|
| Bed count by ward/specialty | USZ, Hirslanden (clinic) | KIS / bed-management export (ADT feed) |
| ED→inpatient conversion rate | all | ED system + ADT linkage |
| Monthly/seasonal ED time series | all | provider operational warehouse |
| OR slot capacity & utilisation | all except LUKS | OR scheduling system |
| Staffing ratios per ward | all | rostering/HR system |
| Rehab/Spitex/nursing-home handoff volumes | all | discharge coordination system (e.g. LUKiS) <cite>turn1search46</cite> |

---

## Section 4 — Unified mapping model

### 4.1 Chain: Disease → Treatment → Specialty → Hospital service → Capacity unit

```text
┌───────────┐   treats   ┌────────────┐  delivered_by  ┌────────────┐
│  DISEASE   │──────────▶│ TREATMENT   │──────────────▶│ SPECIALTY   │
│ (ICD-10)   │           │ (CHOP)      │               │ (FMH/Fachb.)│
└─────┬──────┘           └─────┬───────┘               └─────┬───────┘
      │ grouped_to              │ priced_by                   │ offered_as
      ▼                         ▼                             ▼
┌────────────┐           ┌────────────┐               ┌──────────────────┐
│ CarePathway│           │   DRG       │               │ HOSPITAL SERVICE │
│            │           │ (SwissDRG)  │               │ (Center/Institute│
└─────┬──────┘           └─────────────┘               │  /Department)    │
      │                                                 └─────┬────────────┘
      │ generates demand for                                  │ allocated_to
      ▼                                                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│   CAPACITY UNIT:  Ward/Unit  →  Bed  +  StaffingPool  +  OR slot      │
│   measured by:  occupancy %, census, LOS, throughput/day             │
└───────────────────────────┬──────────────────────────────────────────┘
                            ▼
            ┌───────────────────────────────────┐
            │  HospitalisationEpisode (control   │
            │  unit, pseudonymised) → feeds       │
            │  Forecasting + Discharge AI         │
            └───────────────────────────────────┘
```

### 4.2 Worked example (cross-hospital)

| Disease | Treatment | Specialty (Fachbereich) | Hospital service (per site) | Capacity unit |
|---|---|---|---|---|
| Brustkrebs / Breast cancer | Surgery + oncology pathway | Gynäkologie-Onkologie | USZ: Comprehensive Cancer Center <cite>turn1search24</cite> · LUKS: Tumorzentrum · HSL: Tumour Centre Zurich <cite>turn1search11</cite> · Zolliker.: Brustzentrum <cite>turn1search17</cite> | Oncology ward bed + OR slot |
| Stroke / Hirnschlag | Thrombolysis, stroke-unit monitoring | Neurologie | USZ: Stroke dept · HSL: **Stroke Center** <cite>turn1search11</cite> · LUKS: Neurozentrum | Monitored stroke-unit bed |
| Bandscheibenvorfall (disc herniation) | Spinal surgery | Wirbelsäulenchirurgie | LUKS: Spinal surgery <cite>turn1search1</cite> · Zolliker.: Wirbelsäulenchirurgie <cite>turn1search17</cite> · HSL: Spine centre <cite>turn1search11</cite> | Orthopaedic bed + OR |
| Geburt / Birth | Obstetric care | Geburtshilfe | Zolliker.: Geburtshilfe+Neonatologie <cite>turn1search17</cite> · LUKS: Frauenklinik · HSL: Maternity Unit <cite>turn1search11</cite> | Delivery room + maternity bed |

### 4.3 Canonical mapping keys
- `Disease.icd10` ↔ `DRG.drg_code` (many-to-one) — enables case-mix-weighted demand.
- `Treatment.chop` ↔ `Specialty.fmh` — routes procedures to capacity owners.
- `Specialty.id` ↔ `HospitalService.id` ↔ `Ward.specialty_id` — connects clinical demand to physical capacity.
- `HospitalisationEpisode.specialty_id + admit_ts` — the join key for **specialty-level 72h forecasting**.

---

## Section 5 — Standardised schema & data-collection recommendations

### 5.1 Standardised schema (reusable across all Swiss hospitals)

Aligned to `DATA.md` data contracts. JSON-ish field spec; every record carries the governance tags from §1.5.

```yaml
# --- CLINICAL LAYER ---
Disease:        {disease_id, name_de, name_en, synonyms[], icd10[], body_system, acuity, emergency_relevant:bool}
Treatment:      {treatment_id, name, chop[], modality, setting, disease_ids[]}
DRG:            {drg_code, description, cost_weight, mean_los_norm, los_low, los_high, system:[SwissDRG|TARPSY|ST-Reha]}
Specialty:      {specialty_id, name, fmh_discipline, parent_division}
CarePathway:    {pathway_id, disease_id, steps[], typical_los_band, handoffs[]}

# --- OPERATIONAL LAYER ---
HospitalService:{service_id, name, type:[center|institute|department], specialty_ids[], hospital_id}
Ward:           {unit_id, name, hospital_id, specialty_id, unit_type, bed_count}
Bed:            {bed_id, unit_id, bed_class, status, status_ts}
StaffingPool:   {pool_id, hospital_id, unit_id, role, shift_capacity, skill_tags[]}
HospitalisationEpisode: # CONTROL UNIT — pseudonymised, PHI-sensitive
                {episode_id, hospital_id, specialty_id, drg_code, admit_ts, discharge_ts,
                 los, admission_source:[ED|elective|transfer], discharge_blocker, residency_tag}

# --- PLANNING LAYER ---
DemandDriver:   {driver_id, type, value, valid_from, valid_to, source}
ReferralPattern:{source_org, hospital_id, specialty_id, share, urgency_mix}
DischargeHandoff:{handoff_id, episode_id, handoff_type, expected_lead_time, status}

# --- FORECASTING FEATURE STORE ---
CapacityTimeSeries: {hospital_id, specialty_id, ts(hour), ed_arrivals, admissions, discharges,
                     census, occupancy_pct, free_beds, staffing_ratio,
                     dow, holiday_flag, season_index, epidemic_index, weather_index,
                     lag_24h, lag_168h, roll_7d_mean, target_horizon:72h}
```

### 5.2 Suggested data contracts (extends `DATA.md` contract groups)
| Contract group | Example ID | Adds for this framework |
|---|---|---|
| Ingestion | `DC-ING-ADT-v1` | episode admit/discharge/transfer events |
| Curation | `DC-CUR-CAPACITY-v1` | specialty-level census & occupancy |
| Clinical reference | **`DC-REF-DISEASE-v1`** *(new)* | Disease↔ICD↔DRG↔Specialty crosswalk |
| AI feature | `DC-AI-FEATURES-v1` | the `CapacityTimeSeries` feature store |
| AI output | `DC-AI-FORECAST-v1` | 72h specialty forecast + run metadata |
| Integration | `DC-INT-DISCHARGE-v1` | handoff trigger/acknowledgement |

### 5.3 Governance & retention (from `DATA.md`)
- **Classification:** `HospitalisationEpisode` = PHI-sensitive (Swiss residency, strict RBAC); aggregated capacity = Operational confidential; logs = Governance evidence.
- **Retention:** R1 transient 30–90d · R2 analytics 13mo · R3 AI trace 24mo · R4 compliance 24–120mo · R5 legal hold. (Multi-year retention recommended for seasonality/drift learning, per sizing report.) <cite>turn1search46</cite>
- **Controls:** CH-C01 inventory/legal-basis · CH-C02 least-privilege · CH-C03 lineage/audit · CH-C05 residency gates.

### 5.4 Gaps & data-collection recommendations

| # | Gap | Inferred vs explicit today | Recommendation |
|---|---|---|---|
| 1 | No standard Disease↔ICD↔DRG crosswalk across sites | 🟡 inferred | Build `DC-REF-DISEASE-v1`; seed from LUKS synonym lists + ICD-10-GM / SwissDRG catalogues |
| 2 | Bed/ward counts missing for USZ & Hirslanden clinic | 🔴 missing | Pull from KIS/bed-management; until then use bed-proxy index |
| 3 | No public ED→inpatient conversion or monthly ED series | 🔴 missing | Acquire from ED/ADT during discovery; do **not** invent peaks |
| 4 | Heterogeneous site axes (disease vs centre vs department) | 🟢 explicit (structural) | Normalise via `HospitalService` ↔ `Specialty` mapping table per hospital |
| 5 | Discharge handoff volumes (rehab/Spitex/transport) unquantified | 🔴 missing | Instrument discharge system (LUKiS pattern, daily-10:30 checkpoint) <cite>turn1search46</cite> |
| 6 | Seasonality/epidemic signals not yet wired | 🟡 partial | Ingest BAG Sentinella + MeteoSwiss as external features |
| 7 | Staffing ratios per ward absent | 🔴 missing | Integrate rostering feed into `StaffingPool` |

### 5.5 Optimisation for the AI forecasting system
- **Forecast unit = `(hospital_id, specialty_id, hour)`** over a **72h horizon, hourly refresh** — matches the documented AI infusion point and sizing (≈10 specialty cohorts × 72 buckets × 24 refreshes). <cite>turn1search46</cite><cite>turn1search33</cite>
- **Cohort granularity** governed by site axis: disease-level where available (USZ/LUKS), specialty-level fallback (Hirslanden/Zollikerberg).
- **Two throughput classes** (per sizing report): high-volume scoring (all active inpatients ~4×/day) vs lower-volume downstream workflow triggers. <cite>turn1search46</cite>
- **Pseudonymisation-by-design:** forecasting/feature store uses `episode_id` only; PII re-linkage happens at the hospital endpoint at display time. <cite>turn1search36</cite>
- **Burst headroom 1.5×–2.0×** above average baseline; continuous (not batch-only) ingestion. <cite>turn1search46</cite>

---

### Source summary
Structures & figures drawn from: USZ Diseases & treatments <cite>turn1search25</cite> and departments <cite>turn1search30</cite>; LUKS *Was wir behandeln* glossary <cite>turn1search1</cite>, scale <cite>turn1search3</cite><cite>turn1search2</cite> and disciplines <cite>turn1search5</cite>; Hirslanden centres/institutes <cite>turn1search11</cite><cite>turn1search13</cite><cite>turn1search15</cite>; Spital Zollikerberg Fachbereiche & facts <cite>turn1search17</cite><cite>turn1search19</cite><cite>turn1search22</cite>; internal sizing & data-design baselines <cite>turn1search46</cite><cite>turn1search36</cite><cite>turn1search33</cite>.
