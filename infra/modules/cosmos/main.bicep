// Sprint 16 T1 — CSA Cosmos DB deployment wrapper (resourceGroup scope).
//
// Cosmos may be deployed as its own top-level deployment (separate from
// infra/main.bicep) because it is gated behind an `approved-to-apply` comment
// per AGENTS.md §4 and provisioned on demand. Parameters live in
// infra/modules/cosmos/parameters/<env>.bicepparam.

targetScope = 'resourceGroup'

@description('Deployment environment name.')
@allowed([
  'dev'
  'sit'
  'prod'
])
param environmentName string

@description('Solution short name used in Azure resource names.')
param solutionShortName string = 'ihzhhpf'

@description('Location for all resources. Defaults to resource group location.')
param location string = resourceGroup().location

@description('Owner tag value.')
param owner string = 'platform-team'

@description('Cost center tag value.')
param costCenter string = 'tbd'

@description('Workload tag value.')
param workload string = 'hospital-capacity'

@description('Object ID of the Sprint 13 agent-host managed identity for Cosmos DB Built-in Data Contributor. Empty string skips the assignment.')
param agentHostMiPrincipalId string = ''

@description('When true, provisions a private endpoint into the specified VNet subnet plus the Azure-managed `privatelink.documents.azure.com` private DNS zone. Required in SIT because MCAPSGov policies force Cosmos publicNetworkAccess=Disabled.')
param enablePrivateEndpoint bool = false

@description('Resource ID of the VNet that hosts the private endpoint subnet + will be linked to the private DNS zone.')
param vnetResourceId string = ''

@description('Subnet name inside vnetResourceId that hosts the Cosmos private endpoint.')
param privateEndpointSubnetName string = 'snet-data'

var nameSuffix = '${solutionShortName}-${environmentName}'

var tags = {
  env: environmentName
  owner: owner
  costCenter: costCenter
  workload: workload
}

module csa './csa.bicep' = {
  name: 'cosmos-csa-${nameSuffix}'
  params: {
    location: location
    nameSuffix: nameSuffix
    tags: tags
    agentHostMiPrincipalId: agentHostMiPrincipalId
    enablePrivateEndpoint: enablePrivateEndpoint
    vnetResourceId: vnetResourceId
    privateEndpointSubnetName: privateEndpointSubnetName
  }
}

@description('Cosmos account name.')
output accountName string = csa.outputs.accountName

@description('Cosmos account document endpoint.')
output documentEndpoint string = csa.outputs.documentEndpoint

@description('Container names provisioned.')
output containerNames array = csa.outputs.containerNames
