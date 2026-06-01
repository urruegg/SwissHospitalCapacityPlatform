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
