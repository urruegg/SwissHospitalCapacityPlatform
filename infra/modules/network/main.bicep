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

@description('Address prefix for the Container Apps Environment (CAE) infrastructure subnet. Consumed by `cae-<suffix>.vnetConfiguration.infrastructureSubnetId` (ADR-0029 Option A). MUST be delegated to `Microsoft.App/environments` — any NEW modern-API CAE with `infrastructureSubnetId` requires the delegation regardless of workload profile (verified 2026-07-14 after `ManagedEnvironmentSubnetDelegationError` on the fresh create). The earlier `ManagedEnvironmentV1SubnetDelegationNotAllowed` error on the existing v1 CAE was ARM refusing to reconfigure a v1 CAE with a subnet at all, misreported as a delegation issue. Minimum size is /27 for a workload-profiles CAE; we use /23 for headroom.')
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
					// REQUIRED delegation for CAE VNet integration on modern-API CAEs.
					// Without this, ARM refuses the CAE create with
					// `ManagedEnvironmentSubnetDelegationError`. Do NOT combine with
					// an NSG on this subnet — CAE network policies are managed by
					// the Container Apps control plane. Ref:
					// https://learn.microsoft.com/azure/container-apps/networking#custom-vnet-configuration
					delegations: [
						{
							name: 'Microsoft.App.environments'
							properties: {
								serviceName: 'Microsoft.App/environments'
							}
						}
					]
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

@description('Container Apps Environment (CAE) infrastructure subnet resource ID (ADR-0029 Option A). Delegated to `Microsoft.App/environments`; consumed at CAE creation time by `cae-<suffix>.vnetConfiguration.infrastructureSubnetId`.')
output caeSubnetResourceId string = resourceId('Microsoft.Network/virtualNetworks/subnets', platformVnet.name, 'snet-cae')

@description('Virtual network resource ID (needed to link the private DNS zone for Cosmos when the PE lives inside this VNet).')
output vnetResourceId string = platformVnet.id

@description('Network module scaffold input echo for validation only.')
output scaffoldInput object = {
	location: location
	nameSuffix: nameSuffix
	tagCount: length(items(tags))
}
