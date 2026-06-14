@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. chhealthpf-sit or chhealthpf-prod.')
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

var storageAccountName = toLower('stdp${replace(nameSuffix, '-', '')}')

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
		keyVaultId: sourceSqlKeyVaultId
		sqlAdminPasswordSecretName: sourceSqlAdminPasswordSecretName
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

@description('Data platform module scaffold input echo for validation only.')
output scaffoldInput object = {
	location: location
	nameSuffix: nameSuffix
	tagCount: length(items(tags))
}
