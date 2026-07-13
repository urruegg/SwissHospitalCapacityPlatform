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

@description('Optional ACR login server (e.g. cri75lbu5sj4hza.azurecr.io) for MI-based image pull. Required together with containerRegistryResourceId. When empty, the CA uses no `registries` block and relies on public/anonymous pull.')
param containerRegistryLoginServer string = ''

@description('Optional ACR resource ID. Required together with containerRegistryLoginServer.')
param containerRegistryResourceId string = ''

// Sprint 13 T5 — Container Apps environment + agent-host app. Uses a
// **user-assigned managed identity** (`id-ca-agent-host-<suffix>`) so the
// AcrPull role assignment can be provisioned BEFORE the CA references the
// identity, avoiding the chicken-and-egg problem that system-assigned MI hits
// on the first ACR pull attempt. Matches the sim-capacity pattern
// (`infra/modules/apps/sim-capacity/main.bicep`).
//
// REDIS_HOST/REDIS_PORT env vars are injected only when the parent module
// supplies a non-empty redisHostName (ADR-0028). The agent-host runtime uses
// an in-memory grounding cache today; the env vars only take effect if/when
// a real Redis client is wired into apps/hcc-agent-host/src/cache/redis_client.py.

// AcrPull role definition id (built-in).
var acrPullRoleId = '7f951dda-4ed3-4680-a7ca-43fe172d538d'
var useAcrMiPull = !empty(containerRegistryLoginServer) && !empty(containerRegistryResourceId)

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

// User-assigned MI for the agent-host CA. Created BEFORE the CA so the AcrPull
// role assignment can land first — the CA then references an already-authorised
// identity when it triggers its first (or updated) revision pull.
resource agentHostIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-ca-agent-host-${nameSuffix}'
  location: location
  tags: tags
}

// AcrPull on the ACR when MI-based pull is enabled. Scoped to the ACR resource
// so the identity has only pull rights on this one registry.
resource acr 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' existing = if (useAcrMiPull) {
  name: last(split(containerRegistryResourceId, '/'))
}

resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (useAcrMiPull) {
  scope: acr
  name: guid(containerRegistryResourceId, agentHostIdentity.id, acrPullRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPullRoleId)
    principalId: agentHostIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    description: 'Sprint 13 T5 — agent-host CA pulls image from ACR via user-assigned MI.'
  }
}

resource agentHost 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-agent-host-${nameSuffix}'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${agentHostIdentity.id}': {}
    }
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
      registries: useAcrMiPull ? [
        {
          server: containerRegistryLoginServer
          identity: agentHostIdentity.id
        }
      ] : []
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
  dependsOn: [
    // Ensure the AcrPull role assignment lands before the CA revision attempts
    // its first pull. Only meaningful when useAcrMiPull=true, but Bicep evaluates
    // dependsOn statically — the array element resolves to the module-scope
    // resource when the conditional is true and is silently ignored otherwise.
    acrPullRoleAssignment
  ]
}

output fqdn string = agentHost.properties.configuration.ingress.fqdn
output principalId string = agentHostIdentity.properties.principalId
output identityResourceId string = agentHostIdentity.id
output identityClientId string = agentHostIdentity.properties.clientId
