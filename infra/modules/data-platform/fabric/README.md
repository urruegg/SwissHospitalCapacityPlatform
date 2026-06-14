# Fabric foundation module

Sprint 08 walking-skeleton W1.2. Provides the bronze landing zone for the
capacity data product by deploying a Microsoft Fabric capacity and configuring
a workspace, lakehouse, and KIS mirror via the Fabric REST API.

## Scope

- **In scope (Bicep):** Fabric capacity (`Microsoft.Fabric/capacities`, SKU `F2`,
  region `switzerlandnorth` per ADR-0003).
- **In scope (post-deploy):** Workspace `ws-chhealthpf-sit-data`, lakehouse
  `lh_chhealthpf_sit` (Delta + 3-zone via `enableSchemas`), mirrored database
  `mir_chhealthpf_kis` bound to the `kis` schema of the source SQL.
- **Out of scope:** Pipelines, notebooks, RBAC for workspace members,
  semantic models. Those land in later walking-skeleton tasks (W1.3+).

## Parameters

| Name | Type | Description |
| --- | --- | --- |
| `nameSuffix` | `string` | e.g. `chhealthpf-sit`. Capacity name derives from this with hyphens stripped. |
| `location` | `string` | Must be `switzerlandnorth` (ADR-0003). |
| `tags` | `object` | Applied to the capacity. |
| `capacityAdmins` | `array` | Object IDs of Fabric capacity administrators. |

## Outputs

| Name | Description |
| --- | --- |
| `capacityName` | The deployed Fabric capacity name (e.g. `fabricchhealthpfsit`). |
| `capacityId` | Full ARM resource ID of the Fabric capacity. |
| `moduleStatus` | Sentinel string for the parent module's status map. |

## Dependencies

- **Requires W1.1 deployed first.** The mirror's source connection binds to the
  Azure SQL server and `kis` database created by `s08-source-sql`. Running the
  post-deploy script before W1.1 is deployed produces a mirror with no source.
- Requires `enableDataPlatformModule = true`. The parent `infra/main.bicep`
  emits a `fabricFoundationGatingWarning` output when this constraint is not
  met.

## Post-deploy steps

The Bicep deployment only creates the capacity. Workspace, lakehouse, and
mirror are configured by the PowerShell script under `post-deploy/`:

```powershell
# After capacity is deployed AND W1.1's SQL server is reachable:
./post-deploy/configure-fabric.ps1 `
    -CapacityId '<capacity-id-from-bicep-output>' `
    -SourceServerFqdn 'sql-chhealthpf-sit.database.windows.net' `
    -SourceDatabase 'kis'
```

Per `AGENTS.md` §4, both `az deployment group create` and execution of
`configure-fabric.ps1` against Azure require an explicit `approved-to-apply`
comment on the governing issue/PR. The script supports a `-DryRun` switch that
loads the payload-builder functions without making any REST calls — that is
what the Pester suite under `post-deploy/tests/` exercises.

## Tests

```powershell
Invoke-Pester -Path infra/modules/data-platform/fabric/post-deploy/tests/configure-fabric.Tests.ps1
```

Three tests cover the workspace, lakehouse, and mirror payload shapes. They
run offline; no Azure auth required.

## Walking-skeleton scope

This module is gated by `enableFabricFoundationModule` (default `false`). It is
enabled only in `sit` for the Sprint 08 walking skeleton; `prod` keeps it
disabled until promotion criteria are met.
