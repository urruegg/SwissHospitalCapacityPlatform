@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. chhealthpf-sit or chhealthpf-prod.')
@minLength(3)
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

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
  }
}

@description('AI/ML foundation module implementation marker.')
output moduleStatus string = 'ai-ml-foundation-implemented'

@description('ML workspace name.')
output machineLearningWorkspaceName string = mlWorkspace.name
