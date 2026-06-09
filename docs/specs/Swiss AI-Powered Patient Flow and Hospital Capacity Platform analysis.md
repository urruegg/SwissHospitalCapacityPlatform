# Swiss AI-Powered Patient Flow and Hospital Capacity Platform analysis

## Baseline reference providers

USZ and LUKS are used as baseline references for scale and operating patterns.
The platform pattern is reusable for other Swiss hospitals.

---

## 1) Scope, positioning, and what changed

This analysis defines a provider-internal platform pattern.
It is not a cantonal shared platform and not a multi-provider shared tenancy.
The platform is instantiated inside one hospital provider at a time, for example:

- Universitatsspital Zurich (USZ)
- Luzerner Kantonsspital (LUKS)

The second provider is used as a reference baseline only, not as a co-owner or shared-governance participant.

Publicly shared scale indicators support the need for a dedicated provider deployment:

- USZ reports around 45,000 emergency patients per year
- USZ reports around 41,138 stationary discharges in 2024
- LUKS Group reports more than 50,000 stationary patients in 2024
- LUKS Group reports more than 925,000 ambulatory contacts in 2024

### Core value (narrowed)

The platform is explicitly focused on AI-powered operational copilots for hospital operations teams.
It is not positioned as:

- A broad workflow/case-management platform
- A cantonal shared operating platform for external actors

External actors such as Spitex, rehabilitation clinics, transport services, and nursing homes are integration endpoints only.

### Explicitly out of scope

Dynamics 365 Customer Service / Care Coordination is out of scope in this analysis.

### Technology focus retained

- Microsoft Fabric (analytics backbone)
- Azure Health Data Services (healthcare-grade normalization where needed)
- Azure Machine Learning (predictive models)
- Azure OpenAI (copilot layer)
- Azure Logic Apps (integration orchestration)
- Power BI (operational analytics)

---

## 2) Executive view - what this platform is and is not

### Positioning statement

A provider-internal AI operational control layer for one hospital provider (for example USZ or LUKS) that improves:

- Emergency demand anticipation
- Discharge readiness coordination
- Bed/capacity decision support

This happens inside the provider boundary, with controlled integration to external care partners.

### In scope

- 72-hour forecasting of emergency demand within one target provider
- Discharge coordination AI inside the provider, with partner notifications by integration
- GenAI bed management copilot for internal operations teams
- Fabric-based provider-internal analytical platform
- Logic Apps for outbound/inbound integration only

### Out of scope

- Cantonal multi-provider shared operating model
- Shared governance/data ownership across providers
- External partner direct platform access
- Dynamics 365 case-management UI scenarios
- Full clinician workstation replacement

---

## 3) Why USZ and LUKS are the right baseline references

USZ is a strong public baseline for emergency demand forecasting and bed operations signals.
LUKS is a strong public baseline for discharge coordination patterns and interdisciplinary discharge workflows.

The architectural pattern is the same for both, but initial sequencing can differ:

- USZ-first: 72-hour ED forecasting + bed copilot
- LUKS-first: discharge coordination AI + bed copilot

The scope remains provider-internal in both cases.

---

## 4) Public capacity baseline governing design

Federal and provider public data indicates operational scale is sufficient to justify a dedicated AI operational platform.

A caveat remains: some 2024 Swiss reporting comparability is limited due to transition effects in national publication models.
Therefore, public figures should be used as order-of-magnitude anchors, then validated with provider-native data.

### 4.1 Public facts used as sizing anchors

| Public fact | Value | Type | Source |
| ----------- | ----- | ---- | ------ |
| Switzerland hospitalizations in 2024 | 1,549,037 | Public fact | BFS patient and hospitalization statistics |
| Switzerland ambulatory hospital patients in 2024 | 4,414,274 | Public fact | BFS patient and hospitalization statistics |
| Switzerland acute LOS in 2024 | 4.9 days (men), 4.8 days (women) | Public fact | BFS patient and hospitalization statistics |
| Hospitals in Switzerland (2024) | 270 | Public fact | BFS health system statistics |
| Beds in Swiss hospitals (2024) | 37,792 | Public fact | BFS health system statistics |
| USZ emergency patients/year | 45,000 | Public fact | USZ emergency medicine page |
| USZ stationare patient count (annual reporting) | 41,151 | Public fact | USZ annual report 2024 |
| USZ stationare Austritte in 2024 | 41,138 | Public fact | USZ operational release |
| LUKS stationary patients in 2024 | over 50,000 | Public fact | LUKS annual release |
| LUKS ambulatory contacts in 2024 | over 925,000 | Public fact | LUKS annual release |
| Canton Luzern stationary cases in 2024 | 66,300 | Public fact | LUSTAT canton statistics |
| Canton Luzern acute cases in 2024 | 60,100 | Public fact | LUSTAT canton statistics |
| Canton Luzern acute LOS in 2024 | 4.8 days | Public fact | LUSTAT canton statistics |
| Canton Luzern acute beds in 2024 | 929 | Public fact | LUSTAT canton statistics |
| LUKS discharge-planning update deadline | daily by 10:30 | Public fact | LUKS discharge planning publication |

### 4.2 What public data does not provide exactly

The public sources in this analysis do not provide, with complete precision:

- Exact 2024 annual ED total for LUKS
- Complete provider monthly ED time series
- ED-to-inpatient conversion rates
- Exact annual counts for Spitex/rehab/nursing-home handoffs

Therefore, selected NFRs below are architectural assumptions and must be validated in provider data discovery.

---

## 5) AI infusion points (single-provider precision)

### 5.1 Use case 1 - 72-hour demand forecasting

Goal:

- Predict emergency demand/admission pressure by specialty and time window within one provider

Architecture implication:

- Model on provider-internal ED arrivals and downstream capacity signals (beds, discharges, staffing)
- 72-hour horizon
- Specialty and time-bucket outputs

### 5.2 Use case 2 - discharge coordination AI

Goal:

- Identify inpatients approaching discharge readiness inside the provider
- Trigger integration-based downstream actions

Architecture implication:

- Score/rank active inpatients inside provider systems
- Use integration endpoints for external partners
- Write partner acknowledgements/status back into provider analytics

### 5.3 Use case 3 - GenAI bed management copilot

Goal:

- Provide operations teams with real-time insights and recommendations:
  - Current bed state
  - Predicted pressure windows
  - Likely same-day discharges
  - Bottleneck explanations

Architecture implication:

- Copilot must be retrieval-grounded on provider operational data and model outputs
- Copilot remains advisory; human operators retain decision authority

---

## 6) Capacity-driven non-functional requirements (NFRs)

### 6.1 Core volume assumptions per provider

| Dimension | USZ baseline | LUKS baseline | Label | Basis |
| --------- | ------------ | ------------- | ----- | ----- |
| ED arrivals/year | 45,000 | Not publicly identified in retrieved sources | Public fact / gap | USZ emergency page |
| Stationary episodes/year | 41,138 discharges / 41,151 treated inpatients | over 50,000 stationary patients | Public fact | USZ and LUKS public sources |
| Average stationary flow/day | about 113/day | over 137/day | Architectural assumption | annual total / 365 |
| Average ED arrivals/day | about 123/day | Not public in retrieved sources | Architectural assumption from public fact | 45,000 / 365 |
| Average ED arrivals/hour | about 5.1/hour | Not public in retrieved sources | Architectural assumption from public fact | 45,000 / 365 / 24 |
| Active inpatient census | about 541 lower bound | over 658 lower bound | Architectural assumption | annual stationary volume x 4.8-day acute LOS proxy / 365 |

### 6.2 Resulting NFR set

| NFR area | Refined requirement | Fact vs assumption | Why |
| -------- | ------------------- | ------------------ | --- |
| Throughput | Treat platform as operational event platform, not monthly reporting | Derived from public facts | USZ/LUKS volumes justify event-driven design |
| Ingestion frequency | Near-real-time ingestion for ED, ADT/bed state, discharge status | Architectural requirement from operating pattern | 24/7 ED and daily discharge operations |
| Forecast inference cadence | Hourly refresh for 72-hour forecast | Architectural assumption | Operationally useful cadence |
| Discharge scoring cadence | Re-score inpatients multiple times/day | Architectural assumption | Discharge context changes intraday |
| Retention | Keep 3-5 years history for seasonality and drift | Architectural assumption | Multi-year normalization and model stability |
| Availability | Continuous operational service (not overnight batch-only) | Architectural requirement | Operational workflows are continuous |
| Peak headroom | Explicit burst headroom over average throughput | Architectural assumption | Public data lacks full provider peak curves |
| Auditability and explainability | Trace every score, answer, and outbound trigger to source/time context | Architectural requirement | Regulated healthcare and operational-critical decisions |

### 6.3 Example inference sizing (architectural assumptions)

If one provider forecasts 10 specialty cohorts, with 72 hourly forecast buckets and hourly refresh:

- 10 x 72 x 24 = 17,280 forecast values/day per provider

If discharge AI re-scores active inpatients 4 times/day:

- USZ lower-bound scoring volume: about 541 x 4 = about 2,164 scores/day
- LUKS lower-bound scoring volume: over 658 x 4 = over 2,632 scores/day

These are design-level implications from public baseline values, not published hospital operational KPIs.

---

## 7) Refined logical architecture

### 7.1 Architecture principles

1. Provider-owned and provider-governed operation model
2. Operational intelligence first
3. External actors as integration endpoints only
4. Copilot grounded in provider operational truth

### 7.2 Architecture layers

#### A) Source and event layer (provider-internal)

- KIS/EHR and patient administration
- ED operational systems
- Bed management/transfer/location systems
- Staffing and planning systems
- Orders/discharge directives/therapy milestones/operational notes

#### B) Healthcare data normalization

- Azure Health Data Services where FHIR-oriented normalization is beneficial

#### C) Analytical backbone

- Microsoft Fabric + OneLake
- Data Engineering, Data Factory, Real-Time Intelligence, Data Science, Power BI

#### D) AI/ML layer

- Azure Machine Learning for forecasting and discharge models
- Azure OpenAI for copilot reasoning
- Fabric Data Science integration where appropriate

#### E) Integration layer

- Azure Logic Apps for outbound/inbound orchestration

#### F) Serving layer

- Power BI operational command views
- GenAI copilot response layer for operations

---

## 8) Explicit data flows for the three AI use cases

### 8.1 Forecasting flow

ED/KIS/bed/staffing events -> normalization (where needed) -> Fabric OneLake -> feature engineering -> Azure ML forecast model -> provider-specific 72-hour outputs -> Power BI and copilot grounding

### 8.2 Discharge coordination flow

ADT/census/discharge intent/therapy milestones/blockers -> normalization -> Fabric curated data -> Azure ML readiness model -> ranked candidates + reasons -> Logic Apps outbound integration -> acknowledgements back to Fabric -> Power BI and copilot

### 8.3 Bed copilot flow

Current bed census + forecast + discharge readiness + staffing/capacity signals -> Fabric semantic model -> Azure OpenAI grounded retrieval -> responses and recommendations -> optional action suggestions for human operators

---

## 9) Service mapping (refined scope)

| Use case | Primary Microsoft services | Fit for scope |
| -------- | -------------------------- | ------------- |
| 72-hour emergency demand forecasting | Fabric, Azure Health Data Services, Azure Machine Learning, Power BI | End-to-end analytical and predictive workflow inside provider boundary |
| Discharge coordination AI | Fabric, Azure Health Data Services, Azure Machine Learning, Azure Logic Apps, Power BI | Internal scoring + integration endpoint orchestration |
| GenAI bed management copilot | Fabric, Power BI, Azure OpenAI | Grounded operational assistant over provider data |
| Cross-cutting health data layer | Azure Health Data Services | FHIR-oriented healthcare data normalization and secure handling |
| Cross-cutting analytics backbone | Microsoft Fabric | Unified ingestion, transformation, real-time analytics, reporting |
| Cross-cutting integration | Azure Logic Apps | Orchestration for external endpoint interactions |

---

## 10) How public capacity data should govern architecture

### 10.1 What public data justifies immediately

- USZ scale already justifies real-time forecasting and bed/capacity support
- LUKS scale and documented discharge process justify intraday discharge-readiness AI and partner coordination integrations
- National Swiss scale confirms this is mainstream operational demand, not edge-case complexity

### 10.2 What must be validated in provider-native discovery

Before implementation sizing is finalized, validate:

- ED event rates by hour/day/specialty
- Boarder/transfer/bed-state event volumes
- Discharge blocker classes and frequencies
- Partner response and acknowledgement timing distributions

---

## 11) Swiss regulatory and operating interpretation for this scope

A provider-internal first deployment avoids turning first release into cross-provider governance redesign.
This keeps:

- Data ownership clear
- Model and prompt governance local to provider
- Integration policy controlled by provider operations and compliance

External coordination remains critical, but is handled as integration endpoints, not shared platform governance.

---

## 12) Source families used in this analysis

- USZ public emergency and annual reporting pages
- LUKS public annual reporting and discharge-planning pages
- BFS (Swiss Federal Statistical Office) health and hospitalization statistics
- BAG publication context for 2024 hospital key figures caveats
- LUSTAT canton Luzern hospital statistics
- Microsoft documentation for Fabric, Azure Health Data Services, Azure Machine Learning, Azure OpenAI, and Logic Apps

---

---

# Extended Provider Analysis

## 13) Klinik Hirslanden, Zürich — Provider Profile and Platform Fit

### 13.1 Overview and positioning

Klinik Hirslanden is the flagship clinic of the Hirslanden Group, the largest private medical network in Switzerland. The Hirslanden Group operates 17 clinics and more than 300 medical centers and institutes across Switzerland, and is part of the Mediclinic International group, now privately held by Richemont patron Johann Rupert and the Geneva-based MSC shipping group.

Klinik Hirslanden is located at Witellikerstrasse 40, 8032 Zürich, within the Gesundheitscluster Lengg (Lengg health cluster). It serves patients of all insurance categories — basic, semi-private, and private — and positions itself as a leading healthcare provider from birth to advanced age.

In the Newsweek World's Best Hospitals 2026 ranking, Klinik Hirslanden achieved position 56 globally (up from 65) and ranked 5th in Switzerland, reflecting sustained clinical quality and technology investment.

### 13.2 Public capacity baseline (FY 2024/2025)

The Hirslanden fiscal year runs from 1 April to 31 March. The figures below cover the period 1 April 2024 to 31 March 2025.

| Public fact | Value | Type | Source |
| ----------- | ----- | ---- | ------ |
| Beds | 335 | Public fact | Klinik Hirslanden Kennzahlen 2024/2025 |
| Operating rooms | 14 | Public fact | Klinik Hirslanden Kennzahlen 2024/2025 |
| Delivery rooms | 3 | Public fact | Klinik Hirslanden Kennzahlen 2024/2025 |
| Inpatients and women in childbed (FY 2024/25) | 20,097 | Public fact | Klinik Hirslanden Kennzahlen 2024/2025 |
| Emergency entries (FY 2024/25) | 12,898 | Public fact | Klinik Hirslanden Kennzahlen 2024/2025 |
| Newborns (FY 2024/25) | 916 | Public fact | Klinik Hirslanden Kennzahlen 2024/2025 |
| Inpatient admissions (FY 2023/24, excl. newborns) | 19,825 | Public fact | Hirslanden Group annual case data |
| Affiliated and employed doctors | 499 | Public fact | Klinik Hirslanden Kennzahlen 2024/2025 |
| Employees (excl. employed doctors) | 1,879 | Public fact | Klinik Hirslanden Kennzahlen 2024/2025 |
| Occupational groups | 96 | Public fact | Klinik Hirslanden Kennzahlen 2024/2025 |
| Nationalities represented | 67 | Public fact | Klinik Hirslanden Kennzahlen 2024/2025 |
| Hirslanden Group average LOS (FY 2023/24) | 4.0 days | Public fact | Medinside Hirslanden annual reporting |
| Hirslanden Group stationary patients (FY 2023/24) | 112,000 | Public fact | Medinside Hirslanden annual reporting |

**Architectural volume derivations (assumptions):**

| Dimension | Klinik Hirslanden estimate | Basis |
| --------- | -------------------------- | ----- |
| Average stationary flow/day | about 55/day | 20,097 / 365 |
| Average ED arrivals/day | about 35/day | 12,898 / 365 |
| Average ED arrivals/hour | about 1.5/hour | 12,898 / 365 / 24 |
| Active inpatient census lower bound | about 220 | 20,097 × 4.0-day Hirslanden LOS / 365 |
| Active inpatient census with Swiss acute LOS | about 264 | 20,097 × 4.8 days / 365 |

**Interpretation:** Compared to USZ, Klinik Hirslanden operates with a substantially lower ED volume (12,898 vs 45,000 annual emergency entries). This reflects the predominantly elective and planned-surgery character of a private clinic. The active inpatient census of roughly 220–264 is smaller than USZ (~541) but still operationally significant at 335 available beds. The primary platform value at Hirslanden is concentrated in surgical scheduling coordination, elective admission pressure management, and discharge readiness — not high-volume emergency demand forecasting.

### 13.3 Clinical specialties and case mix

Based on Hirslanden Group FY 2023/24 inpatient case data (19,825 total for Klinik Hirslanden), the leading specialties by volume are:

| Specialty | Approximate volume (FY 2023/24) | Notes |
| --------- | ------------------------------- | ----- |
| Surgery / Visceral surgery | 3,263 | Largest single specialty |
| Cardiology | 3,078 | Including cardiac and thoracic vascular surgery cases |
| Gynecology / Obstetrics | 1,974 | Includes birth department with 3 delivery rooms |
| Orthopedics / Sports medicine | 2,047 | |
| Neurosurgery | 1,216 | |
| Urology | 1,418 | Key application area for Da Vinci robotic surgery |
| Internal medicine | 628 | |
| Neurology | 916 | |
| Radiology / Neuroradiology / Nuclear medicine | 609 | |

Surgery/visceral surgery, cardiology, and gynecology/obstetrics jointly account for roughly 40% of total inpatient volume, confirming the high-complexity elective surgical profile.

### 13.4 Technology and digital posture

Klinik Hirslanden has a documented strategy of continuous investment in medical technology. Key systems relevant to the AI platform context:

**Robotic surgery — Da Vinci platform (AI-infused):**
In December 2025, Klinik Hirslanden became the first hospital in Switzerland to deploy the Da Vinci 5 surgical system. The clinic now operates two Da Vinci systems in parallel: the established Da Vinci Xi and the new generation Da Vinci 5. The Da Vinci 5 has up to 10,000 times higher computing power than its predecessor and includes AI functions that evaluate kinematic movement data and surgical video recordings, providing operators with objective performance insights after each procedure. This is the first instance of AI-assisted surgical analytics at a Swiss hospital at this level.

**Radiosurgery and radiation oncology:**
The clinic operates a CyberKnife robotic radiosurgery system (image-guided tumour tracking, sub-millimetre accuracy) and TrueBeam linear accelerators. An INTRABEAM intraoperative radiation therapy system is also in use.

**Hybrid operating room:**
Klinik Hirslanden holds one of the most modern hybrid operating rooms in Europe, designed for interdisciplinary minimally invasive procedures, particularly in neurosurgery and cardiac surgery.

**Imaging:**
Full MRI, CT, PET-CT, mammography, ultrasound, and nuclear medicine suite through the Radiologie Hirslanden Zürich institute.

**Oncology:**
A certified Tumorzentrum Hirslanden Zürich (tumour centre) with structured oncology pathways.

**Telemedicine access layer:**
The Hirslanden Healthline provides telephone-based triage and specialist matching for patients across the group network.

**Current AI/digital gap relative to the platform:**
No public evidence was found of a deployed operational AI platform for real-time patient flow, bed management, or discharge coordination at Klinik Hirslanden. The Da Vinci 5 AI use is clinical/procedural, not operational. This represents a greenfield opportunity for the platform described in this analysis.

### 13.5 Platform fit assessment — Klinik Hirslanden

| Platform use case | Fit rating | Rationale |
| ----------------- | ---------- | --------- |
| 72-hour ED demand forecasting | Moderate | ED volume (~12,898/year) is lower than USZ, but real-time ED triage and inpatient admission routing remain relevant. Elective admissions dominate — forecast horizon may usefully extend to 5–7 days for planned surgery weeks. |
| Discharge coordination AI | High | With a 335-bed inpatient base, multi-specialty surgical case mix, and short LOS target (Hirslanden group average 4.0 days), intraday discharge readiness scoring directly supports OR throughput and bed turnover. |
| GenAI bed management copilot | High | 14 operating rooms, 96 occupational groups, and a complex multi-specialty layout make a grounded operational copilot directly valuable for bed coordinators and flow managers. |

**Sequencing recommendation for Hirslanden:** Start with discharge coordination AI and the bed management copilot. The elective surgical pipeline makes discharge predictability the primary capacity lever. ED forecasting is secondary but still useful for unplanned admissions flowing through the 24/7 emergency number.

**Adaptation notes:**
- Hirslanden fiscal year is April–March: data ingestion schedules and retention windows must account for this if historical data is seeded from public Hirslanden releases.
- Private clinic governance: data governance and consent models will differ from cantonal/public hospital settings. Provider-owned architecture aligns well with Hirslanden's ownership structure.
- The Da Vinci 5 AI data stream (kinematic/video analysis) is surgical-layer only and does not feed operational bed/flow systems. It is out of scope for this platform but signals organizational readiness for AI adoption.

### 13.6 Volume-driven NFR implications — Klinik Hirslanden

| NFR area | Hirslanden-specific implication | Label |
| -------- | ------------------------------- | ----- |
| Discharge scoring volume | about 220 active inpatients × 4 re-scores/day = about 880 scores/day | Architectural assumption |
| ED forecast volume | Smaller event stream than USZ; 10 specialty cohorts × 72 hours × 24 = 17,280 values/day still apply | Derived |
| Elective admission horizon | Extend forecast to cover elective surgical admissions list (5–7 days) | Provider-specific requirement |
| OR scheduling integration | Ingest planned OR schedule as a discharge timing signal | Architectural adaptation |
| LOS target | Hirslanden group average is 4.0 days vs 4.8–4.9 Swiss average; discharge models must be calibrated to this shorter LOS | Architectural adaptation |

---

## 14) Spital Zollikerberg — Provider Profile and Platform Fit

### 14.1 Overview and positioning

Spital Zollikerberg is a public-mandate regional hospital (Regionalspital) located in the municipality of Zollikerberg, southeast of the city of Zürich. It operates under a public service mandate (öffentlicher Leistungsauftrag) for the greater Zürich area and is a member of the VZK (Verband Zürcher Krankenhäuser), carrying the HQuality® quality label.

The hospital is governed by the Stiftung Diakoniewerk Neumünster and is part of the broader Gesundheitswelt Zollikerberg — an integrated care ecosystem accompanying patients from birth to end of life. The institution traces its roots to 1858 (Kranken- und Diakonissenanstalt Neumünster) and moved to Zollikerberg in 1933.

A key differentiator is Spital Zollikerberg's role as a Swiss pioneer in Hospital-at-Home care: since 2021 it has operated the first acute-somatic Hospital-at-Home programme in Switzerland ("Visit – Spital Zollikerberg Zuhause®"), and it hosted the first Hospital-at-Home Congress in Switzerland in November 2024.

### 14.2 Public capacity baseline (2024)

All figures below are calendar year 2024 unless stated.

| Public fact | Value | Type | Source |
| ----------- | ----- | ---- | ------ |
| Beds | 174 | Public fact | Spital Zollikerberg website (Über uns) |
| Operating rooms | 7 | Public fact | Spital Zollikerberg Tätigkeitsbericht 2024 |
| Inpatient patients in 2024 | 11,775 | Public fact | xund24.ch / Spital Zollikerberg 2024 report |
| Ambulatory treatments in 2024 | 65,207 | Public fact | xund24.ch / Spital Zollikerberg 2024 report |
| Inpatient operations in 2024 (record) | 4,884 | Public fact | Spital Zollikerberg Tätigkeitsbericht 2024 |
| Ambulatory surgeries in 2024 | 2,484 | Public fact | xund24.ch / Spital Zollikerberg 2024 report |
| Total operations in 2024 | 7,368 | Public fact | xund24.ch / Spital Zollikerberg 2024 report |
| Births in 2024 | 2,200 | Public fact | Spital Zollikerberg Tätigkeitsbericht 2024 |
| Neonates (NICU) in 2024 | 406 | Public fact | xund24.ch / Spital Zollikerberg 2024 report |
| Internal medicine inpatients in 2024 | 3,171 | Public fact | xund24.ch / Spital Zollikerberg 2024 report |
| Gynecology discharges in 2024 | 580 | Public fact | xund24.ch / Spital Zollikerberg 2024 report |
| Kinder-Permanence patients in 2024 | 11,165 | Public fact | xund24.ch / Spital Zollikerberg 2024 report |
| BrustCentrum Zürich patients in 2024 | 1,201 | Public fact | xund24.ch / Spital Zollikerberg 2024 report |
| Employees | approx. 1,200 | Public fact | Spital Zollikerberg website (Über uns) |
| Inpatient growth vs 2023 | +1.8% (11,565 in 2023) | Public fact | xund24.ch / Spital Zollikerberg 2024 report |
| Ambulatory growth vs 2023 | +0.9% (64,565 in 2023) | Public fact | xund24.ch / Spital Zollikerberg 2024 report |
| Patient satisfaction (inpatient, 2024) | 5.7 / 6.0 | Public fact | Spital Zollikerberg Tätigkeitsbericht 2024 |
| Recommendation rate | 5.9 / 6.0 | Public fact | Spital Zollikerberg Tätigkeitsbericht 2024 |
| Financial result 2024 | CHF -1.2 million | Public fact | xund24.ch / Spital Zollikerberg 2024 report |
| EBITDAR margin 2024 | 7.1% | Public fact | xund24.ch / Spital Zollikerberg 2024 report |
| Hospital-at-Home patients (cumulative to mid-2025) | over 340 | Public fact | Spital Zollikerberg website |

**Architectural volume derivations (assumptions):**

| Dimension | Spital Zollikerberg estimate | Basis |
| --------- | ---------------------------- | ----- |
| Average stationary flow/day | about 32/day | 11,775 / 365 |
| ED arrivals/year | Not publicly stated as a separate figure | Gap — ED volume embedded in total patient figures |
| Active inpatient census lower bound | about 155 | 11,775 × 4.8-day Swiss acute LOS proxy / 365 |
| Active inpatient census with national LOS | about 155 | Limited by 174 physical beds |
| Hospital-at-Home virtual patients (concurrent, order of magnitude) | single-digit to low double-digit | Based on 340+ cumulative patients since 2021 |

**Interpretation:** Spital Zollikerberg operates at a significantly smaller scale than USZ or LUKS, but its 174-bed inpatient unit runs at high utilisation given 11,775 annual inpatients. The 24/7 interdisciplinary emergency centre generates continuous inpatient admission pressure. The Hospital-at-Home programme creates an operationally unique dimension: a virtual ward of patients receiving hospital-equivalent care outside the physical building, monitored via telemedicine from within the hospital.

### 14.3 Clinical specialties and care model

Core service areas as publicly stated:

| Specialty area | Key facts (2024) |
| -------------- | ---------------- |
| Internal medicine | 3,171 inpatients (+3.5% vs 2023); largest single specialty |
| Gynecology and obstetrics | 580 discharges (+13.7% vs 2023); 2,200 births (one of Switzerland's top birth centres, 9th consecutive year over 2,000) |
| Neonatology | 406 neonates (+17% vs 2023) |
| Orthopedics / Spine surgery | Growing volume; specialized spine surgery included |
| General surgery | Included in 4,884 inpatient operations |
| Interdisciplinary emergency centre | 24/7, 365 days/year |
| Kinder-Permanence (paediatric outpatient) | 11,165 children (+6.3% vs 2023) |
| BrustCentrum Zürich (breast oncology) | 1,201 patients (+30.8% vs 2023); Q-label certified by Krebsliga and SGS |
| Hospital-at-Home ("Visit – Spital Zollikerberg Zuhause®") | Over 340 patients since 2021; telemedicine-monitored acute care at home |

The birth centre and neonatology unit generate time-sensitive, unplanned acute admissions around the clock, making the emergency-to-inpatient coordination signal highly relevant regardless of overall ED volume.

### 14.4 Innovation and digital posture

**Hospital-at-Home and telemedicine (strategic differentiator):**
Since 2021, Spital Zollikerberg has operated Switzerland's first acute-somatic Hospital-at-Home programme. Patients are admitted via the emergency department, then transferred to home care if clinically appropriate and within a 15-minute radius of the hospital. The general condition is monitored using telemedicine: chest electrodes continuously measure heart rate, respiratory rate, and oxygen saturation, allowing the hospital-at-home team to monitor the patient remotely and react to changes early. The programme has treated over 340 patients (ages 17–94, median age 67), with 93% indicating they would choose home-equivalent treatment again. Patient satisfaction ratings average 5.9/6 (patients) and 5.8/6 (relatives).

In November 2024, Spital Zollikerberg hosted the first Hospital-at-Home Congress in Switzerland, convening national and international experts on this care model. The hospital is a partner in a Berner Fachhochschule (BFH) research project on HaH evaluation, quality assurance, and technology integration.

By November 2025, Spital Zollikerberg and the Hospital at Home AG together had treated approximately 750 patients across both programmes.

**Agenda 2027 — operational transformation programme:**
The hospital has launched a foundation-wide steering committee focused on "Agenda 2027" with four strategic workstreams: efficient processes and structures, improved cross-divisional cooperation, service portfolio analysis, and new working-time models for 24-hour operations. This explicitly includes process efficiency and operational structure improvement — areas where AI-powered operational tools directly apply.

**Spital Zollikerberg Fachpraxen AG:**
Outpatient specialist practices have been reorganised under a new holding entity (Fachpraxen AG), bundling the GP practice at the Hottingen Health Centre, Prodorso AG (spine/orthopedics), and Onkologie Bellevue AG. This creates a more structured ambulatory referral pathway that generates upstream admission signals.

**Quality and governance:**
HQuality® certified (VZK member). BrustCentrum Zürich holds Q-label certification from Krebsliga and SGS (renewed for four years in 2024).

**Current AI/digital gap relative to the platform:**
No public evidence of a deployed operational AI platform for bed management, discharge coordination, or ED forecasting. The telemetric monitoring used in Hospital-at-Home is patient-clinical in nature, not connected to hospital-wide operational analytics. The hospital's Agenda 2027 workstreams on process efficiency and 24-hour operations create explicit organisational appetite for the platform use cases.

### 14.5 Platform fit assessment — Spital Zollikerberg

| Platform use case | Fit rating | Rationale |
| ----------------- | ---------- | --------- |
| 72-hour ED demand forecasting | Moderate-to-high | 24/7 emergency centre with continuous unplanned admission pressure from internal medicine, obstetrics, and neonatology. Volume is lower than USZ but the 174-bed constraint makes accurate demand forecasting high-value — a single unexpected surge directly affects bed availability across all wards. |
| Discharge coordination AI | High | 11,775 inpatients/year across a compact 174-bed unit means discharge timing is a critical daily constraint. The Hospital-at-Home programme adds a novel discharge pathway: some patients are not discharged home conventionally but transferred to the virtual ward. Discharge AI must recognise and route both conventional and Hospital-at-Home pathways. |
| GenAI bed management copilot | High | Small bed count (174) amplifies the impact of even minor mismatches between admission pressure and discharge readiness. A copilot providing real-time bed state, discharge candidate list, and predictive pressure windows is directly actionable at this scale. Agenda 2027 process efficiency goals support adoption. |

**Sequencing recommendation for Spital Zollikerberg:** Start with discharge coordination AI and the bed management copilot, consistent with the LUKS sequencing pattern. The hospital's Agenda 2027 operational efficiency focus and its existing culture of innovation (Hospital-at-Home) both increase the likelihood of organisational adoption. The Hospital-at-Home virtual ward creates a unique architectural extension: the platform should eventually model both physical and virtual bed state.

### 14.6 Hospital-at-Home as a novel architectural dimension

The Hospital-at-Home programme introduces a dimension not present in the USZ/LUKS baseline pattern: active inpatients physically located outside the hospital building but still under the hospital's care responsibility.

This has direct implications for the platform architecture if Spital Zollikerberg is a target provider:

| Dimension | Implication |
| --------- | ----------- |
| Patient census | Active patient count includes both physical inpatients and virtual (home) patients; discharge scoring must span both cohorts |
| Telemetry integration | Chest-electrode vital sign streams (heart rate, respiratory rate, SpO2) from home patients could serve as clinical deterioration signals feeding the discharge coordination model |
| Discharge pathway routing | Discharge AI must recognise three outcome pathways: conventional home discharge, transfer to Hospital-at-Home, and transfer to post-acute/rehabilitation |
| Integration endpoint | Hospital-at-Home team requires outbound notifications from the discharge coordination layer (Logic Apps integration endpoint pattern already defined in the base architecture) |
| Capacity model | Hospital-at-Home effectively creates overflow capacity: patients shifted to home free physical beds, directly affecting the forecast model's available-bed signal |

This is an architectural adaptation specific to Spital Zollikerberg. It does not change the base platform pattern but extends the patient census and discharge coordination data models to include a virtual ward dimension.

### 14.7 Volume-driven NFR implications — Spital Zollikerberg

| NFR area | Spital Zollikerberg-specific implication | Label |
| -------- | ---------------------------------------- | ----- |
| Discharge scoring volume | about 155 active inpatients × 4 re-scores/day = about 620 scores/day (physical ward only) | Architectural assumption |
| Virtual ward scoring | Low additional volume (single-digit to low double-digit concurrent HaH patients); vital sign telemetry adds a new event stream type | Architectural assumption |
| Capacity constraint sensitivity | Higher sensitivity than large hospital: each bed decision has proportionally greater impact at 174 beds vs 500+ beds | Derived |
| Birth centre surges | Overnight and weekend obstetric admissions create non-uniform admission patterns; forecast model must capture birth centre admission signal | Provider-specific requirement |
| Operational transformation context | Agenda 2027 means processes are in active change; platform onboarding should align with transformation workstream timelines | Provider context |

---

## 15) Extended capacity baseline — all four providers

This section expands the capacity reference table from section 4 and section 6 to include Klinik Hirslanden and Spital Zollikerberg alongside the existing USZ and LUKS baseline providers.

### 15.1 Comparative public capacity facts

| Provider | Beds | ED entries/year | Inpatients/year | Ambulatory/year | Operating rooms | Notes |
| -------- | ---- | --------------- | --------------- | --------------- | --------------- | ----- |
| USZ | Not stated in public sources | 45,000 | 41,151 (2024) | Not stated | Not stated | Public university hospital; largest single ED in the analysis |
| LUKS Group | Not stated in public sources | Not publicly stated | over 50,000 (2024) | over 925,000 (2024) | Not stated | Cantonal hospital group |
| Klinik Hirslanden, Zürich | 335 | 12,898 (FY 2024/25) | 20,097 (FY 2024/25) | Not stated separately | 14 | Private clinic; fiscal year April–March |
| Spital Zollikerberg | 174 | Not stated separately | 11,775 (2024) | 65,207 (2024) | 7 | Public-mandate regional hospital; virtual ward via HaH |

### 15.2 Derived daily flow rates (architectural assumptions)

| Provider | Inpatients/day | ED arrivals/day | Active census (lower bound) | LOS basis used |
| -------- | -------------- | --------------- | --------------------------- | -------------- |
| USZ | about 113/day | about 123/day | about 541 | 4.8-day Swiss acute LOS proxy |
| LUKS | over 137/day | Not derived (public gap) | over 658 | 4.8-day Swiss acute LOS proxy |
| Klinik Hirslanden | about 55/day | about 35/day | about 220–264 | 4.0-day Hirslanden group LOS |
| Spital Zollikerberg | about 32/day | Not derived (public gap) | about 155 | 4.8-day Swiss acute LOS proxy |

### 15.3 Platform use case priority by provider

| Provider | ED forecasting priority | Discharge coordination priority | Bed copilot priority | Primary platform differentiator |
| -------- | ----------------------- | -------------------------------- | -------------------- | -------------------------------- |
| USZ | Very high (45,000 ED/year) | High | High | High-volume ED forecasting at 5.1 arrivals/hour |
| LUKS | High | Very high (documented intraday discharge process) | High | Structured discharge workflow with daily 10:30 deadline |
| Klinik Hirslanden | Moderate (lower ED volume, elective-dominant) | High (short LOS target, elective surgical throughput) | High (14 ORs, multi-specialty) | Elective surgical flow and OR-to-bed coordination |
| Spital Zollikerberg | Moderate-to-high (compact bed constraint amplifies impact) | High (virtual ward extension via HaH) | High (compact ward, tight capacity) | Hospital-at-Home virtual ward as novel discharge pathway |

### 15.4 Discharge scoring volume by provider (architectural assumptions)

| Provider | Active census lower bound | Re-scores/day | Daily scoring volume |
| -------- | ------------------------- | ------------- | -------------------- |
| USZ | about 541 | 4 | about 2,164 scores/day |
| LUKS | over 658 | 4 | over 2,632 scores/day |
| Klinik Hirslanden | about 220–264 | 4 | about 880–1,056 scores/day |
| Spital Zollikerberg | about 155 (physical) | 4 | about 620 scores/day (physical ward) |

All figures are order-of-magnitude architectural assumptions derived from public volume data. Provider-native data discovery is required before implementation sizing is finalized.

---

## 16) Architectural adaptations for additional providers

The base platform architecture defined in sections 7 and 8 applies to all four providers without structural change. Two provider-specific adaptations are identified for the new providers:

### 16.1 Klinik Hirslanden adaptations

| Adaptation | Description |
| ---------- | ----------- |
| Elective admission horizon | Extend forecast model inputs to include the planned surgical admissions list (5–7 day window), in addition to the 72-hour unplanned ED forecast |
| OR schedule integration | Ingest the OR planning system as an additional source event for bed coordination; planned OR slate is a leading indicator of afternoon/evening bed demand |
| LOS calibration | Hirslanden group average LOS (4.0 days) is shorter than Swiss average (4.8 days); discharge scoring thresholds must be calibrated to this shorter window |
| Fiscal year alignment | Data ingestion, retention policies, and historical seeding must accommodate April–March fiscal year boundaries |

### 16.2 Spital Zollikerberg adaptations

| Adaptation | Description |
| ---------- | ----------- |
| Virtual ward census | Patient census model must include Hospital-at-Home patients as an active cohort alongside physical ward patients |
| Telemetry event stream | Vital sign telemetry from home patients (heart rate, respiratory rate, SpO2) is a new event type; architecture must accommodate streaming vital sign data as a clinical signal input |
| Discharge pathway routing | Discharge coordination model must produce three pathway labels: conventional discharge, Hospital-at-Home transfer, and post-acute/rehab transfer; outbound Logic Apps triggers differ per pathway |
| HaH capacity offset | Hospital-at-Home admissions reduce physical bed demand; bed management copilot must reflect virtual ward as an alternative capacity sink |
| Obstetric surge pattern | Birth centre generates non-uniform overnight and weekend admission surges; forecast model must include obstetric admission history as a signal |

---

## 17) Updated source families

This section extends section 12 with sources used for the additional provider profiles.

**Original sources (retained):**
- USZ public emergency and annual reporting pages
- LUKS public annual reporting and discharge-planning pages
- BFS (Swiss Federal Statistical Office) health and hospitalization statistics
- BAG publication context for 2024 hospital key figures caveats
- LUSTAT canton Luzern hospital statistics
- Microsoft documentation for Fabric, Azure Health Data Services, Azure Machine Learning, Azure OpenAI, and Logic Apps

**Additional sources for Klinik Hirslanden, Zürich:**
- Klinik Hirslanden Kennzahlen 2024/2025 (hirslanden.ch/de/klinik-hirslanden/klinikportrait/kennzahlen.html)
- Hirslanden Group inpatient case numbers and specialties per hospital FY 2023/24 (hirslanden.com annual data)
- Medinside: "Hirslanden: Stabile Zahlen bei Personal und Patienten" (June 2024)
- Medinside: "Neues Da-Vinci-System startet in Zürich" (December 2025)
- Klinik Hirslanden Da Vinci Operationstechnik page (hirslanden.ch/de/klinik-hirslanden/centers/...)
- competence.ch: "Erstes Spital der Schweiz mit Operationssystem Da Vinci 5" (December 2025)
- Klinik Hirslanden medical infrastructure page (hirslanden.ch/en/klinik-hirslanden/doctors-care-medical-infrastructur/...)
- Newsweek World's Best Hospitals 2026 ranking (referenced on hirslanden.ch homepage)

**Additional sources for Spital Zollikerberg:**
- Spital Zollikerberg Über uns page (spitalzollikerberg.ch/de/ueber-uns)
- Spital Zollikerberg Annual Report 2024 activity report (spitalzollikerberg.ch/en/blog/tb2024-hospital-zollikerberg)
- xund24.ch: "Spital Zollikerberg: Mehr Patienten, stabiles Wachstum trotz Herausforderungen" (April 2025)
- gesundheitswelt-zollikerberg.ch: Tätigkeitsbericht 2024 Spital Zollikerberg
- Spital Zollikerberg Hospital-at-Home offer page (spitalzollikerberg.ch/en/blog/hospital-at-home-offer-visit)
- Spital Zollikerberg Hospital-at-Home Congress page (spitalzollikerberg.ch/en/blog/opportunities-hospital-at-home)
- Medinside: "Hospital at Home: Zürcher Vorreiter ziehen Bilanz" (November 2025)
- Berner Fachhochschule (BFH): "Hospital at Home care models — evaluation and quality assurance" research project (bfh.ch, 2024)
- Annual reports index (spitalzollikerberg.ch/en/about-us/annual-reports)
