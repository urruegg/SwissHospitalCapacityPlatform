# Step 4 — Master-Data Tables: Schema & Initial-Load Specification

### The full set of OneLake master-data tables (schema + sample CSVs) for the Curavias skills-ontology data product

| Field | Value |
| ----- | ----- |
| **Prepared for** | Urs Rüegg — Sr Solution Engineer Hub, Microsoft Switzerland (CH-STU-InnoHub) |
| **Deliverable** | Step 4 of 4 — *All master-data tables as CSV, with detailed schema* |
| **Realises** | The ontology from Step 1, the competency catalogue from Step 2, and the Work-ID / Skills-Manager integration from Step 3 |
| **Format** | 20 CSV files (UTF-8, comma-separated, header row) in `master-data/`; this document is the schema/dictionary |
| **Sample data** | 3 tenants · 48 org units · 24 departments · **129 synthetic employees** · 682 skill assertions · 134 demand rows · 134 gap rows · 138 eligibility rows |
| **Anonymisation** | **Employee names are synthetic/anonymized** (Swiss-plausible first/last-name pool, combined deterministically). Organisation structure, GLNs, cantons, roles, sources and evidence patterns are kept realistic. **All data is fictitious — for the Curavias demo only.** |
| **Determinism** | Generated with a fixed random seed; reference date = **2026-07-19**. Person GLNs carry a valid GS1 mod-10 check digit |
| **Status** | v1.0 — load-ready |
| **Date** | 19 July 2026 |

> **Conventions.** PK = primary key · FK = foreign key · `enum{…}` = closed value set · dates are ISO-8601 (`YYYY-MM-DD`); empty cell = null. **ESCO/SIWF/SNOMED references in the sample are readable demo slugs** (e.g. `esco:occupation/midwife`, `siwf:facharzt/kardiologie`) — replace them with the real canonical ESCO URIs / SNOMED CT IDs at load time (see §5). GLNs are fictitious demo values.

---

## 1. Table inventory & load order

Load dimensions before facts/bridges. The dependency order below is safe for an initial OneLake load.

| # | Table | Grain (one row per…) | Type | Depends on |
| - | ----- | -------------------- | ---- | ---------- |
| 1 | `dim_tenant` | hospital provider (Curavias instance) | dimension | — |
| 2 | `dim_org_unit` | organisation entity (org/legal/site/dept/gov) | dimension | dim_tenant |
| 3 | `dim_department` | clinical department (Fachbereich/Klinik) | dimension | dim_org_unit |
| 4 | `dim_specialisation` | clinical/nursing/technical specialisation | dimension | — |
| 5 | `dim_occupation_role` | occupation (ESCO/ISCO) | dimension | — |
| 6 | `dim_skill` | skill/competency concept | dimension | dim_issuing_authority |
| 7 | `dim_issuing_authority` | trusted source / issuer | dimension | — |
| 8 | `dim_capacity_unit` | ward/ICU/OR/ED bay/… | dimension | dim_department |
| 9 | `dim_assurance_level` | assurance level L0–L4 | reference | — |
| 10 | `dim_proficiency_level` | proficiency level 1–5 | reference | — |
| 11 | `dim_workforce_position` | budgeted establishment slot | dimension | dim_department, dim_occupation_role |
| 12 | `dim_employee` | employee (health worker), GLN-keyed | dimension | dim_department, dim_workforce_position, dim_occupation_role |
| 13 | `fact_skill_assertion` | worker × skill × evidence | fact | dim_employee, dim_skill, dim_issuing_authority |
| 14 | `bridge_role_skill_demand_template` | occupation/spec × required skill | bridge | dim_occupation_role, dim_skill |
| 15 | `fact_skill_demand` | capacity-unit × skill × shift window | fact | dim_capacity_unit, dim_skill |
| 16 | `fact_skill_gap` | demand − valid supply (computed sample) | fact (derived) | fact_skill_demand |
| 17 | `bridge_worker_unit_eligibility` | worker × unit "can staff now" (computed) | bridge (derived) | dim_employee, dim_capacity_unit |
| 18 | `dim_work_id_profile` | Work-ID consent link | dimension | dim_employee |
| 19 | `map_skill_crosswalk` | skill × external-vocabulary mapping | mapping | dim_skill |
| 20 | `fact_skills_manager_sync_log` | connector sync run | fact | — |

---

## 2. Column dictionaries

### 2.1 `dim_tenant` — the three Curavias instances
| Column | Type | Notes |
| ------ | ---- | ----- |
| `tenant_id` | string PK | `CN` · `CP` · `VT` |
| `tenant_subdomain` | string | `<hospital>.curavias.ch` |
| `tenant_name` | string | display name |
| `archetype` | string | hospital archetype |
| `primary_canton` | string | demo canton code |
| `beds_approx` | string | order-of-magnitude beds |
| `fte_approx` | string | order-of-magnitude FTE |
| `legal_form` | string | Rechtsform |
| `grounded_on` | string | real-world archetype the demo is modelled on |

### 2.2 `dim_org_unit` — the 48-entity organisation hierarchy
| Column | Type | Notes |
| ------ | ---- | ----- |
| `org_unit_id` | string PK | e.g. `CN-D7` |
| `tenant_id` | string FK→dim_tenant | |
| `entity_type` | enum{Hospital-Org,Hospital-Group,Legal-Entity,Governance-Body,Site,Department} | |
| `org_unit_name` | string | |
| `parent_org_unit_id` | string FK→dim_org_unit | null at root |
| `org_level` | int | depth from root (0 = hospital org) |
| `legal_form_or_role` | string | Rechtsform / role |
| `beds` | string | may be null |
| `fte_approx` | string | may be null |
| `location` | string | |
| `canton` | string | |
| `gln` | string(13) | fictitious demo GLN |
| `grounded_on` | string | real-world grounding |
| `is_active` | bool | |

### 2.3 `dim_department` — departments as a first-class concept
| Column | Type | Notes |
| ------ | ---- | ----- |
| `department_id` | string PK (= org_unit_id) | e.g. `CN-D7` |
| `tenant_id` | string FK→dim_tenant | |
| `site_id` | string FK→dim_org_unit | parent site/legal entity |
| `department_name` | string | |
| `medical_area` | string | normalised area (e.g. *Intensiv- & Notfallmedizin*) |
| `beds` | int? | |
| `planned_fte` | int? | establishment size |
| `cost_centre` | string | `CC-<department_id>` |
| `canton` | string | |
| `gln` | string(13) | |
| `grounded_on` | string | |

### 2.4 `dim_specialisation`
| Column | Type | Notes |
| ------ | ---- | ----- |
| `specialisation_id` | string PK | e.g. `SPEC-IPS-NURSE` |
| `specialisation_name_de` / `_en` | string | |
| `spec_type` | enum{medical_specialty,nursing_specialisation,therapy,technical} | |
| `anchor_source` | string | issuing body (SIWF, OdASanté, NAREG, GesReg…) |
| `esco_or_siwf_ref` | string | demo slug — replace with real reference |
| `related_skill_id` | string FK→dim_skill | anchor skill |

### 2.5 `dim_occupation_role`
| Column | Type | Notes |
| ------ | ---- | ----- |
| `occupation_id` | string PK | e.g. `OCC-ICU-RN` |
| `label_de` / `label_en` | string | |
| `isco_08_code` | string | ISCO-08 occupation code |
| `esco_occupation_uri` | string | demo slug — replace with real ESCO URI |
| `professional_register` | enum{MedReg,GesReg,NAREG,PsyReg,none} | which register licences it |
| `licence_assurance` | enum{L0..L4} | assurance of the licence gate |

### 2.6 `dim_skill` — the competency catalogue (66 rows)
| Column | Type | Notes |
| ------ | ---- | ----- |
| `skill_id` | string PK | e.g. `SK-ACLS`, `SK-NDS-IPS`, `SK-LIC-PHYS` |
| `label_de` / `label_en` | string | |
| `skill_category` | enum{clinical,technical,regulatory,language,leadership,digital} | |
| `skill_type` | enum{skill,knowledge,language,transversal} | ESCO pillar |
| `anchor_authority_id` | string FK→dim_issuing_authority | strongest evidence source |
| `default_min_assurance` | enum{L0..L4} | default assurance the anchor supports |
| `is_safety_critical` | bool | does it gate a safety-critical shift |
| `has_expiry` | bool | does the evidence expire |
| `typical_validity_months` | int | 0 = non-expiring |

### 2.7 `dim_issuing_authority` — trusted sources (28 rows)
| Column | Type | Notes |
| ------ | ---- | ----- |
| `authority_id` | string PK | e.g. `AUTH-MEDREG` |
| `authority_name` | string | |
| `authority_kind` | enum{federal_register,specialist_body,education,cert_body,language,research,foreign_recognition,taxonomy,labour_market} | |
| `base_assurance_level` | enum{L0..L4} | highest assurance the source can support |
| `gln_keyed` | enum{yes,no} | can it be joined on GLN |
| `jurisdiction` | string | CH / EU / INT / facility |
| `verify_reference` | string | public verify endpoint (informational) |

### 2.8 `dim_capacity_unit` — the demand side (50 rows)
| Column | Type | Notes |
| ------ | ---- | ----- |
| `unit_id` | string PK | e.g. `CN-D7-U01` |
| `department_id` | string FK→dim_department | |
| `tenant_id` | string FK→dim_tenant | |
| `unit_type` | enum{ICU,ED_bay,OR_slot,ward,delivery_room,dialysis_station,imaging,transport} | |
| `unit_name` | string | |
| `beds_or_slots` | int | capacity of the unit |
| `canton` | string | |
| `staffing_ratio_rule` | string | e.g. `1:1 / 1:2 (Betten:Pflege)` |
| `is_safety_critical` | bool | drives demand generation |

### 2.9 `dim_assurance_level` (L0–L4) & 2.10 `dim_proficiency_level` (1–5)
Small reference tables. `dim_assurance_level`: `assurance_level` PK, `name`, `evidence_source`, `verifiable`, `fit_for`. `dim_proficiency_level`: `proficiency_level` PK, `name`, `description`.

### 2.11 `dim_workforce_position` — the budgeted establishment (76 rows)
| Column | Type | Notes |
| ------ | ---- | ----- |
| `position_id` | string PK | `POS-<dept>-<occ>` |
| `tenant_id` | string FK | |
| `department_id` | string FK→dim_department | |
| `occupation_id` | string FK→dim_occupation_role | |
| `planned_fte` | decimal | budgeted FTE for the slot |
| `headcount_budget` | int | budgeted headcount |
| `shift_pattern` | enum{3-Schicht,Tagdienst} | |
| `is_vacant` | bool | |

### 2.12 `dim_employee` — synthetic health workers (129 rows)
| Column | Type | Notes |
| ------ | ---- | ----- |
| `employee_id` | string PK | `EMP-<tenant>-NNNN` |
| `worker_gln` | string(13) | **golden join** — GS1-valid demo GLN |
| `tenant_id` | string FK | |
| `home_department_id` | string FK→dim_department | |
| `position_id` | string FK→dim_workforce_position | establishment slot filled |
| `primary_occupation_id` | string FK→dim_occupation_role | |
| `given_name` / `family_name` | string | **synthetic/anonymized** |
| `employment_status` | enum{active,active_parttime,on_leave} | |
| `contract_fte` | decimal | |
| `hire_date` | date | |
| `primary_language` | string | e.g. `DE-C1` (CEFR) |
| `additional_languages` | string | `;`-separated CEFR tags |
| `canton` | string | |
| `work_id_ref` | string? | Work-ID pseudonymous ref (if opted in) |

### 2.13 `fact_skill_assertion` — the atomic unit (682 rows)
The evidence-based core. One row = *this worker holds this skill at this proficiency, evidenced by this, valid for this period, at this assurance*.
| Column | Type | Notes |
| ------ | ---- | ----- |
| `assertion_id` | string PK | `ASR-NNNNNN` |
| `worker_gln` | string(13) FK→dim_employee.worker_gln | golden join |
| `employee_id` | string FK→dim_employee | |
| `skill_id` | string FK→dim_skill | |
| `proficiency_level` | int 1–5 | *how capable* |
| `evidence_type` | enum{registration,diploma,certificate,signoff,experience,self_declared} | |
| `issuing_authority_id` | string FK→dim_issuing_authority | |
| `evidence_ref` | string | register/diploma/cert id (demo format) |
| `assurance_level` | enum{L0..L4} | *how proven* — the gate |
| `valid_from` | date | |
| `valid_until` | date? | null = non-expiring; **past date = expired = no supply** |
| `verification_status` | enum{unverified,self,issuer-confirmed,register-verified} | |
| `verified_at` | date | freshness of the check |
| `verification_source` | string | authority the check ran against |
| `jurisdiction_scope` | string | canton (L4 licence) / national / facility |
| `restrictions` | string? | MedReg-style Auflagen (mostly empty) |
| `source_system` | enum{HRIS,LMS,work_id} | lineage |
| `sensitivity_class` | enum{PII-personal} | DSG class (not PHI) |
| `consent_basis` | enum{employment_contract,worker_consent} | legal basis |

### 2.14 `bridge_role_skill_demand_template` — the demand templates (106 rows)
| Column | Type | Notes |
| ------ | ---- | ----- |
| `template_id` | string PK | |
| `applies_to_type` | enum{occupation,specialisation} | |
| `applies_to_id` | string FK→dim_occupation_role | (occupation rows in this sample) |
| `skill_id` | string FK→dim_skill | |
| `min_proficiency` | int 1–5 | |
| `min_assurance` | enum{L0..L4} | |
| `is_mandatory` | bool | mandatory = gates the shift |
| `rationale` | string | |

### 2.15 `fact_skill_demand` — skills demanded by capacity (134 rows)
| Column | Type | Notes |
| ------ | ---- | ----- |
| `demand_id` | string PK | |
| `tenant_id` / `department_id` | string FK | |
| `unit_id` | string FK→dim_capacity_unit | |
| `skill_id` | string FK→dim_skill | |
| `min_proficiency` | int | |
| `min_assurance` | enum{L0..L4} | |
| `headcount_required` | int | per-shift, realistic demo value |
| `shift_window` | enum{Tag,Nacht} | |
| `effective_date` | date | |

### 2.16 `fact_skill_gap` — demand − valid supply (134 rows, derived)
| Column | Type | Notes |
| ------ | ---- | ----- |
| `gap_id` | string PK | |
| `tenant_id` / `department_id` / `unit_id` | string FK | |
| `skill_id` | string FK→dim_skill | |
| `shift_window` | enum{Tag,Nacht} | |
| `headcount_required` | int | from demand |
| `valid_supply` | int | count of Gold, currency-valid, at-floor assertions in the dept pool |
| `gap` | int | `max(0, required − valid_supply)` |
| `nearest_expiry_date` | date? | soonest upcoming credential expiry in the pool (early-warning) |
| `redeploy_candidates_count` | int | same-tenant, other-department eligible holders |
| `computed_at` | date | |

> **How to read it.** A row with `gap>0` is an actionable shortfall; a row with `gap=0` but a near `nearest_expiry_date` is an early-warning (supply is about to drop). `redeploy_candidates_count` is the surge lever. In the sample there are **24 positive gaps** (e.g. a CuraNova ICU `SK-VENT` shortfall of 1 with a candidate to redeploy).

### 2.17 `bridge_worker_unit_eligibility` — can-staff-now (138 rows, derived)
| Column | Type | Notes |
| ------ | ---- | ----- |
| `eligibility_id` | string PK | |
| `employee_id` / `worker_gln` | FK→dim_employee | |
| `unit_id` | string FK→dim_capacity_unit | evaluated only for role↔unit-fitting staff |
| `tenant_id` | string FK | |
| `is_eligible` | bool | all mandatory unit skills valid & at floor |
| `limiting_factor` | string | e.g. `abgelaufen: SK-ACLS (2026-05-30)`, `unter Schwelle: SK-VENT`, `fehlt: SK-DIAL` |
| `nearest_cert_expiry` | date? | the worker's soonest expiring credential |
| `computed_at` | date | |

### 2.18 `dim_work_id_profile` — Work-ID consent link (50 rows)
| Column | Type | Notes |
| ------ | ---- | ----- |
| `work_id_profile_id` | string PK | |
| `employee_id` / `worker_gln` | FK→dim_employee | |
| `work_id_ref` | string | Work-ID pseudonymous id |
| `consent_status` | enum{granted,pending,revoked} | gate on linking/promotion |
| `visibility_scope` | string | e.g. `skills:all`, `skills:non-clinical`, `none` |
| `consent_basis` | enum{worker_consent} | |
| `last_sync_at` | date | |
| `profile_completeness_pct` | int | |
| `external_system` | enum{work_id} | |

### 2.19 `map_skill_crosswalk` — vocabulary reconciliation (66 rows)
| Column | Type | Notes |
| ------ | ---- | ----- |
| `crosswalk_id` | string PK | |
| `internal_skill_id` | string FK→dim_skill | |
| `esco_uri` | string | demo slug — replace with real ESCO URI |
| `snomed_code` | string? | to be mapped where clinical granularity needed |
| `skills_manager_skill_code` | string | vendor code **[confirm with Work-ID AG]** |
| `work_id_skill_label` | string | vendor label **[confirm]** |
| `mapping_confidence` | enum{high,medium,low} | only `high` may drive Gold promotion |

### 2.20 `fact_skills_manager_sync_log` — connector observability (18 rows)
| Column | Type | Notes |
| ------ | ---- | ----- |
| `sync_id` | string PK | |
| `run_ts` | datetime | |
| `direction` | enum{inbound,outbound} | |
| `source_system` / `target_system` | string | e.g. `skills_manager → curavias_bronze` |
| `record_type` | enum{skills_inventory,worker_share,skill_confirmation} | |
| `records_in` / `records_updated` / `records_rejected` | int | |
| `status` | enum{success,partial} | |

---

## 3. How the tables realise the ontology (crosswalk)

| Ontology class (Step 1) | Table(s) |
| ----------------------- | -------- |
| Tenant / HospitalOrganisation / LegalEntity / Site | `dim_tenant`, `dim_org_unit` |
| Department | `dim_department` |
| Specialisation | `dim_specialisation` |
| CapacityUnit | `dim_capacity_unit` |
| WorkforcePosition | `dim_workforce_position` |
| Employee / HealthWorker | `dim_employee` |
| OccupationRole | `dim_occupation_role` |
| Skill | `dim_skill` |
| SkillAssertion + EvidenceRecord + AssuranceLevel + ProficiencyLevel + ValidityPeriod | `fact_skill_assertion` (+ `dim_assurance_level`, `dim_proficiency_level`) |
| IssuingAuthority / TrustedSource | `dim_issuing_authority` |
| RoleSkillTemplate | `bridge_role_skill_demand_template` |
| SkillDemand | `fact_skill_demand` |
| SkillSupply (view) | *computed from* `fact_skill_assertion` (see §4) |
| SkillGap | `fact_skill_gap` |
| WorkerUnitEligibility | `bridge_worker_unit_eligibility` |
| WorkIdProfile | `dim_work_id_profile` |
| (crosswalk) | `map_skill_crosswalk`, `fact_skills_manager_sync_log` |

---

## 4. The supply/gap logic (reproducible in the lakehouse)

`view_skill_supply` is not shipped as a CSV because it is a **computed view**; the sample `fact_skill_gap` was produced with exactly this logic, which you can re-express in SQL/KQL over the loaded tables:

```sql
-- valid supply per (department, skill) as of the forecast date
SELECT a.home_department_id, a.skill_id, COUNT(*) AS valid_supply
FROM   fact_skill_assertion a
JOIN   dim_employee e ON e.worker_gln = a.worker_gln
WHERE  a.assurance_level >= :min_assurance          -- L2+ (Gold gate)
  AND (a.valid_until IS NULL OR a.valid_until >= :as_of)   -- currency
  AND  a.proficiency_level >= :min_proficiency
GROUP BY a.home_department_id, a.skill_id;

-- gap = demand.headcount_required − valid_supply  (floored at 0)
```

Promotion to **Gold** (deny-by-default) requires `assurance ≥ L2 AND now ∈ validity AND (legal roles) a matching L4 licence` — per `DC-SKILL-EVIDENCE-v1` (Step 1 §6).

---

## 5. Initial-load guidance for OneLake / Fabric IQ

1. **Landing.** Drop the 20 CSVs into a OneLake Bronze folder (`/bronze/skills-ontology/`). They are UTF-8 with a header row; use first-row-as-header, comma delimiter, quoted fields where present.
2. **Typing.** Cast per the dictionaries above (dates → `date`, bools `TRUE/FALSE` → boolean, `min_*`/counts → `int`, `*_fte` → `decimal`). Empty string → null.
3. **Keys & relationships.** Set the PKs listed; wire the FKs (Step 1 §7) as Fabric IQ relationship bindings. `worker_gln` is the golden join across `dim_employee` ↔ `fact_skill_assertion` and (in production) the federal registers.
4. **Replace demo references.** Swap the readable `esco:` / `siwf:` / demo `gln` slugs for real ESCO URIs, SIWF/register identifiers and issued GLNs. `snomed_code` is intentionally empty — populate where clinical-act granularity is needed.
5. **Entity vs time-series bindings.** Bind the dimensions as static (lakehouse); bind `fact_skill_assertion.valid_from/valid_until` as a **time-series** property so supply is always evaluated at a point in time (Step 1 §7).
6. **Governance.** Tag `fact_skill_assertion` and `dim_work_id_profile` as `PII-personal` (DSG); record `source_system` / `consent_basis` lineage in Purview; enforce the Gold gate before anything reaches `view_skill_supply`.
7. **Regenerate.** `generate_master_data.py` (shipped alongside) reproduces every CSV deterministically — adjust the `DEPT_PLAN`, catalogue lists, or `ARCH_DEMAND` to rescale the sample.

---

## 6. Data-quality expectations (what the DQ agent should see in this sample)

| Signal | In the sample | DQ rule it exercises |
| ------ | ------------- | -------------------- |
| Expired credentials in the pool | ~27 assertions past `valid_until` | Currency alarm |
| Near-expiry (≤30 d) | ~31 assertions | Expiring-credential sweep (SBA) |
| Positive skill gaps | 24 gap rows > 0 | Skill-gap alarm (SBA/CSA) |
| Blocked eligibility | 103 of 138 evaluated worker×unit pairs, with typed `limiting_factor` | Eligibility bridge |
| Assurance spread | L4≈124, L3≈57, L2≈317, L1≈130, L0≈44 | Assurance-floor gate |
| Consent states | granted / pending / revoked in `dim_work_id_profile` | Consent enforcement (Step 3) |
| GLN validity | 100 % valid GS1 check digits | Orphan-GLN / verification rule |

---

*Prepared 19 July 2026 · Step 4 of 4 · 20 UTF-8 CSVs + this schema · all data fictitious/anonymized, for the Curavias demo only.*
