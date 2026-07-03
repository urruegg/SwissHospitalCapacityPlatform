using '../main.bicep'

param environmentName = 'prod'
param solutionShortName = 'ihzhhpf'
param location = 'westus2'

param owner = 'platform-team'
param costCenter = 'ihzhhpf-prod'
param workload = 'hospital-capacity'

param logAnalyticsRetentionInDays = 180

param enableIdentityModule = true
param enableNetworkModule = true
param enableObservabilityModule = true
param enableDataPlatformModule = true
param enableAiPlatformModule = true
param enableIntegrationModule = true

param enableExperienceHostingModule = true
param enableApiRuntimeModule = true
param enableDataFoundationModule = true
param enableAiMlFoundationModule = true
param enableIntegrationOrchestrationModule = true

param networkVnetAddressPrefix = '10.60.0.0/16'
param networkAppSubnetPrefix = '10.60.1.0/24'

// Sprint 08 W1.1 — source-SQL submodule remains opt-out in PROD until approved.
param enableSourceSqlModule = false

// Sprint 08 W1.2 — Fabric foundation submodule remains opt-out in PROD until separately approved.
param enableFabricFoundationModule = false

// Sprint 09 v2.0.0 T2.2 — Fabric Eventstream module deferred in PROD until Sprint 09 promotes.
param enableFabricEventstreamModule = false
param fabricEventstreamWorkspaceId = ''
param fabricEventstreamDestinationLakehouseId = ''

// Sprint 09 v2.0.0 T2.1 — Event Hubs consumer group RBAC. MIs not provisioned in PROD yet.
param eventHubsSimulatorMiPrincipalId = ''
param eventHubsBmCopilotMiPrincipalId = ''
param eventHubsCsaAgentMiPrincipalId = ''
