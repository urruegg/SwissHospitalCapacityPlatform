# Curavias Organisation & Skills Ontology — Deliverables Index

| Field | Value |
| ----- | ----- |
| **Prepared for** | Urs Rüegg — Sr Solution Engineer Hub, Microsoft Switzerland (CH-STU-InnoHub) |
| **Objective** | Extend the existing Curavias ontology with **Organisation** (Departments, Specialisations, Workforce, Employee, Skills) to enable **evidence-based, skills-based matching** between workforce and demand/available capacity |
| **Date** | 19 July 2026 |
| **Status** | v1.0 — advisory, evidence-based, HITL-governed. All data fictitious/anonymized (Curavias demo). |

This package answers the four-step request end to end. Documents are Markdown; data is UTF-8 CSV.

---

## What was delivered (by step)

| Step | Outcome requested | Deliverable |
| ---- | ----------------- | ----------- |
| **1** | Detailed Ontology Model for skills-based matching (workforce ↔ demand ↔ capacity) | **`Step1-Curavias-Skills-Ontology-Model.md`** — organisation extension (Department, Specialisation, Workforce, Employee, Skill), classes/relations, the 4-stage matching engine, worked Curavias examples, Fabric IQ + FHIR realisation |
| **2** | Swiss skills/competency sources + required-skills list | **`Step2-Swiss-Skills-Competency-Sources-and-Required-Skills.md`** — tiered trusted-source catalogue (MedReg/GesReg/NAREG/PsyReg, SIWF, OdASanté, SRC, ESCO, FHIR…) + a 66-skill competency catalogue with a department→skills demand map |
| **3** | Solution Design: Curavias & Work-ID & Skills-Manager | **`Step3-Solution-Design-Curavias-WorkID-SkillsManager.md`** — integration architecture, consent-first identity/GLN bridge, ESCO crosswalk, connector modes, `DC-WORKID-SKILLS-v1`, bidirectional value, phased rollout |
| **4** | All master-data tables as CSV with detailed schema | **`Step4-Master-Data-Tables-Schema.md`** + **20 CSV files** in `master-data/` (schema, load order, supply/gap logic, OneLake load guidance) |

---

## The master-data tables (`master-data/`, 20 CSV files)

**Dimensions / reference:** `dim_tenant`, `dim_org_unit`, `dim_department`, `dim_specialisation`, `dim_occupation_role`, `dim_skill`, `dim_issuing_authority`, `dim_capacity_unit`, `dim_assurance_level`, `dim_proficiency_level`, `dim_workforce_position`, `dim_employee`.
**Facts / bridges:** `fact_skill_assertion`, `bridge_role_skill_demand_template`, `fact_skill_demand`, `fact_skill_gap`, `bridge_worker_unit_eligibility`.
**Work-ID / Skills-Manager integration:** `dim_work_id_profile`, `map_skill_crosswalk`, `fact_skills_manager_sync_log`.
**Generator:** `generate_master_data.py` reproduces all CSVs deterministically.

Sample scale: **3 tenants · 48 org units · 24 departments · 50 capacity units · 129 synthetic employees · 682 skill assertions · 134 demand & 134 gap rows · 138 eligibility rows.** Referential integrity verified (all foreign keys resolve; all person GLNs carry a valid GS1 check digit).

---

## How it all fits together

```
Demo-Hospitals-Master-Data (given)  ──▶  dim_tenant / dim_org_unit / dim_department      (organisation spine)
Step 2 competency catalogue         ──▶  dim_skill / dim_issuing_authority / dim_specialisation
Employees (synthetic)               ──▶  dim_employee / dim_workforce_position           (keyed on GLN)
Evidence model (assurance L0–L4)    ──▶  fact_skill_assertion                            (the atomic unit)
Matching engine (Step 1)            ──▶  fact_skill_demand → view_skill_supply → fact_skill_gap
                                                            └▶ bridge_worker_unit_eligibility
Work-ID / Skills-Manager (Step 3)   ──▶  dim_work_id_profile / map_skill_crosswalk / sync_log
```

---

## Key design decisions (the load-bearing ones)

1. **Extend, don't replace** — builds on the HCC North-Star ontology and the Curavias Evidence-Based Skills design; reuses their classes and adds the Organisation + Employee + Skill layer.
2. **Two orthogonal axes** — *proficiency* (1–5, how capable) and *assurance* (L0–L4, how proven) are never collapsed; demand gates on both.
3. **GLN golden thread** — one identifier joins HR ↔ federal registers ↔ FHIR `Practitioner`; every match is deterministic.
4. **Gold is deny-by-default** — only L2+ valid (L4 where legally required) counts as safety-critical supply.
5. **Work-ID / Skills-Manager sit below the federal evidence floor** — consent-gated source systems for breadth/discovery, never overriding the safety gate.
6. **No PHI, no performance ranking** — worker skills only; evidenced capability & currency, never an appraisal.

---

## Notes & things to confirm

- **ESCO / SIWF / SNOMED references** in the CSVs are readable **demo slugs** — replace with the real canonical URIs/IDs at load (see Step 4 §5).
- **GLNs** are fictitious demo values (valid check digit, not issued numbers).
- **Work-ID / Skills-Manager** product positioning is confirmed from public sources; the exact API/export surface, internal proficiency scale and skill taxonomy are **to confirm with Work-ID AG** (flagged in Step 3). The Microsoft Innovation Hub Schweiz already runs Skills-Manager — the natural pilot.
- All content is **advisory** and every downstream action remains **human-in-the-loop**.

---

*Prepared 19 July 2026 · builds on `HCC-North-Star-Ontology-Model-Analysis`, `Curavias-Evidence-Based-Skills-Ontology-Analysis-and-Design`, `Demo-Hospitals-Master-Data`, `05_evidence_taxonomy`, `04_knowledge_base_register`.*
