@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. chhealthpf-sit or chhealthpf-prod.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

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

@description('Data platform module implementation marker.')
output moduleStatus string = 'data-platform-implemented'

@description('Storage account name for the data platform baseline.')
output storageAccountName string = storageAccount.name

@description('Blob service resource ID for diagnostics wiring.')
output blobServiceResourceId string = blobService.id

@description('Data platform module scaffold input echo for validation only.')
output scaffoldInput object = {
	location: location
	nameSuffix: nameSuffix
	tagCount: length(items(tags))
}
