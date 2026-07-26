// Sprint 23 WS-A4 (#255) — Container Apps Job for the skills-EVENTS simulator.
//
// A single manual-trigger Container Apps Job that runs the WS-A4
// publish_skill_events.py simulator, publishing synthetic DC-SKILL-EVENT-v1
// records to the LIVE SIT Eventstream `CustomEndpoint` source (the demo lane,
// #379). The CustomEndpoint is an Event-Hub-compatible endpoint reached with a
// SAS connection string; the publisher reads it from SKILLS_EVENTS_CONNECTION_STRING.
//
// SECRET HANDLING (no secrets in repo): the SAS string is stored as a Key Vault
// secret (populated out-of-band by an operator after retrieving it from Fabric).
// This job injects it via a Container Apps Key Vault *secret reference*
// (secrets[].keyVaultUrl + env.secretRef), resolved at runtime by the job's
// User-Assigned Managed Identity (granted `Key Vault Secrets User`). The value
// never appears in Bicep, git, or the deployment history.
//
// HARD CONSTRAINT (design D5 + NFR-SKILL-001): triggerType `Manual` (on-demand
// only). It is NEVER started by a GitHub workflow — an operator or the
// orchestrator invokes `az containerapp job start`. Ingestion/simulation runs as
// Azure Container Apps, not GitHub Actions.

@description('Azure region. Region-pinned to the ADR-0013 demo-scope variant path.')
@allowed([
  'switzerlandnorth'
  'westus2'
])
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
@minLength(3)
param nameSuffix string

@description('Resource tags applied to every resource this module creates.')
param tags object = {}

@description('Optional resource ID of an existing Container Apps managed environment. When empty, a consumption-only environment is created inside this module. Reuse the skills-sim environment where available to avoid a duplicate CAE.')
param containerAppEnvironmentId string = ''

@description('Name for the managed environment when one is created by this module. Ignored when containerAppEnvironmentId is provided.')
@minLength(2)
@maxLength(60)
param containerAppEnvironmentName string = 'cae-skev-${nameSuffix}'

@description('Optional Log Analytics workspace resource ID for the managed environment. Ignored when containerAppEnvironmentId is provided.')
param logAnalyticsWorkspaceResourceId string = ''

@description('Container image the publisher job runs. Defaults to a placeholder; the real skills-events-sim image is published by a follow-up CI workflow (parity with the skills-sim pattern).')
param containerImage string = 'mcr.microsoft.com/dotnet/samples:aspnetapp'

@description('Optional ACR login server the job pulls containerImage from. Set together with containerRegistryResourceId to wire MI-based pull (no admin creds, no secrets).')
param containerRegistryLoginServer string = ''

@description('Optional resource ID of the ACR that hosts containerImage. Required together with containerRegistryLoginServer.')
param containerRegistryResourceId string = ''

@description('Name of the platform Key Vault that holds the CustomEndpoint SAS connection-string secret. The job MI is granted Key Vault Secrets User on this vault.')
@minLength(3)
param keyVaultName string

@description('Name of the Key Vault secret that holds the CustomEndpoint SAS connection string. The value is populated out-of-band (never in Bicep/git).')
@minLength(1)
param connectionStringSecretName string = 'skills-events-connection-string'

@description('Replica timeout (seconds) per job execution.')
@minValue(60)
@maxValue(3600)
param replicaTimeoutSeconds int = 600

@description('When true, the deployment is scoped to the demo path (synthetic data only, ADR-0013). Emits a demoScope tag for provenance.')
param demoScope bool = false

var effectiveTags = union(tags, {
  demoScope: demoScope ? 'true' : 'false'
})

// Built-in role: Key Vault Secrets User (verified against Azure RBAC docs).
var keyVaultSecretsUserRoleId = '4633458b-17de-408a-b874-0445c86b69e6'
// AcrPull role definition id (built-in, verified against Azure docs).
var acrPullRoleId = '7f951dda-4ed3-4680-a7ca-43fe172d538d'

var useAcrMiPull = !empty(containerRegistryLoginServer) && !empty(containerRegistryResourceId)

resource jobIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-skev-${nameSuffix}'
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

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

// The job MI reads the SAS connection-string secret via the Container Apps Key
// Vault secret reference (keyless).
resource keyVaultSecretsUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: keyVault
  name: guid(keyVault.id, jobIdentity.id, keyVaultSecretsUserRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', keyVaultSecretsUserRoleId)
    principalId: jobIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    description: 'Sprint 23 WS-A4 (#255) — skills-events sim job MI reads the CustomEndpoint SAS secret (keyless).'
  }
}

// Manual-trigger job. The container contract (implemented by the real image
// published in a follow-up) runs publish_skill_events.py with the SAS connection
// string supplied via SKILLS_EVENTS_CONNECTION_STRING (a Key Vault secret ref) and
// publishes synthetic DC-SKILL-EVENT-v1 records to the live SIT CustomEndpoint.
resource simJob 'Microsoft.App/jobs@2024-03-01' = {
  name: 'caj-skev-${nameSuffix}'
  location: location
  tags: effectiveTags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${jobIdentity.id}': {}
    }
  }
  properties: {
    environmentId: effectiveEnvironmentId
    configuration: {
      triggerType: 'Manual'
      replicaTimeout: replicaTimeoutSeconds
      replicaRetryLimit: 1
      manualTriggerConfig: {
        parallelism: 1
        replicaCompletionCount: 1
      }
      secrets: [
        {
          name: connectionStringSecretName
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/${connectionStringSecretName}'
          identity: jobIdentity.id
        }
      ]
      registries: useAcrMiPull ? [
        {
          server: containerRegistryLoginServer
          identity: jobIdentity.id
        }
      ] : []
    }
    template: {
      containers: [
        {
          name: 'skills-event-sim'
          image: containerImage
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          env: [
            {
              name: 'AZURE_CLIENT_ID'
              value: jobIdentity.properties.clientId
            }
            {
              name: 'SKILLS_EVENTS_CONNECTION_STRING'
              secretRef: connectionStringSecretName
            }
            {
              name: 'DEMO_SCOPE'
              value: demoScope ? 'true' : 'false'
            }
          ]
        }
      ]
    }
  }
}

// AcrPull role assignment scoped to the ACR (least privilege for image pull).
resource acr 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' existing = if (useAcrMiPull) {
  name: last(split(containerRegistryResourceId, '/'))
}

resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (useAcrMiPull) {
  scope: acr
  name: guid(containerRegistryResourceId, jobIdentity.id, acrPullRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPullRoleId)
    principalId: jobIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    description: 'Sprint 23 WS-A4 (#255) — skills-events sim job MI pulls containerImage from ACR.'
  }
}

@description('Principal ID of the skills-events sim job User-Assigned Managed Identity.')
output principalId string = jobIdentity.properties.principalId

@description('Client ID of the skills-events sim job User-Assigned Managed Identity. Passed to the container as AZURE_CLIENT_ID.')
output clientId string = jobIdentity.properties.clientId

@description('Resource ID of the skills-events sim job User-Assigned Managed Identity.')
output identityResourceId string = jobIdentity.id

@description('Name of the manual-trigger Container Apps Job.')
output jobName string = simJob.name

@description('Name of the Key Vault secret the job reads the CustomEndpoint SAS connection string from.')
output connectionStringSecretName string = connectionStringSecretName

@description('Resource ID of the managed environment used by this job (created by this module or supplied via containerAppEnvironmentId).')
output managedEnvironmentId string = effectiveEnvironmentId

@description('Skills-events sim job module implementation marker.')
output moduleStatus string = 'skills-event-sim-job-implemented'
