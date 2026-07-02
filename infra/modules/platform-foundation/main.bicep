@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Log Analytics retention in days.')
@minValue(30)
@maxValue(730)
param logAnalyticsRetentionInDays int = 90

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-${nameSuffix}'
  location: location
  tags: tags
  properties: {
    retentionInDays: logAnalyticsRetentionInDays
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

// Key Vault names are globally unique across all Azure and soft-delete-locked for 90 days.
// Add a short, deterministic per-(subscription, RG) suffix so ihzhhpf-based names don't collide.
var globalUniquenessSuffix = take(uniqueString(subscription().subscriptionId, resourceGroup().id), 4)

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'kv-${nameSuffix}-${globalUniquenessSuffix}'
  location: location
  tags: tags
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
    enableSoftDelete: true
    enablePurgeProtection: true
    // Required so ARM can resolve keyVault.getSecret() parameter references at deploy time (Sprint 00 source-SQL enable).
    enabledForTemplateDeployment: true
    publicNetworkAccess: 'Enabled'
    softDeleteRetentionInDays: 90
  }
}

output keyVaultName string = keyVault.name
output logAnalyticsWorkspaceName string = logAnalyticsWorkspace.name
