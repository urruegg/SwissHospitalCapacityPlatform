# Sprint 4 - IaC MVP SIT PROD Foundation for Functional Scope

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-04 |
| **Author** | Urs Rueegg |
| **Status** | Planned |
| **Previous Version** | N/A |

## Sprint Goal

Establish the remaining MVP Infrastructure as Code foundation in `SIT` and `PROD` so the team can start implementing functional solution scope (experience, API runtime, data pipelines, AI workflows, and partner integration) on a production-aligned platform baseline.

## Trigger Model

This sprint is executed as a GitHub Issue-driven run. The sprint issue is the tracking anchor, and `@copilot` is the execution trigger for planning, implementation, validation, and evidence updates.

## Traceability

- GitHub Issue: [#9](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/9)
- GitHub Project: Swiss Hospital Capacity Platform Delivery
- Source baseline:
  - `docs/SD.md`
  - `docs/ARCHITECTURE.md`
  - `docs/AI.md`
  - `docs/DATA.md`
  - `docs/SECURITY.md`
  - `docs/COMPLIANCE.md`
- Prior sprint baseline:
  - `sprints/sprint-03-iac-provision-sit-prod.md`
- Sprint PR tracking:
  - [#10](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/10)

## Scope

### In scope

- Define and implement MVP-ready IaC resources missing from Sprint 3 baseline.
- Keep strict `SIT` and `PROD` environment parity for foundational resources.
- Extend CI/CD validation and deployment flow for new IaC modules.
- Preserve approval-gated deployment controls and provider registration controls.
- Produce evidence pack for readiness to start functional build work.

### Out of scope

- Full functional application implementation (UI/API/business logic).
- Data model and feature engineering implementation details.
- Production data migration and cutover.
- Destructive operations in production subscriptions.

## MVP IaC Gap Analysis

The following gap analysis is based on `docs/SD.md` logical domains and the current Sprint 3 resource baseline.

| SD Domain | Current Sprint 3 Baseline | Gap for MVP Foundation | Sprint 4 IaC Target |
| ----- | ----- | ----- | ----- |
| Experience | No dedicated app hosting foundation | Missing web app channel foundation for React MVP path | Provision hosting baseline (App Service or Static Web Apps), identity/auth wiring, diagnostics |
| API and runtime | No containerized runtime foundation | Missing API runtime environment and image flow baseline | Provision Container Apps environment baseline, registry integration, managed identity and ingress controls |
| Data ingestion and curation | Storage baseline only | Missing data ingress/service foundations for healthcare normalization and governed analytics landing zone | Add foundational data service resources and secure connectivity patterns required to begin ingestion implementation |
| AI decisioning | AI Services account baseline | Missing ML workspace and operational AI pipeline foundation | Add ML workspace baseline, model ops storage dependencies, monitoring hooks |
| Integration | Service Bus baseline | Missing workflow orchestration and endpoint integration foundation | Add Logic Apps and integration baseline resources with observability and secret references |
| Security and governance | Key Vault, Log Analytics, RBAC baseline | Missing policy, diagnostics, and governance artifacts for expanded service set | Extend diagnostics/policy coverage and environment guardrails for all new modules |

## Required Sprint 4 IaC Deliverables

1. New or extended IaC modules under `infra/modules/` for MVP foundation gaps:
   - experience-hosting
   - api-runtime
   - data-foundation
   - ai-ml-foundation
   - integration-orchestration
2. Root composition updates in `infra/main.bicep` for module orchestration and outputs.
3. Environment parameter updates:
   - `infra/environments/sit.bicepparam`
   - `infra/environments/prod.bicepparam`
4. Diagnostics and monitoring coverage for all new resources.
5. Identity and secret reference pattern using managed identity and Key Vault.
6. CI validation updates for any new templates and parameter profiles.
7. CD workflow updates only if required by new deployment orchestration dependencies.

## Delivery Sequence

```mermaid
flowchart LR
    A[Gap Analysis from SD] --> B[Module Design]
    B --> C[Implement IaC Modules]
    C --> D[CI Validate and What-If]
    D --> E[SIT Deploy and Verify]
    E --> F[Approval Gate]
    F --> G[PROD Deploy and Verify]
    G --> H[Foundation Ready for Functional Build]
```

## Planned Work Items

1. Confirm target MVP foundation resources per SD domain and architecture constraints.
2. Define module contracts (inputs, outputs, diagnostics, identity model).
3. Implement new modules and compose in `infra/main.bicep`.
4. Update SIT and PROD parameterization with parity checks.
5. Run CI validation (`lint`, `build`, `what-if`) for SIT and PROD.
6. Execute SIT deployment and verify resource inventory and policy posture.
7. Execute approval-gated PROD deployment and verify parity.
8. Publish evidence links in issue and sprint document, then close sprint issue.

## Acceptance Criteria

- All Sprint 4 target foundation modules are represented in IaC and deployed in `SIT` and `PROD`.
- `SIT` and `PROD` parity is maintained for foundational module flags and core configuration shape.
- CI checks pass for markdown, Bicep build, and both what-if jobs.
- SIT and PROD deployments succeed through approval-gated promotion flow.
- Evidence links for workflow runs and Azure verification are captured in issue and sprint artefacts.
- Sprint output is sufficient to begin functional implementation sprints without additional platform bootstrap work.

## Risks and Dependencies

1. Azure provider/SKU availability by region for newly introduced service types.
2. Policy constraints that may block certain resource types or networking modes.
3. Identity and permission propagation delays across environments.
4. Service-specific provisioning times causing transient deployment conflicts.

## Notes

Sprint 4 is the foundation-completion sprint that bridges Sprint 3 infrastructure baseline to MVP functional implementation readiness.
