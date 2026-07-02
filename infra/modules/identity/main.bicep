@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

resource platformIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
	name: 'id-platform-${nameSuffix}'
	location: location
	tags: tags
}

@description('Identity module implementation marker.')
output moduleStatus string = 'identity-implemented'

@description('Principal ID of the platform managed identity.')
output principalId string = platformIdentity.properties.principalId

@description('Client ID of the platform managed identity.')
output clientId string = platformIdentity.properties.clientId

@description('Resource ID of the platform managed identity.')
output resourceId string = platformIdentity.id

@description('Identity module scaffold input echo for validation only.')
output scaffoldInput object = {
	location: location
	nameSuffix: nameSuffix
	tagCount: length(items(tags))
}
