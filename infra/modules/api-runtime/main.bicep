@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. chhealthpf-sit or chhealthpf-prod.')
@minLength(3)
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Container registry SKU.')
@allowed([
  'Basic'
  'Standard'
  'Premium'
])
param containerRegistrySku string = 'Standard'

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: toLower('cr${uniqueString(resourceGroup().id, nameSuffix)}')
  location: location
  tags: tags
  sku: {
    name: containerRegistrySku
  }
  properties: {
    adminUserEnabled: false
    publicNetworkAccess: 'Enabled'
  }
}

resource apiRuntimeIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-api-${nameSuffix}'
  location: location
  tags: tags
}

@description('API runtime module implementation marker.')
output moduleStatus string = 'api-runtime-implemented'

@description('Container registry name.')
output containerRegistryName string = containerRegistry.name

@description('API runtime identity resource ID.')
output apiRuntimeIdentityResourceId string = apiRuntimeIdentity.id
