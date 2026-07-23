# Step 2 — Swiss Skills & Competency Sources + Required-Skills List for Curavias

### Trusted-source research and the detailed catalogue of skills/competencies required across the Curavias organisation

| Field | Value |
| ----- | ----- |
| **Prepared for** | Urs Rüegg — Sr Solution Engineer Hub, Microsoft Switzerland (CH-STU-InnoHub) |
| **Deliverable** | Step 2 of 4 — *Detailed list of possible skills & competency + trusted sources* |
| **Scope** | (a) the authoritative Swiss competency/registry sources, tiered by assurance; (b) the required-skills catalogue per Curavias department, role and specialisation |
| **Feeds** | `dim_skill`, `dim_issuing_authority`, `dim_occupation_role`, `dim_specialisation`, `bridge_role_skill_demand_template` (Step 4 CSVs) |
| **Assurance model** | L0–L4 ladder from `Curavias-Evidence-Based-Skills-Ontology-Analysis-and-Design`, cross-checked against the `official_swiss → private_unverified` evidence hierarchy in `05_evidence_taxonomy` |
| **Status** | Research v1.0 — sources confirmed against live public pages (July 2026) |
| **Date** | 19 July 2026 |

> **How to read the assurance mapping.** Each source is tagged with the assurance level it can support. This reconciles two schemes: the healthcare **L4→L0** ladder (federal register → self-declared) used by the Curavias evidence design, and the **official_swiss → private_unverified** hierarchy used in the Nutrition & Sport project's `05_evidence_taxonomy`. They agree on the essential point — *official/federal beats self-declared* — and the mapping column shows the correspondence.

---

## Part A — Trusted Swiss competency & registry sources

### A.1 The assurance ↔ evidence-hierarchy crosswalk

| Curavias assurance | Meaning | `05_evidence_taxonomy` equivalent | Fit for capacity |
| ------------------ | ------- | --------------------------------- | ---------------- |
| **L4** — federally registered / licensed | Public federal register, GLN-keyed; legal gate | *official_swiss* (registry tier) | Any safety-critical rostering; legal eligibility |
| **L3** — accredited diploma / specialist title | Issuer-verifiable diploma or eidg. title | *official_swiss* / *scientific* | Scope-of-practice, sub-specialty allocation |
| **L2** — issued dated certificate | Issuer + ID + **expiry** | *official_swiss* (cert) / *internal_approved* | Task competency **within validity window** |
| **L1** — manager sign-off / supervised log | Internal only | *internal_approved* | Refines currency; not a standalone gate |
| **L0** — self-declared / inferred | Unverifiable | *website_brand* / *private_unverified* | Discovery & suggestions only |

### A.2 Federal & national registries — the L4 backbone (verifiable, GLN-keyed)

| Source | Operator / legal base | Professions covered | Evidence exposed (public) | GLN-keyed |
| ------ | --------------------- | ------------------- | ------------------------- | --------- |
| **MedReg** — Medizinalberuferegister | BAG / MedBG (SR 811.11) | University medical professions: doctors, dentists, pharmacists, vets, chiropractors | Diploma; **Weiterbildungstitel** (specialisations); **language skills**; **cantonal practice licence** + restrictions; narcotics authorisation | **Yes — GLN is the person key** |
| **GesReg** — Gesundheitsberuferegister | GDK/CDS + Swiss Red Cross (SRK) / GesBG | Non-university, own-responsibility licence: **Pflege HF & BSc**, Physio, Ergo, **Hebamme**, Ernährung/Diätetik, Optometrie, Osteopathie | Name, **GLN**, UID, profession, diploma + country/date, registration no., recognition date, **practice licence** | **Yes** |
| **NAREG** — Nat. Register of Health Professions | GDK/CDS / IKV + SRK | Further HF titles: **Operationstechnik HF (scrub/TOA)**, **Radiologie HF (MTRA)**, **Rettungssanitäter HF (paramedic)**, biomed. analyst HF, Aktivierung HF, Logopädie, med. Masseur | Same public field set as GesReg | **Yes** |
| **PsyReg** | BAG / PsyG | Psychology professions (incl. clinical psychotherapy) | Diploma, federal Weiterbildungstitel, licence | Yes |

> **Why this is the backbone for capacity.** For exactly the roles Curavias staffs — ICU/ED/OR nursing, scrub techs, radiographers, paramedics, midwives and all physicians — an L4 record with a **cantonal practice licence** is both the *legal gate* and the *strongest supply signal*. Because all three registers publish the **GLN**, the employee's HR record joins to the federal evidence with no fuzzy matching (see the GLN golden thread, Step 1 §7).

### A.3 Specialist titles, sub-specialty & continuing education (L3, + currency)

| Source | What it certifies | Capacity relevance |
| ------ | ----------------- | ------------------ |
| **SIWF / ISFM** (under FMH) | ~45 federal **Facharzttitel** + Schwerpunkte; the *eidgenössischer Weiterbildungstitel* is the prerequisite for independent practice; runs the **CME/Fortbildung** logbook | Which physicians can cover which specialty demand; CME = currency |
| **Swiss medical societies** — SGAR (anaesthesia), SGI (intensive care), **SGNOR** (emergency medicine) | Sub-specialty / *Schwerpunkt* frameworks & fellowship credentials | Fine-grained surge competency (e.g. *Klinische Notfallmedizin*) |
| **OdASanté** (nat. OdA health) + **SBFI/SEFRI** | Competency profiles & eidg. anerkannte diplomas incl. **NDS HF Intensivpflege / Anästhesiepflege / Notfallpflege** | The single most capacity-critical nursing credentials — define who may staff ICU/OR/ED |
| **SBK/ASI eLog** | Nurses' CPD logbook (Fortbildungsnachweis) | Currency evidence for nursing competencies (L1→L2) |

### A.4 Education, VET & higher education (L3 diploma provenance)

| Source | Role |
| ------ | ---- |
| **SBFI/SEFRI** | Federal VET/PET diplomas (EFZ, eidg. Fachausweis, eidg. Diplom, HF); NQF levels; foreign non-health recognition |
| **EDK/CDIP** | Recognition of teaching & certain therapy diplomas (e.g. Logopädie) |
| **swissuniversities / swissdoc** | University & UAS (FH) degree provenance; ECTS |
| **Höhere Fachschulen (HF)** | Issue HF diplomas + NDS HF post-diploma specialisations |
| **berufsberatung.ch / SDBB** | Official occupation & competency descriptions (the *official_swiss* reference used in `05_evidence_taxonomy`) |

### A.5 Safety & life-support certificates (L2 — dated, expiring)

| Source | Certificate | Capacity relevance |
| ------ | ----------- | ------------------ |
| **SRC — Swiss Resuscitation Council** | **BLS-AED**, **ACLS/ALS**, **PALS**, ERC-aligned | Hard requirement for many ICU/ED/OR shifts; **expires** — currency-critical |
| **IVR-IAS** (Interverband für Rettungswesen) | Rescue-service / paramedic competency levels | ED & transport staffing |
| **BAG radiation protection** (Strahlenschutz) | *Strahlenschutz-Sachkunde* for staff using ionising radiation | Gate for interventional/radiology rostering |
| **Swissnoso-aligned IPC** | Infection-prevention & control competencies | Outbreak-scenario staffing (CSA) |
| **In-house device/skills passports** | Ventilator, ECMO, dialysis, specific pump sign-offs | Finest-grain competency; typically L1/L2 internal |

### A.6 Recognition of foreign diplomas (bridges non-CH evidence to L3/L4)

| Source | Role |
| ------ | ---- |
| **SRK — Swiss Red Cross** | Recognition of foreign **non-university** health diplomas → enables GesReg/NAREG entry |
| **MEBEKO** (BAG) | Recognition of foreign **university** medical diplomas → MedReg entry |
| **SBFI** | Recognition of foreign VET/PET diplomas (non-health) |

### A.7 Language competency (an under-rated capacity gate)

| Source | Evidence | Why it is capacity, not HR trivia |
| ------ | -------- | --------------------------------- |
| **fide** (Swiss language-competency system) + **CEFR**; telc / Goethe / DELF / CELI | DE / FR / IT proficiency A1–C2 | MedReg records language because a clinician cannot safely run a ward round or consent a patient without the local language at level. A genuine constraint on who can staff which ward/region |

### A.8 Publications & research evidence (L2/L3 — sub-specialty depth, never a gate)

| Source | Access | Evidence |
| ------ | ------ | -------- |
| **ORCID** | Persistent ID + public API | Authoritative person→publications link; clean join key |
| **PubMed / MEDLINE** | NCBI E-utilities API | Peer-reviewed output — depth in a clinical sub-field |
| **SNSF P3** | Public research DB | Funded projects / PI status — research leadership |
| **Institutional repositories** (ZORA, BORIS…) | OAI-PMH | Institution-verified outputs |
| Google Scholar / ResearchGate | Web | **Low trust** — discovery only (L0) |

> Publications evidence a physician's *sub-specialty depth*, useful for complex-case allocation — but never a currency or safety signal. They inform *preference ranking*, not *eligibility*.

### A.9 Taxonomy & interoperability rails (normalise & exchange)

| Rail | What it gives Curavias |
| ---- | ---------------------- |
| **ESCO** (EU Skills, Competences, Qualifications & Occupations) | Canonical skills taxonomy; ~13,939 skills; 28 languages incl. **DE/FR/IT**; occupations mapped to **ISCO-08**; open + API; per-skill metadata (type: knowledge/skill/language/transversal) |
| **HL7 FHIR R5** | Canonical data model for verified qualifications — `Practitioner` (identifier = GLN, `qualification` = code+issuer+period) + `PractitionerRole` (specialty, org, location) |
| **SNOMED CT** | Codes for procedures/competencies needing finer clinical granularity than ESCO |
| **ISCO-08** | Occupation backbone ESCO maps onto |
| **Work-ID / Skills-Manager** (Work-ID AG) | Swiss skills-based matching ecosystem — the individual skills passport (Work-ID) and company skills inventory (Skills-Manager); a *labour-market* skills source that **complements** the federal *evidence* sources (see Step 3). Assurance: skills held here are typically **L0–L1** (self-declared / employer-confirmed) until backed by a federal record |

---

## Part B — Required-skills catalogue for the Curavias organisation

The catalogue is organised in three tiers so it maps cleanly onto the ontology and the Step-4 tables:

1. **Skill categories** (the `skill_category` enum): `clinical · technical · regulatory · language · leadership · digital`.
2. **Cross-cutting skills** — required across most departments (life-support, IPC, language, safety, digital).
3. **Department/role-specific skills** — the capacity-critical competencies per Curavias department.

Each skill row carries: a stable `skill_id`, DE/EN labels, category, the **anchor evidence source**, the **assurance level** that source supports, and whether it is **safety-critical** (i.e. gates a shift). These become `dim_skill` + `bridge_role_skill_demand_template` in Step 4.

### B.1 Cross-cutting / foundational skills (most roles)

| skill_id | Skill (DE) | Skill (EN) | Category | Anchor source | Assurance | Safety-critical | Currency |
| -------- | ---------- | ---------- | -------- | ------------- | --------- | --------------- | -------- |
| SK-BLS | Basale Reanimation BLS-AED | Basic life support BLS-AED | clinical | SRC | L2 | Yes | expires ~2 y |
| SK-ACLS | Erweiterte Reanimation ACLS/ALS | Advanced life support ACLS | clinical | SRC | L2 | Yes | expires ~2 y |
| SK-PALS | Pädiatrische Reanimation PALS | Paediatric advanced LS | clinical | SRC | L2 | Yes | expires ~2 y |
| SK-IPC | Infektionsprävention & Hygiene | Infection prevention & control | clinical | Swissnoso / in-house | L1/L2 | Yes (outbreak) | annual refresh |
| SK-MEDADMIN | Sichere Medikamentenverabreichung | Safe medication administration | clinical | GesReg diploma + in-house | L3/L1 | Yes | stable |
| SK-DOC | Klinische Dokumentation (KIS) | Clinical documentation (HIS) | digital | in-house LMS | L1 | No | on system change |
| SK-DEESC | Deeskalation / Patientensicherheit | De-escalation / patient safety | clinical | in-house | L1 | No | periodic |
| SK-DE-B2 | Deutsch Stationssprache B2+ | German ward language ≥ B2 | language | fide / CEFR / MedReg | L2/L4 | Yes (region) | stable |
| SK-FR-B2 | Französisch B2+ | French ≥ B2 | language | fide / CEFR | L2 | region-dependent | stable |
| SK-IT-B2 | Italienisch B2+ | Italian ≥ B2 | language | fide / CEFR | L2 | region-dependent | stable |
| SK-DATA | Datenschutz DSG / Informationssicherheit | Data protection / infosec | regulatory | in-house | L1 | No | annual |

### B.2 Registration / licence anchors (L4 — the legal gates)

| skill_id | Anchor qualification | Register (L4) | Roles it gates |
| -------- | -------------------- | ------------- | -------------- |
| SK-LIC-NURSE | Pflegefachfrau/-mann HF or BSc Pflege — Berufsausübungsbewilligung | **GesReg** | all registered nurses |
| SK-LIC-MIDWIFE | Hebamme BSc — licence | **GesReg** | midwives |
| SK-LIC-OTA | Fachfrau/mann Operationstechnik HF | **NAREG** | scrub / OR techs |
| SK-LIC-MTRA | Fachfrau/mann Radiologie HF / BSc | **NAREG** | radiographers |
| SK-LIC-PARA | Rettungssanitäter/in HF | **NAREG** | paramedics |
| SK-LIC-PHYS | Eidg. Arztdiplom + cantonal Berufsausübungsbewilligung | **MedReg** | all physicians |
| SK-LIC-PHYSIO | Physiotherapeut/in HF/BSc — licence | **GesReg** | physiotherapists |
| SK-LIC-PSY | Psychotherapie — federal Weiterbildungstitel | **PsyReg** | clinical psychologists |

### B.3 Nursing specialisation skills (NDS HF — the capacity-critical core)

| skill_id | Skill (DE) | Category | Anchor source | Assurance | Safety-critical | Currency |
| -------- | ---------- | -------- | ------------- | --------- | --------------- | -------- |
| SK-NDS-IPS | NDS HF Intensivpflege | clinical | OdASanté / SBFI + HF school | L3 | Yes | diploma stable; +ACLS currency |
| SK-NDS-ANAES | NDS HF Anästhesiepflege | clinical | OdASanté / SBFI | L3 | Yes | +ACLS currency |
| SK-NDS-NOTF | NDS HF Notfallpflege | clinical | OdASanté / SBFI | L3 | Yes | +ACLS/PALS currency |
| SK-VENT | Beatmung / Ventilator-Management | clinical | in-house sign-off | L1/L2 | Yes | device sign-off |
| SK-HAEMO | Hämodynamisches Monitoring | clinical | NDS HF + in-house | L3/L1 | Yes | stable |
| SK-ECMO | ECMO-Betreuung | clinical | in-house sign-off | L1/L2 | Yes | sign-off cycle |
| SK-DIAL | Dialyse / Nierenersatzverfahren | technical | in-house + NDS | L1/L3 | Yes | device sign-off |
| SK-SCRUB | Perioperative Instrumentierung (Scrub) | clinical | NAREG OTA + procedure sign-offs | L4/L1 | Yes | stable |
| SK-TRIAGE | Notfall-Triage | clinical | NDS HF Notfall + in-house | L3/L1 | Yes | periodic |
| SK-OBST | Geburtshilfliche Betreuung | clinical | GesReg Hebamme | L4 | Yes | stable |
| SK-NEO | Neonatologische Pflege | clinical | NDS + in-house | L3/L1 | Yes | sign-off |
| SK-WOUND | Komplexes Wundmanagement | clinical | in-house / WundExperte | L1/L2 | No | periodic |
| SK-ONCO-NURSE | Onkologiepflege / Chemo-Handling | clinical | in-house + HöFa | L1/L2 | Yes (chemo) | periodic |

### B.4 Physician specialty skills (SIWF Facharzttitel + Schwerpunkte — L3, MedReg-gated L4)

| skill_id | Facharzttitel / Schwerpunkt (DE) | Anchor source | Assurance | Currency |
| -------- | -------------------------------- | ------------- | --------- | -------- |
| SK-FMH-ANAES | FMH Anästhesiologie | SIWF + MedReg | L3 + L4 | CME |
| SK-FMH-INTENS | Schwerpunkt Intensivmedizin | SIWF + MedReg | L3 + L4 | CME |
| SK-FMH-NOTF | Schwerpunkt Klinische Notfallmedizin | SGNOR / SIWF + MedReg | L3 + L4 | CME |
| SK-FMH-CARD | FMH Kardiologie | SIWF + MedReg | L3 + L4 | CME |
| SK-FMH-CARDSURG | FMH Herz- und thorakale Gefässchirurgie | SIWF + MedReg | L3 + L4 | CME |
| SK-FMH-NEURO | FMH Neurologie | SIWF + MedReg | L3 + L4 | CME |
| SK-FMH-NEUROSURG | FMH Neurochirurgie | SIWF + MedReg | L3 + L4 | CME |
| SK-FMH-ONCO | FMH Medizinische Onkologie | SIWF + MedReg | L3 + L4 | CME |
| SK-FMH-RADONC | FMH Radio-Onkologie | SIWF + MedReg | L3 + L4 | CME |
| SK-FMH-SURG | FMH Chirurgie (Viszeral) | SIWF + MedReg | L3 + L4 | CME |
| SK-FMH-ORTHO | FMH Orthopädie & Traumatologie | SIWF + MedReg | L3 + L4 | CME |
| SK-FMH-GYN | FMH Gynäkologie & Geburtshilfe | SIWF + MedReg | L3 + L4 | CME |
| SK-FMH-PAED | FMH Kinder- und Jugendmedizin | SIWF + MedReg | L3 + L4 | CME |
| SK-FMH-NEONAT | Schwerpunkt Neonatologie | SIWF + MedReg | L3 + L4 | CME |
| SK-FMH-INTMED | FMH Allgemeine Innere Medizin | SIWF + MedReg | L3 + L4 | CME |
| SK-FMH-RADIOL | FMH Radiologie | SIWF + MedReg | L3 + L4 | CME |
| SK-FMH-NUCMED | FMH Nuklearmedizin | SIWF + MedReg | L3 + L4 | CME |
| SK-FMH-NEPHRO | FMH Nephrologie | SIWF + MedReg | L3 + L4 | CME |
| SK-FMH-PALL | Schwerpunkt Palliativmedizin | SIWF + MedReg | L3 + L4 | CME |
| SK-FMH-OPHT | FMH Ophthalmologie | SIWF + MedReg | L3 + L4 | CME |

### B.5 Technical / diagnostic & radiation skills

| skill_id | Skill (DE) | Category | Anchor source | Assurance | Safety-critical |
| -------- | ---------- | -------- | ------------- | --------- | --------------- |
| SK-RADPROT | Strahlenschutz-Sachkunde | regulatory | BAG Strahlenschutz | L2 | Yes |
| SK-CT | CT-Bildgebung | technical | NAREG MTRA + in-house | L4/L1 | Yes |
| SK-MRI | MRT-Bildgebung | technical | NAREG MTRA + in-house | L4/L1 | Yes |
| SK-PETCT | PET-CT / SPECT-CT | technical | MTRA + FMH Nuklearmedizin | L4/L3 | Yes |
| SK-MAMMO | Mammographie / BrustCentrum | technical | MTRA + cert | L4/L2 | Yes |
| SK-LAB | Biomedizinische Analytik | technical | NAREG biomed. analyst HF | L4 | No |
| SK-PATH | Pathologie-Aufarbeitung | technical | in-house + diploma | L3/L1 | No |

### B.6 Leadership / operations skills (the agent-facing coordination roles)

| skill_id | Skill (DE) | Category | Anchor source | Assurance | Notes |
| -------- | ---------- | -------- | ------------- | --------- | ----- |
| SK-BEDFLOW | Bettenmanagement / Patientenfluss | leadership | in-house cert | L1 | BMCA-facing |
| SK-ORCOORD | OP-Koordination / Slate-Management | leadership | in-house cert | L1 | ORSA-facing |
| SK-DISCHARGE | Austrittsplanung / Care-Transition | leadership | GesReg + in-house | L4/L1 | DCA-facing |
| SK-CRISIS | Krisen-/Lagemanagement (Incident Command) | leadership | in-house doctrine cert | L1 | CSA-facing |
| SK-ROSTER | Dienstplanung / Personaleinsatz | leadership | in-house | L1 | SBA-facing |
| SK-DQSTEWARD | Datenqualität / Ontologie-Stewardship | digital | professional cert | L1/L2 | DQ-facing |
| SK-WARDLEAD | Stationsleitung (HöFa/Leadership) | leadership | in-house + HF | L1/L3 | No |

### B.7 Department → required-skills map (the demand-template source)

This is the core of the deliverable — for each Curavias department archetype, the capacity-critical skills the ontology should demand. `M` = mandatory (gates the shift); `P` = preferred (ranking, not eligibility). Grounded in the 24 departments of `Demo-Hospitals-Master-Data`.

| Department archetype (examples) | Mandatory skills (M) | Preferred / depth (P) |
| ------------------------------- | -------------------- | --------------------- |
| **Intensiv-/Notfallmedizin** (CN-D7, VT-D6, CP-D6) | SK-LIC-NURSE, SK-NDS-IPS, SK-VENT, SK-ACLS, SK-BLS, SK-DE-B2, SK-IPC · physicians: SK-LIC-PHYS + SK-FMH-INTENS/SK-FMH-NOTF | SK-ECMO, SK-HAEMO, SK-CRISIS |
| **Herz-/Gefässzentrum** (CN-D1, CP-D1) | SK-LIC-NURSE, SK-ACLS, SK-DE-B2 · physicians: SK-FMH-CARD / SK-FMH-CARDSURG + SK-LIC-PHYS | SK-NDS-IPS, publications depth |
| **Neuro-/Kopfzentrum** (CN-D2, CP-D2) | SK-LIC-NURSE, SK-DE-B2 · physicians: SK-FMH-NEURO / SK-FMH-NEUROSURG + SK-LIC-PHYS | SK-NDS-IPS |
| **Innere Medizin & Onkologie** (CN-D3, VT-D1, CP-D3) | SK-LIC-NURSE, SK-MEDADMIN, SK-DE-B2 · SK-ONCO-NURSE (onco) · physicians: SK-FMH-INTMED / SK-FMH-ONCO / SK-FMH-RADONC | SK-FMH-PALL (palliative), SK-WOUND |
| **Trauma / Orthopädie & Unfallchirurgie** (CN-D4, CP-D7, VT-D4) | SK-LIC-NURSE, SK-BLS, SK-DE-B2 · physicians: SK-FMH-ORTHO / SK-FMH-SURG + SK-LIC-PHYS | SK-SCRUB support |
| **Frauen-/Kinderzentrum, Geburtshilfe & Neonatologie** (CN-D5, CP-D4/D5, VT-D2) | SK-LIC-MIDWIFE, SK-OBST, SK-PALS, SK-NEO (neo), SK-DE-B2 · physicians: SK-FMH-GYN / SK-FMH-PAED / SK-FMH-NEONAT | SK-NDS-IPS (NICU) |
| **OP / Operationsbereich** (all surgical depts) | SK-LIC-OTA, SK-SCRUB, SK-IPC · anaesthesia: SK-NDS-ANAES + SK-ACLS · physician: SK-FMH-ANAES | procedure sign-offs |
| **Diagnostik, Radiologie & Nuklearmedizin** (CN-D6, CP-D8, VT-D8) | SK-LIC-MTRA, SK-RADPROT, SK-CT/SK-MRI · physicians: SK-FMH-RADIOL / SK-FMH-NUCMED | SK-PETCT, SK-MAMMO |
| **Nephrologie & Dialyse** (VT-D7) | SK-LIC-NURSE, SK-DIAL, SK-DE-B2 · physician: SK-FMH-NEPHRO | SK-NDS-IPS |
| **Notfallzentrum & Rettungsdienst 144** (CP-D6, VT-D5) | SK-LIC-PARA, SK-ACLS, SK-TRIAGE, SK-BLS · physician: SK-FMH-NOTF | SK-PALS, SK-CRISIS |
| **Augenzentrum** (CP-LE3) | SK-LIC-PHYS + SK-FMH-OPHT · SK-LIC-NURSE | — |
| **Palliativ / Langzeit / Alterszentren** (VT-D1 palliative, VT-LE2/LE3) | SK-LIC-NURSE, SK-FMH-PALL, SK-WOUND, SK-DE-B2 | SK-DISCHARGE |
| **Coordination / command roles** (across all) | role cert: SK-BEDFLOW / SK-ORCOORD / SK-DISCHARGE / SK-CRISIS / SK-ROSTER / SK-DQSTEWARD | domain clinical background |

### B.8 Region / language gating note

The showcase tenants sit in demo cantons **HN** (CuraNova, Vialta) and **CA / TK / VS** (Curalp group), all German-speaking archetypes, so **SK-DE-B2** is the default mandatory ward-language skill. The model keeps **SK-FR-B2 / SK-IT-B2** in the catalogue because (a) MedReg records language as a first-class credential and (b) a multi-site provider spanning a language border (or the Höhenklinik in VS) can flip the mandatory language per unit's canton — language is a genuine `SkillDemand`, not HR trivia.

---

## Part C — Source-selection rules (carried from the evidence taxonomy)

Consistent with `05_evidence_taxonomy` and `04_knowledge_base_register`, the platform's agents must:

- **Must** — tag every capacity-critical skill with its evidence level; prioritise official/federal sources over self-declared; never present a private certificate as *eidgenössisch anerkannt*.
- **May** — use scientific/society sources for sub-specialty depth (ranking, not gating); use Work-ID/Skills-Manager labels for *discovery* of latent skills.
- **Must not** — treat L0/L1 (self-declared, marketing) as safety-critical supply; derive a health/performance judgement of an individual from skills data.

---

## Summary

The Curavias skills demand is anchored by **four federal registers** (MedReg, GesReg, NAREG, PsyReg — all GLN-keyed, L4), refined by **SIWF titles + NDS HF diplomas** (L3), gated at task level by **expiring SRC/radiation certificates** (L2), normalised by **ESCO** and exchanged via **HL7 FHIR** — with **Work-ID / Skills-Manager** contributing a labour-market skills layer (L0–L1) that this design deliberately keeps *below* the federal evidence floor. Part B is the concrete competency catalogue (66 skills across 6 categories) that becomes `dim_skill` and the department demand-templates in Step 4.

---

*Prepared 19 July 2026 · Step 2 of 4 · sources confirmed against live public pages, July 2026 · advisory, evidence-based.*
