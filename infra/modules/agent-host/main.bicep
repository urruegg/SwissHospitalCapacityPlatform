@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Container image reference for the agent-host (registry/repository:tag).')
param agentHostImage string

@description('Log Analytics workspace resource ID for the Container Apps environment. Keys are derived internally via reference()/listKeys() so no secret material crosses module boundaries.')
param logAnalyticsWorkspaceResourceId string

@description('Enable the Azure Managed Redis grounding cache (ADR-0007 §1). Default true for PROD; set to false in SIT per ADR-0028 (Managed Redis Balanced_B0 SKU is not offered in westus2 for the MCAPS demo subscription; the agent-host runtime already uses an in-memory cache so there is no functional loss for demo scope).')
param enableRedisModule bool = true

@description('Optional live Fabric Data Agent consumption endpoint. Empty string keeps the agent-host synthetic fallback.')
param fabricDataAgentEndpoint string = ''

@description('Optional Fabric workspace ID that hosts the live Fabric Data Agent. Empty string keeps the agent-host synthetic fallback.')
param fabricWorkspaceId string = ''

@description('Optional Fabric Data Agent ID. Empty string keeps the agent-host synthetic fallback.')
param fabricDataAgentId string = ''

@description('Optional ACR login server (e.g. cri75lbu5sj4hza.azurecr.io) for MI-based image pull. Required together with containerRegistryResourceId to enable Entra-MI-based pull once real images land in ACR.')
param containerRegistryLoginServer string = ''

@description('Optional ACR resource ID. Required together with containerRegistryLoginServer.')
param containerRegistryResourceId string = ''

@description('Optional CAE infrastructure subnet resource ID (ADR-0029 Option A). When set, the CAE joins that VNet subnet AND the Cosmos private-endpoint module is invoked (both parts of Option A are gated together — a PE without VNet integration is useless, and vice versa).')
param caeInfrastructureSubnetResourceId string = ''

@description('Optional VNet resource ID that hosts the CAE subnet + Cosmos private endpoint subnet. Required together with caeInfrastructureSubnetResourceId — used to locate the private-endpoint subnet in the same VNet.')
param vnetResourceId string = ''

@description('Name of the subnet (inside vnetResourceId) that hosts the Cosmos private endpoint. Defaults to snet-data — the same subnet used by the CSA cosmos private endpoint (ADR-0029 Option A precedent).')
param privateEndpointSubnetName string = 'snet-data'

// Sprint 13 T5 — Container Apps agent-host + optional Redis grounding cache + Cosmos DB
// (ADR-0007). This is a UC1-style output template; it is NOT deployed by this
// PR. Deployment requires the AGENTS.md §4 `approved-to-apply` gate.
//
// Redis conditionality (ADR-0028): the Managed Redis module is optional at SIT
// scope. When enableRedisModule=false the container-app module receives empty
// Redis coordinates and skips the REDIS_HOST/REDIS_PORT env vars. The Python
// agent-host code uses an in-memory grounding cache today (no live redis client
// wiring exists in apps/hcc-agent-host/src/cache/redis_client.py), so the
// runtime behaviour is identical for a single-replica demo.

module cosmos 'cosmos.bicep' = {
  name: 'agent-host-cosmos'
  params: {
    location: location
    nameSuffix: nameSuffix
    tags: tags
  }
}

// ADR-0029 Option A — Cosmos private endpoint in snet-data. Gated on the CAE
// VNet-integration parameter because a PE without a VNet-integrated CAE gives
// no reachability improvement (Container Apps would still use the public
// resolver). Both halves land in the same deploy.
var enableVnetIntegration = !empty(caeInfrastructureSubnetResourceId) && !empty(vnetResourceId)

module cosmosPrivateEndpoint 'cosmos-pe.bicep' = if (enableVnetIntegration) {
  name: 'agent-host-cosmos-pe'
  params: {
    location: location
    nameSuffix: nameSuffix
    tags: tags
    cosmosAccountResourceId: cosmos.outputs.cosmosAccountResourceId
    privateEndpointSubnetResourceId: '${vnetResourceId}/subnets/${privateEndpointSubnetName}'
  }
}

module redis 'redis.bicep' = if (enableRedisModule) {
  name: 'agent-host-redis'
  params: {
    location: location
    nameSuffix: nameSuffix
    tags: tags
  }
}

module containerApp 'container-app.bicep' = {
  name: 'agent-host-container-app'
  params: {
    location: location
    nameSuffix: nameSuffix
    tags: tags
    agentHostImage: agentHostImage
    logAnalyticsCustomerId: reference(logAnalyticsWorkspaceResourceId, '2023-09-01').customerId
    logAnalyticsSharedKey: listKeys(logAnalyticsWorkspaceResourceId, '2023-09-01').primarySharedKey
    cosmosEndpoint: cosmos.outputs.cosmosEndpoint
    fabricDataAgentEndpoint: fabricDataAgentEndpoint
    fabricWorkspaceId: fabricWorkspaceId
    fabricDataAgentId: fabricDataAgentId
    redisHostName: enableRedisModule ? redis!.outputs.redisHostName : ''
    redisPort: enableRedisModule ? redis!.outputs.redisPort : 0
    containerRegistryLoginServer: containerRegistryLoginServer
    containerRegistryResourceId: containerRegistryResourceId
    caeInfrastructureSubnetResourceId: caeInfrastructureSubnetResourceId
  }
}

// ADR-0029 Option A follow-up — Cosmos DB data-plane RBAC for the agent-host
// user-assigned managed identity. The Cosmos account has disableLocalAuth=true
// (no keys), so the CA can only reach data via this role. Mirrors the CSA
// Cosmos pattern (`infra/modules/cosmos/csa.bicep` §agentHostDataContributor).
// Role: `Cosmos DB Built-in Data Contributor` (built-in id
// 00000000-0000-0000-0000-000000000002) scoped to this account only.
resource agentHostCosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' existing = {
  name: 'cosmos-${nameSuffix}'
}

// The user-assigned MI is created inside container-app.bicep with a
// deterministic name — reference it here so we can read principalId
// at deploy-start (containerApp.outputs.principalId is only known at
// deploy-end, which fails the BCP120 constraint on `name`).
resource agentHostMi 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: 'id-ca-agent-host-${nameSuffix}'
}

var cosmosDataContributorRoleId = '00000000-0000-0000-0000-000000000002'

resource agentHostCosmosDataContributor 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2024-12-01-preview' = {
  parent: agentHostCosmosAccount
  name: guid(agentHostCosmosAccount.id, agentHostMi.id, cosmosDataContributorRoleId)
  properties: {
    roleDefinitionId: '${agentHostCosmosAccount.id}/sqlRoleDefinitions/${cosmosDataContributorRoleId}'
    principalId: agentHostMi.properties.principalId
    scope: agentHostCosmosAccount.id
  }
  dependsOn: [
    // Ensure both the cosmos account and the CA (which owns the MI) exist
    // before the sqlRoleAssignment tries to bind them.
    cosmos
    containerApp
  ]
}

output agentHostFqdn string = containerApp.outputs.fqdn
output cosmosAccountName string = cosmos.outputs.cosmosAccountName
// Exposed so the orchestrator can grant this MI Cosmos DB Built-in Data
// Contributor on the CSA Cosmos account (issue #252 Phase A) without an
// out-of-band role assignment.
output agentHostMiPrincipalId string = agentHostMi.properties.principalId
output redisName string = enableRedisModule ? redis!.outputs.redisName : ''
output redisEnabled bool = enableRedisModule
