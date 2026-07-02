@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

resource aiServices 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
	name: 'ai-${nameSuffix}'
	location: location
	tags: tags
	kind: 'AIServices'
	sku: {
		name: 'S0'
	}
	properties: {
		publicNetworkAccess: 'Enabled'
	}
}

@description('AI platform module implementation marker.')
output moduleStatus string = 'ai-platform-implemented'

@description('AI services account name.')
output aiServicesAccountName string = aiServices.name

@description('AI services endpoint.')
output aiServicesEndpoint string = aiServices.properties.endpoint

@description('AI platform module scaffold input echo for validation only.')
output scaffoldInput object = {
	location: location
	nameSuffix: nameSuffix
	tagCount: length(items(tags))
}
