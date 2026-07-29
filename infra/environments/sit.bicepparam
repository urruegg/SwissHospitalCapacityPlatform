using '../main.bicep'

param environmentName = 'sit'
param solutionShortName = 'ihzhhpf'
param location = 'westus2'

param owner = 'platform-team'
param costCenter = 'ihzhhpf-sit'
param workload = 'hospital-capacity'

param logAnalyticsRetentionInDays = 90

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

// Sprint 08 W1.1 / Sprint 00 Slice 2 — source-SQL submodule (synthetic KIS feed).
// TEMPORARILY DISABLED for the Sprint 00 demo scope: MCAPS sandbox subscription
// 66a9953a-... is blocked from provisioning Azure SQL Database in westus2 (and most
// other regions except centralus, francecentral, germanywestcentral, japaneast).
// Deferring source-SQL until either (a) support ticket lifts the restriction, or
// (b) we accept a cross-region SQL deployment. All the underlying Bicep improvements
// (network snet-data subnet, auto-wiring, SQL uniqueString suffix, AAD-only auth block,
// KV enabledForTemplateDeployment) remain in place and are ready when this flips to true.
param enableSourceSqlModule = false
param sourceSqlDataSubnetId = ''
param sourceSqlKeyVaultId = ''
param sourceSqlAdminPasswordSecretName = 'sql-admin-password'
param sourceSqlAadAdminLogin = 'admin@mngenvmcap164444.onmicrosoft.com'
param sourceSqlAadAdminObjectId = '7b9830a6-989b-4edd-b720-0d4bff7ffb2e'
param sourceSqlAadAdminPrincipalType = 'User'

// Private DNS zone for SQL private endpoint. Owned by a separate platform-foundation slice
// (hub-spoke DNS). Leave empty here and wire post-deploy; do not invent a resource ID.
param sourceSqlPrivateDnsZoneId = ''

// Sprint 08 W1.2 / Sprint 00 Slice 1 — Fabric foundation submodule (F2 capacity + workspace/lakehouse/mirror).
// Enabled for the Sprint 00 demo scope on the new tenant per ADR-0013.
// Capacity admin is the operator's Entra UPN (email) in the new tenant.
// NB: Fabric API rejects object IDs here — must be UPN (email format).
param enableFabricFoundationModule = true
param fabricCapacityAdmins = [
    'admin@mngenvmcap164444.onmicrosoft.com'
]

// Sprint 09 v2.0.0 T4.5 — Foundry-hosted runtime agents (BM-Copilot + CSA).
// Attaches Managed Identities + RBAC to the already-provisioned Foundry
// resource `ai-ihzhhpf-sit` in westus2 per ADR-0013.
//
// Event Hub namespace + hub names updated 2026-07-07 per S10.15 root-cause
// investigation. Previous placeholder values (`evh-ihzhhpf-sit` /
// `evh-capacity-events-sit`) did not match the actual deployed resources
// (the eventhubs module uses `uniqueString(sub, RG.id)` for the namespace
// name and default `events` for the hub inside). Wiring via module output
// (recommended long-term) requires a `main.bicep` refactor to conditionally
// resolve the namespace name from the `data-foundation` module output when
// `enableDataFoundationModule=true` — deferred to a future PR.
param enableFoundryHostedAgents = true
param foundryHostedAgentsLocation = 'westus2'
param foundryHostedAgentsEventHubNamespace = 'evh-ihzhhpf-sit-y26y'
param foundryHostedAgentsEventHubName = 'events'
param foundryHostedAgentsBmCopilotConsumerGroup = 'cg-bm-copilot-agent'
param foundryHostedAgentsCsaConsumerGroup = 'cg-csa-agent'

// Sprint 09 v2 T3.7 — sim-capacity ACA producer. Enabled in SIT for the demo path.
// Sprint 10 T1 (ADR-0019): producer retargeted from Azure EH `evh-ihzhhpf-sit-y26y` /
// `demand-encounters` to the Fabric Eventstream Custom Endpoint. The MCAPS tenant Modify
// policy keeps `disableLocalAuth=true` on Azure EH namespaces, and Fabric's Azure EH
// source connector only supports SAS today — so ingest via that path is impossible.
// Values below come from workspace f3af9733-9503-4e92-98f9-a901d96f1c87 →
// eventstream 7b65dfa1-c523-412f-93b2-a78eaa2788fa → source `capacity-events-source`.
// Producer identity: id-ca-sim-capacity-ihzhhpf-sit (Entra objectId
// b646f093-cbbc-496f-8a65-376b39ff04d3), Contributor on the workspace.
param enableSimCapacityModule = true
param simCapacityLocation = 'westus2'
param simCapacityContainerImage = 'cri75lbu5sj4hza.azurecr.io/sim-capacity:sprint10-t1'
param simCapacityContainerRegistryLoginServer = 'cri75lbu5sj4hza.azurecr.io'
param simCapacityContainerRegistryResourceId = '/subscriptions/66a9953a-df37-4c51-856c-9971b9bf3e03/resourceGroups/rg-ihzhhpf-sit/providers/Microsoft.ContainerRegistry/registries/cri75lbu5sj4hza'
param simCapacityEventHubNamespace = 'esehmwhyivddgq8acv3ghwv.servicebus.windows.net'
param simCapacityEventHubName = 'esehmwhyivddgq8acv3ghwv_eh'
param simCapacityDemoScope = true

// Sprint 09 v2.0.0 T2.2 — Fabric Eventstream module (scaffold-only Bicep + REST-API post-deploy).
// Enabled in SIT per design spec §4.2 (EH → Eventstream → bronze/eventstream/).
// workspaceId and destinationLakehouseId are populated post-deploy from configure-fabric.ps1
// outputs; leave empty until Sprint 09 T2 execution wires them.
param enableFabricEventstreamModule = true
param fabricEventstreamWorkspaceId = ''
param fabricEventstreamDestinationLakehouseId = ''

// Sprint 23 WS-A4 (#255) — Skills-events Eventstream lane (design D4, scaffold-only Bicep +
// REST-API post-deploy). Enabled in SIT; carries only the three near-real-time skills events.
// workspaceId/destinationLakehouseId populated post-deploy from configure-fabric.ps1 output.
param enableSkillsEventstreamModule = true
param skillsEventstreamWorkspaceId = ''
param skillsEventstreamDestinationLakehouseId = ''
// Design D4 demo-scope (ADR-0013): CustomEndpoint source mirrors the working
// es-capacity-events-sit lane and is fully live-deployable via the post-deploy REST
// script. EventHub is the Swiss-GA target-state (needs a Fabric-managed connection).
param skillsEventstreamSourceMode = 'CustomEndpoint'

// Sprint 09 v2.0.0 T2.1 — Event Hubs consumer group RBAC.
// Simulator MI (T3.7) and agent MIs (T4.5) don't exist yet; leaving empty means the three
// role assignments are conditionally skipped. Populate as those Sprint 09 v2.0.0 tasks land.
param eventHubsSimulatorMiPrincipalId = ''
param eventHubsBmCopilotMiPrincipalId = ''
param eventHubsCsaAgentMiPrincipalId = ''

// Sprint 23 WS-A1 (#255) — ADLS Gen2 landing zone for Curavias org/skills master data.
// Enabled in SIT for the demo scope (synthetic, no-PHI extracts per D5). The pipeline
// managed identity is created by WS-A3 (Container Apps Jobs); until then the principal
// ID is empty so the role assignment is conditionally skipped. Blob diagnostics stay
// off in SIT (populated in PROD).
param enableMasterdataLandingModule = true
param masterdataLandingPipelinePrincipalId = ''
param masterdataLandingLogAnalyticsWorkspaceId = ''

// Sprint 23 WS-A3 (#255) — Container Apps Jobs for the skills-evidence simulators.
// Enabled in SIT for the demo scope. Four manual-trigger jobs seed synthetic
// extracts into the WS-A1 landing zone via their MI (granted Storage Blob Data
// Contributor by the landing module). Image is a placeholder until the skills-sim
// CI workflow publishes a real one (parity with sim-capacity). NEVER triggered by
// a GitHub workflow — on-demand `az containerapp job start` only.
param enableSkillsSimJobsModule = true
param skillsSimJobsImage = 'mcr.microsoft.com/dotnet/samples:aspnetapp'

// Sprint 28 WS-INF (#377) — Curavias Product Owner Agent (Foundry IQ domain #1).
// Enabled in SIT for the demo scope (synthetic, no-PHI corpus per D2). Region
// pinned to westus2 (ADR-0013); diagnostics stay off in SIT (populated in PROD).
// Runtime + refresh-job image is a placeholder until the PO Agent CI workflow
// publishes a real one. The corpus refresh runs as a scheduled Container Apps
// Job — NEVER a GitHub workflow.
param poAgentLocation = 'westus2'
// SIT infra is westus2 but Azure OpenAI has no quota there — pin the PO Agent
// OpenAI account to eastus2 (ADR-0013 demo cross-region / ADR-0032). Fixes the
// SpecialFeatureOrQuotaIdRequired SIT what-if failure introduced by #384.
param poAgentOpenAiLocation = 'eastus2'
param enablePoAgentSearchModule = true
param enablePoAgentKnowledgeBaseModule = true
param enablePoAgentCorpusLandingModule = true
// RE-ENABLED (2026-07-26): the historical block was the runtime module defaulting
// to gpt-4o/Standard (ServiceModelDeprecating on every SIT what-if, #384). That is
// fixed — the module now defaults to gpt-5 / 2025-08-07 / GlobalStandard
// (po-agent-runtime openAiModelName/openAiSkuName), the same wiring that deploys
// cleanly in PROD (live oai-poihzhhpfprod runs gpt-5 GlobalStandard). eastus2 quota
// OpenAI.GlobalStandard.gpt-5 is 110/1000 used, so the cap-10 SIT deployment fits.
param enablePoAgentRuntimeModule = true
param poAgentContainerImage = 'mcr.microsoft.com/dotnet/samples:aspnetapp'
param poAgentLogAnalyticsWorkspaceId = ''
// Enabled here to close Sprint 13 DoD S13.3 + S13.7 + S13.8 (see the
// 2026-07-10 sprint-review checklist). Image is a placeholder — matches
// sim-capacity pattern — until agent-host-build.yml is extended to push
// the real image to ACR (follow-up gap-fill after Sprint 13.1 issue #181).
param enableAgentHostModule = true
// Issue #252 Phase A — CSA Cosmos DB now wired into the orchestrator (was a
// standalone deploy). `true` here adopts the already-deployed
// `cosmos-csa-ihzhhpf-sit` (+ private endpoint, network on) idempotently; the
// what-if must show no changes to the account, containers, or role assignment.
param enableCsaCosmosModule = true
// Bumped 3433f72 -> 478b115 to ship the M5 live Fabric Data Agent client
// (real OpenAI-Assistants flow, ADR-0033 Option A); ci-build-agent-host.yml
// pushed the tag. Deploy is approval-gated per AGENTS.md §4 (approved-to-apply
// by @urruegg 2026-07-18).
// Bumped b796961 -> f596cf2 to ship #424 M2: the agent-host GET /golden/{resource}
// RLS-scoped live golden-source read surface (PR #476 merge to main). f596cf2 is a
// superset of b796961 (all prior agent-host code incl. the M5 Fabric Data Agent
// client + the new golden service). Deploy approval-gated per AGENTS.md §4
// (approved-to-apply by @urruegg 2026-07-28T10:47+02:00).
// Bumped f596cf2 -> dadd7ce to ship #424 M3: the agent-host ThreadProvider seam +
// POST /agents/{name}/threads mint endpoint + thread-scoped /chat (PR #495 merge to
// main). dadd7ce is a superset of f596cf2 (all prior agent-host code incl. the M2
// golden service + M5 Fabric Data Agent client). Deploy approval-gated per AGENTS.md
// §4 (approved-to-apply by @urruegg 2026-07-28).
// Bumped dadd7ce -> 583f633 to ship #424 M4: the agent-host RlsProvider seam
// (evidence-grounded capability ladder — SimulatedRlsProvider default +
// FabricDataAgentRlsProvider Rung 1) + the new /golden/network resource + _rls
// block + X-Rls-* headers (PR #512 merge to main). 583f633 is a superset of
// dadd7ce. SIT keeps the default RLS_PROVIDER=simulated (agentHostRlsProvider
// param default). Deploy approval-gated per AGENTS.md §4 (approved-to-apply by
// @urruegg 2026-07-28).
// #424 M6 parity (2026-07-29): bumped 583f633 -> 62cc2ae (PR #522, M5 OBO
// seam). 62cc2ae is a superset of 583f633; OBO stays off (agentHostOboEnabled
// default false) so this is a behaviour-parity redeploy. Matches PROD per M6
// SIT+PROD parity. approved-to-apply by @urruegg 2026-07-29.
param agentHostImage = 'cri75lbu5sj4hza.azurecr.io/hcc-agent-host:62cc2ae'

// Sprint 26 WS-C (#335) — enable the decision-tier live-apply Container Apps
// Job (caj-decision-apply) in SIT. Manual-trigger, plan-first by default
// (AGENTS.md §4); a live apply swaps the job template command via
// `az containerapp job update --yaml` (job start --command/--args overrides are
// ignored here) with --approved-to-apply per docs/runbooks/decision-tier-live-apply.md.
// The Job is pinned to the decision-CLI-enabled image :a071fbe (built by
// ci-build-agent-host on the #417 merge — the Foundry Agent Service /agents API
// fix; superseded :2b83a49, which 401'd on the wrong Assistants API) WITHOUT
// bumping agentHostImage, so the running agent-host Container App stays on
// b796961 (Option B, low blast radius).
param enableDecisionApplyJobModule = true
param decisionApplyJobImage = 'cri75lbu5sj4hza.azurecr.io/hcc-agent-host:a071fbe'

// ADR-0028: skip Azure Managed Redis in SIT demo scope.
// Root cause: the Managed Redis `Balanced_B0` SKU is not offered in `westus2`
// for our MCAPS demo subscription (verified 2026-07-13 via the provider SKU
// catalog: only Enterprise_E1..E400 and EnterpriseFlash_F300..F1500 are
// available). The agent-host runtime (apps/hcc-agent-host/src/cache/redis_client.py)
// already uses an in-memory grounding cache — no live Redis client is wired
// — so the deploy loses nothing functionally for demo scope.
// Reversibility: flip to `true` when PROD is provisioned in a region that
// offers Balanced_B0 (or when a follow-up PR migrates the SKU to Enterprise_E1).
param agentHostEnableRedis = false
// M5 (ADR-0033 Option A): live Fabric Data Agent grounding for the agent-host.
// Live SIT artefacts in workspace f3af9733 (westus2) — see
// docs/architecture/fabric-iq-ready-evidence.md. Endpoint is the published Data
// Agent OpenAI-Assistants surface; the agent-host MI must hold workspace Viewer.
param fabricDataAgentEndpoint = 'https://api.fabric.microsoft.com/v1/workspaces/f3af9733-9503-4e92-98f9-a901d96f1c87/aiskills/b2e53c23-182a-452d-9321-e63f6009e80b/aiassistant/openai'
param fabricWorkspaceId = 'f3af9733-9503-4e92-98f9-a901d96f1c87'
param fabricDataAgentId = 'b2e53c23-182a-452d-9321-e63f6009e80b'

// Sprint 13 T1 — hcc-app-fluent Container App (React/Vite bundle behind nginx:8080).
// Enabled here to close Sprint 13 DoD S13.2 (see the 2026-07-10 sprint-review
// checklist). Image tag is bumped as a deliberate manual review step after
// `ci-build-app-fluent.yml` pushes a new tag to ACR (per that workflow's
// header comment + AGENTS.md §4). Bumped b796961 -> 43ace03 to ship Epic #276
// (Curavias app prototype-parity, Sprints 1-6: dca/bmca/orsa/sba/csa RoleBoards,
// golden-thread ring, START role launcher, BACKSTAGE story tab, Helvion->Curavias
// title rebrand) from the #297 consolidation merge commit 43ace03.
// Bumped 43ace03 -> cb21e2c to ship Sprint 20 OOA (occupancy) screen parity
// (PR #313, digest sha256:107137a07f48105e35922c43370e1d38dd65938716b72f0371b6350c6fcc4f2b).
// Bumped ff3dd76 -> bd1fa7e to ship #424 M2 (live golden-source read path): the app
// now reads live board payloads from GET <GOLDEN_SOURCE_URL>/{resource} when Live is
// toggled. bd1fa7e = PR #480 merge (M2 app code from #476 + the app-only Docker build
// fix). Deploy approval-gated per AGENTS.md §4 (approved-to-apply by @urruegg
// 2026-07-28T10:47+02:00).
param enableAppFluentModule = true
// Bumped bd1fa7e -> dadd7ce to ship #424 M3 (live per-agent thread minting): the app
// now mints a real per-(user x agent) thread via the agent-host (POST /threads) and
// threads it onto every chat turn when FOUNDRY_THREADS_ENABLED is on. dadd7ce = PR
// #495 merge (M3 app code). Deploy approval-gated per AGENTS.md §4 (approved-to-apply
// by @urruegg 2026-07-28).
param appFluentImage = 'cri75lbu5sj4hza.azurecr.io/hcc-app-fluent:a7fb478'
// #447 — runtime agent-host URL (per-env), injected into window.__ENV__ at
// container start so the SIT app calls the SIT agent-host (no build-time bake).
param appFluentAgentHostUrl = 'https://ca-agent-host-ihzhhpf-sit.salmonsand-fb86922a.westus2.azurecontainerapps.io'
// #424 M2 — golden-source URL. Left unset so the module auto-derives
// `${appFluentAgentHostUrl}/golden` (Option 1: the agent-host serves the RLS-scoped
// golden surface). Set explicitly only for a future divergent (Fabric-backed) source.
// #424 M3 — enable the live per-(user x agent) thread minter in SIT. The app mints a
// real thread via the SIT agent-host (POST /threads) and threads it onto every chat
// turn; provider stays native (no OBO) until M5. westus2 synthetic/no-PHI scope
// (ADR-0013). Deploy approval-gated per AGENTS.md §4.
param appFluentFoundryThreadsEnabled = true

// Sprint 13.1 T-DNS (ADR-0030) — public custom hostname on curavias.ch.
// Deploy sequence:
//   1. First deploy with `appFluentEnableCustomDomainCert = false` -> creates the
//      Azure DNS zone for curavias.ch + the CNAME/TXT records. Cert issuance skipped.
//   2. Follow the runbook `docs/runbooks/curavias-dns-godaddy-delegation.md` to set
//      NS records at GoDaddy pointing at the Azure DNS name servers (from the
//      `curaviasNameServers` deploy output). Wait for propagation (usually <1h).
//   3. Verify propagation: `dig +short curavias.ch NS` returns the Azure name servers.
//   4. Flip `appFluentEnableCustomDomainCert = true` and redeploy -> Managed
//      Certificate resource issues a free Let's Encrypt cert (~15-30 min) + CA binds
//      the custom domain via SNI.
//
// Phase 2 completed 2026-07-14 — steps 1-3 done in earlier iterations; NS delegation
// confirmed via .ch TLD authoritative servers (a.nic.ch / d.nic.ch returning Azure NS).
// Flipping to `true` triggers Managed Certificate issuance for `appsit.curavias.ch`.
param appFluentCustomHostname = 'appsit.curavias.ch'
param appFluentEnableCustomDomainCert = true
