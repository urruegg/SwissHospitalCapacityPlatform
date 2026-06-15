# `source-sql` module

Sprint 08 walking-skeleton (W1.1): Azure SQL source for the synthetic KIS
(Klinik-Informationssystem) feed that lands in bronze.

## Purpose

Provisions the synthetic upstream system that emits episode rows for the
walking-skeleton end-to-end path:

```text
source-sql (this module)  ->  bronze  ->  silver  ->  gold  ->  semantic model
```

The walking-skeleton variant seeds exactly **one** `kis.Episode` row via
[`infra/scripts/seed-synthetic-kis.ps1`](../../../scripts/seed-synthetic-kis.ps1).

## Scope

- One Azure SQL logical server (`sql-<nameSuffix>`) with system-assigned managed
  identity and `publicNetworkAccess = Disabled`.
- One database `kis` on `GP_Gen5_2` (General Purpose, 2 vCore).
- One private endpoint into the data subnet.
- TLS 1.2 minimum, locally-redundant backups (SIT only — ADR-0001 GA-only MVP).
- Region locked to `switzerlandnorth` (ADR-0003).

PHI is **forbidden** in SIT (ADR-0003 + ADR-0004). All seed data is synthetic.

## Parameters

| Name | Type | Required | Description |
| ---- | ---- | -------- | ----------- |
| `nameSuffix` | string | yes | Suffix appended to resource names (e.g. `chhealthpf-sit`). |
| `location` | string | yes | Deployment region. Must be `switzerlandnorth`. |
| `tags` | object | yes | Resource tags applied to all resources. |
| `dataSubnetId` | string | yes | Resource ID of the data subnet for the SQL private endpoint. |
| `sqlAdminPassword` | securestring | yes | SQL admin password. Caller must pass via `keyVault.getSecret(...)`; never hard-code. |
| `sqlAdminLogin` | string | no | SQL admin login (default `sqladmin`). |
| `privateDnsZoneId` | string | no | Resource ID of the existing `privatelink.database.windows.net` private DNS zone. Empty = wire DNS externally. |

## Outputs

| Name | Description |
| ---- | ----------- |
| `sqlServerName` | Logical server name (`sql-<nameSuffix>`). |
| `sqlServerFqdn` | Fully-qualified domain name of the server. |
| `sqlDatabaseName` | Database name (`kis`). |
| `sqlServerPrincipalId` | Principal ID of the server's system-assigned managed identity. |
| `sqlPrivateDnsWarning` | `'ok'` when DNS is wired by this module, otherwise a `WARN:` string asking the operator to wire DNS externally. |
| `moduleStatus` | Implementation marker (`source-sql-implemented`). |

## Prerequisites

Before deploying this module via the parent data-platform / top-level entry:

- Caller must enable `enableDataPlatformModule = true`. If the data-platform
  module is gated off, `enableSourceSqlModule = true` is silently ignored
  (the top-level `sourceSqlGatingWarning` output flags this).
- The target Key Vault must have `enabledForTemplateDeployment = true` so the
  parent module's `Microsoft.KeyVault/vaults@2023-07-01 existing` + `getSecret`
  flow can dereference the admin password at deploy time.
- The target Key Vault must already contain a secret named in
  `sourceSqlAdminPasswordSecretName` with the SQL admin password. The deploying
  principal needs `get` on that secret.
- The data subnet referenced by `dataSubnetId` must allow private endpoints
  (`privateEndpointNetworkPolicies: 'Disabled'`) and have routing/NSGs that
  permit traffic to the SQL FQDN.
- Private DNS: either supply `sourceSqlPrivateDnsZoneId` pointing at an existing
  `privatelink.database.windows.net` zone, **or** wire DNS externally
  (hub-managed zone / DNS forwarders) before clients can resolve the SQL FQDN.
  When omitted, the module emits `sqlPrivateDnsWarning` and does not create the
  DNS zone group.

## Walking-skeleton scope (W1.1)

- One row in `kis.Episode` only — see
  [`infra/scripts/seed-synthetic-kis.ps1`](../../../scripts/seed-synthetic-kis.ps1)
  for the seed payload and Pester tests under
  [`infra/scripts/tests/seed-synthetic-kis.Tests.ps1`](../../../scripts/tests/seed-synthetic-kis.Tests.ps1).
- Volume, fidelity, and additional KIS tables are out of scope for W1 and
  will land in later sprint-08 PRs.

## Related

- Spec: `docs/superpowers/specs/2026-06-14-sprint-08-data-platform-design.md` §8.1
- Requirements: FR-DATA-001, FR-DATA-003, NFR-RES-001, NFR-SEC-002, NFR-GOV-006
- Tracking issue: #66 (sprint-08 umbrella)
