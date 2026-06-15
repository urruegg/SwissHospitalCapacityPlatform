targetScope = 'resourceGroup'

@description('Suffix appended to resource names (e.g. chhealthpf-sit).')
param nameSuffix string

@description('Deployment region. Must be switzerlandnorth (ADR-0003).')
@allowed([
  'switzerlandnorth'
])
param location string

@description('Resource tags applied to all resources.')
param tags object

@description('Object ID(s) of Fabric capacity administrators.')
@minLength(1)
param capacityAdmins array

var capacityName = 'fabric${replace(nameSuffix, '-', '')}'

resource fabricCapacity 'Microsoft.Fabric/capacities@2023-11-01' = {
  name: capacityName
  location: location
  tags: tags
  sku: {
    name: 'F2'
    tier: 'Fabric'
  }
  properties: {
    administration: {
      members: capacityAdmins
    }
  }
}

output capacityName string = fabricCapacity.name
output capacityId string = fabricCapacity.id
output moduleStatus string = 'fabric-foundation-implemented'
