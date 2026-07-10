@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Container image reference for the agent-host (registry/repository:tag).')
param agentHostImage string

@description('Log Analytics workspace resource ID for the Container Apps environment. customerId + sharedKey are resolved via reference/listKeys (deferred until the workspace exists).')
param logAnalyticsWorkspaceResourceId string

@description('Cosmos DB endpoint the agent-host reads/writes (ADR-0007 §2).')
param cosmosEndpoint string

@description('Redis host name for the grounding cache (ADR-0007 §1).')
param redisHostName string

@description('Target port the agent-host container listens on.')
param targetPort int = 8080

// Sprint 13 T5 — Container Apps environment + agent-host app. System-assigned
// managed identity is used for all downstream auth (Cosmos, Redis, Foundry) so
// no connection strings or keys are stored (copilot-instructions §4).

resource managedEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-${nameSuffix}'
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: reference(logAnalyticsWorkspaceResourceId, '2023-09-01').customerId
        sharedKey: listKeys(logAnalyticsWorkspaceResourceId, '2023-09-01').primarySharedKey
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
          env: [
            {
              name: 'COSMOS_ENDPOINT'
              value: cosmosEndpoint
            }
            {
              name: 'REDIS_HOST'
              value: redisHostName
            }
            {
              name: 'AGENTS_ROOT'
              value: '/app/agents'
            }
          ]
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
