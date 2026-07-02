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

// Sprint 08 W1.1 — source-SQL submodule (synthetic KIS feed).
// Temporarily disabled until real subnet and Key Vault IDs are supplied.
param enableSourceSqlModule = false
param sourceSqlDataSubnetId = '/subscriptions/<SUB>/resourceGroups/rg-ihzhhpf-sit/providers/Microsoft.Network/virtualNetworks/vnet-ihzhhpf-sit/subnets/snet-data-sit'
param sourceSqlKeyVaultId = '/subscriptions/<SUB>/resourceGroups/rg-ihzhhpf-sit/providers/Microsoft.KeyVault/vaults/kv-ihzhhpf-sit'
param sourceSqlAdminPasswordSecretName = 'sql-admin-password'

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
