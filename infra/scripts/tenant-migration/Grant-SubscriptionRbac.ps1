<#
.SYNOPSIS
    Idempotently grants a role to a service principal at subscription scope.
.PARAMETER PrincipalId
    The service principal object ID.
.PARAMETER SubscriptionId
    The target subscription ID.
.PARAMETER RoleName
    The RBAC role to grant. Defaults to 'Contributor'.
.EXAMPLE
    ./Grant-SubscriptionRbac.ps1 -PrincipalId 11111111-... -SubscriptionId 22222222-... -RoleName Contributor
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [guid]$PrincipalId,

    [Parameter(Mandatory)]
    [guid]$SubscriptionId,

    [Parameter()]
    [string]$RoleName = 'Contributor'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$scope = "/subscriptions/$SubscriptionId"

Set-AzContext -Subscription $SubscriptionId | Out-Null

$existing = Get-AzRoleAssignment -ObjectId $PrincipalId -Scope $scope -RoleDefinitionName $RoleName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Role assignment already exists: $RoleName on $scope for $PrincipalId - skipping." -ForegroundColor Yellow
    return $existing
}

if ($PSCmdlet.ShouldProcess("$scope", "grant $RoleName to $PrincipalId")) {
    $assignment = New-AzRoleAssignment -ObjectId $PrincipalId -RoleDefinitionName $RoleName -Scope $scope
    Write-Host "Granted $RoleName on $scope to $PrincipalId." -ForegroundColor Green
    return $assignment
}
