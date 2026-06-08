# Sprint 4 - IaC MVP SIT PROD Foundation for Functional Scope

| Field | Value |
| ----- | ----- |
| **Version** | 1.7.0 |
| **Date** | 2026-06-08 |
| **Author** | Urs Rueegg |
| **Status** | In Progress |
| **Previous Version** | 1.6.0 (completed data-foundation SIT and PROD rollout evidence) |

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

## Implementation Progress (Current)

### Completed in first implementation slice

1. Added new Sprint 4 foundation module scaffolds with concrete baseline resources:
  - `infra/modules/experience-hosting/main.bicep`
  - `infra/modules/api-runtime/main.bicep`
  - `infra/modules/data-foundation/main.bicep`
  - `infra/modules/ai-ml-foundation/main.bicep`
  - `infra/modules/integration-orchestration/main.bicep`
2. Extended root composition in `infra/main.bicep` with new module flags and conditional module wiring.
3. Added new module parity flags to:
  - `infra/environments/sit.bicepparam`
  - `infra/environments/prod.bicepparam`
4. Extended provider registration coverage in deployment workflows for new resource providers:
  - `Microsoft.Web`
  - `Microsoft.ContainerRegistry`
  - `Microsoft.EventHub`
  - `Microsoft.MachineLearningServices`
  - `Microsoft.Logic`

### Completed in second implementation slice

1. Completed local validation baseline for Sprint 4 module wiring:
  - `az bicep build --file infra/main.bicep`
  - `az bicep build-params --file infra/environments/sit.bicepparam`
  - `az bicep build-params --file infra/environments/prod.bicepparam`
2. Selected phased domain enablement strategy for new Sprint 4 modules:
  - enable one new module in `SIT`, verify deployment and inventory,
  - then promote the same module to `PROD` via approval-gated rollout.
3. Enabled first Sprint 4 domain module in `SIT`:
  - `enableExperienceHostingModule = true` in `infra/environments/sit.bicepparam`.
4. Kept `PROD` Sprint 4 module flags unchanged (`false`) pending SIT evidence and explicit promotion approval.

### Completed in third implementation slice

1. Resolved SIT deployment blocker by completing owner-side subscription provider registration for `Microsoft.Web`.
2. Re-ran SIT deployment workflow successfully for the same Sprint 4 slice:
  - https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/26997959531
3. Verified `SIT` experience-hosting resource footprint in `rg-chhealthpf-sit`:
  - `asp-platform-chhealthpf-sit` (`Microsoft.Web/serverFarms`)
  - `app-platform-chhealthpf-sit` (`Microsoft.Web/sites`)
4. Promoted phased parity change to `PROD` for the same domain by enabling:
  - `enableExperienceHostingModule = true` in `infra/environments/prod.bicepparam`.

### Completed in fourth implementation slice

1. Enabled second phased domain in `SIT`:
  - `enableApiRuntimeModule = true` in `infra/environments/sit.bicepparam`.
2. Initial SIT deployment failed due missing provider registration for `Microsoft.ContainerRegistry`:
  - https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/26998834387
3. Completed owner-side provider registrations for remaining Sprint 4 domains:
  - `Microsoft.ContainerRegistry`
  - `Microsoft.EventHub`
  - `Microsoft.MachineLearningServices`
  - `Microsoft.Logic`
4. Re-ran SIT deployment successfully for api-runtime slice:
  - https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/26999510532
5. Verified api-runtime SIT footprint in `rg-chhealthpf-sit`:
  - `id-api-chhealthpf-sit` (`Microsoft.ManagedIdentity/userAssignedIdentities`)
  - `crxnc4xt4uara6e` (`Microsoft.ContainerRegistry/registries`)
6. Promoted phased parity change to `PROD` for api-runtime by enabling:
  - `enableApiRuntimeModule = true` in `infra/environments/prod.bicepparam`.

### Completed in fifth implementation slice

1. Executed approval-gated PROD rollout for api-runtime successfully:
  - https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/26999705849
2. Verified api-runtime PROD footprint in `rg-chhealthpf-prod`:
  - `id-api-chhealthpf-prod` (`Microsoft.ManagedIdentity/userAssignedIdentities`)
  - `crvxmk7kyel3cjg` (`Microsoft.ContainerRegistry/registries`)
3. Confirmed phased parity status:
  - experience-hosting and api-runtime are now enabled and validated in both `SIT` and `PROD`.

### Completed in sixth implementation slice

1. Completed phased `SIT` rollout for data-foundation successfully:
  - https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/27119261102
2. Verified data-foundation `SIT` footprint in `rg-chhealthpf-sit`:
  - `evh-chhealthpf-sit` (`Microsoft.EventHub/namespaces`)
3. Promoted data-foundation parity change to `PROD` by enabling:
  - `enableDataFoundationModule = true` in `infra/environments/prod.bicepparam`.
4. Executed approval-gated `PROD` rollout for data-foundation successfully:
  - https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/27119400214
5. Verified data-foundation `PROD` footprint in `rg-chhealthpf-prod`:
  - `evh-chhealthpf-prod` (`Microsoft.EventHub/namespaces`)
6. Confirmed phased parity status:
  - experience-hosting, api-runtime, and data-foundation are now enabled and validated in both `SIT` and `PROD`.

### Completed in seventh implementation slice

1. Enabled `ai-ml-foundation` in `SIT` and executed the first phased deployment attempt:
  - Failed run: https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/27119903682
2. Diagnosed and fixed the ML workspace deployment contract in `infra/modules/ai-ml-foundation/main.bicep`:
  - Added required dependency references for existing `Key Vault`, `Application Insights`, `Storage Account`, and `Container Registry`.
3. Re-ran the phased `SIT` deployment successfully after fix-forward:
  - Successful run: https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/27120886274
4. Verified ai-ml `SIT` footprint in `rg-chhealthpf-sit`:
  - `mlw-chhealthpf-sit` (`Microsoft.MachineLearningServices/workspaces`)
5. Promoted ai-ml parity change to `PROD` by enabling:
  - `enableAiMlFoundationModule = true` in `infra/environments/prod.bicepparam`.
6. Executed approval-gated `PROD` rollout for ai-ml successfully:
  - https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/27123055394
7. Verified ai-ml `PROD` footprint in `rg-chhealthpf-prod`:
  - `mlw-chhealthpf-prod` (`Microsoft.MachineLearningServices/workspaces`)
8. Confirmed phased parity status:
  - experience-hosting, api-runtime, data-foundation, and ai-ml-foundation are now enabled and validated in both `SIT` and `PROD`.

### Pending in next slice

1. Capture issue and PR tracking comments for completed ai-ml-foundation SIT->PROD slice.
2. Repeat the phased cycle for integration-orchestration.

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
