// Sprint 13.1 — ADR-0029 Option A. Private Endpoint + private DNS zone group
// for `cosmos-<nameSuffix>` (the agent-host Cosmos DB account provisioned by
// `./cosmos.bicep`). Mirrors the working pattern in
// `infra/modules/cosmos/csa.bicep` §Private endpoint block.
//
// Why a separate module: (a) the agent-host Cosmos + agent-host CA are on
// different lifecycle boundaries than the CSA Cosmos, (b) the CAE VNet
// integration is what actually unblocks reachability — the PE is one half
// of that; the other half is the `vnetConfiguration` on the CAE.
//
// Private DNS zone reuse: the zone `privatelink.documents.azure.com` and its
// VNet link are created by the CSA module the first time it deploys
// (`infra/modules/cosmos/csa.bicep` lines ~308-323). This module references
// that existing zone with `existing`; it does NOT create a duplicate. In a
// fresh RG the CSA module must deploy first — enforced via `dependsOn` at
// the top-level `infra/main.bicep`.
//
// Ownership: user-assigned MI grants are configured elsewhere. This module
// only wires networking (PE + DNS record via zone group).

@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Resource ID of the Cosmos DB account to expose via private endpoint.')
param cosmosAccountResourceId string

@description('Resource ID of the subnet that hosts the private endpoint. Must have `privateEndpointNetworkPolicies: Disabled`.')
param privateEndpointSubnetResourceId string

@description('Existing private DNS zone name — Azure-managed for Cosmos SQL is exactly `privatelink.documents.azure.com`. Do not override.')
param privateDnsZoneName string = 'privatelink.documents.azure.com'

// The private DNS zone is created by the CSA cosmos module in the same RG.
// We only need a reference to attach a zone group; the CSA module also owns
// the VNet link, which is fine because a single zone can back many PEs.
resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' existing = {
  name: privateDnsZoneName
}

resource privateEndpoint 'Microsoft.Network/privateEndpoints@2023-11-01' = {
  name: 'pe-cosmos-${nameSuffix}'
  location: location
  tags: tags
  properties: {
    subnet: {
      id: privateEndpointSubnetResourceId
    }
    privateLinkServiceConnections: [
      {
        name: 'pe-cosmos-${nameSuffix}-conn'
        properties: {
          privateLinkServiceId: cosmosAccountResourceId
          groupIds: [
            'Sql'
          ]
        }
      }
    ]
  }
}

resource privateDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-11-01' = {
  parent: privateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'privatelink-documents-azure-com'
        properties: {
          privateDnsZoneId: privateDnsZone.id
        }
      }
    ]
  }
}

@description('Private endpoint resource name.')
output privateEndpointName string = privateEndpoint.name

@description('Private endpoint resource ID.')
output privateEndpointResourceId string = privateEndpoint.id
