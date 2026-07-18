using '../main.bicep'

// Sprint 19 (#239) — Full PROD deployment in eastus2, region-isolated.
// Option 1 (design §7 v1.1.0): reuse the SIT-proven orchestrator infra/main.bicep
// via this PROD param file instead of a fresh module tree. PROD is LEANER than
// SIT — the legacy App Service / ML-workspace topology (experience-hosting,
// api-runtime, ai-ml-foundation) is deliberately excluded. The abandoned westus2
// rg-ihzhhpf-prod was decommissioned 2026-07-19 (approved-to-apply @urruegg) so
// PROD is fixed to eastus2.
//
// This is the FIRST SLICE: foundation (identity + network + observability) +
// AI platform (Foundry account) + compute (agent-host + app-fluent Container
// Apps, Cosmos). Later phases enable Fabric (P6), Event Hubs/Service Bus (P4),
// Foundry agents (P5), and DNS cutover (P7).

param environmentName = 'prod'
param solutionShortName = 'ihzhhpf'
param location = 'eastus2'

param owner = 'platform-team'
param costCenter = 'ihzhhpf-prod'
param workload = 'hospital-capacity'

param logAnalyticsRetentionInDays = 90

// --- Foundation ---
param enableIdentityModule = true
param enableNetworkModule = true
param enableObservabilityModule = true

// Region-isolated VNet. Same private address space as SIT is fine — it is a
// separate VNet in a separate region/RG with no peering.
param networkVnetAddressPrefix = '10.60.0.0/16'
param networkAppSubnetPrefix = '10.60.1.0/24'
param networkDataSubnetPrefix = '10.60.2.0/24'

// --- AI platform (Foundry account ai-ihzhhpf-prod in eastus2) ---
param enableAiPlatformModule = true

// --- Container image registry (cross-region pull from the SIT ACR) ---
// User decision 2026-07-19: reuse the existing SIT ACR for the first deploy;
// defer a dedicated PROD ACR. The agent-host + app-fluent modules consume these
// two params (they share the sim-capacity registry inputs) and grant their MIs
// AcrPull on the SIT ACR (cross-RG role assignment; GH OIDC principal is
// Contributor on rg-ihzhhpf-sit).
param simCapacityContainerRegistryLoginServer = 'cri75lbu5sj4hza.azurecr.io'
param simCapacityContainerRegistryResourceId = '/subscriptions/66a9953a-df37-4c51-856c-9971b9bf3e03/resourceGroups/rg-ihzhhpf-sit/providers/Microsoft.ContainerRegistry/registries/cri75lbu5sj4hza'

// --- Compute: agent-host (Container App + Cosmos conversations/audit/approval-events) ---
param enableAgentHostModule = true
param agentHostImage = 'cri75lbu5sj4hza.azurecr.io/hcc-agent-host:b796961'
// Redis: the Managed Redis Balanced SKU availability in eastus2 is unverified.
// Start with the in-memory grounding cache (proven in SIT per ADR-0028) to avoid
// a deploy-time AllocationFailed. Flip to true once the SKU is confirmed in
// eastus2 (PROD hardening, ADR-0007 intent).
param agentHostEnableRedis = false
// PROD Fabric Data Agent is not published yet (P6). Empty keeps the agent-host
// synthetic fallback until the PROD workspace + Data Agent exist.
param fabricDataAgentEndpoint = ''
param fabricWorkspaceId = ''
param fabricDataAgentId = ''

// --- Compute: hcc-app-fluent (Container App) ---
param enableAppFluentModule = true
param appFluentImage = 'cri75lbu5sj4hza.azurecr.io/hcc-app-fluent:b796961'
// DNS cutover (app.curavias.ch) is P7. Empty custom hostname is REQUIRED here to
// avoid creating a SECOND curavias.ch DNS zone — the zone already exists in
// rg-ihzhhpf-sit. P7 binds app.curavias.ch to the PROD CA against the existing zone.
param appFluentCustomHostname = ''
param appFluentEnableCustomDomainCert = false

// --- Deferred to later Sprint 19 phases (explicit for intent) ---
// P4 data lane — Event Hubs / Service Bus / data-foundation
param enableDataFoundationModule = false
param enableDataPlatformModule = false
// P5 Foundry runtime agents — registered via the Sprint 18 API pattern against the
// PROD project (the foundry-hosted module is region-locked to switzerlandnorth|westus2).
param enableFoundryHostedAgents = false
// P6 Fabric F2 capacity + PROD workspace
param enableFabricFoundationModule = false
param enableFabricEventstreamModule = false
// sim-capacity is region-locked to switzerlandnorth|westus2 and needs an EH source; defer.
param enableSimCapacityModule = false
// Legacy App Service / ML topology — excluded from PROD by design (spec §7 v1.1.0).
param enableExperienceHostingModule = false
param enableApiRuntimeModule = false
param enableAiMlFoundationModule = false
param enableIntegrationModule = false
param enableIntegrationOrchestrationModule = false
param enableSourceSqlModule = false
