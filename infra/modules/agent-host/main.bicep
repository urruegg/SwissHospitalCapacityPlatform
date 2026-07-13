@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Container image reference for the agent-host (registry/repository:tag).')
param agentHostImage string

@description('Log Analytics workspace resource ID for the Container Apps environment. Keys are derived internally via reference()/listKeys() so no secret material crosses module boundaries.')
param logAnalyticsWorkspaceResourceId string

@description('Enable the Azure Managed Redis grounding cache (ADR-0007 §1). Default true for PROD; set to false in SIT per ADR-0028 (Managed Redis Balanced_B0 SKU is not offered in westus2 for the MCAPS demo subscription; the agent-host runtime already uses an in-memory cache so there is no functional loss for demo scope).')
param enableRedisModule bool = true

// Sprint 13 T5 — Container Apps agent-host + optional Redis grounding cache + Cosmos DB
// (ADR-0007). This is a UC1-style output template; it is NOT deployed by this
// PR. Deployment requires the AGENTS.md §4 `approved-to-apply` gate.
//
// Redis conditionality (ADR-0028): the Managed Redis module is optional at SIT
// scope. When enableRedisModule=false the container-app module receives empty
// Redis coordinates and skips the REDIS_HOST/REDIS_PORT env vars. The Python
// agent-host code uses an in-memory grounding cache today (no live redis client
// wiring exists in apps/hcc-agent-host/src/cache/redis_client.py), so the
// runtime behaviour is identical for a single-replica demo.

module cosmos 'cosmos.bicep' = {
  name: 'agent-host-cosmos'
  params: {
    location: location
    nameSuffix: nameSuffix
    tags: tags
  }
}

module redis 'redis.bicep' = if (enableRedisModule) {
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
    logAnalyticsCustomerId: reference(logAnalyticsWorkspaceResourceId, '2023-09-01').customerId
    logAnalyticsSharedKey: listKeys(logAnalyticsWorkspaceResourceId, '2023-09-01').primarySharedKey
    cosmosEndpoint: cosmos.outputs.cosmosEndpoint
    redisHostName: enableRedisModule ? redis!.outputs.redisHostName : ''
    redisPort: enableRedisModule ? redis!.outputs.redisPort : 0
  }
}

output agentHostFqdn string = containerApp.outputs.fqdn
output cosmosAccountName string = cosmos.outputs.cosmosAccountName
output redisName string = enableRedisModule ? redis!.outputs.redisName : ''
output redisEnabled bool = enableRedisModule
