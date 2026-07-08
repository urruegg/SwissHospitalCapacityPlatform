// Sprint 09 v2 — T3.7: ACA hosting for the sim-capacity producer.
// User-Assigned Managed Identity + self-contained ACA managed environment + Container App.
// The MI's principalId is exposed so T2.1 can grant Azure Event Hubs Data Sender on the target namespace.

@description('Azure region. Region-pinned to the Swiss-region variant path per ADR-0013 demo scope.')
@allowed([
  'switzerlandnorth'
  'westus2'
])
param location string

@description('Name for the Container App resource.')
@minLength(2)
@maxLength(32)
param containerAppName string

@description('Optional resource ID of an existing Container Apps managed environment. When empty, a new consumption-only environment is created inside this module.')
param containerAppEnvironmentId string = ''

@description('Name for the managed environment when one is created by this module. Ignored when containerAppEnvironmentId is provided.')
@minLength(2)
@maxLength(60)
param containerAppEnvironmentName string = 'cae-${containerAppName}'

@description('Optional Log Analytics workspace resource ID for the ACA environment. Ignored when containerAppEnvironmentId is provided.')
param logAnalyticsWorkspaceResourceId string = ''

@description('Container image the simulator runs. Defaults to a placeholder; the actual sim-capacity image is published in a later sprint.')
param containerImage string = 'mcr.microsoft.com/dotnet/samples:aspnetapp'

@description('Optional ACR login server (e.g. \'cri75lbu5sj4hza.azurecr.io\') the Container App pulls containerImage from. When set together with containerRegistryResourceId, the module wires MI-based image pull (no admin creds, no secrets).')
param containerRegistryLoginServer string = ''

@description('Optional resource ID of the ACR (Microsoft.ContainerRegistry/registries) that hosts containerImage. Required together with containerRegistryLoginServer to enable MI-based pull + AcrPull role assignment.')
param containerRegistryResourceId string = ''

@description('Event Hub namespace (fully qualified DNS suffix appended in-container) the simulator emits to.')
param eventHubNamespace string

@description('Event Hub (entity) name inside the namespace.')
param eventHubName string

@description('Minimum replica count.')
@minValue(0)
@maxValue(10)
param minReplicas int = 1

@description('Maximum replica count.')
@minValue(1)
@maxValue(30)
param maxReplicas int = 3

@description('When true, the deployment is scoped to the Sprint 09 v2 demo path (synthetic data only, ADR-0013 westus2 fallback). Emits a demoScope tag for provenance.')
param demoScope bool = false

@description('Resource tags applied to every resource this module creates.')
param tags object = {}

var effectiveTags = union(tags, {
  demoScope: demoScope ? 'true' : 'false'
})

resource simulatorIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-${containerAppName}'
  location: location
  tags: effectiveTags
}

resource managedEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = if (empty(containerAppEnvironmentId)) {
  name: containerAppEnvironmentName
  location: location
  tags: effectiveTags
  properties: {
    appLogsConfiguration: !empty(logAnalyticsWorkspaceResourceId) ? {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: reference(logAnalyticsWorkspaceResourceId, '2023-09-01').customerId
        sharedKey: listKeys(logAnalyticsWorkspaceResourceId, '2023-09-01').primarySharedKey
      }
    } : {
      destination: 'azure-monitor'
    }
    zoneRedundant: false
  }
}

var effectiveEnvironmentId = !empty(containerAppEnvironmentId) ? containerAppEnvironmentId : managedEnvironment.id

var useAcrMiPull = !empty(containerRegistryLoginServer) && !empty(containerRegistryResourceId)

// AcrPull role definition id (built-in, verified against Azure docs).
var acrPullRoleId = '7f951dda-4ed3-4680-a7ca-43fe172d538d'

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: containerAppName
  location: location
  tags: effectiveTags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${simulatorIdentity.id}': {}
    }
  }
  properties: {
    environmentId: effectiveEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: null
      registries: useAcrMiPull ? [
        {
          server: containerRegistryLoginServer
          identity: simulatorIdentity.id
        }
      ] : []
    }
    template: {
      containers: [
        {
          name: 'sim-capacity'
          image: containerImage
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          env: [
            {
              name: 'AZURE_CLIENT_ID'
              value: simulatorIdentity.properties.clientId
            }
            {
              name: 'EVENT_HUB_NAMESPACE'
              value: eventHubNamespace
            }
            {
              name: 'EVENT_HUB_NAME'
              value: eventHubName
            }
            {
              name: 'DEMO_SCOPE'
              value: demoScope ? 'true' : 'false'
            }
          ]
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
      }
    }
  }
}

// AcrPull role assignment scoped to the ACR (least privilege for image pull).
// Uses an existing-resource reference so the scope resolves to the actual registry
// resource, not just its resource id string.
resource acr 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' existing = if (useAcrMiPull) {
  name: last(split(containerRegistryResourceId, '/'))
}

resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (useAcrMiPull) {
  scope: acr
  name: guid(containerRegistryResourceId, simulatorIdentity.id, acrPullRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPullRoleId)
    principalId: simulatorIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    description: 'Sprint 10 T1 (ADR-0019) — sim-capacity MI pulls containerImage from ACR.'
  }
}

@description('Principal ID of the simulator User-Assigned Managed Identity. Consumed by T2.1 for Azure Event Hubs Data Sender role assignment.')
output principalId string = simulatorIdentity.properties.principalId

@description('Client ID of the simulator User-Assigned Managed Identity. Passed to the container as AZURE_CLIENT_ID.')
output clientId string = simulatorIdentity.properties.clientId

@description('Resource ID of the simulator User-Assigned Managed Identity.')
output identityResourceId string = simulatorIdentity.id

@description('Name of the deployed Container App.')
output containerAppName string = containerApp.name

@description('Resource ID of the deployed Container App.')
output containerAppId string = containerApp.id

@description('Resource ID of the managed environment used by this Container App (created by this module or supplied via containerAppEnvironmentId).')
output managedEnvironmentId string = effectiveEnvironmentId

@description('Sim-capacity module implementation marker.')
output moduleStatus string = 'sim-capacity-implemented'
