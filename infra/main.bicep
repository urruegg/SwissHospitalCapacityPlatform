targetScope = 'resourceGroup'

// No-op change for workflow gate dry-run validation.

@description('Deployment environment name.')
@allowed([
  'dev'
  'sit'
  'prod'
])
param environmentName string

@description('Solution short name used in Azure resource names.')
param solutionShortName string = 'ihzhhpf'

@description('Location for all resources. Defaults to resource group location.')
param location string = resourceGroup().location

@description('Owner tag value.')
param owner string = 'platform-team'

@description('Cost center tag value.')
param costCenter string = 'tbd'

@description('Workload tag value.')
param workload string = 'hospital-capacity'

@description('Optional Log Analytics retention in days.')
@minValue(30)
@maxValue(730)
param logAnalyticsRetentionInDays int = 90

@description('Enable identity module deployment scaffold.')
param enableIdentityModule bool = false

@description('Enable network module deployment scaffold.')
param enableNetworkModule bool = false

@description('Address prefix for the platform virtual network.')
param networkVnetAddressPrefix string = '10.60.0.0/16'

@description('Address prefix for the platform application subnet.')
param networkAppSubnetPrefix string = '10.60.1.0/24'

@description('Address prefix for the platform data subnet (private endpoints).')
param networkDataSubnetPrefix string = '10.60.2.0/24'

@description('Enable observability module deployment scaffold.')
param enableObservabilityModule bool = false

@description('Enable data platform module deployment scaffold.')
param enableDataPlatformModule bool = false

@description('Enable the source-SQL submodule inside data-platform (Sprint 08 W1.1 synthetic KIS feed).')
param enableSourceSqlModule bool = false

@description('Resource ID of the data subnet used for the source-SQL private endpoint. Required when enableSourceSqlModule = true.')
param sourceSqlDataSubnetId string = ''

@description('Resource ID of the Key Vault that stores the source-SQL admin password. Required when enableSourceSqlModule = true.')
param sourceSqlKeyVaultId string = ''

@description('Name of the Key Vault secret holding the source-SQL admin password. Required when enableSourceSqlModule = true.')
param sourceSqlAdminPasswordSecretName string = ''

@description('Optional. Resource ID of the existing privatelink.database.windows.net private DNS zone for the source-SQL private endpoint. Leave empty to wire DNS externally.')
param sourceSqlPrivateDnsZoneId string = ''

@description('Entra ID login (UPN or group displayName) of the source-SQL AAD admin. Required by tenant AAD-only auth policy when enableSourceSqlModule = true.')
param sourceSqlAadAdminLogin string = ''

@description('Object ID (SID) of the source-SQL AAD admin principal. Required when enableSourceSqlModule = true.')
param sourceSqlAadAdminObjectId string = ''

@description('Principal type of the source-SQL AAD admin.')
@allowed([
  'User'
  'Group'
  'ServicePrincipal'
])
param sourceSqlAadAdminPrincipalType string = 'User'

@description('Enable Fabric foundation submodule (capacity + post-deploy workspace/lakehouse/mirror).')
param enableFabricFoundationModule bool = false

@description('Object ID(s) of Fabric capacity administrators. Required when enableFabricFoundationModule = true.')
param fabricCapacityAdmins array = []

@description('Enable Fabric Eventstream module (Sprint 09 v2.0.0 T2.2). Requires enableDataFoundationModule=true (event hub source) and enableDataPlatformModule + enableFabricFoundationModule (workspace/lakehouse destination). Scaffold-only Bicep + REST-API post-deploy; see modules/data-platform/fabric-eventstream/README.md.')
param enableFabricEventstreamModule bool = false

@description('Fabric workspace ID that hosts the Eventstream. Required when enableFabricEventstreamModule=true. Obtain via configure-fabric.ps1 post-deploy output.')
param fabricEventstreamWorkspaceId string = ''

@description('Optional Fabric Lakehouse ID for the Eventstream destination. Empty defers destination wiring (Eventstream created source-only). Optional at Bicep composition time; required at post-deploy time for full wiring.')
param fabricEventstreamDestinationLakehouseId string = ''

@description('Enable AI platform module deployment scaffold.')
param enableAiPlatformModule bool = false

@description('Enable integration module deployment scaffold.')
param enableIntegrationModule bool = false

@description('Enable experience hosting foundation module deployment.')
param enableExperienceHostingModule bool = false

@description('Enable API runtime foundation module deployment.')
param enableApiRuntimeModule bool = false

@description('Enable data foundation module deployment.')
param enableDataFoundationModule bool = false

@description('Object ID of the simulator managed identity that publishes to Event Hubs (Sprint 09 v2.0.0 T2.1/T3.7). Empty = role assignment skipped.')
param eventHubsSimulatorMiPrincipalId string = ''

@description('Object ID of the BM-Copilot managed identity that reads from cg-bm-copilot-agent (Sprint 09 v2.0.0 T2.1/T4.5). Empty = role assignment skipped.')
param eventHubsBmCopilotMiPrincipalId string = ''

@description('Object ID of the CSA (Capacity Simulation Agent) managed identity that reads from cg-csa-agent (Sprint 09 v2.0.0 T2.1/T4.5). Empty = role assignment skipped.')
param eventHubsCsaAgentMiPrincipalId string = ''

@description('Enable AI/ML foundation module deployment.')
param enableAiMlFoundationModule bool = false

@description('Enable integration orchestration foundation module deployment.')
param enableIntegrationOrchestrationModule bool = false

@description('Enable Foundry-hosted runtime agents module (BM-Copilot + CSA UAMIs + RBAC). Sprint 09 v2.0.0 T4.5.')
param enableFoundryHostedAgents bool = false

@description('Location for the Foundry-hosted agents UAMIs. Must match the Foundry account region — westus2 for the demo scope per ADR-0013.')
@allowed([
  'switzerlandnorth'
  'westus2'
])
param foundryHostedAgentsLocation string = 'westus2'

@description('Event Hub namespace name that BM-Copilot/CSA MIs receive from. Placeholder wiring while T2 (data-foundation Event Hubs) lives on a separate branch.')
param foundryHostedAgentsEventHubNamespace string = ''

@description('Event Hub name that BM-Copilot/CSA MIs receive from. Placeholder wiring while T2 (data-foundation Event Hubs) lives on a separate branch.')
param foundryHostedAgentsEventHubName string = ''

@description('Consumer group name for BM-Copilot.')
param foundryHostedAgentsBmCopilotConsumerGroup string = 'cg-bm-copilot-agent'

@description('Consumer group name for CSA.')
param foundryHostedAgentsCsaConsumerGroup string = 'cg-csa-agent'

@description('Enable the sim-capacity ACA module (Sprint 09 v2 T3.7). Default true in SIT, false in PROD.')
param enableSimCapacityModule bool = false

@description('Region for the sim-capacity ACA module. Pinned to the ADR-0013 demo-scope variant path.')
@allowed([
  'switzerlandnorth'
  'westus2'
])
param simCapacityLocation string = 'westus2'

@description('Container image the sim-capacity Container App runs. Placeholder until the sim-capacity image is published.')
param simCapacityContainerImage string = 'mcr.microsoft.com/dotnet/samples:aspnetapp'

@description('Optional ACR login server (e.g. \'cri75lbu5sj4hza.azurecr.io\') for pulling simCapacityContainerImage. Together with simCapacityContainerRegistryResourceId enables MI-based pull (no admin creds).')
param simCapacityContainerRegistryLoginServer string = ''

@description('Optional resource ID of the ACR that hosts simCapacityContainerImage. Required together with simCapacityContainerRegistryLoginServer.')
param simCapacityContainerRegistryResourceId string = ''

@description('Event Hub namespace the sim-capacity producer emits to. When empty and enableDataFoundationModule=true, the sim-capacity module is skipped (no namespace to target).')
param simCapacityEventHubNamespace string = ''

@description('Event Hub entity name the sim-capacity producer emits to.')
param simCapacityEventHubName string = 'demand-encounters'

@description('When true, the sim-capacity deployment is scoped to the Sprint 09 v2 demo path (synthetic data only per ADR-0013 / ADR-0016).')
param simCapacityDemoScope bool = true

// Sprint 13 T5 — Container Apps agent-host (loads BMCA/OOA/DCA/ORSA/SBA/CSA/data-quality
// manifests at startup). Deploys Container App + Cosmos (conversations/audit/approval-events
// per ADR-0007) + Redis (grounding cache).
@description('Enable the Sprint 13 agent-host module (Container App + Cosmos + Redis per ADR-0007).')
param enableAgentHostModule bool = false

@description('Container image reference for the agent-host (registry/repository:tag). Placeholder matches sim-capacity pattern until agent-host CI pushes real images to ACR.')
param agentHostImage string = 'mcr.microsoft.com/dotnet/samples:aspnetapp'

// Sprint 13 T1 — Fluent baseline Container App (React/Vite bundle served via nginx on 8080).
@description('Enable the Sprint 13 hcc-app-fluent Container App module.')
param enableAppFluentModule bool = false

@description('Container image reference for the hcc-app-fluent (registry/repository:tag). Placeholder until app-build.yml pushes real images to ACR.')
param appFluentImage string = 'nginxinc/nginx-unprivileged:1.27-alpine'

var envSuffix = environmentName == 'dev' ? '' : '-${environmentName}'
var resourceSuffix = '${solutionShortName}${envSuffix}'

var tags = {
  env: environmentName
  owner: owner
  costCenter: costCenter
  workload: workload
}

module platformFoundation './modules/platform-foundation/main.bicep' = {
  name: 'platform-foundation-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
    logAnalyticsRetentionInDays: logAnalyticsRetentionInDays
  }
}

module identity './modules/identity/main.bicep' = if (enableIdentityModule) {
  name: 'identity-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
  }
}

module network './modules/network/main.bicep' = if (enableNetworkModule) {
  name: 'network-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
    vnetAddressPrefix: networkVnetAddressPrefix
    appSubnetPrefix: networkAppSubnetPrefix
    dataSubnetPrefix: networkDataSubnetPrefix
  }
}

module observability './modules/observability/main.bicep' = if (enableObservabilityModule) {
  name: 'observability-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
  }
}

module dataPlatform './modules/data-platform/main.bicep' = if (enableDataPlatformModule) {
  name: 'data-platform-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
    enableSourceSqlModule: enableSourceSqlModule
    // Auto-wire from network module output when the caller passes empty; otherwise honour the explicit param.
    sourceSqlDataSubnetId: !empty(sourceSqlDataSubnetId) ? sourceSqlDataSubnetId : (enableNetworkModule ? network.outputs.dataSubnetResourceId : '')
    // Auto-wire from platform-foundation module (always deployed) when the caller passes empty.
    sourceSqlKeyVaultId: !empty(sourceSqlKeyVaultId) ? sourceSqlKeyVaultId : resourceId('Microsoft.KeyVault/vaults', platformFoundation.outputs.keyVaultName)
    sourceSqlAdminPasswordSecretName: sourceSqlAdminPasswordSecretName
    sourceSqlPrivateDnsZoneId: sourceSqlPrivateDnsZoneId
    sourceSqlAadAdminLogin: sourceSqlAadAdminLogin
    sourceSqlAadAdminObjectId: sourceSqlAadAdminObjectId
    sourceSqlAadAdminPrincipalType: sourceSqlAadAdminPrincipalType
    enableFabricFoundationModule: enableFabricFoundationModule
    fabricCapacityAdmins: fabricCapacityAdmins
  }
}

module aiPlatform './modules/ai-platform/main.bicep' = if (enableAiPlatformModule) {
  name: 'ai-platform-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
  }
}

module integration './modules/integration/main.bicep' = if (enableIntegrationModule) {
  name: 'integration-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
  }
}

module experienceHosting './modules/experience-hosting/main.bicep' = if (enableExperienceHostingModule) {
  name: 'experience-hosting-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
  }
}

module apiRuntime './modules/api-runtime/main.bicep' = if (enableApiRuntimeModule) {
  name: 'api-runtime-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
  }
}

module dataFoundation './modules/data-foundation/main.bicep' = if (enableDataFoundationModule) {
  name: 'data-foundation-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
    simulatorMiPrincipalId: eventHubsSimulatorMiPrincipalId
    bmCopilotMiPrincipalId: eventHubsBmCopilotMiPrincipalId
    csaAgentMiPrincipalId: eventHubsCsaAgentMiPrincipalId
  }
}

module aiMlFoundation './modules/ai-ml-foundation/main.bicep' = if (enableAiMlFoundationModule) {
  name: 'ai-ml-foundation-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
  }
}

module integrationOrchestration './modules/integration-orchestration/main.bicep' = if (enableIntegrationOrchestrationModule) {
  name: 'integration-orchestration-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
  }
}

// Sprint 09 v2.0.0 T4.5 — Foundry-hosted runtime agents (BM-Copilot + CSA).
// Attaches Managed Identities + RBAC to the already-provisioned Foundry
// resource `ai-<solutionShortName>-<env>`. Does NOT create the Foundry
// resource itself (owned by ai-platform/main.bicep).
module foundryHostedAgents './modules/agents/foundry-hosted/main.bicep' = if (enableFoundryHostedAgents) {
  name: 'foundry-hosted-agents-${environmentName}'
  params: {
    location: foundryHostedAgentsLocation
    environment: environmentName
    solutionShortName: solutionShortName
    eventHubNamespaceName: foundryHostedAgentsEventHubNamespace
    eventHubName: foundryHostedAgentsEventHubName
    bmCopilotConsumerGroup: foundryHostedAgentsBmCopilotConsumerGroup
    csaConsumerGroup: foundryHostedAgentsCsaConsumerGroup
    tags: tags
  }
}

// Sprint 09 v2 — T3.7: sim-capacity ACA producer. Only deploys when a target Event Hub namespace is known
// (either passed explicitly via simCapacityEventHubNamespace or produced by the data-foundation module).
var simCapacityHasEhSource = !empty(simCapacityEventHubNamespace) || enableDataFoundationModule
var resolvedSimEventHubNamespace = !empty(simCapacityEventHubNamespace)
  ? simCapacityEventHubNamespace
  : (enableDataFoundationModule ? dataFoundation!.outputs.eventHubNamespaceName : '')

module simCapacity './modules/apps/sim-capacity/main.bicep' = if (enableSimCapacityModule && simCapacityHasEhSource) {
  name: 'sim-capacity-${environmentName}'
  params: {
    location: simCapacityLocation
    containerAppName: 'ca-sim-capacity-${resourceSuffix}'
    containerAppEnvironmentName: 'cae-sim-${resourceSuffix}'
    logAnalyticsWorkspaceResourceId: resourceId('Microsoft.OperationalInsights/workspaces', platformFoundation.outputs.logAnalyticsWorkspaceName)
    containerImage: simCapacityContainerImage
    containerRegistryLoginServer: simCapacityContainerRegistryLoginServer
    containerRegistryResourceId: simCapacityContainerRegistryResourceId
    eventHubNamespace: resolvedSimEventHubNamespace
    eventHubName: simCapacityEventHubName
    demoScope: simCapacityDemoScope
    tags: tags
  }
}

// Sprint 13 T5 — Container Apps agent-host + Cosmos (conversations/audit/approval-events)
// + Redis (grounding cache) per ADR-0007. Agent-host image lands via agent-host-build.yml
// once CI push is wired; deploys with placeholder image today (parity with sim-capacity pattern).
// Log Analytics resourceId passed in; module derives customerId/sharedKey internally via
// reference()/listKeys() — same pattern as sim-capacity, no keys crossing module boundaries.
module agentHost './modules/agent-host/main.bicep' = if (enableAgentHostModule) {
  name: 'agent-host-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
    agentHostImage: agentHostImage
    logAnalyticsWorkspaceResourceId: resourceId('Microsoft.OperationalInsights/workspaces', platformFoundation.outputs.logAnalyticsWorkspaceName)
  }
}

// Sprint 13 T1 — Fluent baseline Container App (React/Vite bundle behind nginx on 8080).
// Same reasoning as agent-host for the Log Analytics wiring.
module appFluent './modules/apps/hcc-app-fluent/main.bicep' = if (enableAppFluentModule) {
  name: 'app-fluent-${environmentName}'
  params: {
    location: location
    nameSuffix: resourceSuffix
    tags: tags
    appImage: appFluentImage
    logAnalyticsWorkspaceResourceId: resourceId('Microsoft.OperationalInsights/workspaces', platformFoundation.outputs.logAnalyticsWorkspaceName)
  }
}

// Sprint 09 v2.0.0 T2.2 — Fabric Eventstream scaffold. See modules/data-platform/fabric-eventstream/README.md.
// Region is constrained to switzerlandnorth | westus2 to keep Bicep type-safe; falls back to westus2 for the
// ADR-0013 demo-scope carve-out when the RG location is something else.
module fabricEventstream './modules/data-platform/fabric-eventstream/main.bicep' = if (enableFabricEventstreamModule) {
  name: 'fabric-eventstream-${environmentName}'
  params: {
    workspaceId: fabricEventstreamWorkspaceId
    eventHubNamespace: enableDataFoundationModule ? dataFoundation!.outputs.eventHubNamespaceEndpoint : ''
    eventHubName: enableDataFoundationModule ? dataFoundation!.outputs.eventHubName : ''
    eventHubConsumerGroup: 'cg-fabric-eventstream'
    location: location == 'switzerlandnorth' ? 'switzerlandnorth' : 'westus2'
    demoScope: location != 'switzerlandnorth'
    destinationLakehouseId: fabricEventstreamDestinationLakehouseId
  }
}

output keyVaultName string = platformFoundation.outputs.keyVaultName
output logAnalyticsWorkspaceName string = platformFoundation.outputs.logAnalyticsWorkspaceName
output sourceSqlGatingWarning string = enableSourceSqlModule && !enableDataPlatformModule
  ? 'WARN: enableSourceSqlModule=true requires enableDataPlatformModule=true; source-sql module will NOT deploy.'
  : 'ok'
output fabricFoundationGatingWarning string = enableFabricFoundationModule && !enableDataPlatformModule
  ? 'WARN: enableFabricFoundationModule=true requires enableDataPlatformModule=true; fabric module will NOT deploy.'
  : (enableFabricFoundationModule && empty(fabricCapacityAdmins))
    ? 'WARN: enableFabricFoundationModule=true but fabricCapacityAdmins is empty; deploy will fail.'
    : 'ok'
output fabricEventstreamGatingWarning string = enableFabricEventstreamModule && !enableDataFoundationModule
  ? 'WARN: enableFabricEventstreamModule=true requires enableDataFoundationModule=true; Eventstream module will fail.'
  : (enableFabricEventstreamModule && empty(fabricEventstreamWorkspaceId))
    ? 'WARN: enableFabricEventstreamModule=true but fabricEventstreamWorkspaceId is empty; provide the workspace GUID from configure-fabric.ps1 output.'
    : (enableFabricEventstreamModule && empty(fabricEventstreamDestinationLakehouseId))
      ? 'INFO: fabricEventstreamDestinationLakehouseId empty — Eventstream will be created source-only. Wire lakehouseId post-deploy.'
      : 'ok'
output moduleStatuses object = {
  identity: enableIdentityModule ? identity!.outputs.moduleStatus : 'identity-disabled'
  network: enableNetworkModule ? network!.outputs.moduleStatus : 'network-disabled'
  observability: enableObservabilityModule ? observability!.outputs.moduleStatus : 'observability-disabled'
  dataPlatform: enableDataPlatformModule ? dataPlatform!.outputs.moduleStatus : 'data-platform-disabled'
  sourceSql: enableDataPlatformModule ? dataPlatform!.outputs.sourceSqlStatus : 'source-sql-disabled'
  aiPlatform: enableAiPlatformModule ? aiPlatform!.outputs.moduleStatus : 'ai-platform-disabled'
  integration: enableIntegrationModule ? integration!.outputs.moduleStatus : 'integration-disabled'
  experienceHosting: enableExperienceHostingModule ? experienceHosting!.outputs.moduleStatus : 'experience-hosting-disabled'
  apiRuntime: enableApiRuntimeModule ? apiRuntime!.outputs.moduleStatus : 'api-runtime-disabled'
  dataFoundation: enableDataFoundationModule ? dataFoundation!.outputs.moduleStatus : 'data-foundation-disabled'
  aiMlFoundation: enableAiMlFoundationModule ? aiMlFoundation!.outputs.moduleStatus : 'ai-ml-foundation-disabled'
  integrationOrchestration: enableIntegrationOrchestrationModule ? integrationOrchestration!.outputs.moduleStatus : 'integration-orchestration-disabled'
  fabricEventstream: enableFabricEventstreamModule ? fabricEventstream!.outputs.moduleStatus : 'fabric-eventstream-disabled'
}

output foundryHostedAgentsStatus string = enableFoundryHostedAgents ? foundryHostedAgents!.outputs.moduleStatus : 'foundry-hosted-agents-disabled'
output bmCopilotPrincipalId string = enableFoundryHostedAgents ? foundryHostedAgents!.outputs.bmCopilotPrincipalId : ''
output bmCopilotClientId string = enableFoundryHostedAgents ? foundryHostedAgents!.outputs.bmCopilotClientId : ''
output csaPrincipalId string = enableFoundryHostedAgents ? foundryHostedAgents!.outputs.csaPrincipalId : ''
output csaClientId string = enableFoundryHostedAgents ? foundryHostedAgents!.outputs.csaClientId : ''

// Exposed for T2.1 EH module wiring — read by the parent deployment to feed Azure Event Hubs Data Sender RBAC.
output simCapacityPrincipalId string = (enableSimCapacityModule && simCapacityHasEhSource)
  ? simCapacity!.outputs.principalId
  : ''
output simCapacityStatus string = enableSimCapacityModule
  ? (!simCapacityHasEhSource
      ? 'WARN: enableSimCapacityModule=true but no Event Hub namespace resolved (set simCapacityEventHubNamespace or enable data-foundation module).'
      : simCapacity!.outputs.moduleStatus)
  : 'sim-capacity-disabled'
