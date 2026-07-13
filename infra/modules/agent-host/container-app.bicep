@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Container image reference for the agent-host (registry/repository:tag).')
param agentHostImage string

@description('Log Analytics workspace customer ID (GUID) for the Container Apps environment.')
param logAnalyticsCustomerId string

@description('Log Analytics shared key for the Container Apps environment.')
@secure()
param logAnalyticsSharedKey string

@description('Cosmos DB endpoint the agent-host reads/writes (ADR-0007 §2).')
param cosmosEndpoint string

@description('Redis host name for the grounding cache (ADR-0007 §1). Empty string skips the Redis env vars entirely — used when the parent module is deployed with enableRedisModule=false (ADR-0028, SIT demo scope).')
param redisHostName string = ''

@description('Redis port. Azure Managed Redis uses 10000 for the Enterprise cluster (vs 6380 on the retired classic SKU). Ignored when redisHostName is empty.')
param redisPort int = 10000

@description('Target port the agent-host container listens on.')
param targetPort int = 8080

// Sprint 13 T5 — Container Apps environment + agent-host app. System-assigned
// managed identity is used for all downstream auth (Cosmos, Redis, Foundry) so
// no connection strings or keys are stored (copilot-instructions §4).
//
// REDIS_HOST/REDIS_PORT env vars are injected only when the parent module
// supplies a non-empty redisHostName (ADR-0028). The agent-host runtime uses
// an in-memory grounding cache today; the env vars only take effect if/when
// a real Redis client is wired into apps/hcc-agent-host/src/cache/redis_client.py.

var baseEnv = [
  {
    name: 'COSMOS_ENDPOINT'
    value: cosmosEndpoint
  }
  {
    name: 'AGENTS_ROOT'
    value: '/app/agents'
  }
]

var redisEnv = empty(redisHostName) ? [] : [
  {
    name: 'REDIS_HOST'
    value: redisHostName
  }
  {
    name: 'REDIS_PORT'
    value: string(redisPort)
  }
]

resource managedEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-${nameSuffix}'
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsCustomerId
        sharedKey: logAnalyticsSharedKey
      }
    }
  }
}

resource agentHost 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-agent-host-${nameSuffix}'
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: managedEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: targetPort
        transport: 'auto'
        allowInsecure: false
      }
    }
    template: {
      containers: [
        {
          name: 'agent-host'
          image: agentHostImage
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: concat(baseEnv, redisEnv)
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

output fqdn string = agentHost.properties.configuration.ingress.fqdn
output principalId string = agentHost.identity.principalId
