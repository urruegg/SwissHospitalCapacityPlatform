<#
.SYNOPSIS
    Creates (idempotently) an Entra app registration in the target tenant and adds GitHub OIDC federated credentials for the specified environments.
.PARAMETER DisplayName
    The Entra app registration display name (e.g., 'gh-oidc-swisshospitalcapacityplatform').
.PARAMETER RepoFullName
    The GitHub repo in 'owner/repo' form (e.g., 'urruegg/SwissHospitalCapacityPlatform').
.PARAMETER Environments
    Environment names for which to create federated credentials. Defaults to @('sit', 'prod').
.EXAMPLE
    ./New-OidcFederation.ps1 -DisplayName gh-oidc-shcp -RepoFullName urruegg/SwissHospitalCapacityPlatform
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [string]$DisplayName,

    [Parameter(Mandatory)]
    [string]$RepoFullName,

    [Parameter()]
    [string[]]$Environments = @('sit', 'prod')
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if ($RepoFullName -notmatch '^[^/]+/[^/]+$') {
    throw "RepoFullName must be in 'owner/repo' form; got: $RepoFullName"
}

# ---- App registration (idempotent) ----
$existing = az ad app list --display-name $DisplayName --query "[?displayName=='$DisplayName']" -o json | ConvertFrom-Json
if ($existing.Count -gt 0) {
    $appId = $existing[0].appId
    Write-Host "Reusing existing app registration '$DisplayName' (appId $appId)." -ForegroundColor Yellow
} else {
    if ($PSCmdlet.ShouldProcess($DisplayName, 'create Entra app registration')) {
        $created = az ad app create --display-name $DisplayName --sign-in-audience AzureADMyOrg -o json | ConvertFrom-Json
        $appId = $created.appId
        Write-Host "Created app registration '$DisplayName' (appId $appId)." -ForegroundColor Green
    } else {
        Write-Host "WhatIf: would create app registration '$DisplayName'." -ForegroundColor DarkYellow
        return
    }
}

# ---- Service principal (idempotent) ----
$spExisting = az ad sp list --filter "appId eq '$appId'" -o json | ConvertFrom-Json
if ($spExisting.Count -eq 0) {
    if ($PSCmdlet.ShouldProcess($appId, 'create service principal')) {
        az ad sp create --id $appId | Out-Null
        Write-Host "Created service principal for appId $appId." -ForegroundColor Green
    }
}

# ---- Federated credentials (idempotent) ----
$existingFics = az ad app federated-credential list --id $appId -o json | ConvertFrom-Json
foreach ($env in $Environments) {
    $ficName = "gh-$env"
    $subject = "repo:$RepoFullName:environment:$env"
    if ($existingFics | Where-Object { $_.subject -eq $subject }) {
        Write-Host "Federated credential '$ficName' (subject $subject) already exists - skipping." -ForegroundColor Yellow
        continue
    }
    if ($PSCmdlet.ShouldProcess($ficName, "create federated credential subject=$subject")) {
        $body = @{
            name        = $ficName
            issuer      = 'https://token.actions.githubusercontent.com'
            subject     = $subject
            description = "GitHub Actions OIDC for environment $env"
            audiences   = @('api://AzureADTokenExchange')
        } | ConvertTo-Json -Depth 5 -Compress

        $tmp = New-TemporaryFile
        try {
            $body | Set-Content -Path $tmp -Encoding utf8
            az ad app federated-credential create --id $appId --parameters "@$tmp" | Out-Null
            Write-Host "Created federated credential '$ficName' (subject $subject)." -ForegroundColor Green
        } finally {
            Remove-Item $tmp -ErrorAction SilentlyContinue
        }
    }
}

# NB: Azure token audience for federated OIDC exchange is api://AzureADTokenExchange (Entra endpoint);
# the resulting access token target audience for CI is https://management.azure.com.

# ---- Output ----
$sp = az ad sp list --filter "appId eq '$appId'" -o json | ConvertFrom-Json | Select-Object -First 1
[pscustomobject]@{
    ClientId       = $appId
    PrincipalId    = $sp.id
    DisplayName    = $DisplayName
    Environments   = $Environments
}
