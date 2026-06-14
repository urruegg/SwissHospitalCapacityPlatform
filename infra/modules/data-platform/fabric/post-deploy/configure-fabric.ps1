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
$ws = Invoke-FabricRest -Method POST -Path '/workspaces' -Body (Get-WorkspaceCreatePayload -CapacityId $CapacityId -Region $Region)
Write-Host "Workspace: $($ws.id)"

# 2. Create lakehouse in the workspace
$lh = Invoke-FabricRest -Method POST -Path "/workspaces/$($ws.id)/lakehouses" -Body (Get-LakehouseCreatePayload)
Write-Host "Lakehouse: $($lh.id)"

# 3. Create mirror against the source SQL
$mir = Invoke-FabricRest -Method POST -Path "/workspaces/$($ws.id)/mirroredDatabases" -Body (Get-MirrorCreatePayload -ServerFqdn $SourceServerFqdn -Database $SourceDatabase)
Write-Host "Mirror: $($mir.id)"

Write-Host "Done. Wait up to 5 minutes for the initial replication snapshot."
