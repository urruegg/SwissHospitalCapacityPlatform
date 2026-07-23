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

// Sprint 09 v2.0.0 T2.1 — Event Hubs consumer group RBAC.
// Simulator MI (T3.7) and agent MIs (T4.5) don't exist yet; leaving empty means the three
// role assignments are conditionally skipped. Populate as those Sprint 09 v2.0.0 tasks land.
param eventHubsSimulatorMiPrincipalId = ''
param eventHubsBmCopilotMiPrincipalId = ''
param eventHubsCsaAgentMiPrincipalId = ''

// Sprint 13 T5 — agent-host (Container App + Cosmos + Redis per ADR-0007).
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
param agentHostImage = 'cri75lbu5sj4hza.azurecr.io/hcc-agent-host:b796961'

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
param enableAppFluentModule = true
param appFluentImage = 'cri75lbu5sj4hza.azurecr.io/hcc-app-fluent:cb21e2c'

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
