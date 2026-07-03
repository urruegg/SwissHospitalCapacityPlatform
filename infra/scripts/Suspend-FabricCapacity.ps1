#Requires -Version 5.1

<#
.SYNOPSIS
    Suspend a Fabric F2 capacity (DX.2, Sprint 09 v2.0.0).

.DESCRIPTION
    Idempotent — checks current state before invoking suspend. Returns 0 on success or if already Paused.
    Uses proven Sprint 00 pattern: `az resource invoke-action --action suspend` on the capacity resource ID.

.PARAMETER Environment
    Target environment: sit | prod. Maps to Fabric capacity name via convention:
    - sit  -> fabricihzhhpfsit  in rg-ihzhhpf-sit
    - prod -> fabricihzhhpfprod in rg-ihzhhpf-prod

.PARAMETER SubscriptionId
    Azure subscription ID. Defaults to the tenant migration subscription
    (66a9953a-df37-4c51-856c-9971b9bf3e03) per AGENTS.md.

.EXAMPLE
    .\Suspend-FabricCapacity.ps1 -Environment sit

.NOTES
    Spec:    docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md §4.8
    Runbook: docs/runbooks/fabric-capacity-lifecycle.md
    Tests:   infra/scripts/tests/Suspend-FabricCapacity.Tests.ps1
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('sit', 'prod')]
    [string]$Environment,

    [Parameter()]
    [string]$SubscriptionId = '66a9953a-df37-4c51-856c-9971b9bf3e03'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$capacityName  = "fabricihzhhpf$Environment"
$resourceGroup = "rg-ihzhhpf-$Environment"
$capacityId    = "/subscriptions/$SubscriptionId/resourceGroups/$resourceGroup/providers/Microsoft.Fabric/capacities/$capacityName"

Write-Host "Environment:  $Environment"
Write-Host "Capacity:     $capacityName"
Write-Host "Resource ID:  $capacityId"

# Idempotent guard — check current state
try {
    $showRaw = az resource show --ids $capacityId 2>&1
    $current = $showRaw | ConvertFrom-Json -ErrorAction Stop
    if ($current -and $current.properties -and $current.properties.state -eq 'Paused') {
        Write-Host "[NO-OP] Capacity is already Paused." -ForegroundColor Green
        exit 0
    }
    $observedState = if ($current -and $current.properties) { $current.properties.state } else { 'Unknown' }
    Write-Host "Current state: $observedState -- invoking suspend..."
}
catch {
    Write-Warning "Could not read current state: $_. Proceeding with suspend anyway."
}

# Invoke suspend
try {
    $result = az resource invoke-action --ids $capacityId --action suspend 2>&1
    Write-Host "[OK] Suspend action invoked." -ForegroundColor Green
    if ($result) { Write-Host "Response: $result" }
    exit 0
}
catch {
    Write-Error "Suspend failed: $_"
    exit 3
}
