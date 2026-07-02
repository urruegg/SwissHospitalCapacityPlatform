<#
.SYNOPSIS
    Establishes machine trust for silent sign-in to a target Entra tenant from Azure CLI, Az PowerShell, and VS Code Azure extensions.
.DESCRIPTION
    Enables the Windows Account Manager (WAM) broker for the Azure CLI, signs in interactively to the target tenant via the broker (TPM-bound device key), then signs in Az PowerShell via the same broker. Falls back to device-code sign-in when the broker is unavailable. Prints Workplace Join guidance for optional Conditional Access "device compliant" claims.
.PARAMETER TenantId
    The target Entra tenant ID (GUID).
.PARAMETER SubscriptionId
    Optional. If provided, sets it as the active subscription after sign-in.
.EXAMPLE
    ./Enable-DeveloperTenantTrust.ps1 -TenantId 1337187a-4c41-4da9-8fca-731bba7a4329 -SubscriptionId 00000000-0000-0000-0000-000000000000
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [guid]$TenantId,

    [Parameter()]
    [guid]$SubscriptionId
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Write-Section {
    param([string]$Title)
    Write-Host ''
    Write-Host "==== $Title ====" -ForegroundColor Cyan
}

Write-Section '1. Verify prerequisites'
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    throw 'Azure CLI (az) not found on PATH. Install azure-cli 2.60+.'
}
if (-not (Get-Module -ListAvailable Az.Accounts)) {
    Write-Warning 'Az.Accounts module not found. Install via: Install-Module Az -Scope CurrentUser -Force'
}

Write-Section '2. Enable WAM broker for Azure CLI'
if ($PSCmdlet.ShouldProcess('Azure CLI', 'enable WAM broker (az config set core.enable_broker_on_windows=true)')) {
    az config set core.enable_broker_on_windows=true | Out-Null
    Write-Host 'WAM broker enabled for Azure CLI.' -ForegroundColor Green
}

Write-Section '3. Sign in to Azure CLI (interactive, TPM-bound device key)'
if ($PSCmdlet.ShouldProcess("tenant $TenantId", 'az login --tenant')) {
    try {
        az login --tenant $TenantId.ToString() | Out-Null
    } catch {
        Write-Warning "Broker-based sign-in failed. Falling back to --use-device-code. Reason: $_"
        az login --tenant $TenantId.ToString() --use-device-code | Out-Null
    }
    if ($SubscriptionId) {
        az account set --subscription $SubscriptionId.ToString()
    }
}

Write-Section '4. Sign in to Az PowerShell'
if ($PSCmdlet.ShouldProcess("tenant $TenantId", 'Connect-AzAccount')) {
    $connectArgs = @{ Tenant = $TenantId.ToString() }
    if ($SubscriptionId) { $connectArgs.Subscription = $SubscriptionId.ToString() }
    Connect-AzAccount @connectArgs | Out-Null
}

Write-Section '5. Validate'
$azAccount = az account show --query '{name:name, tenantId:tenantId, subscriptionId:id}' -o json | ConvertFrom-Json
$azContext = Get-AzContext
Write-Host "az account show:   $($azAccount | ConvertTo-Json -Compress)" -ForegroundColor Green
Write-Host "Get-AzContext:     Tenant=$($azContext.Tenant.Id) Sub=$($azContext.Subscription.Id)" -ForegroundColor Green
if ($azAccount.tenantId -ne $TenantId.ToString()) {
    throw "az account tenant ($($azAccount.tenantId)) does not match expected ($TenantId)."
}
if ($azContext.Tenant.Id -ne $TenantId.ToString()) {
    throw "Az context tenant ($($azContext.Tenant.Id)) does not match expected ($TenantId)."
}

Write-Section '6. Optional: Workplace Join (Entra Registered)'
Write-Host @'
For Conditional Access "device compliant" claims and to persist an Entra device certificate:

  Open Settings > Accounts > Access work or school > Connect
  Sign in with your new-tenant account
  Follow the prompts to complete Workplace Join

Verify afterwards with: dsregcmd /status  (look for AzureAdJoined : YES or WorkplaceJoined : YES)
'@ -ForegroundColor Yellow

Write-Section 'Done'
Write-Host "Workstation is trusted to tenant $TenantId. VS Code Azure Account and Azure Resources extensions will pick up the cached token silently." -ForegroundColor Green
