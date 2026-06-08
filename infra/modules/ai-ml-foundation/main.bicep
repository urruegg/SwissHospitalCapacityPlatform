@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. chhealthpf-sit or chhealthpf-prod.')
@minLength(3)
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

var storageAccountName = toLower('stdp${replace(nameSuffix, '-', '')}')
var containerRegistryName = toLower('cr${uniqueString(resourceGroup().id, nameSuffix)}')

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: 'kv-${nameSuffix}'
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: 'appi-${nameSuffix}'
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: storageAccountName
}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: containerRegistryName
}

resource mlWorkspace 'Microsoft.MachineLearningServices/workspaces@2023-10-01' = {
  name: 'mlw-${nameSuffix}'
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  properties: {
    publicNetworkAccess: 'Enabled'
    friendlyName: 'mlw-${nameSuffix}'
    keyVault: keyVault.id
    applicationInsights: appInsights.id
    storageAccount: storageAccount.id
    containerRegistry: containerRegistry.id
  }
}

@description('AI/ML foundation module implementation marker.')
output moduleStatus string = 'ai-ml-foundation-implemented'

@description('ML workspace name.')
output machineLearningWorkspaceName string = mlWorkspace.name
