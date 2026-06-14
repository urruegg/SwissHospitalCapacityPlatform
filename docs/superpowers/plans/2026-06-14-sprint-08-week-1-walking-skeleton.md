# Sprint 08 - Week 1 Walking Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver an end-to-end thin slice of the Sprint 08 data platform: one synthetic KIS episode replicated through Azure SQL -> Fabric Mirror -> bronze -> silver -> gold, plus one event from the ACA simulator into the same gold table, surfaced in Power BI via a Direct Lake Semantic Model showing `Encounter Count = 2`.

**Architecture:** Five parallel PRs against the `sprint-08/...` branch, each adding a self-contained Bicep sub-module under `infra/modules/data-platform/` and (where applicable) PySpark notebooks and Python producer code. Existing repo conventions are honoured: domain-grouped Bicep modules with `enable*Module` flags in `infra/main.bicep`, environment params under `infra/environments/`, residency `switzerlandnorth`, MI + Key Vault + private endpoints throughout. Fabric items (workspace, lakehouse, mirror, eventstream, semantic model) that have no first-class Bicep type are provisioned via Fabric REST API from a Bicep `deploymentScript` resource using the deployment principal's MI.

**Tech Stack:** Bicep, PSRule for Azure, PowerShell 7 + `az` CLI + Fabric REST API, Python 3.11 (PySpark local for notebook tests, `unittest` for simulator), Azure Container Apps, Microsoft Fabric F2 (Mirroring + Eventstream + Direct Lake), Power BI.

**Source spec:** [docs/superpowers/specs/2026-06-14-sprint-08-data-platform-design.md](../specs/2026-06-14-sprint-08-data-platform-design.md)

**Umbrella issue:** `#66`. Baseline PR: `#67`.

---

## Pre-flight

- [ ] **Step 0.1: Confirm working branch**

Run from repo root:

```powershell
git status; git branch --show-current
```

Expected: clean working tree (apart from the three pre-existing dirty files documented in the spec: `SwissHospitalCapacityPlatform.code-workspace`, `docs/reviews/2026-06-10-ama-ciso-challanger-review.md`, `docs/reviews/2026-06-10-ama-design-challanger-review.md` - NEVER stage these); branch `sprint-08/data-platform-resources-and-ingestion-pipeline`.

- [ ] **Step 0.2: Confirm baseline gates pass**

Run:

```powershell
npx --yes markdownlint-cli2 "docs/**/*.md" "#node_modules"
az bicep build --file infra/main.bicep
python data/synthetic/validate_datasets.py --root data/synthetic
python -m unittest discover -s data/synthetic/tests -v
```

Expected: all four commands exit 0. If any fails, stop and fix the baseline first.

- [ ] **Step 0.3: Confirm Azure access**

Run:

```powershell
az account show --query "{sub:id, tenant:tenantId}" -o table
az group show -n rg-chhealthpf-sit --query location -o tsv
```

Expected: subscription you intend to deploy into; RG location `switzerlandnorth`. If the RG does not exist, stop and file an issue - it is out of scope for this plan.

- [ ] **Step 0.4: Confirm Fabric capacity admin rights**

You (the deploying principal) must be a tenant Fabric admin or have `Microsoft.Fabric/capacities/write` at the subscription scope, because W1.2 creates a Fabric capacity and assigns it to a workspace. Verify:

```powershell
az role assignment list --assignee $(az ad signed-in-user show --query id -o tsv) --query "[?contains(roleDefinitionName, 'Owner') || contains(roleDefinitionName, 'Contributor')].roleDefinitionName" -o tsv
```

Expected: at least one of `Owner`, `Contributor` listed at sub or RG scope. If not, stop.

---

## Task 1 (PR W1.1): `s08-source-sql` - Azure SQL with one seeded episode

**Why first:** Nothing downstream can run without bronze data, and nothing lands in bronze without the SQL source. This task is the leftmost arrow in the spec's data-flow diagram and unblocks W1.2 + W1.3.

**Files:**
- Create: `infra/modules/data-platform/source-sql/main.bicep`
- Create: `infra/modules/data-platform/source-sql/README.md`
- Create: `infra/modules/data-platform/source-sql/tests/source-sql.psrule.yaml`
- Create: `infra/scripts/seed-synthetic-kis.ps1`
- Create: `infra/scripts/tests/seed-synthetic-kis.Tests.ps1`
- Modify: `infra/main.bicep` (add `enableSourceSqlModule` flag + module instantiation)
- Modify: `infra/environments/sit.bicepparam` (set `enableSourceSqlModule = true`)
- Modify: `infra/environments/prod.bicepparam` (keep `enableSourceSqlModule = false`)

### Step 1.1: Branch off

```powershell
git checkout sprint-08/data-platform-resources-and-ingestion-pipeline
git pull
git checkout -b s08-source-sql
```

### Step 1.2: Write the failing PSRule test

Create `infra/modules/data-platform/source-sql/tests/source-sql.psrule.yaml`:

```yaml
---
# Per-module PSRule policy: enforces residency, MI, private endpoint, tags.
configuration:
  AZURE_BICEP_FILE_EXPANSION: true
rule:
  include:
    - Source.Sql.Residency
    - Source.Sql.ManagedIdentity
    - Source.Sql.PrivateEndpoint
    - Source.Sql.Tags
---
# Synopsis: Azure SQL server must be in switzerlandnorth (ADR-0003).
Rule 'Source.Sql.Residency' -Type 'Microsoft.Sql/servers' {
    $TargetObject.location -eq 'switzerlandnorth'
}
---
# Synopsis: Azure SQL server must use system-assigned MI - no SQL auth.
Rule 'Source.Sql.ManagedIdentity' -Type 'Microsoft.Sql/servers' {
    $TargetObject.identity.type -in @('SystemAssigned', 'UserAssigned', 'SystemAssigned,UserAssigned')
}
---
# Synopsis: SQL server public network access must be disabled.
Rule 'Source.Sql.PrivateEndpoint' -Type 'Microsoft.Sql/servers' {
    $TargetObject.properties.publicNetworkAccess -eq 'Disabled'
}
---
# Synopsis: Required tags must be present.
Rule 'Source.Sql.Tags' -Type 'Microsoft.Sql/servers', 'Microsoft.Sql/servers/databases' {
    $TargetObject.tags.env -ne $null -and
    $TargetObject.tags.owner -ne $null -and
    $TargetObject.tags.costCenter -ne $null -and
    $TargetObject.tags.workload -ne $null
}
```

### Step 1.3: Run PSRule, confirm it fails

```powershell
Install-Module -Name PSRule, PSRule.Rules.Azure -Scope CurrentUser -Force -SkipPublisherCheck
Invoke-PSRule -InputPath infra/modules/data-platform/source-sql/main.bicep `
    -Path infra/modules/data-platform/source-sql/tests/ -Outcome All -As Detail
```

Expected: failure with "input not found" because `main.bicep` does not exist yet.

### Step 1.4: Implement the Bicep module

Create `infra/modules/data-platform/source-sql/main.bicep`:

```bicep
targetScope = 'resourceGroup'

@description('Suffix appended to resource names (e.g. chhealthpf-sit).')
param nameSuffix string

@description('Deployment region. Must be switzerlandnorth (ADR-0003).')
@allowed(['switzerlandnorth'])
param location string

@description('Resource tags applied to all resources.')
param tags object

@description('Resource ID of the data subnet for the SQL private endpoint.')
param dataSubnetId string

@description('Resource ID of the Key Vault that stores the SQL admin password.')
param keyVaultId string

@description('Name of the Key Vault secret holding the SQL admin password.')
param sqlAdminPasswordSecretName string

@description('SQL admin login.')
param sqlAdminLogin string = 'sqladmin'

var serverName = 'sql-${nameSuffix}'
var databaseName = 'kis'
var privateEndpointName = 'pe-${serverName}'

resource sqlServer 'Microsoft.Sql/servers@2023-08-01-preview' = {
  name: serverName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    administratorLogin: sqlAdminLogin
    administratorLoginPassword: '@Microsoft.KeyVault(SecretUri=${reference(keyVaultId, '2023-07-01').vaultUri}secrets/${sqlAdminPasswordSecretName}/)'
    publicNetworkAccess: 'Disabled'
    minimalTlsVersion: '1.2'
    version: '12.0'
  }
}

resource kisDb 'Microsoft.Sql/servers/databases@2023-08-01-preview' = {
  parent: sqlServer
  name: databaseName
  location: location
  tags: tags
  sku: {
    name: 'GP_Gen5_2'
    tier: 'GeneralPurpose'
    family: 'Gen5'
    capacity: 2
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    zoneRedundant: false
    requestedBackupStorageRedundancy: 'Local'
  }
}

resource sqlPrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-09-01' = {
  name: privateEndpointName
  location: location
  tags: tags
  properties: {
    subnet: {
      id: dataSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'sqlServer'
        properties: {
          privateLinkServiceId: sqlServer.id
          groupIds: ['sqlServer']
        }
      }
    ]
  }
}

output sqlServerName string = sqlServer.name
output sqlServerFqdn string = sqlServer.properties.fullyQualifiedDomainName
output sqlDatabaseName string = kisDb.name
output sqlServerPrincipalId string = sqlServer.identity.principalId
```

### Step 1.5: Wire the module into `infra/main.bicep`

Append after the existing `observability` module (around line 120):

```bicep
@description('Enable Sprint 08 SQL source module.')
param enableSourceSqlModule bool = false

@description('Resource ID of the data subnet for SQL private endpoint (required when enableSourceSqlModule = true).')
param sourceSqlDataSubnetId string = ''

@description('Resource ID of the Key Vault holding the SQL admin password (required when enableSourceSqlModule = true).')
param sourceSqlKeyVaultId string = ''

@description('Name of the Key Vault secret holding the SQL admin password.')
param sourceSqlAdminPasswordSecretName string = 'sql-admin-password'

module sourceSql './modules/data-platform/source-sql/main.bicep' = if (enableSourceSqlModule) {
  name: 'source-sql-${environmentName}'
  params: {
    nameSuffix: resourceSuffix
    location: location
    tags: tags
    dataSubnetId: sourceSqlDataSubnetId
    keyVaultId: sourceSqlKeyVaultId
    sqlAdminPasswordSecretName: sourceSqlAdminPasswordSecretName
  }
}
```

### Step 1.6: Update `sit.bicepparam`

Append:

```bicep
param enableSourceSqlModule = true
param sourceSqlDataSubnetId = '/subscriptions/<SUB>/resourceGroups/rg-chhealthpf-sit/providers/Microsoft.Network/virtualNetworks/vnet-chhealthpf-sit/subnets/snet-data-sit'
param sourceSqlKeyVaultId = '/subscriptions/<SUB>/resourceGroups/rg-chhealthpf-sit/providers/Microsoft.KeyVault/vaults/kv-chhealthpf-sit'
```

Replace `<SUB>` with the actual subscription ID from Step 0.3.

### Step 1.7: Build Bicep and re-run PSRule, confirm tests pass

```powershell
az bicep build --file infra/main.bicep
Invoke-PSRule -InputPath infra/modules/data-platform/source-sql/main.bicep `
    -Path infra/modules/data-platform/source-sql/tests/ -Outcome All -As Detail
```

Expected: bicep builds clean (warnings allowed, errors not), all four PSRule rules pass.

### Step 1.8: Write the seed script test

Create `infra/scripts/tests/seed-synthetic-kis.Tests.ps1`:

```powershell
BeforeAll {
    . "$PSScriptRoot/../seed-synthetic-kis.ps1" -DryRun
}

Describe 'seed-synthetic-kis (dry run)' {
    It 'returns the expected one-episode payload in W1 mode' {
        $result = Get-W1SeedPayload
        $result.tableName | Should -Be 'kis.Episode'
        $result.rowCount | Should -Be 1
        $result.row.episode_id | Should -Match '^EP-[0-9]{8}$'
        $result.row.patient_id | Should -Match '^pseudo-[a-z0-9]{16}$'
    }

    It 'refuses to run without -DryRun unless a connection string is supplied' {
        { . "$PSScriptRoot/../seed-synthetic-kis.ps1" } | Should -Throw '*ConnectionString*'
    }
}
```

### Step 1.9: Run the test, confirm it fails

```powershell
Install-Module Pester -MinimumVersion 5.0 -Scope CurrentUser -Force -SkipPublisherCheck
Invoke-Pester -Path infra/scripts/tests/seed-synthetic-kis.Tests.ps1
```

Expected: 2 tests fail with "script not found".

### Step 1.10: Implement the seed script

Create `infra/scripts/seed-synthetic-kis.ps1`:

```powershell
<#
.SYNOPSIS
Seeds the synthetic KIS schema in Azure SQL. Walking-skeleton variant: one episode row only.
#>
[CmdletBinding()]
param(
    [string]$ConnectionString,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-W1SeedPayload {
    return @{
        tableName = 'kis.Episode'
        rowCount  = 1
        row       = @{
            episode_id   = 'EP-00000001'
            patient_id   = 'pseudo-a1b2c3d4e5f60718'
            admit_ts     = '2026-06-14T08:00:00Z'
            discharge_ts = $null
            ward         = 'INT-A'
            source       = 'walking-skeleton'
        }
    }
}

function Invoke-W1Seed {
    param([Parameter(Mandatory)][string]$ConnectionString)

    Import-Module SqlServer -ErrorAction Stop
    $payload = Get-W1SeedPayload

    $ddl = @"
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'kis')
    EXEC('CREATE SCHEMA kis');
IF OBJECT_ID('kis.Episode', 'U') IS NULL
    CREATE TABLE kis.Episode (
        episode_id   NVARCHAR(32)  NOT NULL PRIMARY KEY,
        patient_id   NVARCHAR(64)  NOT NULL,
        admit_ts     DATETIME2(0)  NOT NULL,
        discharge_ts DATETIME2(0)  NULL,
        ward         NVARCHAR(16)  NOT NULL,
        source       NVARCHAR(32)  NOT NULL
    );
"@

    $merge = @"
MERGE kis.Episode AS target
USING (SELECT @episode_id AS episode_id) AS source
ON target.episode_id = source.episode_id
WHEN NOT MATCHED THEN
    INSERT (episode_id, patient_id, admit_ts, discharge_ts, ward, source)
    VALUES (@episode_id, @patient_id, @admit_ts, @discharge_ts, @ward, @source);
"@

    Invoke-Sqlcmd -ConnectionString $ConnectionString -Query $ddl
    Invoke-Sqlcmd -ConnectionString $ConnectionString -Query $merge -Variable @(
        "episode_id=$($payload.row.episode_id)",
        "patient_id=$($payload.row.patient_id)",
        "admit_ts=$($payload.row.admit_ts)",
        "discharge_ts=$(if ($null -eq $payload.row.discharge_ts) {''} else {$payload.row.discharge_ts})",
        "ward=$($payload.row.ward)",
        "source=$($payload.row.source)"
    )
}

if ($DryRun) {
    return
}

if (-not $ConnectionString) {
    throw 'ConnectionString is required when not running in -DryRun mode.'
}

Invoke-W1Seed -ConnectionString $ConnectionString
```

### Step 1.11: Re-run the test, confirm it passes

```powershell
Invoke-Pester -Path infra/scripts/tests/seed-synthetic-kis.Tests.ps1
```

Expected: 2 tests pass.

### Step 1.12: Markdown lint and Bicep what-if

```powershell
npx --yes markdownlint-cli2 "infra/modules/data-platform/source-sql/README.md"
az bicep build --file infra/main.bicep
az deployment group what-if `
    --resource-group rg-chhealthpf-sit `
    --template-file infra/main.bicep `
    --parameters infra/environments/sit.bicepparam
```

Expected: lint exits 0; what-if shows + Microsoft.Sql/servers + Microsoft.Sql/servers/databases + Microsoft.Network/privateEndpoints, no Modify on existing resources, no Delete.

### Step 1.13: Commit and open the PR

```powershell
git add infra/modules/data-platform/source-sql infra/scripts/seed-synthetic-kis.ps1 `
        infra/scripts/tests/seed-synthetic-kis.Tests.ps1 infra/main.bicep `
        infra/environments/sit.bicepparam
git diff --cached --stat
git commit -m "feat(sprint-08): W1.1 Azure SQL source with one-episode seed script"
git push -u origin s08-source-sql
gh pr create --base sprint-08/data-platform-resources-and-ingestion-pipeline `
             --head s08-source-sql --draft `
             --title "feat(sprint-08): W1.1 Azure SQL source with one-episode seed (#66)" `
             --body-file - <<'EOF'
Closes part of #66 (walking-skeleton W1.1).

**Spec:** docs/superpowers/specs/2026-06-14-sprint-08-data-platform-design.md §8.1
**FR/NFR:** FR-DATA-001, FR-DATA-003, NFR-RES-001, NFR-SEC-002, NFR-GOV-006

## What

- New Bicep module `infra/modules/data-platform/source-sql/` (SQL server + KIS database + private endpoint).
- Seed script `infra/scripts/seed-synthetic-kis.ps1` (walking-skeleton mode = 1 episode row).
- PSRule tests for residency, MI, private endpoint, tags.
- Pester tests for the seed payload shape.

## Acceptance

`kis.Episode` has 1 row in SIT after seed runs.

## Evidence

- `az bicep build`: clean
- `Invoke-PSRule`: 4/4 pass
- `Invoke-Pester`: 2/2 pass
- `what-if`: only Creates, no Modify, no Delete

## Approval

Requires `approved-to-apply` comment before `az deployment group create` is run.
EOF
```

Expected: PR opened in draft. Wait for the `approved-to-apply` comment before deploying. After deploy, paste the verification output (one row in `kis.Episode`) as a follow-up comment.

---

## Task 2 (PR W1.2): `s08-fabric-foundation` - Fabric capacity, workspace, lakehouse, Mirror

**Why:** Provides the bronze landing zone. Mirror replicates `kis.Episode` -> `bronze.kis_episode` automatically once configured, so the downstream notebook task (W1.3) can read bronze data.

**Files:**
- Create: `infra/modules/data-platform/fabric/main.bicep` (Fabric capacity only)
- Create: `infra/modules/data-platform/fabric/post-deploy/configure-fabric.ps1` (workspace, lakehouse, mirror via Fabric REST API)
- Create: `infra/modules/data-platform/fabric/post-deploy/tests/configure-fabric.Tests.ps1`
- Create: `infra/modules/data-platform/fabric/tests/fabric.psrule.yaml`
- Create: `infra/modules/data-platform/fabric/README.md`
- Modify: `infra/main.bicep` (add `enableFabricFoundationModule`)
- Modify: `infra/environments/sit.bicepparam`

### Step 2.1: Branch off main sprint branch (PRs are parallel)

```powershell
git checkout sprint-08/data-platform-resources-and-ingestion-pipeline; git pull
git checkout -b s08-fabric-foundation
```

### Step 2.2: Write the failing PSRule test

Create `infra/modules/data-platform/fabric/tests/fabric.psrule.yaml`:

```yaml
---
configuration:
  AZURE_BICEP_FILE_EXPANSION: true
rule:
  include:
    - Fabric.Capacity.Residency
    - Fabric.Capacity.Sku
    - Fabric.Capacity.Tags
---
# Synopsis: Fabric capacity must be in switzerlandnorth (ADR-0003).
Rule 'Fabric.Capacity.Residency' -Type 'Microsoft.Fabric/capacities' {
    $TargetObject.location -eq 'switzerlandnorth'
}
---
# Synopsis: Fabric capacity must be the F2 SKU floor for SIT.
Rule 'Fabric.Capacity.Sku' -Type 'Microsoft.Fabric/capacities' {
    $TargetObject.sku.name -eq 'F2'
}
---
# Synopsis: Required tags must be present.
Rule 'Fabric.Capacity.Tags' -Type 'Microsoft.Fabric/capacities' {
    $TargetObject.tags.env -ne $null -and
    $TargetObject.tags.owner -ne $null -and
    $TargetObject.tags.costCenter -ne $null -and
    $TargetObject.tags.workload -ne $null
}
```

### Step 2.3: Run PSRule, confirm it fails

```powershell
Invoke-PSRule -InputPath infra/modules/data-platform/fabric/main.bicep `
    -Path infra/modules/data-platform/fabric/tests/ -Outcome All -As Detail
```

Expected: failure "input not found".

### Step 2.4: Implement the Fabric capacity Bicep module

Create `infra/modules/data-platform/fabric/main.bicep`:

```bicep
targetScope = 'resourceGroup'

@description('Suffix appended to resource names (e.g. chhealthpf-sit).')
param nameSuffix string

@description('Deployment region. Must be switzerlandnorth (ADR-0003).')
@allowed(['switzerlandnorth'])
param location string

@description('Resource tags applied to all resources.')
param tags object

@description('Object ID(s) of Fabric capacity administrators.')
param capacityAdmins array

var capacityName = 'fabric${replace(nameSuffix, '-', '')}'

resource fabricCapacity 'Microsoft.Fabric/capacities@2023-11-01' = {
  name: capacityName
  location: location
  tags: tags
  sku: {
    name: 'F2'
    tier: 'Fabric'
  }
  properties: {
    administration: {
      members: capacityAdmins
    }
  }
}

output capacityName string = fabricCapacity.name
output capacityId string = fabricCapacity.id
```

### Step 2.5: Wire into `infra/main.bicep`

Append:

```bicep
@description('Enable Sprint 08 Fabric foundation module.')
param enableFabricFoundationModule bool = false

@description('Object IDs of Fabric capacity administrators.')
param fabricCapacityAdmins array = []

module fabricFoundation './modules/data-platform/fabric/main.bicep' = if (enableFabricFoundationModule) {
  name: 'fabric-foundation-${environmentName}'
  params: {
    nameSuffix: resourceSuffix
    location: location
    tags: tags
    capacityAdmins: fabricCapacityAdmins
  }
}
```

### Step 2.6: Update `sit.bicepparam`

Append (replace `<your-aad-object-id>` with your account's object ID from `az ad signed-in-user show --query id -o tsv`):

```bicep
param enableFabricFoundationModule = true
param fabricCapacityAdmins = [
    '<your-aad-object-id>'
]
```

### Step 2.7: Build Bicep and re-run PSRule, confirm tests pass

```powershell
az bicep build --file infra/main.bicep
Invoke-PSRule -InputPath infra/modules/data-platform/fabric/main.bicep `
    -Path infra/modules/data-platform/fabric/tests/ -Outcome All -As Detail
```

Expected: 3/3 PSRule rules pass.

### Step 2.8: Write the configure-fabric script test (workspace + lakehouse + mirror)

Create `infra/modules/data-platform/fabric/post-deploy/tests/configure-fabric.Tests.ps1`:

```powershell
BeforeAll {
    . "$PSScriptRoot/../configure-fabric.ps1" -DryRun
}

Describe 'configure-fabric (dry run payloads)' {
    It 'workspace payload pins the right capacity and region' {
        $p = Get-WorkspaceCreatePayload -CapacityId 'fabric-chhealthpf-sit' -Region 'switzerlandnorth'
        $p.capacityId | Should -Be 'fabric-chhealthpf-sit'
        $p.displayName | Should -Be 'ws-chhealthpf-sit-data'
    }

    It 'lakehouse payload requests Delta + 3-zone layout' {
        $p = Get-LakehouseCreatePayload
        $p.displayName | Should -Be 'lh_chhealthpf_sit'
        $p.creationPayload.enableSchemas | Should -Be $true
    }

    It 'mirror payload binds source server + database + KIS schema' {
        $p = Get-MirrorCreatePayload -ServerFqdn 'sql-chhealthpf-sit.database.windows.net' -Database 'kis'
        $p.displayName | Should -Be 'mir_chhealthpf_kis'
        $p.sourceConnection.server | Should -Be 'sql-chhealthpf-sit.database.windows.net'
        $p.sourceConnection.database | Should -Be 'kis'
        $p.sourceConnection.schemas | Should -Contain 'kis'
    }
}
```

### Step 2.9: Run the test, confirm it fails

```powershell
Invoke-Pester -Path infra/modules/data-platform/fabric/post-deploy/tests/configure-fabric.Tests.ps1
```

Expected: 3 tests fail with "script not found".

### Step 2.10: Implement the configure-fabric script

Create `infra/modules/data-platform/fabric/post-deploy/configure-fabric.ps1`:

```powershell
<#
.SYNOPSIS
Configures Fabric workspace, lakehouse, and mirror via the Fabric REST API.
.NOTES
Run AFTER the Bicep deployment creates the capacity. Uses az CLI for token acquisition.
Docs: https://learn.microsoft.com/rest/api/fabric/
#>
[CmdletBinding()]
param(
    [string]$CapacityId,
    [string]$Region = 'switzerlandnorth',
    [string]$SourceServerFqdn,
    [string]$SourceDatabase = 'kis',
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-WorkspaceCreatePayload {
    param([string]$CapacityId, [string]$Region)
    return @{
        displayName = 'ws-chhealthpf-sit-data'
        description = 'Sprint 08 data platform workspace (SIT, switzerlandnorth)'
        capacityId  = $CapacityId
    }
}

function Get-LakehouseCreatePayload {
    return @{
        displayName     = 'lh_chhealthpf_sit'
        description     = 'Bronze / silver / gold zones for the capacity data product'
        creationPayload = @{
            enableSchemas = $true
        }
    }
}

function Get-MirrorCreatePayload {
    param([string]$ServerFqdn, [string]$Database)
    return @{
        displayName      = 'mir_chhealthpf_kis'
        description      = 'Mirror of the synthetic KIS Azure SQL source'
        sourceConnection = @{
            type     = 'AzureSqlDatabase'
            server   = $ServerFqdn
            database = $Database
            schemas  = @('kis')
        }
    }
}

function Invoke-FabricRest {
    param([string]$Method, [string]$Path, [object]$Body)
    $token = az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv
    $uri = "https://api.fabric.microsoft.com/v1$Path"
    Invoke-RestMethod -Method $Method -Uri $uri `
        -Headers @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' } `
        -Body ($Body | ConvertTo-Json -Depth 10)
}

if ($DryRun) { return }

if (-not $CapacityId) { throw 'CapacityId required.' }
if (-not $SourceServerFqdn) { throw 'SourceServerFqdn required.' }

# 1. Create workspace bound to the capacity
$ws = Invoke-FabricRest -Method POST -Path '/workspaces' `
    -Body (Get-WorkspaceCreatePayload -CapacityId $CapacityId -Region $Region)
Write-Host "Workspace: $($ws.id)"

# 2. Create lakehouse in the workspace
$lh = Invoke-FabricRest -Method POST -Path "/workspaces/$($ws.id)/lakehouses" `
    -Body (Get-LakehouseCreatePayload)
Write-Host "Lakehouse: $($lh.id)"

# 3. Create mirror against the source SQL
$mir = Invoke-FabricRest -Method POST -Path "/workspaces/$($ws.id)/mirroredDatabases" `
    -Body (Get-MirrorCreatePayload -ServerFqdn $SourceServerFqdn -Database $SourceDatabase)
Write-Host "Mirror: $($mir.id)"

Write-Host "Done. Wait up to 5 minutes for the initial replication snapshot."
```

### Step 2.11: Re-run the test, confirm it passes

```powershell
Invoke-Pester -Path infra/modules/data-platform/fabric/post-deploy/tests/configure-fabric.Tests.ps1
```

Expected: 3/3 pass.

### Step 2.12: Markdown lint + Bicep what-if

```powershell
npx --yes markdownlint-cli2 "infra/modules/data-platform/fabric/README.md"
az bicep build --file infra/main.bicep
az deployment group what-if `
    --resource-group rg-chhealthpf-sit `
    --template-file infra/main.bicep `
    --parameters infra/environments/sit.bicepparam
```

Expected: lint clean; what-if shows + Microsoft.Fabric/capacities only.

### Step 2.13: Commit and open the PR

```powershell
git add infra/modules/data-platform/fabric infra/main.bicep infra/environments/sit.bicepparam
git commit -m "feat(sprint-08): W1.2 Fabric capacity + workspace + lakehouse + mirror config"
git push -u origin s08-fabric-foundation
gh pr create --base sprint-08/data-platform-resources-and-ingestion-pipeline `
             --head s08-fabric-foundation --draft `
             --title "feat(sprint-08): W1.2 Fabric foundation (capacity + workspace + lakehouse + mirror) (#66)" `
             --body "Closes part of #66 (walking-skeleton W1.2). Spec §8.1. Requires W1.1 (`s08-source-sql`) merged + deployed first so the Mirror has a source to bind to. Approval gate: `approved-to-apply` before `az deployment group create` and before running `configure-fabric.ps1`."
```

Expected: PR opened. After approval and deploy, run `configure-fabric.ps1` and post the resulting workspace/lakehouse/mirror IDs as a comment. Verify with `az rest -m GET -u "https://api.fabric.microsoft.com/v1/workspaces/<id>/items"` - the lakehouse should appear, and after the initial snapshot, `bronze.kis_episode` should have 1 row.

---

## Task 3 (PR W1.3): `s08-silver-gold-thin` - Notebooks for one-table path

**Why:** Conforms the mirrored bronze row to the silver and gold contracts. This is the only task with genuine local-PySpark TDD.

**Files:**
- Create: `infra/modules/data-platform/fabric/notebooks/nb_silver_transform.py`
- Create: `infra/modules/data-platform/fabric/notebooks/nb_gold_publish.py`
- Create: `infra/modules/data-platform/fabric/notebooks/_lib/transforms.py` (pure functions for local testing)
- Create: `infra/modules/data-platform/fabric/notebooks/tests/__init__.py`
- Create: `infra/modules/data-platform/fabric/notebooks/tests/test_silver_transform.py`
- Create: `infra/modules/data-platform/fabric/notebooks/tests/test_gold_publish.py`
- Create: `infra/modules/data-platform/fabric/notebooks/tests/conftest.py`
- Create: `infra/modules/data-platform/fabric/notebooks/requirements-dev.txt`

### Step 3.1: Branch off

```powershell
git checkout sprint-08/data-platform-resources-and-ingestion-pipeline; git pull
git checkout -b s08-silver-gold-thin
```

### Step 3.2: Create the test harness

Create `infra/modules/data-platform/fabric/notebooks/requirements-dev.txt`:

```text
pyspark==3.5.1
pytest==8.2.0
great-expectations==0.18.16
```

Create `infra/modules/data-platform/fabric/notebooks/tests/conftest.py`:

```python
import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    return (
        SparkSession.builder.master("local[2]")
        .appName("sprint08-notebook-tests")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.driver.memory", "512m")
        .getOrCreate()
    )
```

### Step 3.3: Write the failing silver test

Create `infra/modules/data-platform/fabric/notebooks/tests/test_silver_transform.py`:

```python
from pyspark.sql import Row

from infra.modules.data_platform.fabric.notebooks._lib import transforms


def test_silver_episode_drops_non_allowlisted_columns(spark):
    bronze = spark.createDataFrame([
        Row(
            episode_id="EP-00000001",
            patient_id="pseudo-a1b2c3d4e5f60718",
            admit_ts="2026-06-14T08:00:00Z",
            discharge_ts=None,
            ward="INT-A",
            source="walking-skeleton",
            leaked_column="should-not-survive",
        )
    ])
    silver = transforms.bronze_to_silver_episode(bronze)
    assert "leaked_column" not in silver.columns
    assert set(silver.columns) == {
        "episode_id", "patient_id", "admit_ts", "discharge_ts", "ward",
    }
    assert silver.count() == 1


def test_silver_quarantines_bad_pseudonym(spark):
    bronze = spark.createDataFrame([
        Row(
            episode_id="EP-00000002",
            patient_id="John Doe",  # not a valid pseudonym
            admit_ts="2026-06-14T09:00:00Z",
            discharge_ts=None,
            ward="INT-A",
            source="walking-skeleton",
        )
    ])
    silver, quarantine = transforms.bronze_to_silver_episode_with_quarantine(bronze)
    assert silver.count() == 0
    assert quarantine.count() == 1
    assert quarantine.first()["quarantine_reason"] == "pii-shape-mismatch"
```

### Step 3.4: Write the failing gold test

Create `infra/modules/data-platform/fabric/notebooks/tests/test_gold_publish.py`:

```python
from pyspark.sql import Row

from infra.modules.data_platform.fabric.notebooks._lib import transforms


def test_gold_demand_encounter_from_silver_episode(spark):
    silver = spark.createDataFrame([
        Row(
            episode_id="EP-00000001",
            patient_id="pseudo-a1b2c3d4e5f60718",
            admit_ts="2026-06-14T08:00:00Z",
            discharge_ts=None,
            ward="INT-A",
        )
    ])
    gold = transforms.silver_episode_to_gold_demand_encounter(silver, provenance_source="kis-mirror")
    row = gold.first()
    assert row["episode_id"] == "EP-00000001"
    assert row["provenance_source"] == "kis-mirror"
    assert row["purpose_tags"] == ["capacity-planning"]
    assert row["residency"] == "CH"


def test_gold_rejects_silver_without_residency_tag(spark):
    silver = spark.createDataFrame([
        Row(
            episode_id="EP-00000001",
            patient_id="pseudo-a1b2c3d4e5f60718",
            admit_ts="2026-06-14T08:00:00Z",
            discharge_ts=None,
            ward="INT-A",
        )
    ])
    gold = transforms.silver_episode_to_gold_demand_encounter(silver, provenance_source="kis-mirror")
    # The transform itself stamps residency='CH'; the test confirms it is always present.
    assert gold.filter(gold.residency.isNull()).count() == 0
```

### Step 3.5: Run tests, confirm they fail

```powershell
python -m venv .venv-sprint08
.venv-sprint08\Scripts\Activate.ps1
pip install -r infra/modules/data-platform/fabric/notebooks/requirements-dev.txt
pytest infra/modules/data-platform/fabric/notebooks/tests/ -v
```

Expected: 4 failures with `ModuleNotFoundError: ... transforms`.

### Step 3.6: Implement the transform library

Create `infra/modules/data-platform/fabric/notebooks/_lib/__init__.py` (empty file).

Create `infra/modules/data-platform/fabric/notebooks/_lib/transforms.py`:

```python
"""Pure transforms used by silver/gold notebooks. Local-testable, no Fabric runtime."""
from __future__ import annotations

import re
from typing import Tuple

from pyspark.sql import DataFrame, functions as F, types as T


_EPISODE_ALLOWLIST = ["episode_id", "patient_id", "admit_ts", "discharge_ts", "ward"]
_PSEUDONYM_RE = r"^pseudo-[a-z0-9]{16}$"


def bronze_to_silver_episode(bronze: DataFrame) -> DataFrame:
    """Allow-list columns, return silver shape only (no quarantine handling)."""
    silver, _ = bronze_to_silver_episode_with_quarantine(bronze)
    return silver


def bronze_to_silver_episode_with_quarantine(bronze: DataFrame) -> Tuple[DataFrame, DataFrame]:
    """Apply allow-list + PII-shape invariant. Returns (silver, quarantine)."""
    projected = bronze.select(*[c for c in _EPISODE_ALLOWLIST if c in bronze.columns])

    valid = projected.filter(F.col("patient_id").rlike(_PSEUDONYM_RE))
    invalid = projected.filter(~F.col("patient_id").rlike(_PSEUDONYM_RE))

    quarantine = invalid.withColumn(
        "quarantine_reason", F.lit("pii-shape-mismatch")
    ).withColumn(
        "quarantine_ts", F.current_timestamp()
    )

    return valid, quarantine


def silver_episode_to_gold_demand_encounter(
    silver: DataFrame,
    provenance_source: str,
) -> DataFrame:
    """Conform silver episodes to DC-DEMAND-ENCOUNTER-v1 envelope."""
    return (
        silver
        .withColumn("provenance_source", F.lit(provenance_source))
        .withColumn("purpose_tags", F.array(F.lit("capacity-planning")))
        .withColumn("residency", F.lit("CH"))
        .withColumn("emitted_ts", F.current_timestamp())
    )
```

### Step 3.7: Run tests, confirm they pass

```powershell
pytest infra/modules/data-platform/fabric/notebooks/tests/ -v
```

Expected: 4/4 pass.

### Step 3.8: Wrap the transforms in the Fabric notebook entrypoints

Create `infra/modules/data-platform/fabric/notebooks/nb_silver_transform.py`:

```python
# Databricks-style Fabric notebook. Cells separated by `# COMMAND ----------`.
# Imports the local _lib transforms (Fabric copies this directory at deploy time).

# COMMAND ----------
from _lib import transforms

# COMMAND ----------
LAKEHOUSE = "lh_chhealthpf_sit"

bronze = spark.read.format("delta").table(f"{LAKEHOUSE}.bronze_kis_episode")

silver, quarantine = transforms.bronze_to_silver_episode_with_quarantine(bronze)

# COMMAND ----------
(
    silver.write.format("delta")
    .mode("append")
    .option("mergeSchema", "true")
    .saveAsTable(f"{LAKEHOUSE}.silver_episode")
)

(
    quarantine.write.format("delta")
    .mode("append")
    .option("mergeSchema", "true")
    .saveAsTable(f"{LAKEHOUSE}.silver_quarantine_episode")
)
```

Create `infra/modules/data-platform/fabric/notebooks/nb_gold_publish.py`:

```python
# Fabric notebook. Reads silver, writes gold.demand_encounter (mirror path).

# COMMAND ----------
from _lib import transforms

# COMMAND ----------
LAKEHOUSE = "lh_chhealthpf_sit"

silver = spark.read.format("delta").table(f"{LAKEHOUSE}.silver_episode")
gold = transforms.silver_episode_to_gold_demand_encounter(silver, provenance_source="kis-mirror")

# COMMAND ----------
(
    gold.write.format("delta")
    .mode("append")
    .option("mergeSchema", "true")
    .saveAsTable(f"{LAKEHOUSE}.gold_demand_encounter")
)
```

### Step 3.9: Commit and open the PR

```powershell
git add infra/modules/data-platform/fabric/notebooks
git commit -m "feat(sprint-08): W1.3 silver/gold notebooks for one-table walking-skeleton path"
git push -u origin s08-silver-gold-thin
gh pr create --base sprint-08/data-platform-resources-and-ingestion-pipeline `
             --head s08-silver-gold-thin --draft `
             --title "feat(sprint-08): W1.3 silver/gold notebooks (Episode-only) (#66)" `
             --body "Closes part of #66 (walking-skeleton W1.3). Spec §8.1. Local PySpark tests: 4/4 pass. Requires W1.2 merged + Fabric workspace/lakehouse created so the notebook can be uploaded. Upload after merge via Fabric UI or REST `/workspaces/{id}/notebooks` (out of scope for this PR's Bicep)."
```

---

## Task 4 (PR W1.4): `s08-semantic-model-thin` - Direct Lake Semantic Model with one measure

**Why:** Makes the data visible to a human in Power BI - the only acceptance criterion that's not a CLI grep.

**Files:**
- Create: `infra/modules/data-platform/fabric/semantic-model/definition/definition.pbism` (Power BI Project model definition)
- Create: `infra/modules/data-platform/fabric/semantic-model/definition/model.bim` (tabular model with one measure)
- Create: `infra/modules/data-platform/fabric/semantic-model/post-deploy/publish-semantic-model.ps1`
- Create: `infra/modules/data-platform/fabric/semantic-model/post-deploy/tests/publish-semantic-model.Tests.ps1`
- Create: `infra/modules/data-platform/fabric/semantic-model/README.md`

### Step 4.1: Branch off

```powershell
git checkout sprint-08/data-platform-resources-and-ingestion-pipeline; git pull
git checkout -b s08-semantic-model-thin
```

### Step 4.2: Write the failing test for the model definition

Create `infra/modules/data-platform/fabric/semantic-model/post-deploy/tests/publish-semantic-model.Tests.ps1`:

```powershell
BeforeAll {
    . "$PSScriptRoot/../publish-semantic-model.ps1" -DryRun
}

Describe 'publish-semantic-model (dry run)' {
    It 'Encounter Count measure exists in the model definition' {
        $bim = Get-Content -Raw "$PSScriptRoot/../../definition/model.bim" | ConvertFrom-Json
        $measure = $bim.model.tables[0].measures | Where-Object { $_.name -eq 'Encounter Count' }
        $measure | Should -Not -BeNullOrEmpty
        $measure.expression | Should -Be "COUNTROWS('gold_demand_encounter')"
    }

    It 'model is Direct Lake (mode = directLake)' {
        $bim = Get-Content -Raw "$PSScriptRoot/../../definition/model.bim" | ConvertFrom-Json
        $bim.model.tables[0].partitions[0].mode | Should -Be 'directLake'
    }
}
```

### Step 4.3: Run the test, confirm it fails

```powershell
Invoke-Pester -Path infra/modules/data-platform/fabric/semantic-model/post-deploy/tests/publish-semantic-model.Tests.ps1
```

Expected: 2 tests fail with "file not found".

### Step 4.4: Implement the model definition

Create `infra/modules/data-platform/fabric/semantic-model/definition/model.bim`:

```json
{
  "name": "sm_capacity_data_product",
  "compatibilityLevel": 1604,
  "model": {
    "culture": "en-CH",
    "defaultPowerBIDataSourceVersion": "powerBI_V3",
    "sourceQueryCulture": "en-CH",
    "tables": [
      {
        "name": "gold_demand_encounter",
        "partitions": [
          {
            "name": "gold_demand_encounter",
            "mode": "directLake",
            "source": {
              "type": "entity",
              "entityName": "gold_demand_encounter",
              "schemaName": "dbo",
              "expressionSource": "DatabaseQuery"
            }
          }
        ],
        "columns": [
          { "name": "episode_id", "dataType": "string", "sourceColumn": "episode_id" },
          { "name": "patient_id", "dataType": "string", "sourceColumn": "patient_id" },
          { "name": "admit_ts", "dataType": "dateTime", "sourceColumn": "admit_ts" },
          { "name": "ward", "dataType": "string", "sourceColumn": "ward" },
          { "name": "provenance_source", "dataType": "string", "sourceColumn": "provenance_source" },
          { "name": "residency", "dataType": "string", "sourceColumn": "residency" }
        ],
        "measures": [
          {
            "name": "Encounter Count",
            "expression": "COUNTROWS('gold_demand_encounter')",
            "formatString": "#,0"
          }
        ]
      }
    ]
  }
}
```

Create `infra/modules/data-platform/fabric/semantic-model/definition/definition.pbism`:

```json
{
  "version": "4.0",
  "settings": {}
}
```

### Step 4.5: Implement the publish script

Create `infra/modules/data-platform/fabric/semantic-model/post-deploy/publish-semantic-model.ps1`:

```powershell
[CmdletBinding()]
param(
    [string]$WorkspaceId,
    [string]$LakehouseId,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($DryRun) { return }

if (-not $WorkspaceId -or -not $LakehouseId) {
    throw 'WorkspaceId and LakehouseId are required.'
}

$bimPath = Join-Path $PSScriptRoot '..\definition\model.bim'
$bim = Get-Content -Raw $bimPath | ConvertFrom-Json

# Inject the Direct Lake source pointing at the lakehouse SQL endpoint
$bim.model.tables[0].partitions[0].source.expressionSource = "DatabaseQuery_$LakehouseId"

$token = az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv

$payload = @{
    displayName = 'sm_capacity_data_product'
    description = 'Direct Lake semantic model over the capacity data product gold zone'
    definition  = @{
        format = 'TMSL'
        parts  = @(
            @{
                path        = 'model.bim'
                payload     = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($bim | ConvertTo-Json -Depth 30)))
                payloadType = 'InlineBase64'
            }
        )
    }
}

$response = Invoke-RestMethod -Method POST `
    -Uri "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/semanticModels" `
    -Headers @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' } `
    -Body ($payload | ConvertTo-Json -Depth 20)

Write-Host "Semantic model published: $($response.id)"
```

### Step 4.6: Re-run the test, confirm it passes

```powershell
Invoke-Pester -Path infra/modules/data-platform/fabric/semantic-model/post-deploy/tests/publish-semantic-model.Tests.ps1
```

Expected: 2/2 pass.

### Step 4.7: Commit and open the PR

```powershell
git add infra/modules/data-platform/fabric/semantic-model
git commit -m "feat(sprint-08): W1.4 Direct Lake semantic model with Encounter Count"
git push -u origin s08-semantic-model-thin
gh pr create --base sprint-08/data-platform-resources-and-ingestion-pipeline `
             --head s08-semantic-model-thin --draft `
             --title "feat(sprint-08): W1.4 Direct Lake semantic model (thin) (#66)" `
             --body "Closes part of #66 (walking-skeleton W1.4). Spec §8.1. Requires W1.2 (workspace + lakehouse) merged. After merge + deploy, connect Power BI Desktop to the workspace, refresh, confirm Encounter Count returns 1 (mirror only, simulator not yet wired)."
```

---

## Task 5 (PR W1.5): `s08-simulator-thin` - ACA producer emits one event

**Why:** Demonstrates the second path into gold and completes the demo. After this PR is deployed, Power BI's `Encounter Count` flips from `1` to `2`.

**Files:**
- Create: `apps/sim-capacity/pyproject.toml`
- Create: `apps/sim-capacity/Dockerfile`
- Create: `apps/sim-capacity/src/sim_capacity/__init__.py`
- Create: `apps/sim-capacity/src/sim_capacity/contracts.py`
- Create: `apps/sim-capacity/src/sim_capacity/producer.py`
- Create: `apps/sim-capacity/tests/__init__.py`
- Create: `apps/sim-capacity/tests/test_envelope_invariants.py`
- Create: `apps/sim-capacity/tests/test_producer.py`
- Create: `infra/modules/data-platform/simulator/main.bicep`
- Create: `infra/modules/data-platform/simulator/tests/simulator.psrule.yaml`
- Create: `infra/modules/data-platform/simulator/README.md`
- Modify: `infra/main.bicep`
- Modify: `infra/environments/sit.bicepparam`

### Step 5.1: Branch off

```powershell
git checkout sprint-08/data-platform-resources-and-ingestion-pipeline; git pull
git checkout -b s08-simulator-thin
```

### Step 5.2: Scaffold the Python project

Create `apps/sim-capacity/pyproject.toml`:

```toml
[project]
name = "sim-capacity"
version = "0.1.0"
description = "Real-time capacity simulator for Sprint 08 walking skeleton"
requires-python = ">=3.11"
dependencies = [
    "azure-eventhub==5.12.0",
    "azure-identity==1.17.0",
]

[project.optional-dependencies]
dev = ["pytest==8.2.0"]

[tool.pytest.ini_options]
pythonpath = ["src"]
```

Create `apps/sim-capacity/src/sim_capacity/__init__.py` (empty).

### Step 5.3: Write the failing envelope test

Create `apps/sim-capacity/tests/test_envelope_invariants.py`:

```python
import pytest

from sim_capacity.contracts import build_demand_encounter_envelope, EnvelopeViolation


def test_envelope_contains_required_fields():
    env = build_demand_encounter_envelope(
        episode_id="EP-SIM-00000001",
        patient_id="pseudo-z9y8x7w6v5u43210",
        admit_ts="2026-06-14T10:00:00Z",
        ward="INT-A",
    )
    assert env["purpose_tags"] == ["capacity-planning"]
    assert env["residency"] == "CH"
    assert env["provenance_source"] == "simulator"
    assert env["episode_id"] == "EP-SIM-00000001"


def test_envelope_rejects_bad_pseudonym():
    with pytest.raises(EnvelopeViolation, match="patient_id"):
        build_demand_encounter_envelope(
            episode_id="EP-SIM-00000002",
            patient_id="John Doe",
            admit_ts="2026-06-14T10:00:00Z",
            ward="INT-A",
        )


def test_envelope_rejects_pii_field_names():
    with pytest.raises(EnvelopeViolation, match="pii"):
        build_demand_encounter_envelope(
            episode_id="EP-SIM-00000003",
            patient_id="pseudo-z9y8x7w6v5u43210",
            admit_ts="2026-06-14T10:00:00Z",
            ward="INT-A",
            extra={"full_name": "Erika Muster"},
        )
```

### Step 5.4: Write the failing producer test

Create `apps/sim-capacity/tests/test_producer.py`:

```python
from unittest.mock import MagicMock

from sim_capacity.producer import emit_once


def test_emit_once_sends_one_valid_event():
    client = MagicMock()
    emit_once(client=client, profile_name="walking-skeleton")
    assert client.send_event.call_count == 1
    sent = client.send_event.call_args[0][0]
    assert sent.body_as_json()["provenance_source"] == "simulator"
    assert sent.body_as_json()["purpose_tags"] == ["capacity-planning"]


def test_emit_once_skips_invalid_events_without_calling_client():
    client = MagicMock()
    # Force the profile to yield a row that fails the contract.
    emit_once(
        client=client,
        profile_name="walking-skeleton",
        _override_payload={"patient_id": "John Doe"},  # bad pseudonym
    )
    assert client.send_event.call_count == 0
```

### Step 5.5: Run tests, confirm they fail

```powershell
cd apps/sim-capacity
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest -v
cd ../..
```

Expected: 5 failures (ModuleNotFoundError).

### Step 5.6: Implement the contracts module

Create `apps/sim-capacity/src/sim_capacity/contracts.py`:

```python
"""DC-DEMAND-ENCOUNTER-v1 envelope construction with contract enforcement."""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Mapping


_PSEUDONYM_RE = re.compile(r"^pseudo-[a-z0-9]{16}$")
_PII_DENY_FIELDS = frozenset({
    "full_name", "first_name", "last_name", "ssn", "ahv", "dob",
    "address", "email", "phone",
})


class EnvelopeViolation(ValueError):
    """Raised when a payload would violate the data contract."""


def build_demand_encounter_envelope(
    *,
    episode_id: str,
    patient_id: str,
    admit_ts: str,
    ward: str,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if not _PSEUDONYM_RE.match(patient_id):
        raise EnvelopeViolation(f"patient_id does not match pseudonym shape: {patient_id!r}")

    if extra:
        leaked = _PII_DENY_FIELDS & set(extra.keys())
        if leaked:
            raise EnvelopeViolation(f"pii deny-list fields present: {sorted(leaked)}")

    return {
        "episode_id": episode_id,
        "patient_id": patient_id,
        "admit_ts": admit_ts,
        "discharge_ts": None,
        "ward": ward,
        "provenance_source": "simulator",
        "purpose_tags": ["capacity-planning"],
        "residency": "CH",
        "emitted_ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
```

### Step 5.7: Implement the producer module

Create `apps/sim-capacity/src/sim_capacity/producer.py`:

```python
"""Always-on producer entrypoint. Walking-skeleton: emits ONE event on start."""
from __future__ import annotations

import json
import logging
import os
from typing import Any

from azure.eventhub import EventData, EventHubProducerClient
from azure.identity import DefaultAzureCredential

from .contracts import EnvelopeViolation, build_demand_encounter_envelope


log = logging.getLogger("sim_capacity.producer")


def _walking_skeleton_payload() -> dict[str, Any]:
    return {
        "episode_id": "EP-SIM-00000001",
        "patient_id": "pseudo-z9y8x7w6v5u43210",
        "admit_ts": "2026-06-14T10:00:00Z",
        "ward": "INT-A",
    }


def emit_once(
    *,
    client: EventHubProducerClient,
    profile_name: str,
    _override_payload: dict[str, Any] | None = None,
) -> None:
    """Emit a single envelope. Profile choice + payload override are testing hooks."""
    if profile_name != "walking-skeleton":
        raise NotImplementedError(f"profile {profile_name!r} is not in W1 scope")

    raw = {**_walking_skeleton_payload(), **(_override_payload or {})}

    try:
        envelope = build_demand_encounter_envelope(
            episode_id=raw["episode_id"],
            patient_id=raw["patient_id"],
            admit_ts=raw["admit_ts"],
            ward=raw["ward"],
        )
    except EnvelopeViolation as exc:
        log.warning("envelope rejected before send: %s", exc)
        return

    event = EventData(json.dumps(envelope))
    client.send_event(event)
    log.info("emitted: episode_id=%s", envelope["episode_id"])


def main() -> None:
    eventstream_fqdn = os.environ["EVENTSTREAM_FQDN"]
    eventstream_name = os.environ["EVENTSTREAM_NAME"]

    credential = DefaultAzureCredential()
    client = EventHubProducerClient(
        fully_qualified_namespace=eventstream_fqdn,
        eventhub_name=eventstream_name,
        credential=credential,
    )
    try:
        emit_once(client=client, profile_name="walking-skeleton")
    finally:
        client.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
```

### Step 5.8: Run tests, confirm they pass

```powershell
cd apps/sim-capacity; .venv\Scripts\Activate.ps1; pytest -v; cd ../..
```

Expected: 5/5 pass.

### Step 5.9: Add the Dockerfile

Create `apps/sim-capacity/Dockerfile`:

```dockerfile
FROM mcr.microsoft.com/cbl-mariner/distroless/python:3.11

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src

# Install deps into a virtualenv to keep the distroless image minimal
USER root
RUN python -m pip install --no-cache-dir .

USER nonroot
ENV PYTHONPATH=/app/src
ENTRYPOINT ["python", "-m", "sim_capacity.producer"]
```

### Step 5.10: Add ACA Bicep module

Create `infra/modules/data-platform/simulator/main.bicep`:

```bicep
targetScope = 'resourceGroup'

@description('Suffix appended to resource names (e.g. chhealthpf-sit).')
param nameSuffix string

@description('Deployment region. Must be switzerlandnorth (ADR-0003).')
@allowed(['switzerlandnorth'])
param location string

@description('Resource tags applied to all resources.')
param tags object

@description('Resource ID of the ACA subnet.')
param acaSubnetId string

@description('Resource ID of the Log Analytics workspace.')
param logAnalyticsId string

@description('FQDN of the Eventstream namespace (e.g. eh-chhealthpf-sit.servicebus.windows.net).')
param eventstreamFqdn string

@description('Name of the Eventstream inside the namespace.')
param eventstreamName string

@description('Container image (e.g. acr-chhealthpf-sit.azurecr.io/sim-capacity:<sha>).')
param image string

var envName = 'cae-${nameSuffix}'
var appName = 'aca-sim-producer'
var uamiName = 'id-sim-${nameSuffix}'

resource uami 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: uamiName
  location: location
  tags: tags
}

resource acaEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: envName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: reference(logAnalyticsId, '2022-10-01').customerId
        sharedKey: listKeys(logAnalyticsId, '2022-10-01').primarySharedKey
      }
    }
    vnetConfiguration: {
      infrastructureSubnetId: acaSubnetId
      internal: true
    }
  }
}

resource simProducer 'Microsoft.App/containerApps@2024-03-01' = {
  name: appName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${uami.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: acaEnv.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: null
    }
    template: {
      containers: [
        {
          name: 'producer'
          image: image
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'EVENTSTREAM_FQDN', value: eventstreamFqdn }
            { name: 'EVENTSTREAM_NAME', value: eventstreamName }
            { name: 'AZURE_CLIENT_ID', value: uami.properties.clientId }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1
      }
    }
  }
}

output uamiPrincipalId string = uami.properties.principalId
output containerAppName string = simProducer.name
```

### Step 5.11: PSRule for simulator

Create `infra/modules/data-platform/simulator/tests/simulator.psrule.yaml`:

```yaml
---
configuration:
  AZURE_BICEP_FILE_EXPANSION: true
rule:
  include:
    - Simulator.Residency
    - Simulator.UAMI
    - Simulator.NoIngress
    - Simulator.ScaleAlwaysOn
---
Rule 'Simulator.Residency' -Type 'Microsoft.App/containerApps', 'Microsoft.App/managedEnvironments' {
    $TargetObject.location -eq 'switzerlandnorth'
}
---
Rule 'Simulator.UAMI' -Type 'Microsoft.App/containerApps' {
    $TargetObject.identity.type -eq 'UserAssigned'
}
---
Rule 'Simulator.NoIngress' -Type 'Microsoft.App/containerApps' {
    $null -eq $TargetObject.properties.configuration.ingress
}
---
Rule 'Simulator.ScaleAlwaysOn' -Type 'Microsoft.App/containerApps' {
    $TargetObject.properties.template.scale.minReplicas -ge 1
}
```

### Step 5.12: Build, what-if, PSRule

```powershell
az bicep build --file infra/main.bicep
Invoke-PSRule -InputPath infra/modules/data-platform/simulator/main.bicep `
    -Path infra/modules/data-platform/simulator/tests/ -Outcome All -As Detail
az deployment group what-if `
    --resource-group rg-chhealthpf-sit `
    --template-file infra/main.bicep `
    --parameters infra/environments/sit.bicepparam
```

Expected: 4/4 PSRule pass; what-if shows + ACA env + ACA app + UAMI.

### Step 5.13: Commit and open the PR

```powershell
git add apps/sim-capacity infra/modules/data-platform/simulator infra/main.bicep `
        infra/environments/sit.bicepparam
git commit -m "feat(sprint-08): W1.5 ACA simulator producer emits one walking-skeleton event"
git push -u origin s08-simulator-thin
gh pr create --base sprint-08/data-platform-resources-and-ingestion-pipeline `
             --head s08-simulator-thin --draft `
             --title "feat(sprint-08): W1.5 simulator producer (one event) (#66)" `
             --body "Closes part of #66 (walking-skeleton W1.5). Spec §8.1. Requires W1.2 (Eventstream resource) merged + deployed. After deploy: Power BI Encounter Count flips from 1 to 2. Approval gate before any deploy."
```

---

## Week 1 Demo Gate

After all five PRs (`s08-source-sql`, `s08-fabric-foundation`, `s08-silver-gold-thin`, `s08-semantic-model-thin`, `s08-simulator-thin`) are merged into `sprint-08/data-platform-resources-and-ingestion-pipeline` and deployed to SIT:

- [ ] **Demo Step 1: Verify the mirror row**

```powershell
az rest -m GET `
    -u "https://api.fabric.microsoft.com/v1/workspaces/<ws-id>/lakehouses/<lh-id>/tables" `
    --headers "Authorization=Bearer $(az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv)"
```

Expected: `bronze_kis_episode`, `silver_episode`, `gold_demand_encounter` all listed; `gold_demand_encounter` row count >= 1.

- [ ] **Demo Step 2: Verify the simulator row**

```powershell
az containerapp logs show --name aca-sim-producer --resource-group rg-chhealthpf-sit --tail 20
```

Expected: log line `emitted: episode_id=EP-SIM-00000001`.

- [ ] **Demo Step 3: Verify Power BI Encounter Count = 2**

Open Power BI, connect to workspace `ws-chhealthpf-sit-data`, refresh `sm_capacity_data_product`. Confirm `Encounter Count = 2` (one from mirror, one from simulator). Screenshot it. Attach to issue `#66`.

- [ ] **Demo Step 4: Close walking-skeleton sub-milestone**

Comment on `#66`:

```text
Walking skeleton (W1) complete. Power BI shows Encounter Count = 2 (mirror + simulator).
Demo evidence attached. Proceeding to W2 plan.
```

---

## Self-Review (run after writing this plan, before handoff)

**1. Spec coverage** - every numbered W1 item in spec §8.1 has a Task in this plan: W1.1 -> Task 1, W1.2 -> Task 2, W1.3 -> Task 3, W1.4 -> Task 4, W1.5 -> Task 5. ✅

**2. Placeholder scan** - searched for "TBD", "TODO", "implement later", "similar to" - none present. The one inline `<SUB>`, `<your-aad-object-id>`, `<ws-id>`, `<lh-id>` placeholders are flagged in their respective steps as "replace with actual value from Step X" and are correct in a plan (a plan cannot know subscription IDs).

**3. Type consistency** - `transforms.bronze_to_silver_episode_with_quarantine` is the canonical name in Task 3 implementation and tests. `Get-W1SeedPayload`, `Get-WorkspaceCreatePayload`, `Get-LakehouseCreatePayload`, `Get-MirrorCreatePayload`, `Encounter Count`, `gold_demand_encounter`, `provenance_source`, `purpose_tags`, `residency` - all consistent across tasks.

**4. Dependency order** - W1.1 must deploy before W1.2's Mirror can bind; W1.2 must deploy before W1.3's notebooks can read bronze; W1.3 must deploy before W1.4's Direct Lake reads gold; W1.5 is independent of W1.3/W1.4 for code review but its deploy must follow W1.2 (Eventstream). PR creation order can be parallel; deploy order is enforced by the `approved-to-apply` gate.

**5. Approval gates** - every deploy step requires `approved-to-apply` per `AGENTS.md` §4. Never bypass.

---

## References

- Spec: [docs/superpowers/specs/2026-06-14-sprint-08-data-platform-design.md](../specs/2026-06-14-sprint-08-data-platform-design.md)
- Sprint baseline: [docs/sprints/sprint-08-data-platform-resources-and-ingestion-pipeline.md](../../sprints/sprint-08-data-platform-resources-and-ingestion-pipeline.md)
- Umbrella issue: `#66`
- Baseline PR: `#67`
- ADRs: [ADR-0003](../../adr/0003-swiss-regional-inference-for-phi.md), [ADR-0004](../../adr/0004-block-global-and-data-zone-for-phi.md)
- Fabric REST API: <https://learn.microsoft.com/rest/api/fabric/>
