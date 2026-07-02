@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

// Service Bus namespaces need globally unique DNS names (<ns>.servicebus.windows.net).
var globalUniquenessSuffix = take(uniqueString(subscription().subscriptionId, resourceGroup().id), 4)

resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
	name: 'sb-${nameSuffix}-${globalUniquenessSuffix}'
	location: location
	tags: tags
	sku: {
		name: 'Standard'
		tier: 'Standard'
	}
	properties: {
		publicNetworkAccess: 'Enabled'
		minimumTlsVersion: '1.2'
	}
}

@description('Integration module implementation marker.')
output moduleStatus string = 'integration-implemented'

@description('Service Bus namespace name.')
output serviceBusNamespaceName string = serviceBusNamespace.name

@description('Service Bus namespace resource ID.')
output serviceBusNamespaceResourceId string = serviceBusNamespace.id

@description('Integration module scaffold input echo for validation only.')
output scaffoldInput object = {
	location: location
	nameSuffix: nameSuffix
	tagCount: length(items(tags))
}
