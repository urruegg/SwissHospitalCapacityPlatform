# Integral Capacity Management (IKM) & Hospital Command Center (HCC) — Business and Technical Analysis

### Incorporating Vetterli Roth & Partners know-how into the Swiss AI-Powered Patient Flow & Hospital Capacity Platform

| Field | Value |
| ----- | ----- |
| **Prepared for** | Urs Rüegg — Sr Solution Engineer Hub, Microsoft (CH-STU-InnoHub) |
| **Subject** | Comparative analysis of Vetterli Roth & Partners (VR&P) IKM / HCC vs. the current Swiss Hospital Capacity Platform, with an incorporation blueprint |
| **Sources analysed** | VR&P *Integrales Kapazitätsmanagement (IKM)* page; VR&P *Universitäts-Kinderspital Zürich* case study; current platform docs (PRD, ARCHITECTURE, AI, DATA, INFRASTRUCTURE, OPERATIONS, SD, plus the case-study and provider analysis) |
| **Status** | Draft v1.0 for internal review |
| **Format** | Markdown business + technical analysis |

---

## 1. Executive Summary

The current **Swiss AI-Powered Patient Flow and Hospital Capacity Platform** is a mature, provider-internal *technology* platform. It is built around three operational AI use cases — 72-hour emergency demand forecasting, discharge coordination AI, and a GenAI bed-management copilot — on a Microsoft Fabric / Azure Machine Learning / Azure OpenAI backbone, with best-in-class Swiss data-residency, governance, security, reliability/DR and auditability engineering.

**Vetterli Roth & Partners' Integrales Kapazitätsmanagement (IKM)** and **Hospital Command Center (HCC)** offering is, by contrast, an *operating-model and process-transformation* play. Its distinctive strength is holistic ("integral") steering of **all** hospital resources — beds, operating rooms, staff, medical technology and rooms — combined with Lean / Design-Thinking process re-engineering and a central command-center operating rhythm, as demonstrated at the University Children's Hospital Zurich (Kispi).

The two are highly complementary rather than competitive. The single most important finding of this analysis is:

> **Our platform optimises three operational signals inside a strong cloud architecture; VR&P optimises the whole capacity system inside a strong operating model. The largest improvement opportunity is to widen our platform from "patient-flow + beds" to true *integral* capacity management — most urgently by adding operating-room (OR) and staffing capacity — and to wrap it in an HCC operating model (roles, decision cadences, Lean process standardisation) and a strategic what-if simulation capability.**

### Top improvement themes (detailed in §5–§7)

1. **Add operating-room / surgical capacity as a first-class domain** — VR&P's biggest visible lever at Kispi (OR steering dashboard, idle-time reduction, cancellation avoidance, anaesthesia-consultation redesign). Today we have **no OR module**.
2. **Move from single-resource to *integral* resource scope** — add **staffing/personnel**, **rooms** and **medical technology** as managed capacity dimensions, not just forecast input signals.
3. **Add strategic & tactical *scenario simulation* ("what-if")** alongside our operational 72-hour forecast — the class of question VR&P answers ("what if orthopaedics moves to Monday operating?").
4. **Wrap the technology in a Hospital Command Center *operating model*** — people, roles, daily/tactical/strategic decision cadences and coaching, not only a React UI and Power BI views.
5. **Adopt a Lean / Design-Thinking / Gemba process-standardisation front end** — process discovery, harmonisation and clear responsibility rules *before and alongside* the digital tooling.
6. **Introduce a business-outcome KPI framework** (OR utilisation, short-notice cancellations, bed occupancy, discharge-by-time) to complement our current technical SLOs.
7. **Package for maturity-tiered adoption** ("Reiseroute" / journey) and for **new-building commissioning** scenarios (the Kispi context).

None of these require abandoning our architecture. They extend it — and several map cleanly onto capabilities we have already flagged as optional (e.g. Fabric IQ Ontology, provider-specific onboarding profiles, OR-schedule ingestion for Hirslanden).

---

## 2. Method and Evidence Base

This analysis triangulates three evidence sets:

- **VR&P public material** — the IKM/HCC service page and the Kispi case study (both German-language; summarised here in English, not reproduced verbatim).
- **Current platform documentation** — PRD v1.3, ARCHITECTURE v0.12, AI v0.5, DATA v0.5, INFRASTRUCTURE v1.3, OPERATIONS v1.2, SD v1.3, plus the Case Study 26 brief and the four-provider capacity analysis.
- **Structured gap mapping** — capability-by-capability comparison, followed by a business and a technical incorporation blueprint mapped back to existing requirement IDs.

A note on confidence: VR&P's public pages are marketing-level and do not disclose their internal data model, algorithms or software-partner stack. Where this analysis infers technical shape (e.g. "discrete-event simulation"), it is labelled as inference, not established fact, and should be validated in a direct VR&P conversation or a joint workshop.

---

## 3. What Vetterli Roth & Partners' IKM / HCC Actually Is

### 3.1 Integral Capacity Management (IKM) — the concept

VR&P defines IKM as the **holistic planning and steering of all hospital resources — beds and OR through personnel to medical technology and rooms** — with the explicit goal of matching those resources optimally to patient demand *and to each other*, avoiding bottlenecks, and maximising both **care quality and economic efficiency**. The promised effects are improved workflows, reduced waiting times, lower cost and higher patient satisfaction.

Three properties distinguish this from our current framing:

- **Multi-resource by definition.** Beds are only one of five named resource classes. OR, staff, equipment and rooms are peers, not context.
- **Balance objective.** IKM optimises resources *against each other* (e.g. an OR plan is only good if beds and staff downstream can absorb it), not each in isolation.
- **Dual value target.** Quality *and* economics are co-equal objectives.

### 3.2 The Hospital Command Center (HCC)

VR&P positions the HCC as the **central control hub of the hospital — the "heart" of an IKM initiative** — that uses modern technology and **real-time data** to steer processes and resources. It monitors key indicators such as **bed occupancy, emergency volume and staff availability**, so that **over-capacity and bottlenecks are detected early** and fast, well-founded decisions become possible. VR&P explicitly notes that **AI is used to forecast future demand** (short-term elective patients *and* emergencies) so planning can react ahead of time.

Crucially, the HCC is described as an **operating capability, not only a screen**: after go-live VR&P continues to **accompany the teams and decision-makers on everyday, tactical and strategic questions** with expertise, analytics, coaching and decision support. This is an operating-model + managed-service concept, not a dashboard.

### 3.3 Engagement and packaging model

VR&P offers **tiered packages by maturity** of the IKM initiative:

- **Potential analysis** — assessment of the technical and process foundations plus an estimate of the transformation's potential.
- **Data-based decision support** — targeted analytics on selected capacity / patient-flow questions as a complement to an existing BI environment.
- **Full IKM projects** — from first steps to a mature, system-wide command center, connecting new areas and data sources step by step along an individual "**Reiseroute**" (journey/roadmap).
- **Software licences and simulation/forecasting modules** — delivered with different software partners, with initial training included and continuous coaching optional.

They also expose **scenario/simulation** questions as a headline capability: *what happens to bed availability if a patient group grows disproportionately; what if orthopaedics starts operating on Mondays; how many rooms are needed if ambulatory clinics run interdisciplinarily in a new building; what is the potential of optimised capacity planning?* These are **tactical and strategic planning** questions, answered by modelling future scenarios and identifying both bottlenecks and over-capacity.

### 3.4 The Kinderspital Zürich (Kispi) case study — what they actually did

**Context.** With the move into its **new building**, Kispi had to fundamentally rework the operating processes of different disciplines and centres. The stated aim was to create — through **harmonisation and standardisation** — a *unified platform for inpatient areas and the OR*, an essential precondition for digital, process-oriented steering. IKM was introduced **in parallel with a new operating model**, to intelligently connect beds, ORs, planning and staffing, and to massively raise data quality and steerability through consistent digitalisation.

**Approach.** Together with the client, VR&P analysed all workflows in inpatient areas, the OR and disposition — both through **on-site Gemba walks and data-based analysis**. Findings fed a **standard base model** and the interdisciplinary development of solution elements, including:

- the inpatient day-to-day clinical routine;
- **OR registration, the anaesthesia consultation, and OR daily processes**;
- an **OR-steering dashboard for early control**;
- **interface harmonisation and clear responsibility rules**;
- a **24/7 discharge-management process**.

The digital solutions were integrated **both technically and process-wise**, to enable one unified operating logic across all wards and OR theatres.

**Results reported.**

- An **OR-steering dashboard** to avoid short-notice cancellations and idle slots.
- **Reduced OR idle time** through day plans coordinated early.
- **More efficient anaesthesia consultations** through new structure and processes.
- **Improved interface logic across all departments**.
- **More time for patients** through newly organised interprofessional collaboration.
- **Unified capacity management across all platforms**, plus a **digital tool to steer bed and OR capacity**.
- **Clearly structured discharge processes**, reliable even during acute bottlenecks.

VR&P's other referenced engagements — **Klinikum Ernst von Bergmann** (IKM) and **LKH-Univ. Klinikum Graz** (Lean-OP: more procedures through stronger teams and clearer processes) — reinforce that the method combines **Lean, Design Thinking and capacity management** (the themes of their own newsletter).

---

## 4. What Our Current Platform Is (and Is Not)

### 4.1 Scope and use cases

The platform is a **provider-internal AI operational control layer** for one hospital provider at a time (USZ or LUKS as baselines, with Hirslanden and Zollikerberg profiled as further targets). It is explicitly **not** a cantonal shared platform and **not** a broad workflow/case-management platform; external actors (Spitex, rehab, transport, nursing homes) are **integration endpoints only**.

Three AI use cases anchor the product:

1. **72-hour emergency demand forecasting** by specialty and time window.
2. **Discharge coordination AI** — ranks inpatients approaching discharge readiness, triggers downstream partner actions, captures acknowledgements.
3. **GenAI bed-management copilot** — grounded, advisory operational Q&A over bed state, predicted pressure, likely same-day discharges and bottleneck explanations.

These are realised as MVP agents **OOA / DCA / BMCA** over onboarded data, with a mandatory **React command-center** channel and Power BI operational views.

### 4.2 Technology and engineering strengths

- **Data & AI backbone:** Microsoft Fabric + OneLake, Azure Health Data Services (FHIR normalisation), Azure Machine Learning, Azure OpenAI, Logic Apps, Power BI.
- **Swiss compliance depth:** DSG, KVG/LAMal and cantonal alignment; PHI inference pinned to Switzerland North/West with Standard/Regional deployments only; Global/Data-Zone/Developer deployment types blocked for PHI; cross-region PHI failover default-deny; EPDG/EPDV-aware controls.
- **Governance & auditability:** end-to-end traceability from source event → model output → user answer → partner trigger; versioned data contracts; Purview lineage; retention classes R1–R5.
- **Delivery & operations maturity:** CAF/WAF-aligned landing zone, IaC-first (Bicep) DEV/SIT/PROD promotion, ADR-governed decisions, reliability/DR profile with recovery classes, Application Insights observability, incident/change management.
- **Responsible AI:** advisory-only, human-in-the-loop, retrieval-grounded with citations, model/version/timestamp traceability, provider-local prompt governance.

### 4.3 The honest shape of the current product

It is an **operational-intelligence platform** for **emergency inflow, bed state and discharge outflow**. Its resource lens is essentially **beds + patient flow**. Staffing is used as an *interpretation signal*, not a managed resource; **OR/surgical capacity, rooms and medical technology are absent**; the time horizon is **operational (72 hours)** rather than tactical/strategic; and it ships as a **technology platform**, not an operating model with a process methodology and a managed command-center cadence.

---

## 5. Comparative Analysis

### 5.1 Capability overlap and gap map

| Capability dimension | VR&P IKM / HCC | Current platform | Assessment |
| --- | --- | --- | --- |
| Emergency demand forecasting | Yes (AI forecast of electives + emergencies) | **Strong** — 72-hour ED forecast by specialty | **Parity / we lead technically** |
| Bed / capacity state | Yes (bed occupancy monitoring) | **Strong** — bed-state domain + copilot | **Parity** |
| Discharge management | Yes (24/7 discharge process) | **Strong** — discharge-readiness AI + partner triggers | **Parity; they add process rigor** |
| **Operating-room (OR) capacity** | **Yes — flagship (OR dashboard, idle-time, cancellations, anaesthesia)** | **Absent** | **Major gap** |
| **Staffing / personnel as managed resource** | **Yes (staff availability, working-time models)** | Input signal only | **Major gap** |
| **Rooms & medical technology capacity** | **Yes (rooms, Medizintechnik)** | Absent | **Gap** |
| **Integral cross-resource optimisation** | **Core principle** | Per-signal, not balanced across resources | **Concept gap** |
| **Scenario / what-if simulation (tactical/strategic)** | **Yes (headline capability)** | Absent (predictive forecast only) | **Major gap** |
| **HCC operating model (roles, cadences, coaching)** | **Core — the "heart" of IKM** | UI + dashboards only | **Operating-model gap** |
| **Lean / Design-Thinking / Gemba process method** | **Core differentiator** | Not in scope | **Method gap** |
| **Business-outcome KPI framework** | Yes (occupancy, cancellations, idle time) | Technical SLOs dominate | **Gap** |
| Cloud architecture, IaC, MLOps | Not disclosed (uses partner software) | **Strong** | **We lead** |
| Swiss data residency / DSG / EPDG engineering | Implied (Swiss firm) but not a product feature | **Strong, explicit, enforced** | **We lead** |
| Grounded GenAI copilot with citations & audit | Not evidenced | **Strong** | **We lead** |
| Governance, lineage, auditability, Responsible AI | Not evidenced as a platform feature | **Strong** | **We lead** |

### 5.2 Reading of the map

- **We are technically ahead** on cloud architecture, compliance/residency, MLOps, grounded GenAI, and auditability — exactly the areas a boutique consultancy typically does *not* build itself.
- **They are ahead on scope and operating model** — OR, staffing, rooms/equipment, integral optimisation, simulation, the command-center cadence, and Lean process transformation.
- The overlap (ED forecast, bed state, discharge) is real but **complementary**: our AI depth × their process rigor is additive.

The strategic conclusion: **absorb VR&P's scope and operating-model concepts into our platform; keep our architectural and compliance advantages as the moat.**

---

## 6. Business Analysis

### 6.1 Enhanced value proposition

Today's positioning ("provider-internal AI operational copilots for ED, beds and discharge") should evolve to:

> **"A Swiss-resident Integral Capacity Management platform and Hospital Command Center — AI-driven planning and real-time steering of beds, OR, staff, rooms and equipment, from the 72-hour operational horizon to strategic what-if planning, delivered with a proven command-center operating model."**

This reframes the product from a point solution to the **system-of-record for hospital capacity**, which:

- expands the addressable value from ED/discharge efficiency to **OR throughput** (typically the largest revenue and cost centre in an acute hospital);
- makes the platform relevant to **CFO/COO and medical-director buyers**, not only operations teams;
- differentiates against both pure consultancies (we add the engineered, compliant, auditable platform) and pure analytics tools (we add integral scope + operating model).

### 6.2 Target scenarios unlocked

1. **New-building / campus commissioning (the Kispi pattern).** Switzerland has an active pipeline of hospital new-builds and consolidations. A greenfield move is the ideal moment to standardise processes and stand up an HCC. We should package a **"new-hospital capacity commissioning"** offer (process standardisation + simulation for the new footprint + HCC stand-up). This is directly evidenced by the Kispi case.
2. **Brownfield efficiency turnaround.** For providers under margin pressure (e.g. the Zollikerberg CHF −1.2m 2024 result, "Agenda 2027" efficiency programme), lead with **potential analysis → OR/discharge optimisation → HCC**.
3. **Elective-surgery-led providers (e.g. Hirslanden).** Our own provider analysis already identifies OR-to-bed coordination and elective surgical flow as the primary lever at Hirslanden — an OR module makes that provider a much stronger fit.

### 6.3 Commercial / packaging model to adopt

Mirror VR&P's maturity tiers, but as **platform SKUs**:

| Tier | Offer | Platform mapping |
| --- | --- | --- |
| **T0 Potential analysis** | Data + process assessment, opportunity sizing | Discovery engagement using our data-quality/lineage tooling + a Gemba/process review |
| **T1 Decision support** | Targeted capacity analytics on top of existing BI | Power BI + Fabric semantic models as a complement, no full rollout |
| **T2 Operational HCC** | ED forecast + bed + discharge + **OR steering**, React command center | Current MVP **+ OR module** |
| **T3 Integral HCC** | Add staffing, rooms, equipment, **scenario simulation**, cross-resource optimisation | Full IKM platform |
| **T3+ Managed steering** | Ongoing coaching, tactical/strategic decision support | Managed-service wrap around the platform |

This creates a **land-and-expand "Reiseroute"** that matches how VR&P sells and how hospitals actually mature — and gives Microsoft/partners recurring revenue beyond licences.

### 6.4 Outcome KPI framework (business value case)

Introduce an explicit **operational-outcome KPI layer** (distinct from our current technical SLOs), aligned to the outcomes VR&P and our own case-study brief already target:

- **OR:** utilisation %, short-notice cancellation rate, first-case on-time start, turnover time, idle-slot minutes.
- **Beds/flow:** occupancy %, ED boarding time, admission-to-bed time, elective cancellation due to no bed.
- **Discharge:** discharge-before-noon %, discharge-delay hours, blocker resolution time.
- **Staffing:** demand-to-roster match %, agency/overtime hours avoided.
- **System:** LOS vs. benchmark, patient and staff satisfaction.

Each KPI should have a baseline-capture step in T0 so value is measurable — the foundation of the business case and of managed-service renewal.

### 6.5 Partnering consideration

VR&P is a plausible **implementation/process partner**, not only a benchmark. Their Lean/Design-Thinking/Gemba capability and clinical-operations credibility complement our platform engineering. A **co-sell / co-delivery** model (VR&P runs process transformation + HCC operating model; we provide the compliant Azure platform and AI) could accelerate Swiss market entry. This should be explored explicitly, with IP and data-governance boundaries defined up front.

### 6.6 Business risks

- **Scope creep / dilution.** Widening from 3 use cases to full IKM risks slowing the MVP. Mitigate with the tiered SKUs — OR first, then integral.
- **Change-management dependency.** IKM value depends on process adoption, not just software. Under-investing in the operating model is the classic failure mode. The Kispi results came from process + tool together.
- **Buyer complexity.** Broader scope means more stakeholders (surgical, anaesthesia, nursing, HR). Longer sales cycles; needs executive sponsorship.
- **Competitive framing.** If VR&P is a partner in one deal and a competitor in another, channel conflict must be managed.

---

## 7. Technical Analysis and Incorporation Blueprint

This section translates the gaps into concrete, architecture-consistent changes. Everything below stays inside the existing principles: GA-only critical path, Swiss PHI residency, provider-internal boundary, advisory/HITL AI, IaC-first, evidence-first governance.

### 7.1 Extended reference architecture

Add three capability blocks to the current layered architecture without changing its shape:

```
Source & event layer      +  OR/surgical scheduling systems, anaesthesia,
                             staffing/rostering, room booking, biomedical/asset mgmt
Normalization             +  FHIR resources: Appointment, Slot, Schedule, Encounter(surgical),
                             ServiceRequest, PractitionerRole, Device, HealthcareService
Data platform (Fabric)    +  New curated domains: OR capacity, Staffing capacity,
                             Room/Equipment capacity  +  a Capacity Ontology (semantic layer)
AI & decision layer       +  OR optimisation model, Staffing-demand match model,
                             Scenario Simulation Engine (what-if / discrete-event)
Copilot & experience      +  OR-steering command view, HCC decision-cadence workbooks,
                             simulation console  +  new copilot skills
Orchestration             +  (unchanged pattern) triggers to OR/anaesthesia/staffing systems
```

### 7.2 New data domains and contracts

Extend the existing domain model (which today covers patient-flow, bed/capacity, staffing-context, discharge, partner events, AI trace, governance) with **managed** capacity domains, each with a versioned data contract in the established `DC-*` style:

| New domain | Purpose | Proposed contract(s) | Primary FHIR/CDM basis |
| --- | --- | --- | --- |
| **OR / surgical capacity** | Theatre slates, case durations, cancellations, turnover, anaesthesia consult status | `DC-OR-SCHEDULE-v1`, `DC-OR-CASE-v1` | `Appointment`, `Slot`, `Schedule`, surgical `Encounter`, `ServiceRequest` |
| **Staffing capacity** | Rosters, skills, availability, demand-to-supply match | `DC-STAFF-ROSTER-v1`, `DC-STAFF-DEMAND-v1` | `PractitionerRole`, `Schedule`, `Slot` |
| **Room & equipment capacity** | Room availability, biomedical device availability/PM windows | `DC-ROOM-STATE-v1`, `DC-DEVICE-STATE-v1` | `Location`, `HealthcareService`, `Device` |
| **Scenario / simulation** | Scenario definitions, assumptions, run outputs | `DC-SIM-SCENARIO-v1`, `DC-SIM-RESULT-v1` | bespoke |

These extend — and reuse the partition-key, minimisation and validation patterns of — the existing `DC-SUPPLY-LOCATION-v1` / `DC-DEMAND-ENCOUNTER-v1` / `DC-MATCH-RECOMMENDATION-v1` data-product family already defined for capacity planning. The Sprint-6 provider-extension mechanism (`DC-ONB-CAPACITY-*`) is the right template for provider-specific OR/staffing profiles (Hirslanden OR-heavy; Zollikerberg virtual-ward/HaH).

### 7.3 New AI / analytics capabilities

1. **OR optimisation & steering model.** Predict case durations and cancellation risk; flag idle slots and over-runs; propose early day-plan adjustments. Directly mirrors the Kispi OR-steering dashboard. Advisory + HITL, consistent with `NFR-AI-001`.
2. **Staffing-demand match.** Compare predicted demand (from the forecast + OR slate + census) against rostered supply by skill/ward; surface under/over-staffing windows. Turns staffing from a passive signal into a managed dimension.
3. **Scenario Simulation Engine (the biggest net-new AI/analytics asset).** A tactical/strategic **what-if / discrete-event simulation** capability that models future states: patient-mix growth, schedule changes (e.g. "orthopaedics operates Mondays"), new-building footprints, and identifies resulting bottlenecks *and* over-capacity. This answers VR&P's headline scenario questions and extends us from *operational forecasting* to *strategic capacity planning*. Candidate realisation: Azure ML + a simulation library (e.g. SimPy-class discrete-event modelling) running as Azure Container Apps jobs, reading Fabric curated capacity data, writing `DC-SIM-RESULT-v1`. *(Implementation shape is an inference to validate.)*
4. **Cross-resource ("integral") optimisation.** Where feasible, jointly evaluate OR + bed + staff feasibility so a recommended OR plan is checked against downstream bed and staff capacity — operationalising IKM's balance principle.

### 7.4 New agents and copilot skills

Extend the OOA/DCA/BMCA agent set:

- **OR Steering Agent (ORSA)** — surfaces slate risk, idle slots, cancellation-avoidance actions; advisory/HITL.
- **Capacity Simulation Agent (CSA)** — lets planners pose natural-language what-if questions grounded in `DC-SIM-*` outputs.
- **Staffing Balance Agent (SBA)** — flags staffing/demand mismatch windows.

All follow the existing deterministic-service-vs-agentic-flow classification, remain advisory, retrieval-grounded and audit-traceable, and inherit the same Swiss-region inference and prompt-governance controls.

### 7.5 Fabric IQ Ontology becomes strategically justified

Architecture Pattern 1 (Fabric IQ Ontology + Data Agents) is currently *deferred* because it is preview and not required for the 3-use-case MVP. **Integral capacity management is the use case that justifies it.** An explicit **Capacity Ontology** — formalising patient flow, capacity unit, OR slot, staff role, room, discharge readiness, transfer window and their relationships — is exactly what keeps five resource domains semantically consistent across dashboards, models, simulation and copilot, and it strengthens explainability/traceability (`NFR-AI-003/004`). Recommendation: keep it off the *near-term* OR-module critical path (GA/residency gating still applies), but elevate it from "optional" to "**the target semantic backbone for the integral tier**," with a minimal ontology bounded to OR + bed + staff first.

### 7.6 Hospital Command Center — the operating-model layer

The React command center and Power BI views are necessary but not sufficient. Add an **HCC operating-model layer** as a first-class deliverable:

- **Decision cadences:** daily operational huddle views, tactical (weekly) and strategic (monthly/quarterly) planning views — each a governed Power BI/semantic surface with the relevant horizon (real-time → 72h → simulation).
- **Roles & RACI:** a capacity-command RACI extending the existing operations RACI (who owns OR steering, staffing balance, discharge escalation).
- **Playbooks:** standardised responses to bottleneck states ("acute bed shortage," "OR over-run," "staffing gap"), echoing Kispi's "clearly structured discharge processes reliable even during acute bottlenecks."
- **Coaching/managed-service hooks:** telemetry and KPI packs that support ongoing decision support (the T3+ tier).

### 7.7 Process-standardisation front end (Lean / Design Thinking / Gemba)

Add a **pre-platform discovery and standardisation method** to the delivery model, not the codebase:

- **Gemba + data discovery** to map current OR/bed/discharge/staffing workflows (VR&P's exact method).
- **Process harmonisation & standardisation** to a "standard base model" before digitalisation — this is what made Kispi's unified operating logic possible, and it also improves our **multi-provider reusability** (`NFR-MAINT-004`).
- **Clear responsibility rules and interface harmonisation** captured as configuration and RACI.
- **Change management / interprofessional collaboration** design as an explicit workstream.

This is best delivered via a **partner-led services layer** (potentially VR&P) wrapped around the platform.

### 7.8 Compliance, residency and governance — unchanged and reused

Every new domain, model and agent inherits the existing controls with **no relaxation**: Swiss-region PHI inference only; Global/Data-Zone/Developer deployment types blocked for PHI; cross-region PHI failover default-deny; data contracts with classification/residency tags; Purview lineage; retention classes; end-to-end audit trace; advisory/HITL AI. New OR/staffing data is largely **operational-confidential** rather than deep PHI, which *eases* residency handling for those domains, but the same classification-first discipline applies. This preserved rigor is precisely our differentiator versus a consultancy-plus-partner-software stack.

### 7.9 Requirement crosswalk (proposed new families)

Extend the PRD with new requirement families that slot into the existing FR/NFR structure:

| Proposed family | Scope | Anchored to existing |
| --- | --- | --- |
| **FR-OR-00x** | OR slate ingestion, case-duration & cancellation prediction, idle-slot steering, anaesthesia-consult status | extends FR-FC / FR-CX |
| **FR-STAFF-00x** | Staffing capacity ingestion, demand-to-roster match, gap surfacing | new; reuses FR-DATA patterns |
| **FR-CAP-00x** | Room & equipment capacity state | new; reuses FR-DATA patterns |
| **FR-SIM-00x** | Scenario definition, simulation runs, bottleneck/over-capacity outputs | new; consumes curated + AI domains |
| **FR-HCC-00x** | Decision-cadence surfaces, capacity RACI, bottleneck playbooks | extends FR-CX / FR-GOV |
| **NFR-KPI-00x** | Operational-outcome KPI capture and baselining | extends OPERATIONS KPI baseline |

Existing NFR families (compliance, security, DQ, performance, reliability, AI, maintainability) apply unchanged to the new families.

---

## 8. Phased Incorporation Roadmap

Aligned to the existing sprint/phase delivery model and the tiered SKUs.

| Horizon | Objective | Key deliverables | SKU |
| --- | --- | --- | --- |
| **Now → near-term** | Prove the OR gap-close | OR data contracts (`DC-OR-*`), OR-steering command view + KPIs, ORSA agent (advisory), Gemba/process discovery method, outcome-KPI baselining | T2 |
| **Mid-term** | Integral resource scope | Staffing + room/equipment domains, staffing-demand match (SBA), minimal Capacity Ontology (OR+bed+staff), HCC operating-model layer (cadences, RACI, playbooks) | T3 |
| **Longer-term** | Strategic planning + managed steering | Scenario Simulation Engine (CSA), cross-resource optimisation, new-building commissioning offer, managed decision-support service, full ontology + Data Agents (subject to GA/residency) | T3 / T3+ |

Sequencing rationale: **OR first** delivers the highest, most visible operational value (the Kispi flagship) with the least architectural disruption; **integral scope and the operating model** create the durable differentiation; **simulation and managed steering** open the strategic-planning and recurring-revenue frontier.

---

## 9. Risks, Dependencies and Open Questions

**Delivery risks**

- Scope expansion could destabilise the MVP timeline → contain via OR-first T2 before integral T3.
- Simulation is a genuinely new capability class (skills, validation, data) → treat as a distinct workstream with its own acceptance criteria; label current technical assumptions (e.g. discrete-event approach) as *to be validated*.
- OR/staffing source-system integration is provider-specific and can be complex (surgical scheduling and rostering systems vary widely) → discovery-led, contract-first.

**Dependencies**

- Fabric IQ Ontology GA + Switzerland-region availability for the integral semantic backbone (already a tracked gate).
- Access to OR, anaesthesia and rostering source systems per provider.
- Executive sponsorship for the process/operating-model change (the non-software half of IKM value).

**Open questions to resolve (ideally with VR&P and pilot providers)**

1. VR&P's actual software-partner stack and data model — where would we integrate vs. replace vs. co-sell?
2. Which provider is the best OR-module pilot — Hirslanden (elective/OR-heavy) is the strongest technical fit per our own analysis.
3. Simulation fidelity required (strategic annual planning vs. weekly tactical) — drives the modelling approach.
4. Partner vs. build decision for the Lean/Design-Thinking/Gemba services layer.
5. KPI baseline availability at each target provider (needed for the value case).

---

## 10. Conclusion

The current platform and VR&P's IKM/HCC are two halves of the same target picture. We have built the **compliant, auditable, AI-grounded technology core**; VR&P has proven the **integral scope and the operating model** that turn that core into hospital-wide capacity transformation. The path to a category-leading Swiss offering is clear and low-risk architecturally:

1. **Close the OR gap first** — the single highest-value, most visible move.
2. **Widen to integral scope** — staffing, rooms, equipment, and cross-resource balance.
3. **Add strategic simulation** — from 72-hour forecasting to true what-if planning.
4. **Wrap it in a Hospital Command Center operating model** — roles, cadences, playbooks, coaching — underpinned by a Lean/Design-Thinking process method.
5. **Package for maturity-tiered adoption and new-building commissioning**, with a business-outcome KPI framework proving the value.

Doing this keeps our compliance and architecture advantages as the moat while adopting exactly the know-how that makes VR&P's IKM/HCC compelling — and positions the platform as the **Swiss-resident system-of-record for integral hospital capacity management**.

---

### Appendix A — Source terminology (VR&P, English gloss)

| German term | English gloss |
| --- | --- |
| Integrales Kapazitätsmanagement (IKM) | Integral / integrated capacity management |
| Hospital Command Center (HCC) | Central real-time capacity control hub |
| Gemba-Walk | On-site process observation (Lean) |
| Austrittsmanagement (24/7) | 24/7 discharge management |
| OP-Steuerung / OP-Leerlaufzeiten | OR steering / OR idle time |
| Anästhesie-Sprechstunde | Anaesthesia pre-op consultation |
| Schnittstellenharmonisierung | Interface harmonisation |
| Reiseroute | Adoption journey / roadmap |
| Bettenbelegung | Bed occupancy |

### Appendix B — Document set reviewed

Current platform: PRD v1.3, ARCHITECTURE v0.12, AI v0.5, DATA v0.5, INFRASTRUCTURE v1.3, OPERATIONS v1.2, SD v1.3, Case Study 26 brief, four-provider capacity analysis. VR&P: IKM/HCC service page; Universitäts-Kinderspital Zürich case study.
