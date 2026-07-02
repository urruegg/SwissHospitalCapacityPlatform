targetScope = 'resourceGroup'

@description('Suffix appended to resource names (e.g. ihzhhpf-sit).')
param nameSuffix string

@description('Deployment region. switzerlandnorth (ADR-0003 default) or westus2 (ADR-0013 demo-scope carve-out).')
@allowed([
  'switzerlandnorth'
  'westus2'
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
