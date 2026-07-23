# WS-C2 - Missing demo master data (skills + care_setting)

| Field | Value |
| --- | --- |
| Sprint | 23 (issue #255) |
| Work stream | WS-C2 (skills + live-vs-simulated + bed-vs-ops care_setting) |
| Sequencing | Option 1 - gold-first (skills-gold transform PR, then measures PR) |
| Data class | Synthetic / no-PHI only |
| Location of existing CSVs | `data/master-data/curavias-org-skills/` |

## Summary

The skills domain is already rich. **Supply / demand / gap / eligibility (T6)
need no new data** - they are fully covered by the existing CSVs:

| Measure input | Existing table | Rows |
| --- | --- | --- |
| Supply | `fact_skill_assertion.csv` | 682 |
| Demand | `fact_skill_demand.csv` | 134 |
| Gap | `fact_skill_gap.csv` | 134 |
| Eligibility | `bridge_worker_unit_eligibility.csv` | 138 |
| Demand templates | `bridge_role_skill_demand_template.csv` | 106 |

Only **two features** lack source data:

1. **`care_setting` split (T14)** - report nursing (bed) vs medical (ops)
   skill gaps separately.
2. **Live-vs-simulated badge** - a measure that reads a real `source_mode`
   flag (never invented).

## Why care_setting must be explicit on demand + gap

`fact_skill_demand` and `fact_skill_gap` are **skill-grained**
(`tenant_id, department_id, unit_id, skill_id, shift_window`) and carry **no
occupation**. Cross-cutting skills such as `SK-BLS`, `SK-IPC`, `SK-DE-B2` are
required by **both** nurses and physicians, so a demand/gap row for such a
skill **cannot** be attributed to bed vs ops by derivation. Therefore
`care_setting_id` must be an **explicit column** on the demand and gap facts.

Everything else is derivable (see the last section) and needs no data from you.

## Items to provide

### 1. `dim_care_setting.csv` (NEW - static dimension)

Small, static. I can author this myself if you prefer - included here so the
contract is explicit.

```csv
care_setting_id,label_de,label_en,staff_group,description
bed,Bettenbezogen (Pflege),Bed-based (nursing),nursing,"Pflege-/Betreuungsbedarf gebunden an betriebene Betten (Pflegepersonal)"
ops,Betrieblich (aerztlich/spezialisiert),Operational (medical/specialised),medical,"Aerztlicher und spezialisierter Funktionsbedarf (Aerzte + spezialisierte Rollen)"
```

| Column | Type | Notes |
| --- | --- | --- |
| `care_setting_id` | string (PK) | `bed` or `ops` |
| `label_de` | string | German display label |
| `label_en` | string | English display label |
| `staff_group` | string | `nursing` or `medical` |
| `description` | string | Free text |

### 2. `fact_skill_demand.csv` - add 2 columns

Keep every existing column; append:

| New column | Type | Allowed values | How to populate |
| --- | --- | --- | --- |
| `care_setting_id` | string (FK -> `dim_care_setting`) | `bed` \| `ops` | The staff group this demand row models: a nursing slot -> `bed`; a physician / specialised slot -> `ops`. |
| `source_mode` | string | `live` \| `simulated` | `live` for seeded master data; the runtime simulator injects `simulated` rows. A realistic mix is welcome. |

Example (existing `DEM-0001` extended):

```csv
demand_id,tenant_id,department_id,unit_id,skill_id,min_proficiency,min_assurance,headcount_required,shift_window,effective_date,care_setting_id,source_mode
DEM-0001,CN,CN-D1,CN-D1-U02,SK-ACLS,3,L2,1,Tag,2026-07-19,ops,live
```

### 3. `fact_skill_gap.csv` - add the same 2 columns

Append `care_setting_id` and `source_mode`, consistent with the matching
demand row (same `tenant_id, department_id, unit_id, skill_id, shift_window`).

Example (existing `GAP-0001` extended):

```csv
gap_id,tenant_id,department_id,unit_id,skill_id,shift_window,headcount_required,valid_supply,gap,nearest_expiry_date,redeploy_candidates_count,computed_at,care_setting_id,source_mode
GAP-0001,CN,CN-D1,CN-D1-U02,SK-ACLS,Tag,1,0,1,,9,2026-07-19,ops,live
```

### 4. `fact_skill_assertion.csv` - add 1 column

Append `source_mode` (`live` \| `simulated`) for the supply-side badge.
`care_setting` is **not** needed here - it is derivable from the worker's
occupation.

| New column | Type | Allowed values | How to populate |
| --- | --- | --- | --- |
| `source_mode` | string | `live` \| `simulated` | `live` for HRIS / LMS / work_id seeded rows; simulator adds `simulated`. |

## Care_setting assignment guide (for populating demand + gap)

Use the occupation the demand models. Reference `dim_occupation_role` ISCO
codes:

| ISCO-08 | Occupations (examples) | `care_setting_id` |
| --- | --- | --- |
| 2212 | Physicians (anaesthetist, surgeon, cardiologist, ...) | `ops` |
| 2221 | Registered / ICU / anaesthesia / emergency nurse | `bed` |
| 2222 | Midwife | `bed` |
| 3211 | Radiographer, scrub / OR technician | `bed` |
| 3258 | Paramedic | `bed` |
| 2264 | Physiotherapist | `bed` |
| 1342 | Bed / OR / crisis manager, ward lead | `ops` |
| 2521 | Data / ontology steward | `ops` |

For a demand row whose skill is required by several occupations, pick the
care setting of the role the slot is actually staffing (e.g. an `SK-BLS`
demand on a ward nursing roster -> `bed`; an `SK-BLS` demand on an anaesthesia
physician roster -> `ops`).

## Derivable - no data needed from you

I will compute these in the gold transform (documented + unit-tested), so
please do **not** hand-produce them:

* **occupation -> care_setting** from `dim_occupation_role.isco_08_code` using
  the table above.
* **demand-template care_setting** - `bridge_role_skill_demand_template`
  already links each template to an occupation (`applies_to_type = occupation`
  for all 106 rows), so care_setting follows from the occupation.
* **supply / eligibility care_setting** - `dim_employee.primary_occupation_id`
  -> occupation -> care_setting.

## Delivery

* Drop the updated / new CSVs into `data/master-data/curavias-org-skills/`.
* UTF-8 (with or without BOM is fine - the gold reader uses `utf-8-sig`).
* Synthetic / no-PHI only.
* Once provided, I will build the skills-gold transform PR (TDD) first, then
  the TMDL + measures PR - each small, linked to #255, for your review + merge.
