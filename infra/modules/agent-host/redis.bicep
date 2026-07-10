@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

// Sprint 13 T5 hardening (2026-07-10): migrated from the retired Azure Cache for
// Redis (Microsoft.Cache/redis, Basic C0) to Azure Managed Redis
// (Microsoft.Cache/redisEnterprise, Balanced_B0). Trigger: SIT deploy 29090732422
// failed with:
//   "Azure Cache for Redis is retiring, create Azure Managed Redis instance instead.
//    Learn more: https://aka.ms/AzureCacheForRedisRetirement"
//
// Balanced_B0 is the smallest SKU per Microsoft Learn
// (https://learn.microsoft.com/azure/templates/microsoft.cache/redisenterprise).
// Access-key auth disabled in favour of Entra managed identity per ADR-0007 §1.
//
// NOTE — cost implication: Balanced_B0 is materially more expensive than the
// retired Basic C0 (~$110/month vs ~$16/month at 730 hours). This is a MCAPS
// tenant demo-scope cost. Consider making the module optional in a future PR
// if the demo does not exercise Redis grounding.

resource redis 'Microsoft.Cache/redisEnterprise@2024-10-01' = {
  name: 'redis-${nameSuffix}'
  location: location
  tags: tags
  sku: {
    name: 'Balanced_B0'
  }
  properties: {
    highAvailability: 'Enabled'
    minimumTlsVersion: '1.2'
  }
}

// Managed Redis requires an explicit `database` child resource — this is where
// the Redis endpoint actually lives. The cluster resource above only wraps
// the SKU + HA + TLS envelope.
resource redisDatabase 'Microsoft.Cache/redisEnterprise/databases@2024-10-01' = {
  parent: redis
  name: 'default'
  properties: {
    clientProtocol: 'Encrypted'
    port: 10000
    clusteringPolicy: 'EnterpriseCluster'
    evictionPolicy: 'NoEviction'
    persistence: {
      aofEnabled: false
      rdbEnabled: false
    }
    // Access-key auth disabled per ADR-0007 §1 — Entra MI is the sole auth path.
    accessKeysAuthentication: 'Disabled'
  }
}

@description('Cluster resource name.')
output redisName string = redis.name

@description('Cluster host name (endpoint). Managed Redis uses port 10000 by default; ensure the agent-host client is configured for the enterprise cluster port + TLS.')
output redisHostName string = redis.properties.hostName

@description('Managed Redis port (fixed at 10000 for the Enterprise cluster).')
output redisPort int = 10000
