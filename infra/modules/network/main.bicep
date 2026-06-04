@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. chhealthpf-sit or chhealthpf-prod.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Address prefix for the platform virtual network.')
param vnetAddressPrefix string = '10.60.0.0/16'

@description('Address prefix for the platform application subnet.')
param appSubnetPrefix string = '10.60.1.0/24'

resource platformVnet 'Microsoft.Network/virtualNetworks@2023-09-01' = {
	name: 'vnet-platform-${nameSuffix}'
	location: location
	tags: tags
	properties: {
		addressSpace: {
			addressPrefixes: [
				vnetAddressPrefix
			]
		}
		subnets: [
			{
				name: 'snet-app'
				properties: {
					addressPrefix: appSubnetPrefix
				}
			}
		]
	}
}

@description('Network module implementation marker.')
output moduleStatus string = 'network-implemented'

@description('Virtual network name.')
output vnetName string = platformVnet.name

@description('Application subnet resource ID.')
output appSubnetResourceId string = resourceId('Microsoft.Network/virtualNetworks/subnets', platformVnet.name, 'snet-app')

@description('Network module scaffold input echo for validation only.')
output scaffoldInput object = {
	location: location
	nameSuffix: nameSuffix
	tagCount: length(items(tags))
}
