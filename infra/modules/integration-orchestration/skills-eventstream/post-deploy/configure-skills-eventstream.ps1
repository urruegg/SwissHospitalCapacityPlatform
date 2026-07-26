<#
.SYNOPSIS
Provisions the Sprint 23 WS-A4 (design D4) skills-events Fabric Eventstream
(CustomEndpoint source -> DefaultStream -> Lakehouse destination) via the Fabric REST API.

.DESCRIPTION
Materialises what the Bicep sibling module `main.bicep` scaffolds. The skills-events lane is
intentionally NARROW: it carries ONLY the three near-real-time skills events
(credential-expiry, consent-grant-or-revoke, newly-confirmed-assertion) that must move faster
than the next batch master-data load.

Transport (design D4 + demo-scope, ADR-0013): this script wires a **CustomEndpoint** source,
mirroring the already-working `es-capacity-events-sit` topology in the SIT workspace. The
Container Apps publisher (NFR-SKILL-001) POSTs `DC-SKILL-EVENT-v1` envelopes to the
Eventstream ingestion URL. The EventHub source (Bicep `sourceMode=EventHub`) remains the
Swiss-GA target-state and is deferred until a Fabric-managed connection to the Event Hubs
namespace exists (out-of-band `POST /v1/connections`).

Narrow-scope guardrail: the script asserts the manifest carries EXACTLY the three allowed
event kinds. Runtime enforcement of the kind allow-list + the PHI/consent gate is performed
downstream by the silver skills-events notebook (deny-by-default quarantine), per the module
manifest `guardrails.phiGateEnforcedBy`. An in-Eventstream Filter operator is a documented
target-state follow-up.

Uses az CLI for Fabric API token acquisition. Idempotent: if an Eventstream with the target
display name already exists in the workspace, the script reports its id and exits without
re-creating (use -Force to replace).

Docs:
- Eventstream item REST:   https://learn.microsoft.com/rest/api/fabric/eventstream/items
- Definition schema:       https://learn.microsoft.com/fabric/real-time-hub/create-manage-an-eventstream

.PARAMETER ManifestPath
Path to a JSON file containing the manifest emitted by the Bicep module's `eventstreamManifest`
output (see README `## Post-deploy invocation`).

.PARAMETER WorkspaceId
Optional override for the Fabric workspace GUID. Falls back to the manifest `workspaceId`.
Required (here or in the manifest) for a live POST.

.PARAMETER DestinationLakehouseId
Optional override for the destination Lakehouse GUID. Falls back to the manifest
`destination.lakehouseId`. Empty => Eventstream created source-only (a warning is emitted).

.PARAMETER DestinationTableName
Optional override for the destination Delta table name. Falls back to the manifest
`destination.tablePrefix`.

.PARAMETER Force
Replace an existing Eventstream of the same display name (delete + re-create).

.PARAMETER ConnectionId
Fabric-managed connection GUID for the Event Hubs namespace (created out-of-band via
`POST /v1/connections`). Required for a live EventHub-source wire (manifest `source.kind=EventHub`);
ignored for a CustomEndpoint source. Falls back to nothing — the script refuses an EventHub live
POST without it.

.PARAMETER DryRun
Prints the request body but does not POST anything. Also validates the three-kind guardrail.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ManifestPath,
    [string]$WorkspaceId,
    [string]$DestinationLakehouseId,
    [string]$DestinationTableName,
    [string]$ConnectionId,
    [switch]$Force,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path $ManifestPath)) {
    throw "Manifest file not found: $ManifestPath"
}

$manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json

# --- D4 narrow-scope guardrail: the manifest must carry EXACTLY the three allowed kinds. ---
$canonicalKinds = @('credential-expiry', 'consent-grant-or-revoke', 'newly-confirmed-assertion')
$manifestKinds = @($manifest.source.allowedEventKinds | Sort-Object)
$expected = @($canonicalKinds | Sort-Object)
if (($manifestKinds -join ',') -ne ($expected -join ',')) {
    throw "D4 guardrail violation: manifest allowedEventKinds [$($manifestKinds -join ', ')] does not match the exactly-three canonical set [$($canonicalKinds -join ', ')]. Broadening the event set is a design change (design spec section 6 open items)."
}

# --- Resolve live inputs (parameter override > manifest). ---
$wsId = if ($WorkspaceId) { $WorkspaceId } else { $manifest.workspaceId }
$lakehouseId = if ($PSBoundParameters.ContainsKey('DestinationLakehouseId')) { $DestinationLakehouseId } else { $manifest.destination.lakehouseId }
$tableName = if ($DestinationTableName) { $DestinationTableName } else { $manifest.destination.tablePrefix }
$displayName = $manifest.eventstream.displayName
$sourceKind = $manifest.source.kind

if ($sourceKind -eq 'EventHub') {
    Write-Host "manifest source.kind='EventHub' (Swiss-GA / ADR-0043 path). Wiring an Azure Event Hubs source on the dedicated per-domain skills-events hub via a Fabric-managed connection. namespaceHost=$($manifest.source.namespaceHost), eventHub=$($manifest.source.eventHubName), consumerGroup=$($manifest.source.consumerGroup)."
} elseif ($sourceKind -ne 'CustomEndpoint') {
    throw "Unsupported manifest source.kind='$sourceKind'. Expected 'CustomEndpoint' or 'EventHub'."
}

if ($manifest.guardrails.demoScope) {
    Write-Host "[demoScope=true] ADR-0013 region carve-out active. residencyTag=$($manifest.guardrails.residencyTag). Synthetic data only, no PHI. PHI gate enforced by: $($manifest.guardrails.phiGateEnforcedBy)."
}

# --- Build the Eventstream item definition (authoritative live schema: streams + compat 1.1). ---
# The source node follows the manifest source.kind: CustomEndpoint (D4 demo-scope, publisher POSTs
# to the ingestion URL) or AzureEventHub (Swiss-GA / ADR-0043, bound to the dedicated skills-events
# hub through a Fabric-managed connection). The rest of the topology (DefaultStream -> Lakehouse) is
# identical, so the downstream bronze/silver contract does not change with the transport.
$resolvedConnectionId = if ($ConnectionId) {
    $ConnectionId
} elseif ($manifest.source.PSObject.Properties.Name -contains 'connectionId') {
    $manifest.source.connectionId
} else {
    $null
}
if ($sourceKind -eq 'EventHub') {
    if ((-not $DryRun) -and [string]::IsNullOrWhiteSpace($resolvedConnectionId)) {
        throw "manifest source.kind='EventHub' but no Fabric-managed connection id was provided (pass -ConnectionId or set manifest source.connectionId). Create it out-of-band via POST /v1/connections against namespace '$($manifest.source.namespaceHost)' first."
    }
    $sourceNode = [ordered]@{
        name       = 'skills-events-source'
        type       = 'AzureEventHub'
        properties = [ordered]@{
            dataConnectionId   = $resolvedConnectionId
            consumerGroupName  = $manifest.source.consumerGroup
            inputSerialization = @{ type = 'Json'; properties = @{ encoding = 'UTF8' } }
        }
    }
} else {
    $sourceNode = [ordered]@{
        name       = 'skills-events-source'
        type       = 'CustomEndpoint'
        properties = @{}
    }
}
$streamName = "$displayName-stream"
$topology = [ordered]@{
    sources      = @($sourceNode)
    destinations = @()
    streams      = @(
        [ordered]@{
            name       = $streamName
            type       = 'DefaultStream'
            properties = @{}
            inputNodes = @(@{ name = 'skills-events-source' })
        }
    )
    operators          = @()
    compatibilityLevel = '1.1'
}

if ([string]::IsNullOrWhiteSpace($lakehouseId)) {
    Write-Warning "destinationLakehouseId is empty. Skipping destination wiring - Eventstream will be created source-only. Wire the lakehouseId in a follow-up pass."
} else {
    $topology.destinations = @(
        [ordered]@{
            name       = 'lakehouse-bronze-skills'
            type       = 'Lakehouse'
            properties = [ordered]@{
                workspaceId              = $wsId
                itemId                   = $lakehouseId
                schema                   = 'dbo'
                deltaTable               = $tableName
                minimumRows              = 100
                maximumDurationInSeconds = 60
                inputSerialization       = @{ type = 'Json'; properties = @{ encoding = 'UTF8' } }
            }
            inputNodes = @(@{ name = $streamName })
        }
    )
}

$eventstreamJson       = $topology | ConvertTo-Json -Depth 20
$eventstreamProperties = @{ retentionTimeInDays = 1; eventThroughputLevel = 'Low'; schemaMode = 'None' } | ConvertTo-Json -Depth 10
$platformJson          = [ordered]@{
    '$schema' = 'https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json'
    metadata  = @{ type = 'Eventstream'; displayName = $displayName }
    config    = @{ version = '2.0'; logicalId = '00000000-0000-0000-0000-000000000000' }
} | ConvertTo-Json -Depth 10

function ConvertTo-Part {
    param([string]$Path, [string]$Payload)
    @{ path = $Path; payload = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($Payload)); payloadType = 'InlineBase64' }
}

$body = @{
    displayName = $displayName
    description = $manifest.eventstream.description
    definition  = @{
        parts = @(
            (ConvertTo-Part -Path 'eventstream.json' -Payload $eventstreamJson),
            (ConvertTo-Part -Path 'eventstreamProperties.json' -Payload $eventstreamProperties),
            (ConvertTo-Part -Path '.platform' -Payload $platformJson)
        )
    }
}

if ($DryRun) {
    Write-Host "[DryRun] Guardrail OK (three allowed kinds). Source kind = '$sourceKind'. Would POST Eventstream '$displayName' to workspace '$wsId'."
    Write-Host '--- eventstream.json ---'
    Write-Host $eventstreamJson
    return
}

if ([string]::IsNullOrWhiteSpace($wsId)) {
    throw 'WorkspaceId is empty (not in manifest and not passed via -WorkspaceId). Cannot POST.'
}

function Invoke-FabricRest {
    param([string]$Method, [string]$Path, [object]$Body)
    $token = az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv
    if (-not $token) { throw 'Failed to acquire Fabric API token. Run `az login` first.' }
    $uri = "https://api.fabric.microsoft.com/v1$Path"
    $headers = @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' }
    if ($null -ne $Body) {
        return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers -Body ($Body | ConvertTo-Json -Depth 25)
    }
    return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers
}

# --- Idempotency: does an Eventstream with this display name already exist? ---
$existing = (Invoke-FabricRest -Method GET -Path "/workspaces/$wsId/eventstreams").value |
    Where-Object { $_.displayName -eq $displayName } | Select-Object -First 1

if ($existing) {
    if (-not $Force) {
        Write-Host "Eventstream '$displayName' already exists (id=$($existing.id)). Nothing to do (pass -Force to replace)."
        return
    }
    Write-Host "Eventstream '$displayName' exists (id=$($existing.id)); -Force set - deleting before re-create."
    Invoke-FabricRest -Method DELETE -Path "/workspaces/$wsId/eventstreams/$($existing.id)" | Out-Null
}

Write-Host "Creating Eventstream '$displayName' in workspace $wsId ($sourceKind source)..."
$response = Invoke-FabricRest -Method POST -Path "/workspaces/$wsId/eventstreams" -Body $body

# Fabric item creation with a definition is a long-running operation: the POST commonly
# returns 202 Accepted with an empty body (id arrives asynchronously). Resolve the id
# defensively by display-name lookup with a short retry, rather than assuming a body.
$newId = if ($response -and ($response.PSObject.Properties.Name -contains 'id')) { $response.id } else { $null }
if (-not $newId) {
    for ($i = 0; $i -lt 12 -and -not $newId; $i++) {
        Start-Sleep -Seconds 5
        $found = (Invoke-FabricRest -Method GET -Path "/workspaces/$wsId/eventstreams").value |
            Where-Object { $_.displayName -eq $displayName } | Select-Object -First 1
        if ($found) { $newId = $found.id }
    }
}
if (-not $newId) { throw "Eventstream '$displayName' did not become resolvable after create (async provisioning may still be in progress)." }
Write-Host "Eventstream created. id=$newId"

# --- Verify + surface the topology the publisher targets. ---
$topologyAfter = Invoke-FabricRest -Method GET -Path "/workspaces/$wsId/eventstreams/$newId/topology"
Write-Host 'Topology after create:'
$topologyAfter | ConvertTo-Json -Depth 20
