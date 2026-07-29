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
// Network module ON (ADR-0039, extends ADR-0029 Option A + ADR-0037). Brings
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

// Key Vault private endpoint (ADR-0039). Gives the AAD-only, policy-locked
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
// Bumped b796961 -> f596cf2 to bring PROD to parity with SIT on the latest main
// agent-host build, which bakes in the Sprint 32 Signal Agent (SGA) pack
// (agents/signal-agent, runtime: agent-host — auto-discovered by the manifest
// loader). f596cf2 is a superset of b796961 (all prior agent-host code incl. the
// M5 Fabric Data Agent client + the #424 M2 golden service). Image imported into
// crihzhhpfprod via `az acr import` from the SIT ACR. Deploy approval-gated per
// AGENTS.md §4 (approved-to-apply by @urruegg 2026-07-28T12:28+02:00); see
// docs/sprints/sprint-32/signal-agent-sit-prod-parity.md for live /agents evidence.
// #424 M6 SIT+PROD parity (2026-07-29): bumped f596cf2 -> 62cc2ae (PR #522, M5
// OBO seam). 62cc2ae is a superset of f596cf2 (verified `git merge-base
// --is-ancestor`) so the Signal Agent pack + #424 M3/M4 seams are retained; OBO
// stays off (agentHostOboEnabled default false) and RLS stays simulated, so this
// is a behaviour-parity redeploy that lifts PROD from M2 to M5. Image imported
// into crihzhhpfprod via `az acr import` from the SIT ACR. approved-to-apply by
// @urruegg 2026-07-29.
param agentHostImage = 'crihzhhpfprod.azurecr.io/hcc-agent-host:62cc2ae'
// Redis: start with the in-memory grounding cache (proven in SIT per ADR-0028)
// to avoid a deploy-time AllocationFailed on an unverified swn Balanced SKU.
// Flip to true once the SKU is confirmed in switzerlandnorth (PROD hardening).
param agentHostEnableRedis = false
// PROD Fabric Data Agent (#477) — cloned from the SIT agent into the swn PROD
// workspace 1c8408f4, grounded on the capacity-dashboard + external-signals
// Direct Lake semantic models (ontology grounding deferred). Wiring these live
// switches the agent-host from synthetic fallback to live grounding.
param fabricDataAgentEndpoint = 'https://api.fabric.microsoft.com/v1/workspaces/1c8408f4-6eb7-401f-aee9-77fe4c8a515e/aiskills/39cb57b5-4bbf-4d64-af1c-7f0a81b0d570/aiassistant/openai'
param fabricWorkspaceId = '1c8408f4-6eb7-401f-aee9-77fe4c8a515e'
param fabricDataAgentId = '39cb57b5-4bbf-4d64-af1c-7f0a81b0d570'

// --- Compute: hcc-app-fluent (Container App) ---
param enableAppFluentModule = true
// Sprint 35 (#543) — Backstage restructure (feedback-loop default + 2-tab sub-nav,
// Story/Evidence/Roles removed). Bumped dadd7ce -> a7fb478 (PR #544 squash on main).
// Env-agnostic image (agent-host URL injected at runtime, #447); imported into
// crihzhhpfprod via `az acr import` from the SIT ACR. approved-to-apply by
// @urruegg 2026-07-29. Already live + verified in SIT on appsit.curavias.ch.
param appFluentImage = 'crihzhhpfprod.azurecr.io/hcc-app-fluent:a7fb478'
// #447 — runtime agent-host URL (per-env), injected into window.__ENV__ at
// container start so the PROD app calls the PROD (switzerlandnorth) agent-host
// instead of inheriting the SIT URL from the build-once + import image.
param appFluentAgentHostUrl = 'https://ca-agent-host-ihzhhpf-prod.whiteriver-d854b3bc.switzerlandnorth.azurecontainerapps.io'
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
// Sprint 19 SIT<->PROD data/AI/integration-lane parity (D8, ADR-0042) — rebuild phases P5 (Foundry agents) + P6 (Fabric); experience/API lane already live, reconciled separately.
param enableDataPlatformModule = true
// Sprint 19 follow-up — external-signals provider-runner (ca-signal-runner).
// Codified so it survives future CAE delete/recreate; adopts the live runner
// idempotently. Requires enableAgentHostModule + enableDataFoundationModule
// (both true above). Grants the runner MI EH Data Sender at the evh namespace.
param enableSignalRunnerModule = true
// CSA Cosmos DB wired into the orchestrator. With enableNetworkModule=true
// (ADR-0039) it now gets a private endpoint (privatelink.documents.azure.com in
// snet-data) — matching SIT and satisfying the MCAPSGov Modify-effect policy
// that force-disables public Cosmos subscription-wide. Creates
// cosmos-csa-ihzhhpf-prod + 4 vector containers.
param enableCsaCosmosModule = true
// P5 Foundry runtime agents — enabled for the D8 data/AI/integration parity plan.
param enableFoundryHostedAgents = true
param foundryHostedAgentsLocation = 'switzerlandnorth'
param foundryHostedAgentsEventHubNamespace = 'evh-ihzhhpf-prod-i62t'
param foundryHostedAgentsEventHubName = 'events'
param foundryHostedAgentsBmCopilotConsumerGroup = 'cg-bm-copilot-agent'
param foundryHostedAgentsCsaConsumerGroup = 'cg-csa-agent'
// P6 Fabric F2 capacity + PROD workspace — co-located in switzerlandnorth.
param enableFabricFoundationModule = true
param fabricCapacityAdmins = [
    'admin@mngenvmcap164444.onmicrosoft.com'
]
param enableFabricEventstreamModule = true
param fabricEventstreamWorkspaceId = ''
param fabricEventstreamDestinationLakehouseId = ''
param enableSkillsEventstreamModule = true
param skillsEventstreamWorkspaceId = ''
param skillsEventstreamDestinationLakehouseId = ''
// Sprint 23 WS-A4 (ADR-0043) — PROD swn runs the skills lane in EventHub source mode.
// Eventstream + Event Hubs are GA in Switzerland North, so this is a GA-in-region flip
// (not a preview exception); it auto-provisions the dedicated per-domain skills-events
// hub + cg-skills-eventstream consumer group via the data-foundation module. The live
// wiring still requires an out-of-band Fabric-managed connection (POST /v1/connections)
// before the post-deploy script can bind the source. Synthetic / no-PHI only (ADR-0013).
param skillsEventstreamSourceMode = 'EventHub'
param enableMasterdataLandingModule = true
param masterdataLandingPipelinePrincipalId = ''
param masterdataLandingLogAnalyticsWorkspaceId = ''
param enableSkillsSimJobsModule = true
// SIT-parity: SIT uses the public placeholder (real skills-sim image deferred to
// issue #181); PROD mirrors SIT exactly so both bump together when #181 lands.
param skillsSimJobsImage = 'mcr.microsoft.com/dotnet/samples:aspnetapp'

// Sprint 28 WS-INF (#377) — Curavias Product Owner Agent (Foundry IQ domain #1).
// PROD swn variant: enabled at switzerlandnorth (ADR-0037 / NFR-POA-003) for the
// SIT-parity demo scope. poAgentLocation is declared here (see the NOTE block on
// shared declarations below). Runtime + refresh-job image mirrors SIT until the
// PO Agent CI workflow publishes a real image.
param poAgentLocation = 'switzerlandnorth'
param enablePoAgentSearchModule = true
param enablePoAgentKnowledgeBaseModule = true
param enablePoAgentCorpusLandingModule = true
param enablePoAgentRuntimeModule = true
param poAgentContainerImage = 'mcr.microsoft.com/dotnet/samples:aspnetapp'
param poAgentLogAnalyticsWorkspaceId = ''
// sim-capacity resolves the PROD Event Hub namespace from dataFoundation output.
param enableSimCapacityModule = true
param simCapacityLocation = 'switzerlandnorth'
param simCapacityContainerImage = 'crihzhhpfprod.azurecr.io/sim-capacity:sprint10-t1'
param simCapacityEventHubNamespace = ''
param simCapacityEventHubName = 'events'
param simCapacityDemoScope = true
// Grant the sim-capacity MI (id-ca-sim-capacity-ihzhhpf-prod, principalId below)
// Azure Event Hubs Data Sender on evh-ihzhhpf-prod-i62t/events so the live
// simulator can publish. SIT leaves this empty (latent gap — sim-capacity MI has
// no EH role in SIT either); PROD codifies it (drift-free, PROD-exceeds-SIT).
// Backport to SIT tracked separately. dataFoundation consumes this (main.bicep).
param eventHubsSimulatorMiPrincipalId = '7fa4687e-5c76-4154-a493-ad53f7647d45'
// Legacy App Service / API topology already live; leave off in this data/AI/integration slice.
param enableExperienceHostingModule = false
param enableApiRuntimeModule = false
param enableAiMlFoundationModule = true
// P4 Service Bus namespace (integration module). Region-safe, self-contained.
param enableIntegrationModule = true
param enableIntegrationOrchestrationModule = true
param enableSourceSqlModule = false

// --- Sprint 23 (#255) — Curavias org/skills refactor: SIT→PROD parity ---
// Brings PROD to SIT parity for the org/skills medallion landing surface
// (ADR-0039). Mirrors sit.bicepparam module selection:
//   * masterdata-landing (WS-A1): ADLS Gen2 `stmasterdataihzhhpfprod` + `landing`
//     container + OneLake-shortcut runbook. Region-safe, self-contained.
//   * skills-sim-jobs (WS-A3): manual-trigger Container Apps Jobs writing synthetic
//     extracts to the landing zone via a UAMI; creates its OWN CAE
//     (cae-skills-sim-ihzhhpf-prod), so it does NOT depend on the lean-PROD
//     experience-hosting exclusion. Placeholder public image (same as SIT) — no
//     PROD ACR image dependency.
//   * skills-eventstream (WS-A4): scaffold-only Bicep; requires the EH source
//     (enableDataFoundationModule=true above). Fabric destination IDs stay empty
//     (mirrors SIT) — the Eventstream destination is wired post-deploy via REST
//     once the PROD Fabric workspace/lakehouse are published (P6).
// Single-region PROD: pin the skills-sim CAE to switzerlandnorth (SIT uses westus2).
// NOTE: enableMasterdataLandingModule, enableSkillsSimJobsModule,
// enableSkillsEventstreamModule, and simCapacityLocation are already declared
// above with these same PROD-parity values — they are NOT re-declared here
// (a .bicepparam identifier may be assigned only once; duplicates raise BCP028).
