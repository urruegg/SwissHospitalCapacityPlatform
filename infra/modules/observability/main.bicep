@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. chhealthpf-sit or chhealthpf-prod.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Observability module scaffold marker.')
output moduleStatus string = 'observability-scaffold'

@description('Observability module scaffold input echo for validation only.')
output scaffoldInput object = {
	location: location
	nameSuffix: nameSuffix
	tagCount: length(items(tags))
}
