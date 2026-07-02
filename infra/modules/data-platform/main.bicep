@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Enable the source-SQL submodule (Sprint 08 W1.1 synthetic KIS feed).')
param enableSourceSqlModule bool = false

@description('Resource ID of the data subnet used for the SQL private endpoint. Required when enableSourceSqlModule = true.')
param sourceSqlDataSubnetId string = ''

@description('Resource ID of the Key Vault that stores the SQL admin password. Required when enableSourceSqlModule = true.')
param sourceSqlKeyVaultId string = ''

@description('Name of the Key Vault secret holding the SQL admin password. Required when enableSourceSqlModule = true.')
param sourceSqlAdminPasswordSecretName string = ''

@description('Optional. Resource ID of the existing privatelink.database.windows.net private DNS zone for the source-SQL private endpoint. Leave empty to wire DNS externally.')
param sourceSqlPrivateDnsZoneId string = ''

@description('Entra ID login (UPN or group displayName) of the source-SQL AAD admin. Required by tenant policy.')
param sourceSqlAadAdminLogin string = ''

@description('Object ID (SID) of the source-SQL AAD admin principal.')
param sourceSqlAadAdminObjectId string = ''

@description('Principal type of the source-SQL AAD admin.')
@allowed([
  'User'
  'Group'
  'ServicePrincipal'
])
param sourceSqlAadAdminPrincipalType string = 'User'

@description('Enable the Fabric foundation submodule (capacity).')
param enableFabricFoundationModule bool = false

@description('Object ID(s) of Fabric capacity administrators. Required when enableFabricFoundationModule = true.')
param fabricCapacityAdmins array = []

// Storage account names must be globally unique across all Azure. Add a short, deterministic
// per-(subscription, RG) suffix so ihzhhpf-based names don't collide with unrelated tenants.
var storageAccountName = toLower('stdp${replace(nameSuffix, '-', '')}${take(uniqueString(subscription().subscriptionId, resourceGroup().id), 4)}')

var sourceSqlKvIdParts = split(sourceSqlKeyVaultId, '/')

resource sourceSqlKeyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = if (enableSourceSqlModule && !empty(sourceSqlKeyVaultId)) {
name: last(sourceSqlKvIdParts)
scope: resourceGroup(sourceSqlKvIdParts[2], sourceSqlKvIdParts[4])
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
name: storageAccountName
location: location
tags: tags
kind: 'StorageV2'
sku: {
name: 'Standard_LRS'
}
properties: {
accessTier: 'Hot'
allowBlobPublicAccess: false
minimumTlsVersion: 'TLS1_2'
supportsHttpsTrafficOnly: true
publicNetworkAccess: 'Enabled'
}
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
parent: storageAccount
name: 'default'
properties: {
deleteRetentionPolicy: {
enabled: true
days: 7
}
containerDeleteRetentionPolicy: {
enabled: true
days: 7
}
}
}

@description('Onboarding bootstrap container for synthesized SIT onboarding datasets consumed by the OOA/DCA/BMCA MVP flows (Sprint 6 Phase 1).')
resource onboardingContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
parent: blobService
name: 'onboarding'
properties: {
publicAccess: 'None'
}
}

module sourceSql './source-sql/main.bicep' = if (enableSourceSqlModule) {
name: 'source-sql-${nameSuffix}'
params: {
nameSuffix: nameSuffix
location: location
tags: tags
dataSubnetId: sourceSqlDataSubnetId
sqlAdminPassword: sourceSqlKeyVault.getSecret(sourceSqlAdminPasswordSecretName)
privateDnsZoneId: sourceSqlPrivateDnsZoneId
aadAdminLogin: sourceSqlAadAdminLogin
aadAdminObjectId: sourceSqlAadAdminObjectId
aadAdminPrincipalType: sourceSqlAadAdminPrincipalType
}
}

module fabricFoundation './fabric/main.bicep' = if (enableFabricFoundationModule) {
name: 'fabric-foundation'
params: {
location: location
nameSuffix: nameSuffix
tags: tags
capacityAdmins: fabricCapacityAdmins
}
}

@description('Data platform module implementation marker.')
output moduleStatus string = 'data-platform-implemented'

@description('Source-SQL submodule status (Sprint 08 W1.1).')
output sourceSqlStatus string = enableSourceSqlModule ? sourceSql!.outputs.moduleStatus : 'source-sql-disabled'

@description('Storage account name for the data platform baseline.')
output storageAccountName string = storageAccount.name

@description('Blob service resource ID for diagnostics wiring.')
output blobServiceResourceId string = blobService.id

@description('Onboarding bootstrap container name for synthesized SIT onboarding data.')
output onboardingContainerName string = onboardingContainer.name

@description('Fabric foundation submodule status (or disabled sentinel).')
output fabricFoundationStatus string = enableFabricFoundationModule ? fabricFoundation!.outputs.moduleStatus : 'fabric-foundation-disabled'

@description('Data platform module scaffold input echo for validation only.')
output scaffoldInput object = {
location: location
nameSuffix: nameSuffix
tagCount: length(items(tags))
}
