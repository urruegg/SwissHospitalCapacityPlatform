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
  }
}

@description('Cosmos account name.')
output accountName string = csa.outputs.accountName

@description('Cosmos account document endpoint.')
output documentEndpoint string = csa.outputs.documentEndpoint

@description('Container names provisioned.')
output containerNames array = csa.outputs.containerNames
