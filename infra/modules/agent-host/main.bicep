@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Container image reference for the agent-host (registry/repository:tag).')
param agentHostImage string

@description('Log Analytics workspace resource ID for the Container Apps environment. customerId + sharedKey are resolved from it inside the container-app submodule (deferred until the workspace exists).')
param logAnalyticsWorkspaceResourceId string

// Sprint 13 T5 — Container Apps agent-host + Redis grounding cache + Cosmos DB
// (ADR-0007). This is a UC1-style output template; it is NOT deployed by this
// PR. Deployment requires the AGENTS.md §4 `approved-to-apply` gate.

module cosmos 'cosmos.bicep' = {
  name: 'agent-host-cosmos'
  params: {
    location: location
    nameSuffix: nameSuffix
    tags: tags
  }
}

module redis 'redis.bicep' = {
  name: 'agent-host-redis'
  params: {
    location: location
    nameSuffix: nameSuffix
    tags: tags
  }
}

module containerApp 'container-app.bicep' = {
  name: 'agent-host-container-app'
  params: {
    location: location
    nameSuffix: nameSuffix
    tags: tags
    agentHostImage: agentHostImage
    logAnalyticsWorkspaceResourceId: logAnalyticsWorkspaceResourceId
    cosmosEndpoint: cosmos.outputs.cosmosEndpoint
    redisHostName: redis.outputs.redisHostName
  }
}

output agentHostFqdn string = containerApp.outputs.fqdn
output agentHostPrincipalId string = containerApp.outputs.principalId
output cosmosAccountName string = cosmos.outputs.cosmosAccountName
output redisName string = redis.outputs.redisName
output moduleStatus string = 'agent-host-implemented'
