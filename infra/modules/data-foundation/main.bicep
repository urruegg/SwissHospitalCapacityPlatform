@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
@minLength(3)
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

// Event Hub namespaces need globally unique DNS names (<ns>.servicebus.windows.net).
var globalUniquenessSuffix = take(uniqueString(subscription().subscriptionId, resourceGroup().id), 4)

resource eventHubNamespace 'Microsoft.EventHub/namespaces@2022-10-01-preview' = {
  name: 'evh-${nameSuffix}-${globalUniquenessSuffix}'
  location: location
  tags: tags
  sku: {
    name: 'Standard'
    tier: 'Standard'
    capacity: 1
  }
  properties: {
    minimumTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
  }
}

@description('Data foundation module implementation marker.')
output moduleStatus string = 'data-foundation-implemented'

@description('Event Hub namespace name.')
output eventHubNamespaceName string = eventHubNamespace.name
