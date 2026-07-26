# Infrastructure Baseline

| Field | Value |
| ----- | ----- |
| **Version** | 1.6.0 |
| **Date** | 2026-07-25 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | 1.5.1 (editorial: repaired UTF-8 mojibake; no semantic change) |

## Purpose

Define the infrastructure baseline for Sprint 3 SIT and PROD provisioning and promotion workflows.

## Current Scope

- Root deployment entrypoint: infra/main.bicep
- Foundation module: infra/modules/platform-foundation/main.bicep
- Environment parameters:
  - infra/environments/sit.bicepparam
  - infra/environments/prod-swn.bicepparam (deployed PROD — Switzerland North greenfield, [ADR-0037](adr/0037-prod-region-switzerland-north-greenfield.md))
  - infra/environments/prod.bicepparam (westus2 demo baseline, referenced by `policy/policy-pack.json`)
- CI validation workflow: .github/workflows/ci-infra-validate.yml
- SIT deployment workflow: .github/workflows/cd-infra-deploy-sit.yml
- PROD deployment workflow: .github/workflows/cd-infra-deploy-prod.yml

> **As-deployed note (Sprint 19):** PROD is deployed greenfield in
> **`switzerlandnorth`** (resource group `rg-ihzhhpf-prod`); the automated
> `cd-infra-deploy-prod` pipeline targets `prod-swn.bicepparam` /
> `switzerlandnorth`. SIT stays in `westus2` (+ `eastus2` Foundry split).
> The retired `prod-eastus2.bicepparam` was deleted (#311). Consolidated
> as-deployed view + parity evidence:
> [CURAVIAS-PRODUCT-STATUS.md](CURAVIAS-PRODUCT-STATUS.md).

## Implemented Module Domains

Implemented module domains:

- identity
- network
- observability
- data-platform
- ai-platform
- integration

## Data platform

> **SQL-optional posture (2026-07-02, ADR-0015):** For the MVP demo scope, SQL Server is skipped entirely. Ingestion runs via direct-to-lakehouse (reference/master data) + Event Hubs → Fabric Eventstream (simulator events) → Fabric Spark bronze/silver/gold notebook chain. The `source-sql` Bicep module stays in the tree behind `enableSourceSqlModule=false`; enable when a customer PROD deployment requires KIS integration. See [ADR-0015](adr/0015-skip-sql-for-mvp-demo.md).

## Implemented Topology Snapshot

```mermaid
flowchart TD
  subgraph SIT[Environment: SIT]
    SITKV[kv-ihzhhpf-sit]
    SITLOG[log-ihzhhpf-sit]
    SITAPPI[appi-ihzhhpf-sit]
    SITID[id-platform-ihzhhpf-sit]
    SITVNET[vnet-platform-ihzhhpf-sit]
    SITST[stdpihzhhpfsit]
    SITSB[sb-ihzhhpf-sit]
    SITAI[ai-ihzhhpf-sit]
  end

  subgraph PROD[Environment: PROD]
    PRODKV[kv-ihzhhpf-prod]
    PRODLOG[log-ihzhhpf-prod]
    PRODAPPI[appi-ihzhhpf-prod]
    PRODID[id-platform-ihzhhpf-prod]
    PRODVNET[vnet-platform-ihzhhpf-prod]
    PRODST[stdpihzhhpfprod]
    PRODSB[sb-ihzhhpf-prod]
    PRODAI[ai-ihzhhpf-prod]
  end
```

## Provider Registration Runbook

Use this runbook when workflow identities can deploy resources but cannot perform subscription-level provider registration operations.

Required providers for current module set:

- Microsoft.OperationalInsights
- Microsoft.KeyVault
- Microsoft.ManagedIdentity
- Microsoft.Network
- Microsoft.Insights
- Microsoft.Storage
- Microsoft.CognitiveServices
- Microsoft.ServiceBus

Owner-level bootstrap command:

```powershell
./infra/scripts/register-resource-providers.ps1 -SubscriptionId <subscription-id>
```

Verification command:

```powershell
az provider show --namespace Microsoft.ManagedIdentity --query registrationState -o tsv
```

Expected value: `Registered`.

## PROD Enablement Strategy

Current strategy has progressed from phased rollout to controlled parity enablement:

- Optional module flags are now enabled in `infra/environments/prod.bicepparam`.
- Deployments remain approval-gated and evidence-first via `workflow_dispatch` with explicit confirmation.
- Provider registration remains a prerequisite control and is captured in runbook automation.

## Sprint 05 Landing-Zone Governance Evidence

The CAF/WAF review (§4.1, §7) found landing-zone governance evidence — management-group
hierarchy, policy assignments, and RBAC scopes — weaker than architecture intent. A
dedicated landing-zone governance evidence document is a Phase 2 deliverable, tracked as
`RV-06` (owner `ARCH`) in
[`docs/sprints/sprint-05/requires-validation-register.md`\](sprints/sprint-05/requires-validation-register.md).
Policy assignment and residency/deployment-type enforcement are governed by `ADR-0010`
(policy-as-code) and implemented as CI checks in Sprint 05 Phase 2.

