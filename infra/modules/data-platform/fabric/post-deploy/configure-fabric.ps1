<#
.SYNOPSIS
Configures Fabric workspace, lakehouse, and mirrored database via the Fabric REST API.
.NOTES
Run AFTER the Bicep deployment creates the capacity AND after a Fabric connection
to the source Azure SQL database has been created (portal or POST /v1/connections).
Uses az CLI for token acquisition.
Docs:
- Create mirrored database: https://learn.microsoft.com/fabric/mirroring/mirrored-database-rest-api#create-mirrored-database
- Mirrored database definition: https://learn.microsoft.com/rest/api/fabric/articles/item-management/definitions/mirrored-database-definition
- List capacities:           https://learn.microsoft.com/rest/api/fabric/core/capacities/list-capacities
#>
[CmdletBinding()]
param(
    [string]$CapacityName,
    [string]$ConnectionId,
    [string]$SourceDatabase = 'kis',
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-FabricRest {
    param([string]$Method, [string]$Path, [object]$Body)
    $token = az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv
    $uri = "https://api.fabric.microsoft.com/v1$Path"
    $headers = @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' }
    if ($null -ne $Body) {
        Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers -Body ($Body | ConvertTo-Json -Depth 10)
    } else {
        Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers
    }
}

function Resolve-FabricCapacityIdByName {
    param([Parameter(Mandatory)][string]$CapacityName)
    $resp = Invoke-FabricRest -Method GET -Path '/capacities'
    $match = $resp.value | Where-Object { $_.displayName -eq $CapacityName }
    if (-not $match) { throw "Fabric capacity '$CapacityName' not found via GET /v1/capacities." }
    if ($match -is [array]) { $match = $match[0] }
    return $match.id
}

function Get-WorkspaceCreatePayload {
    param([Parameter(Mandatory)][string]$CapacityId)
    return @{
        displayName = 'ws-ihzhhpf-sit-data'
        description = 'Sprint 08 data platform workspace (SIT, switzerlandnorth)'
        capacityId  = $CapacityId
    }
}

function Get-LakehouseCreatePayload {
    return @{
        displayName     = 'lh_ihzhhpf_sit'
        description     = 'Bronze / silver / gold zones for the capacity data product'
        creationPayload = @{
            enableSchemas = $true
        }
    }
}

function Get-MirrorCreatePayload {
    param(
        [Parameter(Mandatory)][string]$ConnectionId,
        [Parameter(Mandatory)][string]$Database,
        [string]$DefaultSchema = 'kis',
        [int]$RetentionInDays = 30
    )
    $inner = @{
        properties = @{
            source = @{
                type           = 'AzureSqlDatabase'
                typeProperties = @{
                    connection = $ConnectionId
                    database   = $Database
                }
            }
            target = @{
                type           = 'MountedRelationalDatabase'
                typeProperties = @{
                    defaultSchema   = $DefaultSchema
                    format          = 'Delta'
                    retentionInDays = $RetentionInDays
                }
            }
        }
    }
    $json = $inner | ConvertTo-Json -Depth 10
    $base64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($json))
    return @{
        displayName = 'mir_ihzhhpf_kis'
        description = 'Mirror of the synthetic KIS Azure SQL source'
        definition  = @{
            parts = @(
                @{
                    path        = 'mirroring.json'
                    payload     = $base64
                    payloadType = 'InlineBase64'
                }
            )
        }
    }
}

function Get-SemanticModelCreatePayload {
    <#
    .SYNOPSIS
    Builds the Fabric REST payload for `sm_capacity_data_product`, a Direct Lake
    semantic model bound to `lh_ihzhhpf_sit.gold.demand_encounter`.
    .NOTES
    Reads TMDL from ../semantic-model/sm_capacity_data_product/ and substitutes
    the two OneLake GUID placeholders. Posted to /workspaces/{wsId}/items with
    type=SemanticModel and definition.format=tmdl.
    #>
    param(
        [Parameter(Mandatory)][string]$WorkspaceId,
        [Parameter(Mandatory)][string]$LakehouseId
    )

    $modelRoot = Join-Path $PSScriptRoot '../semantic-model/sm_capacity_data_product'
    $tmdlFiles = @(
        'definition/database.tmdl',
        'definition/model.tmdl',
        'definition/dataSources.tmdl',
        'definition/tables/demand_encounter.tmdl'
    )

    $parts = foreach ($rel in $tmdlFiles) {
        $abs = Join-Path $modelRoot $rel
        if (-not (Test-Path $abs)) { throw "TMDL file not found: $abs" }
        $text = Get-Content -Raw -Path $abs
        # Apply placeholder substitution uniformly; the tokens exist only in dataSources.tmdl
        # so this is a no-op for the other three files but keeps the loop branch-free.
        $text = $text.Replace('[WORKSPACE_GUID]', $WorkspaceId).Replace('[LAKEHOUSE_GUID]', $LakehouseId)
        @{
            path        = $rel
            payload     = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($text))
            payloadType = 'InlineBase64'
        }
    }

    return @{
        displayName = 'sm_capacity_data_product'
        description = 'Direct Lake semantic model on gold.demand_encounter (Sprint 08 W1.4 thin slice)'
        type        = 'SemanticModel'
        definition  = @{
            format = 'tmdl'
            parts  = $parts
        }
    }
}

if ($DryRun) { return }

if (-not $CapacityName) { throw 'CapacityName required. Pass the Fabric capacity displayName (Bicep `capacityName` output, e.g. fabricihzhhpfsit).' }
if (-not $ConnectionId) {
    throw 'ConnectionId required. Create a Fabric connection to the Azure SQL source first (portal or POST /v1/connections) and pass the resulting GUID.'
}

# 0. Resolve the Fabric capacity GUID from its displayName (Bicep outputs an ARM resource ID, not the Fabric GUID).
$capacityGuid = Resolve-FabricCapacityIdByName -CapacityName $CapacityName
Write-Host "Capacity GUID: $capacityGuid"

# 1. Create workspace bound to the capacity.
$ws = Invoke-FabricRest -Method POST -Path '/workspaces' -Body (Get-WorkspaceCreatePayload -CapacityId $capacityGuid)
Write-Host "Workspace: $($ws.id)"

# 2. Create lakehouse in the workspace.
$lh = Invoke-FabricRest -Method POST -Path "/workspaces/$($ws.id)/lakehouses" -Body (Get-LakehouseCreatePayload)
Write-Host "Lakehouse: $($lh.id)"

# 3. Create mirrored database bound to the supplied Fabric connection + source database.
$mir = Invoke-FabricRest -Method POST -Path "/workspaces/$($ws.id)/mirroredDatabases" -Body (Get-MirrorCreatePayload -ConnectionId $ConnectionId -Database $SourceDatabase)
Write-Host "Mirror: $($mir.id)"

# 4. Create Direct Lake semantic model bound to gold.demand_encounter.
$sm = Invoke-FabricRest -Method POST -Path "/workspaces/$($ws.id)/items" -Body (Get-SemanticModelCreatePayload -WorkspaceId $ws.id -LakehouseId $lh.id)
Write-Host "Semantic Model: $($sm.id)"

Write-Host 'Done. Wait up to 5 minutes for the initial replication snapshot.'
