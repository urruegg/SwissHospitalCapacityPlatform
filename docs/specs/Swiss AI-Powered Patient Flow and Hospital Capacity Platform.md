# Swiss AI-Powered Patient Flow and Hospital Capacity Platform

> **Document type:** Source specification (scenario)
> **Status:** Draft for Sprint 1 spec parsing
> **Audience:** Product, Architecture, Clinical Operations, Compliance
>
> This document captures the platform scenario that serves as the primary input
> for the initial Product Requirements Document (see [`docs/PRD.md`](../PRD.md)).
> It is the canonical source of truth for *what* the platform is intended to do.

## 1. Vision

Build a regulated, multi-stakeholder, AI-driven platform that gives Swiss
cantonal hospital providers real-time visibility into patient flow and hospital
capacity, and that uses AI to forecast demand and optimize discharge and bed
management across the provider ecosystem.

The platform is **not** a single application. It combines:

- **AI/ML models** — demand forecasting and discharge optimization.
- **Data platform** — ingestion, transformation and a shared semantic model
  (e.g. Microsoft Fabric, Azure Health Data Services).
- **Application layer** — operational apps for bed management and dashboards
  (e.g. Dynamics, Power Platform).
- **Copilot / GenAI layer** — grounded assistants for operational staff.
- **Integration layer** — interoperability across the provider ecosystem
  (e.g. Logic Apps, FHIR, connectors).
- **Security & governance** — strong compliance for Swiss healthcare data.

## 2. Stakeholders

| Stakeholder | Interest |
| --- | --- |
| Cantonal health authority | Regional capacity visibility and steering. |
| Hospital operations / bed managers | Real-time bed and unit occupancy, discharge planning. |
| Clinical staff (ward, ED) | Reduced administrative load, timely capacity signals. |
| IT / platform team | Secure, maintainable, ALM-driven delivery (DEV → SIT → PROD). |
| Data protection / compliance officer | Adherence to the Swiss Data Protection Act (DSG/FADP) and healthcare rules. |
| Patients | Indirect benefit: shorter waits, smoother transitions of care. |

## 3. Core Capabilities

1. **Real-time capacity visibility** — aggregate bed, unit and resource
   availability across participating providers.
2. **Demand forecasting** — predict short-term admissions and occupancy by
   unit/specialty to anticipate bottlenecks.
3. **Discharge optimization** — surface discharge candidates and barriers to
   improve patient throughput.
4. **Operational Copilot** — grounded conversational assistance for bed
   managers and operations leads.
5. **Ecosystem integration** — standards-based exchange (FHIR) with hospital
   information systems and partner providers.
6. **Governance & compliance** — data residency, access control, auditability
   and lineage suitable for Swiss healthcare.

## 4. Constraints

- **Regulatory:** Swiss Data Protection Act (DSG/FADP); healthcare data
  handling; data residency within Switzerland/EEA as required.
- **Interoperability:** must support HL7 FHIR for clinical data exchange.
- **Multi-provider:** no single provider owns all data; access is federated and
  permissioned.
- **Enterprise ALM:** Git-first, structured artefacts, DEV → SIT → PROD
  promotion with auditable pipelines.

## 5. Success Indicators (directional)

- Reduced time-to-visibility of capacity across the canton.
- Improved forecast accuracy for occupancy versus a naïve baseline.
- Reduced discharge-related delays (length-of-stay outliers).
- Demonstrable compliance evidence (access logs, lineage, data residency).

## 6. Out of Scope (for the platform vision, refined per release)

- Direct clinical decision-making or diagnosis.
- Replacing the hospital information system (HIS) / EHR of record.
- Patient-facing scheduling beyond capacity signalling.
