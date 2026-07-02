# Tenant migration script pack

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-02 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | N/A |

## Purpose

Idempotent PowerShell helpers that drive the automatable pieces of the tenant migration runbook ([docs/runbooks/tenant-migration-runbook.md](../../../docs/runbooks/tenant-migration-runbook.md)) — machine trust, Entra OIDC federation, subscription RBAC, and GitHub environment configuration.

Governing spec: [docs/superpowers/specs/2026-07-02-tenant-migration-design.md](../../../docs/superpowers/specs/2026-07-02-tenant-migration-design.md) v1.1.0.

## Prerequisites

- Windows 10/11 with TPM 2.0 (for WAM broker device-bound keys)
- PowerShell 7+
- Azure CLI 2.60+
- Azure PowerShell (`Install-Module Az -Scope CurrentUser`) — `Az.Accounts` and `Az.Resources` at minimum
- GitHub CLI 2.50+ (`gh auth login` completed for the target repo)
- Pester 5.x (`Install-Module Pester -Scope CurrentUser`) — for running the test suite

## Scripts

| Script | Purpose | Idempotent? |
| ------ | ------- | ----------- |
| [`Enable-DeveloperTenantTrust.ps1`](./Enable-DeveloperTenantTrust.ps1) | W1.0. Turns on the Azure CLI WAM broker, signs in Azure CLI + Az PowerShell to the target tenant via the broker (TPM-bound device key), validates via `az account show` + `Get-AzContext`, prints Workplace Join guidance. | Yes — broker toggle is a no-op if set; cached tokens reused when valid. |
| [`New-OidcFederation.ps1`](./New-OidcFederation.ps1) | W1.2. Creates an Entra app registration + service principal in the target tenant, adds GitHub OIDC federated credentials for `sit` and `prod` (subject `repo:<owner/repo>:environment:<env>`, audience `api://AzureADTokenExchange`). Returns `ClientId` + `PrincipalId`. | Yes — reuses existing app by display name; skips existing federated credentials by subject. |
| [`Grant-SubscriptionRbac.ps1`](./Grant-SubscriptionRbac.ps1) | W1.3. Grants a role (default `Contributor`) at subscription scope to a service principal. | Yes — pre-checks with `Get-AzRoleAssignment`; skips if already assigned. |
| [`Set-GithubEnvironmentConfig.ps1`](./Set-GithubEnvironmentConfig.ps1) | W1.4. Sets GitHub environment variables (`AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `BICEP_PARAM_FILE`) and the `AZURE_CLIENT_ID` secret (as `SecureString` to avoid shell-history leaks). Captures a pre-change snapshot for `-Restore` rollback. | Yes — `gh api` PUT semantics; snapshot file enables rollback. |

Each script has a Pester test file under [`tests/`](./tests/).

## Recommended invocation order

Mirror runbook §1:

```powershell
# 1.0 Machine trust
./Enable-DeveloperTenantTrust.ps1 `
    -TenantId 1337187a-4c41-4da9-8fca-731bba7a4329 `
    -SubscriptionId <sit-sub-id>

# 1.2 Entra app registration + federated credentials
$oidc = ./New-OidcFederation.ps1 `
    -DisplayName 'gh-oidc-ihzhhpf' `
    -RepoFullName 'urruegg/SwissHospitalCapacityPlatform'

# 1.3 Grant Contributor on SIT and PROD subscriptions
./Grant-SubscriptionRbac.ps1 -PrincipalId $oidc.PrincipalId -SubscriptionId <sit-sub-id>
./Grant-SubscriptionRbac.ps1 -PrincipalId $oidc.PrincipalId -SubscriptionId <prod-sub-id>

# 1.4 Configure GitHub environments (never echoes ClientId to shell history)
$clientSecure = ConvertTo-SecureString $oidc.ClientId -AsPlainText -Force
./Set-GithubEnvironmentConfig.ps1 `
    -RepoFullName 'urruegg/SwissHospitalCapacityPlatform' `
    -Environment sit `
    -TenantId 1337187a-4c41-4da9-8fca-731bba7a4329 `
    -SubscriptionId <sit-sub-id> `
    -ResourceGroup 'rg-ihzhhpf-sit' `
    -BicepParamFile 'infra/environments/sit.bicepparam' `
    -ClientId $clientSecure

# Repeat -Environment prod with prod sub-id + rg-ihzhhpf-prod
```

## Rollback

`Set-GithubEnvironmentConfig.ps1 -Restore -Environment <env> -SnapshotPath ./tenant-migration-github-env-snapshot-<env>.json` restores the previous variable values captured during the initial run. See runbook §Rollback for the full failure-mode table.

## Tests

```powershell
Invoke-Pester -Path infra/scripts/tenant-migration/tests
```

Expected: 32/32 tests pass across the four scripts.

## Safety and approval

Every script that mutates cloud state supports `-WhatIf`. Actual apply steps that require `approved-to-apply` per [AGENTS.md §4](../../../AGENTS.md#4-confirmation-rule-for-deploy--delete) are driven by the runbook, not by these scripts running silently.
