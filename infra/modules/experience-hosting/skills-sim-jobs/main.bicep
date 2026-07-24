// Sprint 23 WS-A3 (#255) — Container Apps Jobs for the skills-evidence simulators.
//
// Four manual-trigger Container Apps Jobs — one per external source system
// (successfactors / lms / skills-manager / work-id) — that run the WS-B
// skills_evidence_synth.py seeder and write synthetic extract files to the WS-A1
// ADLS Gen2 landing zone via a User-Assigned Managed Identity.
//
// HARD CONSTRAINT (design D5 + issue #255): these jobs are triggerType `Manual`
// (on-demand only). They are NEVER started by a GitHub workflow — an operator or
// the orchestrator invokes `az containerapp job start`. Ingestion/simulation runs
// as Azure Container Apps, not GitHub Actions.
//
// The MI's principalId is exposed so the WS-A1 masterdata-landing module grants it
// Storage Blob Data Contributor on the landing account (wired in infra/main.bicep).

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

@description('Optional resource ID of an existing Container Apps managed environment. When empty, a consumption-only environment is created inside this module.')
param containerAppEnvironmentId string = ''

@description('Name for the managed environment when one is created by this module. Ignored when containerAppEnvironmentId is provided.')
@minLength(2)
@maxLength(60)
param containerAppEnvironmentName string = 'cae-skills-sim-${nameSuffix}'

@description('Optional Log Analytics workspace resource ID for the managed environment. Ignored when containerAppEnvironmentId is provided.')
param logAnalyticsWorkspaceResourceId string = ''

@description('Container image the seeder jobs run. Defaults to a placeholder; the real skills-sim image is published by a follow-up CI workflow (parity with the sim-capacity pattern).')
param containerImage string = 'mcr.microsoft.com/dotnet/samples:aspnetapp'

@description('Optional ACR login server the jobs pull containerImage from. Set together with containerRegistryResourceId to wire MI-based pull (no admin creds, no secrets).')
param containerRegistryLoginServer string = ''

@description('Optional resource ID of the ACR that hosts containerImage. Required together with containerRegistryLoginServer.')
param containerRegistryResourceId string = ''

@description('Name of the WS-A1 ADLS Gen2 landing storage account the jobs write extracts to.')
param landingStorageAccountName string

@description('Name of the landing filesystem (container) inside the landing storage account.')
param landingContainerName string = 'landing'

@description('Root prefix inside the landing container for org/skills extracts.')
param landingPrefix string = 'curavias-org-skills'

@description('External source systems to seed, one Container Apps Job each. `code` drives the resource name (kept short for the 32-char job-name limit); `system` is the externalSystem value passed to the seeder.')
param sources array = [
  { code: 'sf', system: 'successfactors' }
  { code: 'lms', system: 'lms' }
  { code: 'skm', system: 'skills-manager' }
  { code: 'wid', system: 'work-id' }
]

@description('Replica timeout (seconds) per job execution.')
@minValue(60)
@maxValue(3600)
param replicaTimeoutSeconds int = 1800

@description('When true, the deployment is scoped to the demo path (synthetic data only, ADR-0013). Emits a demoScope tag for provenance.')
param demoScope bool = false

var effectiveTags = union(tags, {
  demoScope: demoScope ? 'true' : 'false'
})

resource jobsIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-skills-sim-${nameSuffix}'
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

// One manual-trigger job per source. The container contract (implemented by the
// real image published in a follow-up) reads SOURCE_SYSTEM to pick the connector,
// runs the WS-B skills_evidence_synth.py seeder to --output, then uploads the
// extract to LANDING_STORAGE_ACCOUNT/LANDING_CONTAINER/LANDING_PREFIX/<source>/<date>/
// via the managed identity (AZURE_CLIENT_ID). No secrets — RBAC-only.
resource simJobs 'Microsoft.App/jobs@2024-03-01' = [for s in sources: {
  name: 'caj-sk-${s.code}-${nameSuffix}'
  location: location
  tags: effectiveTags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${jobsIdentity.id}': {}
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
      registries: useAcrMiPull ? [
        {
          server: containerRegistryLoginServer
          identity: jobsIdentity.id
        }
      ] : []
    }
    template: {
      containers: [
        {
          name: 'skills-sim-${s.code}'
          image: containerImage
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          args: [
            '--source'
            s.system
            '--output'
            '/tmp/${s.system}.jsonl'
          ]
          env: [
            {
              name: 'AZURE_CLIENT_ID'
              value: jobsIdentity.properties.clientId
            }
            {
              name: 'SOURCE_SYSTEM'
              value: s.system
            }
            {
              name: 'LANDING_STORAGE_ACCOUNT'
              value: landingStorageAccountName
            }
            {
              name: 'LANDING_CONTAINER'
              value: landingContainerName
            }
            {
              name: 'LANDING_PREFIX'
              value: landingPrefix
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
}]

// AcrPull role assignment scoped to the ACR (least privilege for image pull).
resource acr 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' existing = if (useAcrMiPull) {
  name: last(split(containerRegistryResourceId, '/'))
}

resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (useAcrMiPull) {
  scope: acr
  name: guid(containerRegistryResourceId, jobsIdentity.id, acrPullRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPullRoleId)
    principalId: jobsIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    description: 'Sprint 23 WS-A3 (#255) — skills-sim jobs MI pulls containerImage from ACR.'
  }
}

@description('Principal ID of the skills-sim jobs User-Assigned Managed Identity. Consumed by the WS-A1 masterdata-landing module for the Storage Blob Data Contributor grant.')
output principalId string = jobsIdentity.properties.principalId

@description('Client ID of the skills-sim jobs User-Assigned Managed Identity. Passed to each container as AZURE_CLIENT_ID.')
output clientId string = jobsIdentity.properties.clientId

@description('Resource ID of the skills-sim jobs User-Assigned Managed Identity.')
output identityResourceId string = jobsIdentity.id

@description('Names of the four manual-trigger Container Apps Jobs.')
output jobNames array = [for (s, i) in sources: 'caj-sk-${s.code}-${nameSuffix}']

@description('Resource ID of the managed environment used by these jobs (created by this module or supplied via containerAppEnvironmentId).')
output managedEnvironmentId string = effectiveEnvironmentId

@description('Skills-sim jobs module implementation marker.')
output moduleStatus string = 'skills-sim-jobs-implemented'
