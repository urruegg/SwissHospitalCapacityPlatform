param(
  [Parameter(Mandatory = $true)]
  [string]$SubscriptionId,

  [string[]]$Providers = @(
    'Microsoft.OperationalInsights',
    'Microsoft.KeyVault',
    'Microsoft.ManagedIdentity',
    'Microsoft.Network',
    'Microsoft.Insights',
    'Microsoft.Storage',
    'Microsoft.CognitiveServices',
    'Microsoft.ServiceBus'
  )
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "Setting Azure subscription context to $SubscriptionId"
az account set --subscription $SubscriptionId | Out-Null

foreach ($provider in $Providers) {
  $state = az provider show --namespace $provider --query registrationState -o tsv 2>$null
  if (-not $state) {
    $state = 'NotRegistered'
  }

  if ($state -eq 'Registered') {
    Write-Host "Provider $provider is already registered."
    continue
  }

  Write-Host "Registering provider $provider (current state: $state)"
  az provider register --namespace $provider --wait | Out-Null

  $newState = az provider show --namespace $provider --query registrationState -o tsv
  if ($newState -ne 'Registered') {
    throw "Provider $provider failed to register. Final state: $newState"
  }

  Write-Host "Provider $provider registered successfully."
}

Write-Host 'All required providers are registered.'
