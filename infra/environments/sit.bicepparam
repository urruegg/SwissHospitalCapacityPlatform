using '../main.bicep'

param environmentName = 'sit'
param solutionShortName = 'chhealthpf'
param location = 'switzerlandnorth'

param owner = 'platform-team'
param costCenter = 'chhealthpf-sit'
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

// Sprint 08 W1.1 — source-SQL submodule (synthetic KIS feed). PHI forbidden in SIT.
// Subnet and Key Vault references are placeholders; resolve before the first apply.
param enableSourceSqlModule = true
param sourceSqlDataSubnetId = '/subscriptions/<SUB>/resourceGroups/rg-chhealthpf-sit/providers/Microsoft.Network/virtualNetworks/vnet-chhealthpf-sit/subnets/snet-data-sit'
param sourceSqlKeyVaultId = '/subscriptions/<SUB>/resourceGroups/rg-chhealthpf-sit/providers/Microsoft.KeyVault/vaults/kv-chhealthpf-sit'
param sourceSqlAdminPasswordSecretName = 'sql-admin-password'

// Private DNS zone for SQL private endpoint. Owned by a separate platform-foundation slice
// (hub-spoke DNS). Leave empty here and wire post-deploy; do not invent a resource ID.
param sourceSqlPrivateDnsZoneId = ''

// Sprint 08 W1.2 — Fabric foundation submodule (F2 capacity + workspace/lakehouse/mirror).
// Replace <ADMIN_OBJECT_ID> with the actual AAD object ID before the first apply.
param enableFabricFoundationModule = true
param fabricCapacityAdmins = [
    '<ADMIN_OBJECT_ID>'
]
