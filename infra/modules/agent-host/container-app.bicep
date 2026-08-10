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

@description('Optional live Fabric Data Agent consumption endpoint. Empty string keeps the agent-host synthetic fallback.')
param fabricDataAgentEndpoint string = ''

@description('Optional Fabric workspace ID that hosts the live Fabric Data Agent. Empty string keeps the agent-host synthetic fallback.')
param fabricWorkspaceId string = ''

@description('Optional Fabric Data Agent ID. Empty string keeps the agent-host synthetic fallback.')
param fabricDataAgentId string = ''

@description('Sprint 43 WS-1 -- Foundry Agent Service project account root (e.g. https://ai-ihzhhpf-sit-eastus2.services.ai.azure.com). Empty string keeps the agent-host on the deterministic MockChatModel.')
param foundryProjectEndpoint string = ''

@description('Sprint 43 WS-1 -- Foundry Agent Service project name (e.g. ai-ihzhhpf-sit-eastus2-project). Empty string keeps the agent-host on the deterministic MockChatModel.')
param foundryProjectName string = ''

@description('Sprint 43 WS-2 -- Fabric lakehouse ID for direct OneLake Gold table reads (reuses fabricWorkspaceId for the workspace half). Empty string keeps FabricAdapter on its synthetic 3-row fallback.')
param fabricLakehouseId string = ''

@description('#424 M4 — RLS provider for the structured golden read. `simulated` (default) filters synthetic rows in-process (provenance simulated). `fabric-data-agent` reuses the proven live Fabric Data Agent client but still refuses per-user structured scope until OBO + the dynamic-RLS TMDL predicate land (#424 M5, #510). Config, not code.')
param rlsProvider string = 'simulated'

@description('#424 M5 — enable the OBO ingress seam (`false` default = simulated/native parity with M4). `true` requires a valid caller bearer on the golden read and exchanges it downstream. See ADR-0057. Config, not code.')
param oboEnabled bool = false

@description('Sprint 43 WS-6 — tenant ID for the OBO On-Behalf-Of exchange (agent-host confidential client).')
param oboTenantId string = ''

@description('Sprint 43 WS-6 — client ID of the hcc-agent-host app registration used for the OBO exchange.')
param oboClientId string = ''

@description('Sprint 43 WS-6 — Key Vault secret URI for the agent-host app registration client secret.')
@secure()
param oboClientSecret string = ''

@description('Sprint 43 WS-6 — JWKS URL used to validate the caller bearer (tenant discovery keys endpoint).')
param oboJwksUrl string = ''

@description('Sprint 43 WS-6 — expected audience on the caller bearer token (api://<agent-host-app-id>).')
param oboAudience string = ''

@description('Sprint 43 WS-6 — expected issuer on the caller bearer token.')
param oboIssuer string = ''

@description('Sprint 43 WS-6 — downstream scope for the OBO exchange. auth/obo_context.py defaults this to https://api.fabric.microsoft.com/.default, which does NOT work for OneLake reads (validated live, 401) -- FabricDeltaClient needs a storage.azure.com-scoped token instead.')
param oboFabricScope string = 'https://storage.azure.com/.default'

@description('Sprint 43 WS-6 follow-up — JSON object mapping Entra security-group object IDs (from the hcc-agent-host `groupMembershipClaims` = SecurityGroup `groups` claim) to HCC.* role names. App Role ASSIGNMENT requires a directory role admin@ does not hold (ADR-0057 §1.3); `groupMembershipClaims` is owner-level/self-service and reflects group memberships that already exist. Empty string (default) disables group-derived roles -- only a direct `roles` claim (if ever populated) is honoured. Config, not code; non-secret directory metadata (like oboTenantId/oboClientId above).')
param oboGroupRoleMap string = ''

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

@description('Optional CAE infrastructure subnet resource ID (ADR-0029 Option A). When set, the CAE joins that subnet — Container Apps traffic then reaches Cosmos DB via its private endpoint. Empty string keeps the CAE public (default). Setting this on an EXISTING CAE forces a destructive recreate; the child Container Apps get a new FQDN.')
param caeInfrastructureSubnetResourceId string = ''

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
    // Pin DefaultAzureCredential to the agent-host user-assigned MI so token
    // acquisition (e.g. the live Fabric Data Agent call, M5/ADR-0033) resolves
    // deterministically. Without this the SDK cannot pick among user-assigned
    // identities and fails with "Unable to load the proper Managed Identity".
    name: 'AZURE_CLIENT_ID'
    value: agentHostIdentity.properties.clientId
  }
  {
    name: 'AGENTS_ROOT'
    value: '/app/agents'
  }
  {
    name: 'FABRIC_DATA_AGENT_ENDPOINT'
    value: fabricDataAgentEndpoint
  }
  {
    name: 'FABRIC_WORKSPACE_ID'
    value: fabricWorkspaceId
  }
  {
    name: 'FABRIC_DATA_AGENT_ID'
    value: fabricDataAgentId
  }
  {
    name: 'FOUNDRY_PROJECT_ENDPOINT'
    value: foundryProjectEndpoint
  }
  {
    name: 'FOUNDRY_PROJECT_NAME'
    value: foundryProjectName
  }
  {
    name: 'FABRIC_LAKEHOUSE_ID'
    value: fabricLakehouseId
  }
  {
    name: 'RLS_PROVIDER'
    value: rlsProvider
  }
  {
    name: 'OBO_ENABLED'
    value: oboEnabled ? 'true' : 'false'
  }
  {
    name: 'OBO_TENANT_ID'
    value: oboTenantId
  }
  {
    name: 'OBO_CLIENT_ID'
    value: oboClientId
  }
  {
    name: 'OBO_JWKS_URL'
    value: oboJwksUrl
  }
  {
    name: 'OBO_AUDIENCE'
    value: oboAudience
  }
  {
    name: 'OBO_ISSUER'
    value: oboIssuer
  }
  {
    name: 'OBO_FABRIC_SCOPE'
    value: oboFabricScope
  }
  {
    name: 'OBO_GROUP_ROLE_MAP'
    value: oboGroupRoleMap
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

// Sprint 43 WS-6 — conditional, like redisEnv above: an empty oboClientSecret
// (OBO disabled, or the Key Vault secret not yet resolved) must not produce a
// Container App secret with an empty value -- ARM rejects that outright
// ("value or keyVaultUrl and identity should be provided"), found live
// 2026-08-09 while reverting agentHostOboEnabled back to false.
var oboSecretEnv = !empty(oboClientSecret) ? [
  {
    name: 'OBO_CLIENT_SECRET'
    secretRef: 'obo-client-secret'
  }
] : []

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
    // ADR-0029 Option A — join the delegated `snet-cae` subnet so this CAE
    // (and every Container App it hosts) can egress via the platform VNet and
    // resolve Cosmos DB through its private endpoint. `internal: false`
    // preserves external HTTPS ingress on `*.<default-domain>.azurecontainerapps.io`.
    // Empty caeInfrastructureSubnetResourceId keeps legacy public behaviour.
    vnetConfiguration: empty(caeInfrastructureSubnetResourceId) ? null : {
      infrastructureSubnetId: caeInfrastructureSubnetResourceId
      internal: false
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
      // Sprint 43 WS-6 — OBO client secret, referenced by the container env
      // entry below via secretRef (never a plain env var value). Conditional:
      // an empty oboClientSecret must produce an empty secrets array, not a
      // secret with an empty value (ARM rejects that).
      secrets: !empty(oboClientSecret) ? [
        {
          name: 'obo-client-secret'
          value: oboClientSecret
        }
      ] : []
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
          env: concat(baseEnv, redisEnv, oboSecretEnv)
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

output managedEnvironmentId string = managedEnvironment.id
output fqdn string = agentHost.properties.configuration.ingress.fqdn
output principalId string = agentHostIdentity.properties.principalId
output identityResourceId string = agentHostIdentity.id
output identityClientId string = agentHostIdentity.properties.clientId
