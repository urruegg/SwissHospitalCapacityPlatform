// Sprint 28 WS-INF (#377) — Curavias Product Owner Agent runtime + daily corpus
// refresh (design D2/D4, ADR-0043).
//
// Provisions the experience-hosting surface for Foundry IQ domain #1:
//   * User-Assigned MI            id-po-<suffix>         (single least-privilege identity)
//   * Container App (runtime)     ca-po-<suffix>         (the PO Agent orchestrator host)
//   * Container Apps Job          caj-po-refresh-<suffix> (Schedule trigger — daily corpus refresh)
//   * Cosmos DB (NoSQL)           cosmos-po-<suffix>     (append-only answer/audit store)
//   * Azure OpenAI                oai-po<suffix>         (chat deployment for the orchestrator)
//   * Key Vault                   kvpo<suffix>           (RBAC-only config vault; no secrets seeded here)
//
// HARD CONSTRAINT (design D5 parity + issue #377): the corpus refresh runs as an
// Azure Container Apps Job, NEVER a GitHub workflow. Its triggerType is `Schedule`
// (cron); an operator/orchestrator can still start it on demand via
// `az containerapp job start`.
//
// Everything is RBAC-only / keyless: Search local auth disabled (ai-search module),
// Cosmos + OpenAI + Key Vault `disableLocalAuth` / RBAC authorization. No secret
// ever crosses the module boundary. The MI principalId is exposed so the
// corpus-landing module grants it Storage Blob Data Contributor (wired in
// infra/main.bicep).

@description('Azure region for the runtime, job, Cosmos and Key Vault. PROD = switzerlandnorth (ADR-0037, NFR-POA-003); SIT = westus2 (ADR-0013).')
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
param containerAppEnvironmentName string = 'cae-po-${nameSuffix}'

@description('Optional Log Analytics workspace resource ID for the managed environment. Ignored when containerAppEnvironmentId is provided.')
param logAnalyticsWorkspaceResourceId string = ''

@description('Container image the runtime app + refresh job run. Defaults to a placeholder; the real PO Agent image is published by a follow-up CI workflow.')
param containerImage string = 'mcr.microsoft.com/dotnet/samples:aspnetapp'

@description('Optional ACR login server the runtime/job pull containerImage from. Set together with containerRegistryResourceId to wire MI-based pull (no admin creds, no secrets).')
param containerRegistryLoginServer string = ''

@description('Optional resource ID of the ACR that hosts containerImage. Required together with containerRegistryLoginServer.')
param containerRegistryResourceId string = ''

@description('Query endpoint of the Azure AI Search service (ai-search module output). Threaded to the runtime as SEARCH_ENDPOINT.')
param searchEndpoint string = ''

@description('Resource ID of the Azure AI Search service. When set, the runtime MI is granted Search Index Data Reader scoped to it. Empty string skips the grant.')
param searchServiceId string = ''

@description('Pinned data-plane Search REST api-version (ai-search module output). Threaded to the runtime as SEARCH_API_VERSION.')
param searchRestApiVersion string = '2024-05-01-preview'

@description('Name of the corpus landing storage account (corpus-landing module output). Threaded to the refresh job as CORPUS_STORAGE_ACCOUNT.')
param corpusStorageAccountName string = ''

@description('Landing container name inside the corpus storage account.')
param corpusContainerName string = 'landing'

@description('Root prefix inside the corpus container for product documents.')
param corpusPrefix string = 'curavias-product-corpus'

@description('Region for the Azure OpenAI account. Separated from `location` because MCAP OpenAI quota is region-constrained (ADR-0032); PROD pins switzerlandnorth per NFR-POA-003 once GA quota exists.')
param openAiLocation string = location

@description('Chat model deployment name the orchestrator calls.')
param openAiDeploymentName string = 'gpt-4o'

@description('Chat model name.')
param openAiModelName string = 'gpt-4o'

@description('Chat model version.')
param openAiModelVersion string = '2024-08-06'

@description('Provisioned throughput (TPM in thousands) for the chat deployment.')
@minValue(1)
@maxValue(300)
param openAiCapacity int = 10

@description('Cron expression for the daily corpus refresh job (UTC). Default 02:30 daily.')
param corpusRefreshCron string = '30 2 * * *'

@description('Replica timeout (seconds) for the refresh job execution.')
@minValue(60)
@maxValue(3600)
param replicaTimeoutSeconds int = 1800

@description('Resource ID of the Log Analytics workspace for diagnostic settings on Cosmos / Key Vault. Empty string skips diagnostics (SIT). Populated in PROD per copilot-instructions §3.')
param logAnalyticsWorkspaceId string = ''

@description('When true, the deployment is scoped to the demo path (synthetic data only, ADR-0013). Emits a demoScope tag for provenance.')
param demoScope bool = false

var effectiveTags = union(tags, {
  demoScope: demoScope ? 'true' : 'false'
})

// Names (length-checked against the tightest Azure limit for each resource type).
var openAiName = toLower('oai-po${replace(nameSuffix, '-', '')}')
var cosmosName = toLower('cosmos-po-${nameSuffix}')
var keyVaultName = toLower('kvpo${replace(nameSuffix, '-', '')}')
var runtimeAppName = 'ca-po-${nameSuffix}'
var refreshJobName = 'caj-po-refresh-${nameSuffix}'

// Built-in role IDs (verified against Azure RBAC docs).
var searchIndexDataReaderRoleId = '1407120a-92aa-4202-b7e9-c0e197c71c8f'
var cognitiveServicesOpenAiUserRoleId = '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
var keyVaultSecretsUserRoleId = '4633458b-17de-408a-b874-0445c86b69e6'
var acrPullRoleId = '7f951dda-4ed3-4680-a7ca-43fe172d538d'
// Cosmos DB built-in data-plane role: "Cosmos DB Built-in Data Contributor".
var cosmosDataContributorRoleId = '00000000-0000-0000-0000-000000000002'

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-po-${nameSuffix}'
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

// --- Azure OpenAI (chat deployment for the orchestrator) ---------------------
resource openai 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: openAiName
  location: openAiLocation
  tags: effectiveTags
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: openAiName
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: true
  }
}

resource chatDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: openai
  name: openAiDeploymentName
  sku: {
    name: 'Standard'
    capacity: openAiCapacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: openAiModelName
      version: openAiModelVersion
    }
  }
}

resource openAiUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(openai.id, identity.id, cognitiveServicesOpenAiUserRoleId)
  scope: openai
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesOpenAiUserRoleId)
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
    description: 'Sprint 28 WS-INF (#377) — PO Agent runtime MI calls the chat deployment (keyless).'
  }
}

// --- Cosmos DB (append-only answer/audit store) ------------------------------
resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: cosmosName
  location: location
  tags: effectiveTags
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    disableLocalAuth: true
    enableAutomaticFailover: false
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
  }
}

resource auditDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-05-15' = {
  parent: cosmos
  name: 'po-agent-audit'
  properties: {
    resource: {
      id: 'po-agent-audit'
    }
  }
}

resource answersContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = {
  parent: auditDatabase
  name: 'answers'
  properties: {
    resource: {
      id: 'answers'
      partitionKey: {
        paths: [
          '/classId'
        ]
        kind: 'Hash'
      }
    }
  }
}

resource cosmosDataRole 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2024-05-15' = {
  parent: cosmos
  name: guid(cosmos.id, identity.id, cosmosDataContributorRoleId)
  properties: {
    roleDefinitionId: '${cosmos.id}/sqlRoleDefinitions/${cosmosDataContributorRoleId}'
    principalId: identity.properties.principalId
    scope: cosmos.id
  }
}

// --- Key Vault (RBAC-only config vault; no secrets seeded in Bicep) -----------
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: effectiveTags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    publicNetworkAccess: 'Enabled'
  }
}

resource keyVaultSecretsUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, identity.id, keyVaultSecretsUserRoleId)
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', keyVaultSecretsUserRoleId)
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
    description: 'Sprint 28 WS-INF (#377) — PO Agent runtime MI reads config secrets (keyless auth).'
  }
}

// --- Azure AI Search Index Data Reader (scoped to the existing service) -------
resource existingSearch 'Microsoft.Search/searchServices@2024-06-01-preview' existing = if (!empty(searchServiceId)) {
  name: last(split(searchServiceId, '/'))
}

resource searchReaderRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(searchServiceId)) {
  name: guid(searchServiceId, identity.id, searchIndexDataReaderRoleId)
  scope: existingSearch
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', searchIndexDataReaderRoleId)
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
    description: 'Sprint 28 WS-INF (#377) — PO Agent runtime MI queries the corpus index (Class A retrieval, keyless).'
  }
}

// --- Runtime Container App (the PO Agent orchestrator host) -------------------
resource runtimeApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: runtimeAppName
  location: location
  tags: effectiveTags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identity.id}': {}
    }
  }
  properties: {
    environmentId: effectiveEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8080
        transport: 'auto'
        allowInsecure: false
      }
      registries: useAcrMiPull ? [
        {
          server: containerRegistryLoginServer
          identity: identity.id
        }
      ] : []
    }
    template: {
      containers: [
        {
          name: 'po-agent'
          image: containerImage
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            {
              name: 'AZURE_CLIENT_ID'
              value: identity.properties.clientId
            }
            {
              name: 'SEARCH_ENDPOINT'
              value: searchEndpoint
            }
            {
              name: 'SEARCH_API_VERSION'
              value: searchRestApiVersion
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: openai.properties.endpoint
            }
            {
              name: 'AZURE_OPENAI_DEPLOYMENT'
              value: openAiDeploymentName
            }
            {
              name: 'COSMOS_ENDPOINT'
              value: cosmos.properties.documentEndpoint
            }
            {
              name: 'KEY_VAULT_URI'
              value: keyVault.properties.vaultUri
            }
            {
              name: 'DEMO_SCOPE'
              value: demoScope ? 'true' : 'false'
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 2
      }
    }
  }
}

// --- Corpus refresh (Schedule-trigger Container Apps Job — NOT a workflow) ----
resource refreshJob 'Microsoft.App/jobs@2024-03-01' = {
  name: refreshJobName
  location: location
  tags: effectiveTags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identity.id}': {}
    }
  }
  properties: {
    environmentId: effectiveEnvironmentId
    configuration: {
      triggerType: 'Schedule'
      replicaTimeout: replicaTimeoutSeconds
      replicaRetryLimit: 1
      scheduleTriggerConfig: {
        cronExpression: corpusRefreshCron
        parallelism: 1
        replicaCompletionCount: 1
      }
      registries: useAcrMiPull ? [
        {
          server: containerRegistryLoginServer
          identity: identity.id
        }
      ] : []
    }
    template: {
      containers: [
        {
          name: 'po-corpus-refresh'
          image: containerImage
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          env: [
            {
              name: 'AZURE_CLIENT_ID'
              value: identity.properties.clientId
            }
            {
              name: 'CORPUS_STORAGE_ACCOUNT'
              value: corpusStorageAccountName
            }
            {
              name: 'CORPUS_CONTAINER'
              value: corpusContainerName
            }
            {
              name: 'CORPUS_PREFIX'
              value: corpusPrefix
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

// --- ACR pull (least privilege, scoped to the ACR) ---------------------------
resource acr 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' existing = if (useAcrMiPull) {
  name: last(split(containerRegistryResourceId, '/'))
}

resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (useAcrMiPull) {
  scope: acr
  name: guid(containerRegistryResourceId, identity.id, acrPullRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPullRoleId)
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
    description: 'Sprint 28 WS-INF (#377) — PO Agent runtime + refresh job pull containerImage from ACR.'
  }
}

// --- PROD-only diagnostics -> Log Analytics ----------------------------------
resource cosmosDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (!empty(logAnalyticsWorkspaceId)) {
  name: 'diag-${cosmosName}'
  scope: cosmos
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      {
        category: 'DataPlaneRequests'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'Requests'
        enabled: true
      }
    ]
  }
}

resource keyVaultDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (!empty(logAnalyticsWorkspaceId)) {
  name: 'diag-${keyVaultName}'
  scope: keyVault
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      {
        category: 'AuditEvent'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

@description('PO Agent runtime module implementation marker.')
output moduleStatus string = 'experience-hosting-po-agent-runtime-implemented'

@description('Principal ID of the PO Agent User-Assigned Managed Identity. Consumed by the corpus-landing module for the Storage Blob Data Contributor grant.')
output principalId string = identity.properties.principalId

@description('Client ID of the PO Agent User-Assigned Managed Identity. Passed to containers as AZURE_CLIENT_ID.')
output clientId string = identity.properties.clientId

@description('Resource ID of the PO Agent User-Assigned Managed Identity.')
output identityResourceId string = identity.id

@description('Name of the runtime Container App.')
output runtimeAppName string = runtimeApp.name

@description('Name of the scheduled corpus-refresh Container Apps Job.')
output refreshJobName string = refreshJob.name

@description('Azure OpenAI account endpoint.')
output openAiEndpoint string = openai.properties.endpoint

@description('Cosmos DB document endpoint.')
output cosmosEndpoint string = cosmos.properties.documentEndpoint

@description('Key Vault URI.')
output keyVaultUri string = keyVault.properties.vaultUri

@description('Resource ID of the managed environment used by the runtime app + refresh job.')
output managedEnvironmentId string = effectiveEnvironmentId
