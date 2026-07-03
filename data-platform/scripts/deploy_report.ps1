<#
.SYNOPSIS
    Deploy Power BI PBIP (Report + SemanticModel) to Fabric workspace (T5.3, Sprint 09 v2.0.0).

.DESCRIPTION
    Region-agnostic — flip -Region and -WorkspaceId at CLI for Swiss GA migration.
    Per design spec §5.6 Reference-implementation preservation.

.PARAMETER Region
    westus2 (demo per ADR-0013) | switzerlandnorth (Swiss GA target).

.PARAMETER WorkspaceId
    Fabric workspace GUID.

.PARAMETER PBIPPath
    Path to the .pbip root file. Default: ./data-platform/reports/capacity-dashboard.pbip

.PARAMETER DryRun
    Print payload structure without POSTing.

.EXAMPLE
    ./deploy_report.ps1 -WorkspaceId 00000000-... -Region westus2 -DryRun
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$WorkspaceId,

    [ValidateSet('westus2', 'switzerlandnorth')]
    [string]$Region = 'westus2',

    [string]$PBIPPath = './data-platform/reports/capacity-dashboard.pbip',

    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# --- Resolve PBIP paths
if (-not (Test-Path $PBIPPath)) {
    throw "PBIP file not found: $PBIPPath"
}
$pbipDir = Split-Path -Parent $PBIPPath
$reportDir = Join-Path $pbipDir 'capacity-dashboard.Report'
$semanticModelDir = Join-Path $pbipDir 'capacity-dashboard.SemanticModel'

foreach ($p in @($reportDir, $semanticModelDir)) {
    if (-not (Test-Path $p)) {
        throw "Required directory missing: $p"
    }
}

$fabricApiBase = 'https://api.fabric.microsoft.com/v1'
$deployUrl = "$fabricApiBase/workspaces/$WorkspaceId/items"

Write-Host "Region:        $Region"
Write-Host "Workspace:     $WorkspaceId"
Write-Host "Report dir:    $reportDir"
Write-Host "Sem model dir: $semanticModelDir"
Write-Host "Target URL:    $deployUrl"

$payload = @{
    displayName = 'capacity-dashboard'
    type        = 'Report'
    definition  = @{
        parts = @()  # populated with file references — Fabric REST accepts base64-encoded parts
    }
    regionPin   = $Region
}

if ($DryRun) {
    Write-Host ""
    Write-Host "[DRY-RUN] Would POST to: $deployUrl"
    Write-Host "[DRY-RUN] Payload structure:"
    $payload | ConvertTo-Json -Depth 6
    exit 0
}

# --- Real deploy path
try {
    $token = (Get-AzAccessToken -ResourceUrl 'https://api.fabric.microsoft.com').Token
}
catch {
    Write-Error "Failed to acquire Fabric API token. Run 'Connect-AzAccount' first. Error: $_"
    exit 2
}

# Enumerate files under $reportDir + $semanticModelDir, base64-encode, add to parts
Get-ChildItem -Path $reportDir, $semanticModelDir -Recurse -File | ForEach-Object {
    $relative = $_.FullName.Substring($pbipDir.Length + 1).Replace('\', '/')
    $content = [Convert]::ToBase64String([IO.File]::ReadAllBytes($_.FullName))
    $payload.definition.parts += @{
        path        = $relative
        payload     = $content
        payloadType = 'InlineBase64'
    }
}

$headers = @{
    'Authorization' = "Bearer $token"
    'Content-Type'  = 'application/json'
}

$body = $payload | ConvertTo-Json -Depth 10 -Compress

try {
    $response = Invoke-RestMethod -Uri $deployUrl -Method POST -Headers $headers -Body $body
    Write-Host "OK: Report + SemanticModel deployed to workspace $WorkspaceId"
    Write-Host "Item ID: $($response.id)"
}
catch {
    Write-Error "Deploy failed: $($_.Exception.Message)"
    if ($_.ErrorDetails) {
        Write-Error $_.ErrorDetails.Message
    }
    exit 3
}
