using '../main.bicep'

// Sprint 19 (#239) — PROD greenfield rebuild in switzerlandnorth (ADR-0037).
//
// DR-style region pivot: after Phase 0 decommissions the eastus2/westus2 PROD
// footprint (rg-ihzhhpf-prod-eastus2 + fabricihzhhpfprod), PROD is rebuilt clean
// in a SINGLE region `switzerlandnorth`, in one resource group `rg-ihzhhpf-prod`,
// reusing the SIT-proven orchestrator infra/main.bicep (Option 1). This param
// mirrors the now-decommissioned prod-eastus2.bicepparam module selection with
// `location='switzerlandnorth'` and the ACR resourceId RG retargeted to the new
// single-region PROD RG.
//
// PROD is LEANER than SIT — the legacy App Service / ML-workspace topology
// (experience-hosting, api-runtime, ai-ml-foundation) is deliberately excluded.
//
// Swiss-region simplifications vs the US split (ADR-0037):
//   * Fabric co-locates in switzerlandnorth (quota 0/512) — no westus2 cross-
//     region hop. enableFabricFoundationModule stays a later-phase flip, same
//     phasing as eastus2.
//   * Fresh PROD-local ACR crihzhhpfprod created in switzerlandnorth (images
//     re-imported from the SIT ACR via `az acr import`); the name is reusable
//     because Phase 0 deletes the eastus2 crihzhhpfprod first.
//
// Baseline slice: foundation (identity + observability) + AI platform (Foundry
// account ai-ihzhhpf-prod) + compute (agent-host + app-fluent Container Apps,
// platform Cosmos) + P4 data lane (Event Hubs, Service Bus, CSA Cosmos). Later
// phases enable Fabric (P6, co-located), Foundry agents (P5, via the v2 /agents
// API), and DNS re-point of app.curavias.ch (P7) — all `approved-to-apply`-gated
// per the DR rebuild runbook.

param environmentName = 'prod'
param solutionShortName = 'ihzhhpf'
param location = 'switzerlandnorth'

param owner = 'platform-team'
param costCenter = 'ihzhhpf-prod'
param workload = 'hospital-capacity'

param logAnalyticsRetentionInDays = 90

// Key Vault name override — sidesteps a soft-delete + purge-protection name
// collision: the decommissioned westus2 rg-ihzhhpf-prod (same sub + same RG
// name) left kv-ihzhhpf-prod-i62t soft-deleted AND purge-protected until
// 2026-10-16, and the deterministic uniqueString(sub, rg.id) seed resolves to
// the identical `i62t` token. The name is globally reserved and cannot be
// purged early, so the greenfield rebuild uses an explicit distinct name.
// (EVH/SB namespaces reuse the same seed but have no soft-delete, so their
// names free up when the old RG is deleted — only the Key Vault collides.)
param keyVaultNameOverride = 'kv-ihzhhpf-prod-swn1'

// --- Foundation ---
param enableIdentityModule = true
// Network module ON (ADR-0038, extends ADR-0029 Option A + ADR-0037). Brings
// PROD to SIT network parity: creates vnet-platform-ihzhhpf-prod, VNet-integrates
// the agent-host CAE (cae-ihzhhpf-prod), and wires the Cosmos private endpoint.
// NOTE: VNet integration is immutable after CAE creation — because the swn
// rebuild already created cae-ihzhhpf-prod as a PUBLIC CAE, the gated deploy
// that flips this flag REQUIRES a one-time destructive delete + recreate of
// cae-ihzhhpf-prod (+ ca-agent-host + ca-signal-runner, ~5-10 min outage). The
// separate cae-app-fluent-ihzhhpf-prod (app.curavias.ch) is UNAFFECTED. The SIT
// pre-flight gotchas (Microsoft.App + Microsoft.ContainerService RP registration,
// AllowBringYourOwnPublicIpAddress feature, snet-cae delegation) are already
// handled by cd-infra-deploy-prod.yml + the network module.
param enableNetworkModule = true
param enableObservabilityModule = true

// Key Vault private endpoint (ADR-0038). Gives the AAD-only, policy-locked
// (publicNetworkAccess=Disabled) PROD vault a reachable data plane inside the
// VNet via privatelink.vaultcore.azure.net. Non-destructive on its own.
// Operator interactive access still needs an in-VNet jumpbox/Bastion.
param enableKeyVaultPrivateEndpoint = true

// Region-isolated VNet address space. PROD uses 10.70.0.0/16 to stay
// non-overlapping with SIT's 10.60.0.0/16 (same subscription, different RGs) so
// the two platform VNets could be peered in future without renumbering.
param networkVnetAddressPrefix = '10.70.0.0/16'
param networkAppSubnetPrefix = '10.70.1.0/24'
param networkDataSubnetPrefix = '10.70.2.0/24'
param networkCaeSubnetPrefix = '10.70.4.0/23'

// --- AI platform (Foundry account ai-ihzhhpf-prod in switzerlandnorth, GA) ---
param enableAiPlatformModule = true

// --- Container image registry (PROD-local ACR in switzerlandnorth) ---
// The shared Container App module references the registry BY NAME in the
// deployment RG, so a PROD-local ACR crihzhhpfprod holds the images (imported
// from the SIT ACR via `az acr import`). The agent-host + app-fluent modules
// consume these two params and grant their MIs AcrPull on this in-RG ACR.
param simCapacityContainerRegistryLoginServer = 'crihzhhpfprod.azurecr.io'
param simCapacityContainerRegistryResourceId = '/subscriptions/66a9953a-df37-4c51-856c-9971b9bf3e03/resourceGroups/rg-ihzhhpf-prod/providers/Microsoft.ContainerRegistry/registries/crihzhhpfprod'

// --- Compute: agent-host (Container App + Cosmos conversations/audit/approval-events) ---
param enableAgentHostModule = true
param agentHostImage = 'crihzhhpfprod.azurecr.io/hcc-agent-host:b796961'
// Redis: start with the in-memory grounding cache (proven in SIT per ADR-0028)
// to avoid a deploy-time AllocationFailed on an unverified swn Balanced SKU.
// Flip to true once the SKU is confirmed in switzerlandnorth (PROD hardening).
param agentHostEnableRedis = false
// PROD Fabric Data Agent is published in a later phase (P6). Empty keeps the
// agent-host synthetic fallback until the PROD swn workspace + Data Agent exist.
param fabricDataAgentEndpoint = ''
param fabricWorkspaceId = ''
param fabricDataAgentId = ''

// --- Compute: hcc-app-fluent (Container App) ---
param enableAppFluentModule = true
param appFluentImage = 'crihzhhpfprod.azurecr.io/hcc-app-fluent:b796961'
// app.curavias.ch is bound to the switzerlandnorth CA. The custom hostname +
// managed cert are codified here so CD redeploys preserve the binding (the
// manual P7 `hostname add/bind` would otherwise be stripped on every deploy).
// manageCuraviasDnsZone=false: the curavias.ch zone is SHARED and owned by SIT
// (rg-ihzhhpf-sit); PROD only claims the hostname on its CA and must NOT create
// a conflicting second zone. The `app` CNAME + `asuid.app` TXT records live in
// the SIT-owned zone (asuid is subscription-scoped, so it already validates).
param appFluentCustomHostname = 'app.curavias.ch'
param appFluentEnableCustomDomainCert = true
param manageCuraviasDnsZone = false

// --- P4 data lane — Event Hubs / Service Bus / CSA Cosmos ---
// EVH namespace + hub + consumer groups. Region-safe, public, self-contained.
param enableDataFoundationModule = true
param enableDataPlatformModule = false
// Sprint 19 follow-up — external-signals provider-runner (ca-signal-runner).
// Codified so it survives future CAE delete/recreate; adopts the live runner
// idempotently. Requires enableAgentHostModule + enableDataFoundationModule
// (both true above). Grants the runner MI EH Data Sender at the evh namespace.
param enableSignalRunnerModule = true
// CSA Cosmos DB wired into the orchestrator. With enableNetworkModule=true
// (ADR-0038) it now gets a private endpoint (privatelink.documents.azure.com in
// snet-data) — matching SIT and satisfying the MCAPSGov Modify-effect policy
// that force-disables public Cosmos subscription-wide. Creates
// cosmos-csa-ihzhhpf-prod + 4 vector containers.
param enableCsaCosmosModule = true
// P5 Foundry runtime agents — registered via the Sprint 18 v2 /agents API pattern
// against the PROD project, not Bicep. Stays off here.
param enableFoundryHostedAgents = false
// P6 Fabric F2 capacity + PROD workspace — co-located in switzerlandnorth
// (quota 0/512). Enabled in the P6 phase flip per the runbook.
param enableFabricFoundationModule = false
param enableFabricEventstreamModule = false
// sim-capacity needs an EH source and is region-locked to switzerlandnorth|westus2; defer.
param enableSimCapacityModule = false
// Legacy App Service / ML topology — excluded from PROD by design (design §7 v1.1.0).
param enableExperienceHostingModule = false
param enableApiRuntimeModule = false
param enableAiMlFoundationModule = false
// P4 Service Bus namespace (integration module). Region-safe, self-contained.
param enableIntegrationModule = true
param enableIntegrationOrchestrationModule = false
param enableSourceSqlModule = false
