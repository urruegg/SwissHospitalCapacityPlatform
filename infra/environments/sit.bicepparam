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

// Sprint 13.1 — wire the Sprint 13 app tier into SIT (closes S13.2/S13.3/S13.6/S13.7/S13.8).
// agent-host = Container App (ca-agent-host-ihzhhpf-sit) + Cosmos (cosmos-ihzhhpf-sit with
// conversations/audit/approval-events containers) + Redis (redis-ihzhhpf-sit) per ADR-0007.
// hcc-app-fluent = Container App (ca-app-fluent-ihzhhpf-sit) with external ingress.
// Deploy ceiling = `deploy` (AGENTS.md §3): apply only after an `approved-to-apply` comment.
//
// Container images: both modules default to a public placeholder so provisioning is
// deterministic before the private images are published. The real images
// (apps/hcc-agent-host/Dockerfile and apps/hcc-app-fluent/Dockerfile) are built + published to
// ACR cri75lbu5sj4hza by the Sprint 13 app-build CD track and swapped in via
// `az containerapp update --image` (same sequence sim-capacity followed in Sprint 10 T1).
param enableAgentHostModule = true
param agentHostLocation = 'westus2'

param enableAppFluentModule = true
param appFluentLocation = 'westus2'
param appFluentDemoScope = true
