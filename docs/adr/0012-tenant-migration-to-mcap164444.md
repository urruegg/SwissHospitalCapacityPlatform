# ADR-0012 — Tenant migration to MCAP164444

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-07-02 |
| **Author** | Urs Rüegg |

## Context

The Swiss Hospital Capacity Platform was originally deployed into the MCAP sandbox tenant `2dfb4d85-3ca7-474e-86eb-9ba3762d9474` (`MngEnvMCAP228255.onmicrosoft.com`) with solution short name `chhealthpf`. A new MCAP sandbox tenant `1337187a-4c41-4da9-8fca-731bba7a4329` (`MngEnvMCAP164444.onmicrosoft.com`) was assigned to the solution on 2026-07-02 and must become authoritative for future work.

MCAP-to-MCAP cross-tenant subscription transfer is not permitted; a clean rebuild was the only viable path. The design and runbook are recorded in [docs/superpowers/specs/2026-07-02-tenant-migration-design.md](../superpowers/specs/2026-07-02-tenant-migration-design.md) v1.2.0 and [docs/runbooks/tenant-migration-runbook.md](../runbooks/tenant-migration-runbook.md). Region selection was carved out separately in [ADR-0013](0013-temporary-us-region-demo-scope.md).

## Decision

Rebuild SIT and PROD in the new tenant using a single shared subscription `66a9953a-df37-4c51-856c-9971b9bf3e03` (demo simplification per D9) in region `westus2` (per [ADR-0013](0013-temporary-us-region-demo-scope.md)). Solution short name renamed `chhealthpf` → `ihzhhpf` in live/authoritative files only; historical sprint/spec docs preserve the audit trail. Old tenant remains operational; teardown is deferred to a separate later decision.

### Delivered scope

| Environment | Resource group | Resource count | Provisioning |
| ----------- | -------------- | -------------- | ------------ |
| SIT | `rg-ihzhhpf-sit` | 16 | Succeeded |
| PROD | `rg-ihzhhpf-prod` | 15 | Succeeded |

Opt-out for both environments: source SQL module (`enableSourceSqlModule = false`) and Fabric foundation module (`enableFabricFoundationModule = false`) — unchanged from Sprint 08 baseline; enablement is a separate later decision.

### Deployment identity plane

- Entra app registration: `gh-oidc-ihzhhpf` (client `cbecd109-2ac5-466b-b08e-2a97556274d2`, service principal `3ca4e7c3-e2f9-490c-9ee7-cc4d36ea5e2f`).
- Federated credentials (2): subject `repo:urruegg/SwissHospitalCapacityPlatform:environment:{sit,prod}`, audience `api://AzureADTokenExchange`.
- Subscription RBAC: `Contributor` on `66a9953a-...` (single sub scope; assignment `4fc3d54e-bb2b-4cd1-af96-d9a16de90a43`).
- GitHub environments `sit` and `prod` updated: `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `AZURE_LOCATION` (`westus2`), `BICEP_PARAM_FILE`, plus Fabric-scoped vars (`{SIT,PROD}_FABRIC_*`) and `AZURE_CLIENT_ID` secret.

## Consequences

### Positive

- Deployment plane fully in the new tenant; old-tenant identity plane can be decommissioned at will.
- Naming convention (`ihzhhpf`) refreshed and consistent; no accidental cross-tenant name collisions.
- Discovered and fixed three real Bicep design smells during execution: storage / KV / Web App / Event Hub NS / Service Bus NS all needed `uniqueString()` for global-namespace uniqueness (PRs #75 and #76). Fix is idiomatic Azure practice and future-proof.
- Discovered and fixed a PowerShell string-interpolation bug in `New-OidcFederation.ps1` that had produced malformed federated credential subjects during first run (fixed in place via `az ad app federated-credential update`; script + Pester test hardened in follow-up).

### Negative / follow-up

- Gate G2.2 (walking-skeleton smoke test with `Encounter Count > 0`) is deferred because Fabric + source SQL are opt-out. Tracked as follow-up work.
- Old-tenant resources still incur small residual costs (Log Analytics retention, App Insights). Not addressed by this ADR.
- `Set-GithubEnvironmentConfig.ps1` did not enumerate the Fabric-scoped vars — those were set manually during execution. Tracked as follow-up to extend the script.

## References

- Spec: [docs/superpowers/specs/2026-07-02-tenant-migration-design.md](../superpowers/specs/2026-07-02-tenant-migration-design.md) v1.2.0
- Plan: [docs/superpowers/plans/2026-07-02-tenant-migration-plan.md](../superpowers/plans/2026-07-02-tenant-migration-plan.md)
- Runbook: [docs/runbooks/tenant-migration-runbook.md](../runbooks/tenant-migration-runbook.md)
- Sprint report: [docs/sprints/sprint-00-new-tenantprovisioning.md](../sprints/sprint-00-new-tenantprovisioning.md)
- Region carve-out: [ADR-0013](0013-temporary-us-region-demo-scope.md)
- Bicep hotfixes: PR #75 (storage account), PR #76 (KV, Web App, Event Hub, Service Bus)
