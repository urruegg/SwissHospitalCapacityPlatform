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

// Sprint 09 v2 T3.7 — sim-capacity ACA producer. Enabled in SIT for the demo path.
// EH namespace resolves from data-foundation module output when enableDataFoundationModule=true.
param enableSimCapacityModule = true
param simCapacityLocation = 'westus2'
param simCapacityEventHubName = 'demand-encounters'
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
