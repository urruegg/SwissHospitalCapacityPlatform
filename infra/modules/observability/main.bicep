@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. chhealthpf-sit or chhealthpf-prod.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
	name: 'appi-${nameSuffix}'
	location: location
	tags: tags
	kind: 'web'
	properties: {
		Application_Type: 'web'
	}
}

@description('Observability module implementation marker.')
output moduleStatus string = 'observability-implemented'

@description('Application Insights component name.')
output appInsightsName string = appInsights.name

@description('Application Insights connection string.')
output appInsightsConnectionString string = appInsights.properties.ConnectionString

@description('Observability module scaffold input echo for validation only.')
output scaffoldInput object = {
	location: location
	nameSuffix: nameSuffix
	tagCount: length(items(tags))
}
