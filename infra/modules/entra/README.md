# Entra demo organisation (Sprint 12)

| Field | Value |
| ------- | ------- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-09 |
| **Author** | GitHub Copilot |
| **Status** | Draft for review |
| **Previous Version** | — (initial) |

Bicep + Microsoft Graph modules that provision the demo Entra organisation for
the Swiss Hospital Capacity Platform: app registration, app roles, security
groups, personas, and group-based role assignments in the shared SIT+PROD tenant
`MngEnvMCAP164444.onmicrosoft.com` (per [ADR-0012](../../../docs/adr/0012-tenant-migration-to-mcap164444.md)).

- Design spec: [`docs/superpowers/specs/2026-07-09-sprint-12-org-design.md`](../../../docs/superpowers/specs/2026-07-09-sprint-12-org-design.md)
- Implementation plan: [`docs/superpowers/plans/2026-07-09-sprint-12-org-plan.md`](../../../docs/superpowers/plans/2026-07-09-sprint-12-org-plan.md)

> **Users are shared between SIT and PROD** (design decision D-6). Environment
> scoping is done **in-app** via an `env` claim + hospital-context, not by
> cloning identities.

## Module map

| Module | Purpose | Extension |
| ------ | ------- | --------- |
| `main.bicep` | Subscription-scope orchestrator; chains the modules below. | Graph (child modules) |
| `app-roles.bicep` | Emits the full appRoles catalog (2 super + operational/governance). Pure computation, deterministic GUIDs. | none |
| `app-registration.bicep` | `ihzhhpf-app` application + service principal, appRoles folded in. | Microsoft Graph |
| `security-groups.bicep` | One security group per app role; membership set from personas. | Microsoft Graph |
| `users.bicep` | 23 personas (design spec §6). Temporary password via secure param only. | Microsoft Graph |
| `assignments.bicep` | Group-based app-role assignments to the service principal. | Microsoft Graph |
| `adoption-telemetry.bicep` | Tenant-scoped Entra `SignInLogs` diagnostic setting → Log Analytics. Deployed standalone. | none |
| `parameters/sit.bicepparam` / `parameters/prod.bicepparam` | Env parameter files. `temporaryPassword` is never set here. | — |

## Prerequisites

- `az bicep` ≥ 0.24 (needed for the Microsoft Graph Bicep extension).
- The [Microsoft Graph Bicep extension](https://learn.microsoft.com/graph/templates/overview-bicep-templates-for-graph)
  is registered in [`bicepconfig.json`](bicepconfig.json). `az bicep build`
  restores it from the Microsoft Artifact Registry on first use (network access
  required).
- Graph application permissions on the executing identity: `Directory.ReadWrite.All`,
  `RoleManagement.ReadWrite.Directory`, `Application.ReadWrite.All`.
- `az` authenticated to the SIT tenant `1337187a-4c41-4da9-8fca-731bba7a4329`.

## What-if / apply workflow (gated)

Every apply is a `deploy`-ceiling action and requires an `approved-to-apply`
comment referencing the specific `what-if` output, per
[AGENTS.md §4](../../../AGENTS.md#4-confirmation-rule-for-deploy--delete).

```bash
# 1. Plan (post output as a PR comment, then wait for approved-to-apply)
az deployment sub what-if \
  --location westus2 \
  --template-file infra/modules/entra/main.bicep \
  --parameters infra/modules/entra/parameters/sit.bicepparam \
  --parameters temporaryPassword="$TEMP_PW"

# 2. Apply to SIT only (PROD deferred to a follow-up PR labelled prod-batch)
az deployment sub create \
  --name "sprint-12-sit-$(date +%Y%m%d-%H%M)" \
  --location westus2 \
  --template-file infra/modules/entra/main.bicep \
  --parameters infra/modules/entra/parameters/sit.bicepparam \
  --parameters temporaryPassword="$TEMP_PW"

# Adoption telemetry (tenant-scoped, separate deployment)
az deployment tenant create \
  --location westus2 \
  --template-file infra/modules/entra/adoption-telemetry.bicep \
  --parameters logAnalyticsWorkspaceResourceId="$LA_ID"
```

`$TEMP_PW` is a temporary password supplied at apply time; users must reset it
on first sign-in. It is **never** committed to the repo or posted in a PR
comment (T4 refusal rule).

## Refusal rules (T4)

- Refuse if any UPN uses a domain other than `@mngenvmcap164444.onmicrosoft.com`
  (`users.bicep` exposes an `upnDomainGuard` output that lists any offenders).
- Refuse to commit or PR-comment any user password.
- Refuse to apply PROD before an explicit `prod-batch` label + separate sign-off.

## Role-count reconciliation note

The design spec §1 prose reads "15 Entra app roles (13 operational/governance +
2 super)" — i.e. a **15** headline total. However, the persona catalog in spec §6
actually references **15** distinct operational/governance role values
(`HCC.OperationsLead`, `HCC.BedManager`,
`HCC.FlowManager`, `HCC.EDLead`, `HCC.ORCoordinator`, `HCC.StaffingCoordinator`,
`HCC.DischargeCoordinator`, `HCC.CrisisManager`, `HCC.Executive`,
`HCC.CantonalViewer`, `HCC.PlatformAdmin`, `HCC.OntologySteward`,
`HCC.AIGovernance`, `HCC.DemoOperator`, `HCC.Auditor`) plus the 2 super roles —
**17 total**. In other words the spec §1 "13 operational" count is inconsistent
with its own §6 catalog, which enumerates 15. `app-roles.bicep` provisions all 17
so every persona maps to an existing role and group (internal consistency).
Reviewer action: confirm whether the §6 catalog (15 operational) or the §1 headline
(13 operational) is authoritative — either collapse two operational roles to hit the
"15 total" headline, or correct spec §1 to "15 operational + 2 super = 17" — and
update the spec prose accordingly at the approval gate.
