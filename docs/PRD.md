# Product Requirements Document (PRD) — Draft

**Product:** Swiss AI-Powered Patient Flow and Hospital Capacity Platform
**Status:** Draft v0.1 (Sprint 1 — initial draft from specs)
**Last updated:** Sprint 1
**Owner:** Product (urruegg)

> This is the **initial PRD draft** produced in Sprint 1. It is derived from the
> source specifications and identifies the **MVP scope**. It will be refined in
> later sprints. See the sprint artifact:
> [`sprints/sprint-01-prd-draft-from-specs.md`](../sprints/sprint-01-prd-draft-from-specs.md).

## 1. Source Documents & Traceability

This PRD traces to the following source specifications:

| ID | Source document |
| --- | --- |
| S1 | [`docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform.md`](./specs/Swiss%20AI-Powered%20Patient%20Flow%20and%20Hospital%20Capacity%20Platform.md) |
| S2 | [`docs/specs/Swiss AI-Powered Patient Flow and Hospital Capacity Platform analysis.md`](./specs/Swiss%20AI-Powered%20Patient%20Flow%20and%20Hospital%20Capacity%20Platform%20analysis.md) |

## 2. Problem Statement

Swiss cantonal hospital providers lack a shared, real-time view of patient flow
and capacity across the provider ecosystem. Capacity decisions rely on delayed,
fragmented data, which leads to avoidable bottlenecks, discharge delays and
inefficient use of beds. *(Source: S1 §1–§3, S2 §3.)*

## 3. Goals & Non-Goals

### Goals

- G1. Provide near-real-time visibility of bed/unit capacity across providers.
- G2. Forecast short-term demand/occupancy to anticipate bottlenecks.
- G3. Optimize discharge planning to improve throughput.
- G4. Offer a grounded operational Copilot for capacity questions.
- G5. Enforce Swiss healthcare compliance (DSG/FADP), residency and auditability.

### Non-Goals

- Direct clinical decision-making or diagnosis.
- Replacing the hospital information system / EHR of record.
- Patient-facing scheduling beyond capacity signalling.

*(Source: S1 §1, §6; S2 §3.)*

## 4. Stakeholders & Personas

Cantonal health authority, hospital operations / bed managers, clinical staff,
IT / platform team, data protection / compliance officer, patients (indirect).
*(Source: S1 §2.)*

## 5. Requirements

### 5.1 Functional requirements

| ID | Requirement | Source |
| --- | --- | --- |
| F1 | Aggregate and present current bed/unit/resource availability across participating providers. | S1 §3, S2 §3.1 |
| F2 | Forecast short-term admissions and occupancy by unit/specialty. | S1 §3, S2 §3.1 |
| F3 | Surface discharge candidates and barriers to improve throughput. | S1 §3, S2 §3.1 |
| F4 | Provide a Copilot grounded in F1–F3 data for operational questions. | S1 §3, S2 §3.1 |
| F5 | Exchange clinical/capacity data via HL7 FHIR with HIS and partners. | S1 §3–§4, S2 §3.1 |

### 5.2 Non-functional requirements

| ID | Requirement | Source |
| --- | --- | --- |
| N1 | Comply with Swiss Data Protection Act (DSG/FADP) and healthcare data rules, incl. data residency. | S1 §4, S2 §3.2 |
| N2 | Enforce least-privilege access, audit logging and data lineage. | S2 §3.2 |
| N3 | Provide near-real-time data freshness for operational use. | S1 §3, S2 §3.2 |
| N4 | Deliver via Git-first ALM with auditable DEV → SIT → PROD pipelines. | S1 §4, S2 §3.2 |

## 6. MVP Scope

The MVP is the **smallest end-to-end slice** that delivers operational value
while exercising governance, scoped to a **single provider / canton pilot**.
*(Source: S2 §5.)*

### In scope (MVP)

- **M1 — Capacity visibility (F1):** read-only view of bed/unit occupancy for the
  pilot provider.
- **M2 — FHIR ingestion (F5):** ingest bed/occupancy data via HL7 FHIR into a
  governed semantic model.
- **M3 — Dashboard (F1/apps):** read-only operational dashboard over the governed
  model.
- **M4 — Baseline governance (N1/N2):** access control, audit logging and data
  residency for the pilot dataset.

### Fast-follow (post-MVP)

- Demand forecasting (F2), discharge optimization (F3), operational Copilot (F4),
  and multi-provider federation. These build on the M1/M2 foundation.
*(Source: S2 §5.)*

### Explicitly out of MVP

- Forecasting/optimization models, Copilot, and multi-provider rollout.

## 7. Success Metrics (directional)

- Time-to-visibility of pilot capacity reduced vs. current manual process.
- Dashboard data freshness within the agreed near-real-time target (N3).
- Compliance evidence available: access logs, lineage, residency (N1/N2).

*(Source: S1 §5.)*

## 8. Risks & Open Questions

Carried from S2 §4 and to be resolved before/within the pilot:

- Data-sharing agreements across providers.
- Per-dataset data residency obligations (Switzerland/EEA).
- Source HIS/EHR systems and FHIR profiles in scope.
- Forecast baseline / current process to benchmark against.
- User authentication and authorization model.

## 9. Open Items for Next Sprint

- Validate MVP scope (§6) with operations and compliance stakeholders.
- Confirm pilot provider and in-scope FHIR resources.
- Expand non-functional targets (N3) into measurable SLOs.
