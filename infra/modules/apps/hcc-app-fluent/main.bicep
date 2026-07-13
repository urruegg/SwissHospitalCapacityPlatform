// Sprint 13 T1 — hcc-app-fluent Container App (React/Vite Fluent baseline UI).
// Static bundle served via nginx-unprivileged on port 8080. System-assigned MI so the
// app-shell can request tokens for downstream MSAL OBO flows (Graph, agent-host /chat).
// Minimal by design — the app itself is a static single-page app, not a stateful service.

@description('Azure region.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Container image the app runs (registry/repository:tag). Defaults to nginx-unprivileged placeholder; swap to the built app-fluent image once app-build.yml pushes to ACR.')
param appImage string = 'nginxinc/nginx-unprivileged:1.27-alpine'

@description('Log Analytics workspace resource ID used by the ACA managed environment. Derived from platform-foundation at the top-level main.bicep.')
param logAnalyticsWorkspaceResourceId string

@description('Optional ACR login server (e.g. cri75lbu5sj4hza.azurecr.io) for MI-based image pull. Required together with containerRegistryResourceId to enable no-secrets pull once real images land.')
param containerRegistryLoginServer string = ''

@description('Optional ACR resource ID. Required together with containerRegistryLoginServer.')
param containerRegistryResourceId string = ''

@description('Minimum replica count.')
@minValue(0)
@maxValue(10)
param minReplicas int = 1

@description('Maximum replica count.')
@minValue(1)
@maxValue(30)
param maxReplicas int = 3

@description('Container target port. Fluent Dockerfile serves via nginx-unprivileged on 8080.')
param targetPort int = 8080

// AcrPull role definition id (built-in).
var acrPullRoleId = '7f951dda-4ed3-4680-a7ca-43fe172d538d'
var useAcrMiPull = !empty(containerRegistryLoginServer) && !empty(containerRegistryResourceId)

resource managedEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-app-fluent-${nameSuffix}'
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
    zoneRedundant: false
  }
}

// User-assigned MI for the app-fluent CA. Created BEFORE the CA so the AcrPull
// role assignment can land first — the CA then references an already-authorised
// identity when it triggers its first (or updated) revision pull. Matches the
// sim-capacity pattern.
resource appFluentIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-ca-app-fluent-${nameSuffix}'
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
  name: guid(containerRegistryResourceId, appFluentIdentity.id, acrPullRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPullRoleId)
    principalId: appFluentIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    description: 'Sprint 13 T1 — hcc-app-fluent CA pulls image from ACR via user-assigned MI.'
  }
}

resource appFluent 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-app-fluent-${nameSuffix}'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${appFluentIdentity.id}': {}
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
          identity: appFluentIdentity.id
        }
      ] : []
    }
    template: {
      containers: [
        {
          name: 'app-fluent'
          image: appImage
          resources: {
            cpu: json('0.5')
            memory: '1.0Gi'
          }
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
      }
    }
  }
  dependsOn: [
    acrPullRoleAssignment
  ]
}

@description('Container App FQDN (ingress URL host).')
output appFluentFqdn string = appFluent.properties.configuration.ingress.fqdn

@description('Container App name.')
output appFluentName string = appFluent.name

@description('User-assigned MI principal ID (for OBO/Graph token wiring).')
output appFluentPrincipalId string = appFluentIdentity.properties.principalId

@description('User-assigned MI client ID.')
output appFluentClientId string = appFluentIdentity.properties.clientId

@description('User-assigned MI resource ID.')
output appFluentIdentityResourceId string = appFluentIdentity.id
