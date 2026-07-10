// Sprint 13 T1 / Sprint 13.1 — ACA hosting for the hcc-app-fluent baseline app.
// User-Assigned Managed Identity + self-contained ACA managed environment + Container App
// with external ingress (nginx-unprivileged serves the static Fluent UI bundle on 8080).
// Modelled on infra/modules/apps/sim-capacity/main.bicep; ingress is enabled because this
// is a browser-facing web app (sim-capacity is a headless producer).

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

@description('Container image the Fluent app runs. Defaults to a placeholder; the actual hcc-app-fluent image is published from apps/hcc-app-fluent/Dockerfile.')
param containerImage string = 'mcr.microsoft.com/dotnet/samples:aspnetapp'

@description('Optional ACR login server (e.g. \'cri75lbu5sj4hza.azurecr.io\') the Container App pulls containerImage from. When set together with containerRegistryResourceId, the module wires MI-based image pull (no admin creds, no secrets).')
param containerRegistryLoginServer string = ''

@description('Optional resource ID of the ACR (Microsoft.ContainerRegistry/registries) that hosts containerImage. Required together with containerRegistryLoginServer to enable MI-based pull + AcrPull role assignment.')
param containerRegistryResourceId string = ''

@description('Target port the Fluent app container listens on (nginx-unprivileged serves on 8080).')
param targetPort int = 8080

@description('Minimum replica count.')
@minValue(0)
@maxValue(10)
param minReplicas int = 1

@description('Maximum replica count.')
@minValue(1)
@maxValue(30)
param maxReplicas int = 3

@description('When true, the deployment is scoped to the Sprint 13 demo path (synthetic data only, ADR-0013 westus2 fallback). Emits a demoScope tag for provenance.')
param demoScope bool = false

@description('Resource tags applied to every resource this module creates.')
param tags object = {}

var effectiveTags = union(tags, {
  demoScope: demoScope ? 'true' : 'false'
})

resource appIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
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
      '${appIdentity.id}': {}
    }
  }
  properties: {
    environmentId: effectiveEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: targetPort
        transport: 'auto'
        allowInsecure: false
      }
      registries: useAcrMiPull ? [
        {
          server: containerRegistryLoginServer
          identity: appIdentity.id
        }
      ] : []
    }
    template: {
      containers: [
        {
          name: 'hcc-app-fluent'
          image: containerImage
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
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
resource acr 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' existing = if (useAcrMiPull) {
  name: last(split(containerRegistryResourceId, '/'))
}

resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (useAcrMiPull) {
  scope: acr
  name: guid(containerRegistryResourceId, appIdentity.id, acrPullRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPullRoleId)
    principalId: appIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    description: 'Sprint 13.1 — hcc-app-fluent MI pulls containerImage from ACR.'
  }
}

@description('Principal ID of the Fluent app User-Assigned Managed Identity.')
output principalId string = appIdentity.properties.principalId

@description('Client ID of the Fluent app User-Assigned Managed Identity.')
output clientId string = appIdentity.properties.clientId

@description('Resource ID of the Fluent app User-Assigned Managed Identity.')
output identityResourceId string = appIdentity.id

@description('Name of the deployed Container App.')
output containerAppName string = containerApp.name

@description('Resource ID of the deployed Container App.')
output containerAppId string = containerApp.id

@description('Public FQDN of the Fluent app ingress.')
output fqdn string = containerApp.properties.configuration.ingress.fqdn

@description('Resource ID of the managed environment used by this Container App (created by this module or supplied via containerAppEnvironmentId).')
output managedEnvironmentId string = effectiveEnvironmentId

@description('hcc-app-fluent module implementation marker.')
output moduleStatus string = 'hcc-app-fluent-implemented'
