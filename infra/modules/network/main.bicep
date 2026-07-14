@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Address prefix for the platform virtual network.')
param vnetAddressPrefix string = '10.60.0.0/16'

@description('Address prefix for the platform application subnet.')
param appSubnetPrefix string = '10.60.1.0/24'

@description('Address prefix for the platform data subnet (private endpoints for SQL, KV, Storage).')
param dataSubnetPrefix string = '10.60.2.0/24'

@description('Address prefix for the Container Apps Environment (CAE) infrastructure subnet. Delegated to Microsoft.App/environments. Required for CAE VNet integration (ADR-0029 Option A). Consumption-only CAEs accept /27 minimum; workload-profiles CAEs need /23. We use /23 for headroom.')
param caeSubnetPrefix string = '10.60.4.0/23'

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
			{
				name: 'snet-data'
				properties: {
					addressPrefix: dataSubnetPrefix
					privateEndpointNetworkPolicies: 'Disabled'
				}
			}
			{
				name: 'snet-cae'
				properties: {
					addressPrefix: caeSubnetPrefix
					delegations: [
						{
							name: 'Microsoft.App.environments'
							properties: {
								serviceName: 'Microsoft.App/environments'
							}
						}
					]
					// Azure Container Apps forbids NSGs with certain restrictions on the delegated
					// subnet. Keep it clean for the demo; harden with a curated NSG in PROD if
					// needed. See https://learn.microsoft.com/azure/container-apps/networking#network-security-groups
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

@description('Data subnet resource ID (for private endpoints).')
output dataSubnetResourceId string = resourceId('Microsoft.Network/virtualNetworks/subnets', platformVnet.name, 'snet-data')

@description('Container Apps Environment (CAE) infrastructure subnet resource ID (ADR-0029 Option A). Delegated to Microsoft.App/environments; consumed by cae-<suffix> vnetConfiguration.')
output caeSubnetResourceId string = resourceId('Microsoft.Network/virtualNetworks/subnets', platformVnet.name, 'snet-cae')

@description('Virtual network resource ID (needed to link the private DNS zone for Cosmos when the PE lives inside this VNet).')
output vnetResourceId string = platformVnet.id

@description('Network module scaffold input echo for validation only.')
output scaffoldInput object = {
	location: location
	nameSuffix: nameSuffix
	tagCount: length(items(tags))
}
