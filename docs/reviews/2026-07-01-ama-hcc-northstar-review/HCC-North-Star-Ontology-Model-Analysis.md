# A North Star Ontology Model for the Hospital Command Center (HCC)

### Best-practice-grounded business and technical analysis for the Swiss AI-Powered Patient Flow & Hospital Capacity Platform

| Field | Value |
| ----- | ----- |
| **Prepared for** | Urs Rüegg — Sr Solution Engineer Hub, Microsoft (CH-STU-InnoHub) |
| **Builds on** | *IKM/HCC vs Swiss Capacity Platform* analysis (companion report) |
| **Purpose** | Define a North Star ontology model to support the Hospital Command Center (HCC) capability, and a blueprint to incorporate it into the platform |
| **Best-practice references** | Fabric IQ "Build an ontology from a semantic model" lab; OMRSE *General Strategy for Modeling Health Care Facilities*; Goyer, Fabry, Barton & Ethier (ICBO 2022) *An ontology for healthcare systems*; Jerjas & Hall (KTH 2017) *Specifying an ontology framework to model processes in hospitals*; plus discovered sources — BFO (ISO/IEC 21838-2:2021), OGMS, OOSTT, OBO Foundry, SNOMED CT, and real-world command-center practice (UCSF PCMC / Epic) |
| **Status** | Draft v1.0 for internal review |
| **Format** | Markdown business + technical analysis |

---

## 1. Executive Summary

The companion analysis identified the **Hospital Command Center (HCC)** operating model and an **integral, multi-resource** capacity scope (beds, OR, staff, rooms, equipment) as the platform's largest improvement opportunities — and flagged that a **Fabric IQ ontology** would be the semantic backbone that keeps those resource domains consistent across dashboards, models, simulation and the GenAI copilot. This report specifies **how to build that ontology**, grounded in the best-practice references, and how to incorporate it as a **North Star** target model.

**Core recommendation.** Adopt a **two-layer North Star ontology**:

1. **A reference (foundational) layer** — a realist, BFO/OBO-grounded conceptual model that reuses proven healthcare ontologies (OMRSE for facilities, OGMS for the clinical encounter, Goyer et al. for healthcare-system organisation and roles, OOSTT for organisational structure) and a **process-ontology overlay** (per the KTH framework) so the same model can drive **discrete-event simulation**.
2. **An operational (application) layer** — the executable realisation in **Microsoft Fabric IQ**, generated largely from the platform's existing Power BI semantic model, where **each table becomes an entity type and each relationship becomes a relationship type**, with **static bindings from the lakehouse and time-series bindings from the eventhouse** for real-time capacity signals.

This design deliberately **bridges academic rigour and platform pragmatism**: the reference layer gives semantic precision, interoperability and explainability; the operational layer gives a queryable, GenAI-groundable, real-time graph that ships on GA-track Azure services under Swiss residency controls.

**Why this matters for the HCC.** An HCC is only as good as the shared picture it steers from. Today, "bed", "capacity", "discharge readiness" and "case" are defined implicitly and differently in each dashboard, model and prompt. A North Star ontology makes those concepts **explicit, single-sourced and machine-reasonable**, which directly enables the four things an HCC needs: (a) one consistent real-time operating picture, (b) explainable AI recommendations that trace to defined concepts, (c) what-if simulation on a shared object model, and (d) reusability of the whole pattern across providers.

**Headline actions.**
- Elevate the Fabric IQ Ontology from "deferred/optional" (current `AR-D-002` / `ADR-0002`) to the **target semantic backbone for the integral HCC tier**, gated on Switzerland-region GA.
- Stand up a **Minimum Viable Ontology (MVO)** first — *Facility → Ward → Room → Bed → Encounter → Patient → Care team → Equipment* plus **OR slot** — then grow along the "Reiseroute".
- Ground the model in **BFO + reused OBO ontologies** (do not invent from scratch); align to **FHIR/SNOMED CT** for clinical interoperability.
- Add a new requirement family (`FR-ONT-*`) and an ADR to govern the ontology as a first-class, versioned platform asset.

---

## 2. Method and Evidence Base

Four supplied/anchor references plus discovered best-practice sources were analysed and triangulated:

| Reference | Contribution to the North Star |
| --- | --- |
| **Fabric IQ ontology lab** (Microsoft Learn) | The *implementation mechanics* on our own platform: build manually or auto-generate from a Power BI semantic model; table→entity, relationship→relationship; lakehouse (static) + eventhouse (time-series) bindings; keys and relationship bindings; entity/instance overview. Its sample domain (Hospitals→Departments→Rooms→Patients→VitalSignEquipment→VitalSigns) is almost a literal template for our MVO. Currently **preview**. |
| **OMRSE — Modeling Health Care Facilities** | *Facility modelling pattern.* A facility is "an architectural structure that is the bearer of some function"; a hospital facility is a facility owned/administered by a hospital organisation and bearer of a hospital function. Facilities are **differentiated by the functions they bear and the organisations that own/administer them**. Provides a typology (ED, ambulatory surgery, ICU-adjacent, outpatient clinic, rehabilitation, skilled nursing, etc.). |
| **Goyer, Fabry, Barton & Ethier (ICBO 2022)** | *Healthcare-system organisation and roles.* A realist, OBO-Foundry/BFO model separating **healthcare procedure**, **healthcare service delivery**, **healthcare organisation** (+ *healthcare organisation role*), **health worker** (+ *health worker role*), **healthcare facility** (OGMS *hospital facility*), and **healthcare encounter** (facility-based / remote). Roles (performer, recipient) and `participates_as_…` relations precisely characterise who does what. Aligns to OMRSE and OGMS. |
| **Jerjas & Hall (KTH 2017)** | *Process/simulation overlay.* An OWL-DL ontology framework (146 classes, 34 relations) built on a **generic process ontology** (WorkDefinition→Process/Activity/Task; Resource→Agent/Tool/Method; Role; WorkProduct; Condition pre/post) explicitly to enable **computer simulation** of hospital processes. Confirms an ontology is the right foundation for the platform's proposed **what-if simulation** capability, and supplies a resource/role/agent vocabulary. Notably includes an `Organisation` branch with **MedicalTechnologyAndIT** and a `Resource` branch with **Facility, CareTeam, Tool, Method** — directly matching the integral resource scope. |
| **Discovered — BFO (ISO/IEC 21838-2:2021)** | The **upper ontology**: continuant vs occurrent; independent continuant, quality, role, disposition, function, process, information content entity. The standard, ISO-ratified backbone under all OBO ontologies — gives us reasoning, interoperability and a disciplined skeleton. |
| **Discovered — OGMS, OOSTT, OBO Foundry, SNOMED CT** | OGMS: clinical-encounter terms (patient, disease, diagnosis, healthcare provider). **OOSTT**: an OBO ontology of the *organisational structures of trauma centres/systems* — the closest existing model of hospital **organisational + capacity structure**, directly reusable. OBO Foundry: governance principles (realism, univocity, orthogonality, reuse). SNOMED CT: multilingual clinical terminology binding. |
| **Discovered — real HCC practice (UCSF PCMC / Epic)** | Validates the *operating* target the ontology must serve: a 24/7 capacity command centre, real-time bed-huddle/patient-flow dashboards, discharge lounge — reporting a 45-minute improvement in discharge time-of-day and a 6-hour reduction in ED boarding. The ontology must support exactly these real-time, multi-role, cross-unit views. |

*Confidence note.* Fabric IQ Ontology is a preview capability; its exact GA feature set and Switzerland-region availability must be validated. The reference-layer design is high-confidence (it reuses mature, published ontologies). Any claim about auto-reasoning performance at production scale is an inference to validate in a spike.

---

## 3. What "Ontology" Means Here — and Why an HCC Needs One

### 3.1 Ontology vs. data model vs. semantic model

Following the ontology spectrum (controlled vocabulary → taxonomy → ontology), an **ontology** is a *formal, explicit specification of a shared conceptualisation*: named **classes** (entity types), **relationships** (object properties), **attributes**, and **axioms/rules** that a machine can reason over. It differs from our current assets:

- A **data contract** (e.g. `DC-SUPPLY-LOCATION-v1`) fixes a *payload schema* at one producer→consumer boundary.
- A **Power BI semantic model** fixes *tables, measures and relationships* for analytics.
- An **ontology** fixes the *meaning and relationships of the domain concepts themselves*, independent of any single source system or report — so every dashboard, model, simulation and copilot answer refers to the **same** "bed", "encounter" and "discharge readiness".

Fabric IQ makes this practical: it **generates an ontology from the semantic model** (table→entity type, relationship→relationship type), then lets you enrich it — crucially with **time-series bindings** so an entity (e.g. monitoring equipment, or a bed) carries both static reference data and live measurements.

### 3.2 Why the HCC specifically needs a North Star ontology

| HCC need | Without an ontology | With the North Star ontology |
| --- | --- | --- |
| **One operating picture** | Each source system/dashboard defines capacity differently; reconciliation is manual | Single shared conceptual model; every surface reads the same entities/relationships |
| **Explainable AI** | Copilot answers and model features drift from dashboard definitions | Copilot and Data Agents ground on ontology concepts; answers trace to defined entities and relations (supports `NFR-AI-003/004`) |
| **What-if simulation** | Simulations are bespoke and hard to integrate | Process-ontology overlay gives a shared object model for discrete-event simulation (the KTH thesis' exact purpose) |
| **Integral resource scope** | Beds, OR, staff, rooms, equipment modelled ad hoc | All five are *capacity units* with shared states/relations — the integral view the companion report requires |
| **Multi-provider reuse** | Each provider re-modelled from scratch | A reference ontology + provider extensions; onboard new providers as specialisations (supports `NFR-MAINT-004`) |
| **Regulatory traceability** | Lineage is technical, not conceptual | Concept-level lineage strengthens audit and DSR responses |

---

## 4. The North Star Ontology — Design

### 4.1 Design principles (from the references)

1. **Realist, BFO-first.** Model reality (entities, roles, processes), not database tables. Use **BFO (ISO/IEC 21838-2:2021)** as the upper ontology — continuant vs occurrent — as all OBO ontologies do.
2. **Reuse before invent (OBO orthogonality/univocity).** Import and specialise **OMRSE, OGMS, OOSTT, and the Goyer et al. healthcare-system classes** rather than coining new terms; one term = one meaning.
3. **Roles and functions are first-class.** Separate *organism* from *patient role*, *person* from *surgeon/anaesthetist role*, *building* from *ED/OR function* — the pattern that gives Goyer/OMRSE their precision and lets the same person/room play different roles over time.
4. **Process overlay for simulation.** Layer a generic process ontology (WorkDefinition/Process/Activity/Task, Resource, Agent, Method, Tool, Condition) so the model is simulation-ready (KTH).
5. **Two layers, one lineage.** Keep a rigorous **reference layer** (OWL/RDF, reasoning) and a pragmatic **operational layer** (Fabric IQ property graph), with an explicit crosswalk between them.
6. **Bind to clinical standards.** Crosswalk to **FHIR** resources and **SNOMED CT** codes so clinical semantics interoperate with Azure Health Data Services.
7. **Grow along a Reiseroute.** Ship a Minimum Viable Ontology, then extend by resource domain and provider.

### 4.2 Upper-level skeleton (BFO categories)

```text
BFO: entity
├── continuant
│   ├── independent continuant (material entity)
│   │   ├── object: Hospital organisation, Healthcare facility, Site/Building,
│   │   │           Ward/Unit, Room, Bed, Operating theatre, Person, Device/Equipment
│   │   └── object aggregate: Care team, Capacity pool
│   ├── specifically dependent continuant
│   │   ├── role: patient role, health-worker role (surgeon, anaesthetist, nurse,
│   │   │         bed manager), healthcare-organisation role, discharge-candidate role
│   │   ├── disposition/function: ED function, OR function, ICU function,
│   │   │         outpatient-clinic function (OMRSE facility functions)
│   │   └── quality: bed state (occupied/available/blocked), occupancy level,
│   │             readiness score, acuity
│   └── generically dependent continuant
│       └── information content entity (IAO): forecast, discharge score, capacity plan,
│                 OR slate, staffing roster, care plan, KPI, simulation scenario/result
└── occurrent
    └── process: healthcare encounter (facility-based / remote), health procedure
              (surgical, anaesthesia consult), admission, transfer, discharge process,
              patient-flow process, capacity-steering process, OR-steering process
```

### 4.3 Core class catalogue (reference layer)

Reusing the references' definitions (paraphrased) and mapping each class to its source and to the platform's resource dimensions:

| Class | Reuse source | Definition (paraphrased) | Platform role |
| --- | --- | --- | --- |
| **Hospital organisation** | Goyer / OMRSE / OGMS | Organisation bearing a healthcare-organisation role | Provider tenant boundary |
| **Healthcare facility** (`hospital facility`) | OMRSE / OGMS | Architectural structure that is bearer of a hospital function, owned/administered by a hospital organisation | Site of care; capacity container |
| **Facility function typology** | OMRSE | ED, ambulatory surgery, ICU, outpatient clinic, rehabilitation, skilled nursing, etc. — facilities differentiated by function borne | Classifies units for capacity/forecast |
| **Site / Building / Ward / Room / Bed** | OOSTT + Fabric IQ sample | Recursive part-of hierarchy of physical capacity | Bed & room capacity dimension |
| **Operating theatre / OR slot** | (new, BFO-aligned) | Room bearing an OR function; OR slot = planned time-bounded capacity | **OR capacity dimension** |
| **Person / Organism** | Goyer / OGMS | The human; bearer of patient or health-worker roles | Subject of care / staff |
| **Patient role** | OGMS / Goyer | Role realised by participating as recipient in a healthcare encounter | Demand |
| **Health worker / role** | Goyer | Health worker = organism member of a healthcare organisation bearing a worker role (surgeon, anaesthetist, nurse…) | **Staffing dimension** |
| **Care team** | KTH (`CareTeam`) | Object aggregate of health workers | Staffing aggregate |
| **Device / Equipment** | Fabric IQ sample / KTH (`MedicalTechnologyAndIT`, `Tool`) | Material entity used in procedures/monitoring; may stream time-series | **Equipment dimension** |
| **Healthcare encounter** | Goyer / OGMS | Temporally-connected service delivery aiming to improve a participant's health; facility-based or remote | Flow spine (admission→discharge) |
| **Health procedure** (surgical, anaesthesia) | Goyer | Planned process performed by a health worker realising a worker role | OR/clinical activity |
| **Admission / Transfer / Discharge process** | (new, BFO occurrent) | Sub-processes of the patient-flow process | Flow events |
| **Capacity unit / state** | (new) | Generalisation over bed/OR/room/staff/equipment availability | **Integral capacity abstraction** |
| **Forecast / Discharge score / Capacity plan / OR slate / Roster / Scenario** | IAO | Information content entities produced by AI/analytics | AI outputs & grounding |
| **Process / Activity / Task / Resource / Agent / Method / Condition** | KTH generic process ontology | Simulation-oriented process structure | **Simulation overlay** |

### 4.4 Key relationships (Relation Ontology-aligned)

`is_part_of` (bed⊑room⊑ward⊑building⊑site⊑facility) · `located_in` · `bearer_of` (facility→function; person→role) · `has_role` · `realizes` (process→role) · `participates_in` / `participates_as_recipient` / `participates_as_performer` (Goyer) · `occurs_in` (encounter→facility) · `has_participant` · `assigned_to` (staff/equipment→unit) · `produces` / `consumes` (process↔resource, KTH) · `has_capacity_state` · `forecasts` / `scores` (IAO→entity).

### 4.5 The "integral capacity" abstraction (the key modelling move)

The companion report's core gap was that beds are modelled but OR, staff, rooms and equipment are not. The North Star resolves this with a single generalisation: **Capacity unit** — a material entity (or time-bounded slot) that bears a **capacity function** and has a **capacity state** (available / occupied / blocked / planned). Beds, OR slots, rooms, staff shifts and devices are all subtypes. This lets one set of relations, states, KPIs, forecasts and simulation logic apply across **all five resource dimensions** — the semantic realisation of "integral" capacity management.

---

## 5. Realising the North Star in Microsoft Fabric IQ (operational layer)

### 5.1 Generate-from-semantic-model, then enrich

Per the Fabric IQ lab, the fastest path is **not** to hand-build the graph but to:

1. Curate the operational data in a **lakehouse** (static reference: facilities, wards, rooms, beds, patients, staff, equipment, OR slots) and an **eventhouse/KQL** (time-series: bed-state changes, vital signs, OR status, admissions/discharges).
2. Build a **Power BI semantic model** with the real-world relationships (*ward belongs to facility, room part of ward, bed in room, patient admitted to bed, equipment assigned to patient, OR slot in theatre*).
3. **Generate Ontology** — each table becomes an **entity type**, each relationship a **relationship type**.
4. **Enrich manually**: verify entity **keys**, configure **relationship bindings** (foreign-key columns identifying both sides), and add **time-series bindings** so entities such as *Bed* or *VitalSignEquipment* combine static properties with live streaming measurements.

This maps almost one-to-one onto the lab's healthcare sample (Hospitals→Departments→Rooms→Patients→VitalSignEquipment→VitalSignsReadings), which is why the MVO is low-risk to stand up.

### 5.2 Mapping reference-layer classes to Fabric IQ constructs

| Reference layer (BFO/OBO) | Fabric IQ operational layer |
| --- | --- |
| Class (e.g. *Bed*, *Encounter*) | Entity type |
| Object property (e.g. `is_part_of`) | Relationship type (with binding) |
| Data property / quality (e.g. bed state) | Entity property (static binding) |
| Live measurement (e.g. occupancy over time) | **Time-series binding** (eventhouse) |
| Information content entity (forecast, score) | Entity type bound to AI-output tables |
| Axiom / rule | Enforced in curation + validated in data contracts (Fabric IQ reasoning is lighter than OWL-DL — see §5.4) |

### 5.3 Mapping to existing platform data contracts

The ontology sits **above** the existing contract family and gives it shared meaning:

| Ontology entity | Existing / proposed contract |
| --- | --- |
| Hospital organisation | `DC-SUPPLY-ORGANIZATION-v1` |
| Facility / Ward / Room / Bed | `DC-SUPPLY-LOCATION-v1` (recursive Site/Ward/Bed) |
| Encounter / Patient role | `DC-DEMAND-ENCOUNTER-v1` |
| Match / recommendation (advisory) | `DC-MATCH-RECOMMENDATION-v1` |
| OR slot / Staffing / Room / Equipment | `DC-OR-SCHEDULE-v1`, `DC-STAFF-ROSTER-v1`, `DC-ROOM-STATE-v1`, `DC-DEVICE-STATE-v1` (proposed in companion report) |
| Forecast / Discharge score / Scenario | `DC-AI-FORECAST-v1`, discharge outputs, `DC-SIM-*` (proposed) |

### 5.4 A deliberate two-layer split (and why)

Fabric IQ's ontology is a **property-graph, binding-oriented** model optimised for querying and GenAI grounding — not a full OWL-DL reasoner. The **reference layer** (OWL/RDF in a tool like Protégé, as the KTH thesis used) is where we keep **rigorous axioms, BFO alignment and OBO imports**; the **operational layer** (Fabric IQ) is where we **execute** against live Swiss-resident data. Governance keeps them in lockstep via an explicit crosswalk. This gives the best of both: publishable rigor + production performance, and it de-risks Fabric IQ's preview status (the reference layer is portable if the operational substrate changes).

### 5.5 How the ontology powers HCC capabilities

- **Copilot grounding & Data Agents.** The bed-management copilot and proposed OR/simulation agents ground on ontology entities/relationships, so answers are consistent and **traceable to defined concepts** (`NFR-AI-002/003/004`). Fabric **Data Agents** can reason over the ontology for anomaly detection and semantic query assistance (Architecture Pattern 1).
- **Real-time command view.** Time-series bindings feed live bed/OR/staff state into the same entities the dashboards and copilot use — the UCSF-style single operating picture.
- **What-if simulation.** The process-ontology overlay provides the shared object model the KTH framework was designed for, so simulation, forecasting and operations share one vocabulary.
- **Provider reuse.** New providers are onboarded as **specialisations** (e.g. Hirslanden OR-heavy profile; Zollikerberg Hospital-at-Home virtual-ward extension) rather than re-modelled.

---

## 6. Business Analysis

### 6.1 Value proposition

An ontology is an **enabling asset**, not a feature users see. Its business value is realised through everything it makes better, faster and cheaper:

| Value lever | Mechanism | Ties to |
| --- | --- | --- |
| **Faster, cheaper provider onboarding** | Reuse a reference model + provider extensions instead of re-modelling per site | Multi-provider "pattern"; `NFR-MAINT-004` |
| **Lower semantic-drift cost** | One definition of bed/encounter/readiness across dashboards, models, copilot | Fewer defects, less reconciliation |
| **Trustworthy, explainable AI** | Grounded, concept-traceable copilot & agents | Adoption; regulatory acceptance (`NFR-AI`) |
| **Simulation & strategic planning** | Shared object model for what-if | New T3 revenue tier (companion report) |
| **Interoperability & future-proofing** | BFO/OBO + FHIR/SNOMED CT alignment; vendor-neutral above source systems | Protects against source-system churn |
| **Regulatory traceability** | Concept-level lineage for audit and DSR | DSG/EPDG evidence |
| **FAIR, reusable data estate** | Findable/Interoperable data foundation | Cross-initiative leverage |

### 6.2 The "North Star vs. now" framing

A **North Star** is the *target end-state* model that guides incremental delivery — not a big-bang build. Business discipline: publish the North Star, but **fund the Minimum Viable Ontology first** and expand along the Reiseroute. This avoids the classic ontology failure mode (over-modelling before access patterns stabilise, already flagged as a risk in the platform architecture).

### 6.3 Build vs. reuse (a cost decision)

Reusing OBO ontologies (OMRSE, OGMS, OOSTT, Goyer et al.) is **materially cheaper and lower-risk** than green-field modelling: the hard conceptual work (facility typology, roles, encounter semantics, organisational structure) is already published, peer-reviewed and BFO-consistent. The build effort concentrates on the **capacity-unit abstraction, the OR/staffing/equipment specialisations, the Fabric IQ realisation, and provider extensions**.

### 6.4 Costs, risks and mitigations (business)

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Fabric IQ Ontology is **preview** | Cannot be on a regulated MVP critical path (`AR-D-002`/`ADR-0006`) | Keep reference layer portable; gate operational layer on Switzerland GA; MVO on GA semantic models meanwhile |
| **Governance overhead / ownership ambiguity** | Ontology rot, drift | Assign a semantic owner; OBO-style change workflow; tie to existing data-contract governance & Purview |
| **Over-modelling** before patterns stabilise | Wasted effort, latency | MVO first; bound scope to bed+OR+encounter; materialise semantic views for real-time paths |
| **Scarce ontology skills** | Delivery risk | Reuse published ontologies; partner for reference-layer authoring; upskill via the Fabric IQ lab |
| **Two layers diverge** | Inconsistency | Single crosswalk artefact; CI check that operational entities map to reference classes |

---

## 7. Technical Analysis and Incorporation Blueprint

### 7.1 Target architecture (ontology in the platform)

```text
Reference layer (rigor)              Operational layer (execution, Swiss-resident)
───────────────────────           ────────────────────────────────────────
BFO (ISO 21838-2)                    Fabric IQ Ontology (property graph)
  imports OMRSE, OGMS, OOSTT,   ⇄     generated from Power BI semantic model
  Goyer healthcare-system,      ⇄     entity types  ← lakehouse (static bindings)
  process-ontology overlay      ⇄     relationship types ← FK bindings
  (OWL/RDF, Protégé)                  time-series bindings ← eventhouse (KQL)
        │ crosswalk                            │
        ▼                                       ▼
FHIR / SNOMED CT alignment          Fabric OneLake curated domains + Data Agents
                                     → grounds copilot, dashboards, simulation
```

### 7.2 Alignment to existing architecture decisions

- **Elevate `AR-D-002`/`ADR-0002`.** Fabric IQ Ontology is currently excluded from the MVP critical path (preview, no GA date). Recommend a **superseding ADR**: ontology becomes the **target semantic backbone for the integral/HCC tier**, with a hard Switzerland-region GA gate and a portable reference layer in the interim. This is consistent with Architecture **Pattern 1** (Fabric IQ Ontology + Data Agents), which the architecture already assesses as strategically valuable.
- **Residency/compliance.** The ontology **schema/metadata is not itself PHI**; PHI remains in Swiss-resident stores under existing controls. Time-series and static bindings read Swiss-resident data; **no change to `AR-D-003/004`** (PHI inference in Switzerland regions only). This *eases* adoption: much of the capacity/OR/room/equipment data is operational-confidential, not deep PHI.
- **Governance.** Manage the ontology as a **versioned, Git-tracked asset** with promotion gates (DEV/SIT/PROD), mirroring the platform's IaC-first and data-contract discipline; record lineage/classification in Purview.

### 7.3 Clinical-standards crosswalk

| Ontology concept | FHIR | Terminology |
| --- | --- | --- |
| Facility / Ward / Room / Bed | `Location`, `HealthcareService` | SNOMED CT site/location |
| Encounter / admission / discharge | `Encounter`, `EncounterStatusHistory` | SNOMED CT encounter types |
| Health worker / role | `Practitioner`, `PractitionerRole` | SNOMED CT roles |
| Procedure (surgical/anaesthesia) | `Procedure`, `ServiceRequest`, `Appointment`/`Slot` (OR) | SNOMED CT procedures |
| Device / equipment | `Device` | SNOMED CT devices |

This keeps the ontology interoperable with **Azure Health Data Services** (already in the stack) and with Swiss EPR/FHIR obligations.

### 7.4 New requirement family (proposed)

| ID | Requirement | Anchored to |
| --- | --- | --- |
| `FR-ONT-001` | Maintain a reference ontology grounded in BFO, reusing OMRSE/OGMS/OOSTT/Goyer healthcare-system classes | extends FR-DATA |
| `FR-ONT-002` | Realise the operational ontology in Fabric IQ, generated from the governed semantic model with static + time-series bindings | extends FR-DATA / FR-FC |
| `FR-ONT-003` | Model all five resource dimensions as capacity-unit subtypes with shared states/relations | integral scope (companion report) |
| `FR-ONT-004` | Ground copilot and Data Agents on the ontology with concept-level traceability | extends FR-CX / `NFR-AI-003/004` |
| `FR-ONT-005` | Provide a process-ontology overlay to support what-if simulation | supports `FR-SIM-*` (companion report) |
| `FR-ONT-006` | Crosswalk ontology to FHIR/SNOMED CT for clinical interoperability | extends FR-DATA-002 |
| `FR-ONT-007` | Support provider-specific ontology extensions without re-architecture | `NFR-MAINT-004` |
| `NFR-ONT-001` | Version, govern and promote the ontology as a first-class asset with an explicit reference↔operational crosswalk | `NFR-MAINT-002` |

### 7.5 Implementation phases (MVO → integral → simulation-grade)

| Horizon | Deliverable | Notes |
| --- | --- | --- |
| **Phase 1 — MVO** | Facility→Ward→Room→Bed→Encounter→Patient→Care team→Equipment **+ OR slot**, generated from the semantic model with first time-series bindings (bed state) | Directly follows the Fabric IQ lab; GA semantic-model base; reference layer skeleton in parallel |
| **Phase 2 — Integral** | Add staffing, room, equipment capacity units; capacity-unit abstraction & shared states; Data Agents for anomaly/semantic query; provider extensions (Hirslanden, Zollikerberg) | Realises integral scope; ground copilot on ontology |
| **Phase 3 — Simulation-grade** | Process-ontology overlay; scenario/result entities; simulation grounded on shared object model; full FHIR/SNOMED crosswalk; OBO reference layer published | Enables strategic what-if (T3); revisit Fabric IQ GA/residency gate |

### 7.6 Governance model (OBO-inspired)

- **Realism & univocity**: model reality; one term, one meaning.
- **Orthogonality & reuse**: import, don't duplicate, external ontologies.
- **Semantic change workflow**: proposals → review by a domain owner → versioned release → downstream impact check (mirrors data-contract breaking-change control).
- **Ownership**: an **ontology/semantic owner** in the data-governance RACI; reference↔operational crosswalk is a governed artefact with a CI conformance check.

---

## 8. Risks, Dependencies and Open Questions

**Technical risks** — Fabric IQ preview status and Switzerland-region GA timing; reasoning depth of the property graph vs OWL-DL (mitigated by the two-layer split); real-time performance of time-series bindings at production event volumes (validate in a spike); keeping reference and operational layers in sync.

**Dependencies** — Switzerland-region GA for Fabric IQ Ontology; the companion report's OR/staffing/room/equipment data domains; access to source systems for bindings; ontology-authoring skills or partner.

**Open questions** —
1. Confirm Fabric IQ Ontology GA date and Switzerland-region availability before any critical-path commitment.
2. How much OWL-DL reasoning do we actually need operationally vs. rules enforced in curation/contracts?
3. Which reference ontologies to import wholesale vs. cherry-pick (OOSTT organisational structure is the strongest candidate for full reuse)?
4. Author the reference layer in-house or with an OBO-experienced partner?
5. Pilot provider for the MVO — Hirslanden (OR-heavy) aligns with the OR-first strategy from the companion report.

---

## 9. Conclusion

An HCC steers from a shared picture of reality; a North Star ontology is what makes that picture **explicit, consistent, explainable and reusable**. The best-practice references converge on a clear design: a **realist BFO/OBO reference layer** (reusing OMRSE facilities, OGMS/Goyer encounters and roles, OOSTT organisational structure, and a process overlay for simulation) mapped to an **executable Fabric IQ operational layer** generated from our own semantic model, with static and time-series bindings over Swiss-resident data.

This is low-risk to start (the Fabric IQ lab is nearly a literal template for the MVO), high-leverage to finish (it is the semantic backbone for the integral resource scope, the GenAI copilot's explainability, and the what-if simulation the companion report proposed), and disciplined to govern (OBO principles + the platform's existing contract/IaC/Purview machinery). The single most important next step is to **publish the North Star, stand up the Minimum Viable Ontology, and elevate the Fabric IQ Ontology decision from "deferred" to "target backbone — GA-gated."**

---

### Appendix A — Reference → North Star contribution map

| Reference | Reused in the North Star as |
| --- | --- |
| BFO (ISO/IEC 21838-2:2021) | Upper ontology (continuant/occurrent skeleton) |
| OMRSE | Facility class + function typology; facility differentiation pattern |
| OGMS | Clinical-encounter, patient, provider terms |
| Goyer et al. (ICBO 2022) | Healthcare organisation/role, health worker/role, encounter (facility-based/remote), performer/recipient roles |
| OOSTT | Organisational-structure / capacity-structure reuse |
| Jerjas & Hall (KTH 2017) | Process/simulation overlay; Resource/Agent/Method/Tool; MedicalTechnologyAndIT & CareTeam branches |
| Fabric IQ lab | Operational realisation mechanics (generate-from-semantic-model; static + time-series bindings) |
| SNOMED CT / FHIR | Clinical terminology & resource crosswalk |
| UCSF PCMC / Epic | Real-world HCC operating picture the ontology must serve |

### Appendix B — Glossary

**BFO** — Basic Formal Ontology (ISO-standard upper ontology). **OBO** — Open Biological and Biomedical Ontology Foundry. **OMRSE / OGMS / OOSTT** — reusable OBO domain ontologies (social entities / general medical science / trauma-centre organisational structures). **Continuant / Occurrent** — BFO's persist-through-time vs unfold-over-time split. **Role / Function / Disposition** — realizable dependent entities (e.g. patient role, OR function). **ICE** — Information Content Entity (forecast, score, plan). **Entity type / Relationship type / Binding** — Fabric IQ constructs (class / object property / data source connection). **MVO** — Minimum Viable Ontology. **Reiseroute** — VR&P's incremental adoption journey.
