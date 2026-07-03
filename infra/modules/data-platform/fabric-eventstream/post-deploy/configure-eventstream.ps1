<#
.SYNOPSIS
Provisions a Fabric Eventstream (Event Hubs source → Lakehouse destination) via the Fabric REST API.

.DESCRIPTION
Materialises what the Bicep sibling module `main.bicep` scaffolds. Runs AFTER:
  1. The Fabric workspace and lakehouse have been created (`configure-fabric.ps1`).
  2. A Fabric-managed connection to the Event Hubs namespace has been created out-of-band
     (portal or POST /v1/connections). Design spec §4.2 uses Fabric-managed connection auth.
  3. The three Sprint 09 v2.0.0 consumer groups exist on the event hub (Bicep T2.1).

Uses az CLI for Fabric API token acquisition.

Docs:
- Eventstream item REST:      https://learn.microsoft.com/rest/api/fabric/eventstream/items
- Eventstream topology:       https://learn.microsoft.com/rest/api/fabric/eventstream/topology
- Definition schema:          https://learn.microsoft.com/fabric/real-time-hub/create-manage-an-eventstream

.PARAMETER ManifestPath
Path to a JSON file containing the manifest emitted by the Bicep module's `eventstreamManifest`
output. Populated by the parent orchestration (see infra/scripts/, currently manual for Sprint 09).

.PARAMETER DryRun
Prints the request bodies but does not POST anything.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ManifestPath,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path $ManifestPath)) {
    throw "Manifest file not found: $ManifestPath"
}

$manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json

function Invoke-FabricRest {
    param([string]$Method, [string]$Path, [object]$Body)
    $token = az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv
    if (-not $token) { throw 'Failed to acquire Fabric API token. Run `az login` first.' }
    $uri = "https://api.fabric.microsoft.com/v1$Path"
    $headers = @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' }
    if ($null -ne $Body) {
        return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers -Body ($Body | ConvertTo-Json -Depth 20)
    } else {
        return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers
    }
}

# Eventstream item definition. Per Fabric docs, the `definition` payload is base64-encoded
# `eventstream.json` describing sources → operators → destinations. Sprint 09 v2.0.0 keeps
# the topology minimal: single EH source → single Lakehouse destination.
$topology = @{
    sources = @(
        @{
            name         = 'source-events-hub'
            type         = 'EventHub'
            properties   = @{
                dataConnectionId    = '<REQUIRES-FABRIC-MANAGED-CONNECTION-ID>'
                consumerGroupName   = $manifest.source.consumerGroup
                eventHubEntityName  = $manifest.source.eventHubName
                serviceEndpoint     = "sb://$($manifest.source.namespaceHost)"
            }
        }
    )
    destinations = @(
        @{
            name       = 'dest-bronze-eventstream'
            type       = 'Lakehouse'
            properties = @{
                workspaceId      = $manifest.workspaceId
                itemId           = $manifest.destination.lakehouseId
                tableName        = $manifest.destination.tablePrefix
                deltaTablePath   = $manifest.destination.lakehousePath
                inputSerialization = @{ type = 'Json' }
            }
        }
    )
    # Router property enforced on the EH message header per design spec §4.2.
    operators = @(
        @{
            name       = 'route-by-eventkind'
            type       = 'RoutingRule'
            properties = @{
                routingKey = $manifest.source.routingProperty
            }
        }
    )
}

$body = @{
    displayName = $manifest.eventstream.displayName
    description = $manifest.eventstream.description
    definition  = @{
        parts = @(
            @{
                path        = 'eventstream.json'
                payload     = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($topology | ConvertTo-Json -Depth 20)))
                payloadType = 'InlineBase64'
            }
        )
    }
}

if ($manifest.guardrails.demoScope) {
    Write-Host "[demoScope=true] ADR-0013 region carve-out active. residencyTag=$($manifest.guardrails.residencyTag)."
}

if ([string]::IsNullOrWhiteSpace($manifest.destination.lakehouseId)) {
    Write-Warning "destinationLakehouseId is empty. Skipping destination wiring — Eventstream will be created source-only."
    $body.definition.parts[0].payload = [Convert]::ToBase64String(
        [Text.Encoding]::UTF8.GetBytes((@{ sources = $topology.sources; operators = $topology.operators; destinations = @() } | ConvertTo-Json -Depth 20))
    )
}

$path = "/workspaces/$($manifest.workspaceId)/eventstreams"

if ($DryRun) {
    Write-Host "[DryRun] POST $path"
    Write-Host ($body | ConvertTo-Json -Depth 20)
    return
}

Write-Host "Creating Eventstream '$($manifest.eventstream.displayName)' in workspace $($manifest.workspaceId)..."
$response = Invoke-FabricRest -Method POST -Path $path -Body $body
Write-Host "Eventstream created. id=$($response.id)"
$response | ConvertTo-Json -Depth 20
