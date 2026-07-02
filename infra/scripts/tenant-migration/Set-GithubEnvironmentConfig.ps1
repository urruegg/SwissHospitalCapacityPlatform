<#
.SYNOPSIS
    Sets or restores GitHub environment variables and secrets for tenant migration.
.PARAMETER RepoFullName
    'owner/repo' form.
.PARAMETER Environment
    'sit' or 'prod'.
.PARAMETER TenantId, SubscriptionId, ResourceGroup, BicepParamFile
    Environment variables to set.
.PARAMETER ClientId
    SecureString containing the AZURE_CLIENT_ID (stored as GitHub secret).
.PARAMETER Restore
    When set, reads $SnapshotPath and restores previous values.
.PARAMETER SnapshotPath
    File path to write snapshot (default) or read from (with -Restore).
#>
[CmdletBinding(SupportsShouldProcess, DefaultParameterSetName = 'Set')]
param(
    [Parameter(Mandatory)]
    [string]$RepoFullName,

    [Parameter(Mandatory)]
    [ValidateSet('sit', 'prod')]
    [string]$Environment,

    [Parameter(ParameterSetName = 'Set', Mandatory)]
    [guid]$TenantId,

    [Parameter(ParameterSetName = 'Set', Mandatory)]
    [guid]$SubscriptionId,

    [Parameter(ParameterSetName = 'Set', Mandatory)]
    [string]$ResourceGroup,

    [Parameter(ParameterSetName = 'Set', Mandatory)]
    [string]$BicepParamFile,

    [Parameter(ParameterSetName = 'Set', Mandatory)]
    [System.Security.SecureString]$ClientId,

    [Parameter(ParameterSetName = 'Restore', Mandatory)]
    [switch]$Restore,

    [Parameter()]
    [string]$SnapshotPath = "./tenant-migration-github-env-snapshot-$Environment.json"
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Get-CurrentEnvSnapshot {
    param([string]$Repo, [string]$Env)
    $vars = gh api "/repos/$Repo/environments/$Env/variables" 2>$null | ConvertFrom-Json
    return @{
        environment = $Env
        variables   = $vars.variables | ForEach-Object { @{ name = $_.name; value = $_.value } }
        capturedAt  = (Get-Date).ToString('o')
    }
}

if ($Restore) {
    if (-not (Test-Path $SnapshotPath)) {
        throw "Snapshot file not found: $SnapshotPath"
    }
    $snap = Get-Content $SnapshotPath -Raw | ConvertFrom-Json
    foreach ($v in $snap.variables) {
        if ($PSCmdlet.ShouldProcess("$Environment/$($v.name)", 'restore variable')) {
            gh variable set $v.name --env $Environment --repo $RepoFullName --body $v.value | Out-Null
        }
    }
    Write-Host "Restored $($snap.variables.Count) variables to environment '$Environment' from $SnapshotPath." -ForegroundColor Green
    return
}

# --- Snapshot current state before mutating ---
if ($PSCmdlet.ShouldProcess($SnapshotPath, 'write pre-change snapshot')) {
    Get-CurrentEnvSnapshot -Repo $RepoFullName -Env $Environment |
      ConvertTo-Json -Depth 5 |
      Set-Content -Path $SnapshotPath -Encoding utf8
    Write-Host "Snapshot written to $SnapshotPath." -ForegroundColor Green
}

# --- Set variables ---
$vars = @{
    AZURE_TENANT_ID       = $TenantId.ToString()
    AZURE_SUBSCRIPTION_ID = $SubscriptionId.ToString()
    AZURE_RESOURCE_GROUP  = $ResourceGroup
    BICEP_PARAM_FILE      = $BicepParamFile
}
foreach ($k in $vars.Keys) {
    if ($PSCmdlet.ShouldProcess("$Environment/$k", 'set variable')) {
        gh variable set $k --env $Environment --repo $RepoFullName --body $vars[$k] | Out-Null
    }
}

# --- Set secret (never logged) ---
if ($PSCmdlet.ShouldProcess("$Environment/AZURE_CLIENT_ID", 'set secret')) {
    $plain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($ClientId))
    try {
        $plain | gh secret set AZURE_CLIENT_ID --env $Environment --repo $RepoFullName
    } finally {
        $plain = $null
        [System.GC]::Collect()
    }
}

Write-Host "GitHub environment '$Environment' configured for tenant $TenantId." -ForegroundColor Green
