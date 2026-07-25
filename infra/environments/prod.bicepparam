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

// Sprint 09 v2.0.0 T4.5 — Foundry-hosted runtime agents.
// Deferred in PROD until Fabric IQ reaches Swiss GA and the ADR-0013 westus2
// demo scope is retired. Keep values documented so the flip is a param-only
// change when PROD readiness gates pass.
param enableFoundryHostedAgents = false
param foundryHostedAgentsLocation = 'westus2'
param foundryHostedAgentsEventHubNamespace = 'evh-ihzhhpf-prod'
param foundryHostedAgentsEventHubName = 'evh-capacity-events-prod'
param foundryHostedAgentsBmCopilotConsumerGroup = 'cg-bm-copilot-agent'
param foundryHostedAgentsCsaConsumerGroup = 'cg-csa-agent'

// Sprint 09 v2 T3.7 — sim-capacity ACA producer remains opt-out in PROD until Sprint 09 promotes it.
param enableSimCapacityModule = false

// Sprint 09 v2.0.0 T2.2 — Fabric Eventstream module deferred in PROD until Sprint 09 promotes.
param enableFabricEventstreamModule = false
param fabricEventstreamWorkspaceId = ''
param fabricEventstreamDestinationLakehouseId = ''

// Sprint 23 WS-A4 (#255) — Skills-events Eventstream lane deferred in PROD until promotion.
param enableSkillsEventstreamModule = false
param skillsEventstreamWorkspaceId = ''
param skillsEventstreamDestinationLakehouseId = ''

// Sprint 09 v2.0.0 T2.1 — Event Hubs consumer group RBAC. MIs not provisioned in PROD yet.
param eventHubsSimulatorMiPrincipalId = ''
param eventHubsBmCopilotMiPrincipalId = ''
param eventHubsCsaAgentMiPrincipalId = ''

// Sprint 23 WS-A1 (#255) — ADLS Gen2 landing zone for Curavias org/skills master data.
// Opt-out in PROD until the demo scope is retired and PROD ingestion is approved.
// When PROD comes online: flip enable to true, set the pipeline MI principal ID, and
// wire masterdataLandingLogAnalyticsWorkspaceId to the PROD Log Analytics workspace so
// blob StorageWrite/StorageDelete diagnostics are captured (copilot-instructions §3).
param enableMasterdataLandingModule = false
param masterdataLandingPipelinePrincipalId = ''
param masterdataLandingLogAnalyticsWorkspaceId = ''

// Sprint 23 WS-A3 (#255) — Container Apps Jobs for the skills-evidence simulators.
// Opt-out in PROD until the demo scope is retired and PROD ingestion is approved.
param enableSkillsSimJobsModule = false
param skillsSimJobsImage = 'mcr.microsoft.com/dotnet/samples:aspnetapp'

// Sprint 28 WS-INF (#377) — Curavias Product Owner Agent (Foundry IQ domain #1).
// Opt-out in PROD until the demo scope is retired and PROD onboarding is approved.
// When PROD comes online: flip enables to true, pin poAgentLocation to
// switzerlandnorth (NFR-POA-003), and wire poAgentLogAnalyticsWorkspaceId to the
// PROD Log Analytics workspace so Search/Cosmos/Key Vault diagnostics are captured.
param poAgentLocation = 'switzerlandnorth'
param enablePoAgentSearchModule = false
param enablePoAgentKnowledgeBaseModule = false
param enablePoAgentCorpusLandingModule = false
param enablePoAgentRuntimeModule = false
param poAgentContainerImage = 'mcr.microsoft.com/dotnet/samples:aspnetapp'
param poAgentLogAnalyticsWorkspaceId = ''

// Sprint 13.1 T-DNS (ADR-0030) - dormant in PROD until PROD RG is provisioned + PROD deploy is approved.
// When PROD comes online, this env must be refactored to use an existing reference on the
// SIT-owned curavias.ch zone (or the zone moved to a shared RG) - see docs/adr/0030-*.md follow-ups.
param appFluentCustomHostname = 'app.curavias.ch'
param appFluentEnableCustomDomainCert = false

// Sprint 24 (ADR-0030) — Curavias product landing page (Astro) hosting, PROD-only.
// Two-step custom-domain binding: keep curaviasWebEnableCustomDomains=false on the first
// apply (creates the Static Web App + media storage), add the DNS records + GoDaddy
// delegation, then flip to true so the SWA validates curavias.ch + www.curavias.ch.
param enableCuraviasWebModule = true
param curaviasWebMediaPublisherPrincipalId = ''
param curaviasWebEnableCustomDomains = false
