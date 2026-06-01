# Swiss AI-Powered Patient Flow and Hospital Capacity Platform — Analysis

> **Document type:** Source specification (analysis)
> **Status:** Draft for Sprint 1 spec parsing
>
> This document analyzes the scenario in
> [`Swiss AI-Powered Patient Flow and Hospital Capacity Platform.md`](./Swiss%20AI-Powered%20Patient%20Flow%20and%20Hospital%20Capacity%20Platform.md)
> and decomposes it into architectural layers and candidate requirements. It is
> the second input to [`docs/PRD.md`](../PRD.md).

## 1. Architectural Decomposition

The scenario is a **multi-layered enterprise AI platform**, not a single app.
The recommended repository structure reflects these layers:

```text
patient-flow-ai-platform/
├── docs/                  # PRD, architecture, regulatory mapping, specs
├── infra/                 # Azure infrastructure as code (bicep/terraform, envs)
├── data-platform/         # Fabric / data engineering (ingestion, transforms, semantic model)
├── ai-models/             # ML + AI logic (demand-forecasting, discharge-optimization)
├── copilot/               # GenAI / agent layer (prompts, orchestration, grounding, eval)
├── apps/                  # Operational apps (bed-management, dashboard, Power Platform)
├── integrations/          # APIs & orchestration (Logic Apps, connectors, FHIR)
├── security-governance/   # Purview, access model, policies (Swiss compliance)
└── pipelines/             # CI/CD (github-actions, release)
```

## 2. Scenario → Capability → Layer Mapping

| Scenario Requirement | Capability | Primary Layer |
| --- | --- | --- |
| Multi-provider healthcare ecosystem | Federated data & exchange | `integrations/`, `data-platform/` |
| AI forecasting + optimization | Demand forecasting, discharge optimization | `ai-models/` |
| Copilot for operations | Grounded operational assistant | `copilot/` |
| Real-time visibility | Capacity dashboards | `data-platform/` + `apps/` |
| Swiss compliance (DSG/FADP) | Governance, residency, audit | `security-governance/` |
| Enterprise delivery (SIT/PROD) | ALM, IaC, CI/CD | `infra/` + `pipelines/` |

## 3. Requirements Analysis

### 3.1 Functional themes

- **F1 Capacity visibility:** ingest and present current bed/unit occupancy.
- **F2 Demand forecasting:** model expected occupancy/admissions.
- **F3 Discharge optimization:** identify discharge candidates and blockers.
- **F4 Operational Copilot:** answer capacity questions grounded in F1–F3 data.
- **F5 Interoperability:** FHIR-based exchange with HIS and partners.

### 3.2 Non-functional themes

- **N1 Compliance:** DSG/FADP, healthcare data handling, data residency.
- **N2 Security:** least-privilege access, auditability, lineage.
- **N3 Reliability:** real-time/near-real-time freshness for operational use.
- **N4 ALM:** Git-first, DEV → SIT → PROD with auditable pipelines.

## 4. Risks & Open Questions

- **Data access:** what data-sharing agreements exist across providers?
- **Data residency:** confirm Switzerland/EEA residency obligations per dataset.
- **Source systems:** which HIS/EHR systems and FHIR profiles are in scope?
- **Baseline:** is there an existing forecast/manual process to benchmark?
- **Identity:** how are operational users authenticated and authorized?

## 5. MVP Recommendation (input to PRD)

For the first usable increment, prioritize the smallest end-to-end slice that
delivers operational value while exercising governance:

1. **F1 Capacity visibility** for a single provider/canton pilot, sourced via
   **F5 FHIR ingestion** of bed/occupancy data.
2. A **read-only dashboard** (apps layer) over a governed semantic model.
3. **N1/N2 baseline governance:** access control, audit logging, data residency.

Forecasting (F2), discharge optimization (F3) and Copilot (F4) are **fast-follow**
increments that build on the F1/F5 foundation. This sequencing is carried into
the MVP scope of [`docs/PRD.md`](../PRD.md).
