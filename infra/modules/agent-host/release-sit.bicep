targetScope = 'resourceGroup'

@allowed([
  'sit'
])
param environmentName string

param solutionShortName string
param location string
param owner string
param costCenter string
param workload string
param agentHostImage string
param fabricDataAgentEndpoint string
param fabricWorkspaceId string
param fabricDataAgentId string
param foundryProjectEndpoint string
param foundryProjectName string
param fabricLakehouseId string
param rlsProvider string
param oboEnabled bool
param oboTenantId string
param oboClientId string
param oboClientSecretName string
param oboJwksUrl string
param oboAudience string
param oboIssuer string
param oboFabricScope string
param oboGroupRoleMap string
param containerRegistryLoginServer string
param keyVaultName string

@allowed([
  false
])
param enableRedis bool

var nameSuffix = '${solutionShortName}-${environmentName}'
var tags = {
  env: environmentName
  owner: owner
  costCenter: costCenter
  workload: workload
}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' existing = {
  name: 'log-${nameSuffix}'
}

resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' existing = {
  name: 'cosmos-${nameSuffix}'
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

resource registry 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' existing = {
  name: first(split(containerRegistryLoginServer, '.'))
}

resource vnet 'Microsoft.Network/virtualNetworks@2023-09-01' existing = {
  name: 'vnet-platform-${nameSuffix}'
}

resource caeSubnet 'Microsoft.Network/virtualNetworks/subnets@2023-09-01' existing = {
  parent: vnet
  name: 'snet-cae'
}

module agentHost 'container-app.bicep' = {
  name: 'agent-host-container-app-release-sit'
  params: {
    location: location
    nameSuffix: nameSuffix
    tags: tags
    agentHostImage: agentHostImage
    logAnalyticsCustomerId: logAnalytics.properties.customerId
    logAnalyticsSharedKey: logAnalytics.listKeys().primarySharedKey
    cosmosEndpoint: cosmos.properties.documentEndpoint
    fabricDataAgentEndpoint: fabricDataAgentEndpoint
    fabricWorkspaceId: fabricWorkspaceId
    fabricDataAgentId: fabricDataAgentId
    foundryProjectEndpoint: foundryProjectEndpoint
    foundryProjectName: foundryProjectName
    fabricLakehouseId: fabricLakehouseId
    rlsProvider: rlsProvider
    oboEnabled: oboEnabled
    oboTenantId: oboTenantId
    oboClientId: oboClientId
    oboClientSecret: (oboEnabled && !empty(oboClientSecretName)) ? keyVault.getSecret(oboClientSecretName) : ''
    oboJwksUrl: oboJwksUrl
    oboAudience: oboAudience
    oboIssuer: oboIssuer
    oboFabricScope: oboFabricScope
    oboGroupRoleMap: oboGroupRoleMap
    redisHostName: enableRedis ? 'unsupported-in-sit' : ''
    redisPort: 0
    containerRegistryLoginServer: containerRegistryLoginServer
    containerRegistryResourceId: registry.id
    caeInfrastructureSubnetResourceId: caeSubnet.id
    // Sprint 44 (Option C) — this SIT-scoped wrapper wires the SIT Event Hub the
    // agent-host reads live external signals from (all platform storage is private).
    signalsEventHubNamespace: 'evh-ihzhhpf-sit-y26y'
    signalsEventHubName: 'events'
  }
}

output agentHostFqdn string = agentHost.outputs.fqdn
output keyVaultName string = keyVault.name
