targetScope = 'resourceGroup'

@description('Suffix appended to resource names (e.g. chhealthpf-sit).')
param nameSuffix string

@description('Deployment region. Must be switzerlandnorth (ADR-0003).')
@allowed([
  'switzerlandnorth'
])
param location string

@description('Resource tags applied to all resources.')
param tags object

@description('Resource ID of the data subnet for the SQL private endpoint.')
param dataSubnetId string

@description('Resource ID of the Key Vault that stores the SQL admin password.')
param keyVaultId string

@description('Name of the Key Vault secret holding the SQL admin password.')
param sqlAdminPasswordSecretName string

@description('SQL admin login.')
param sqlAdminLogin string = 'sqladmin'

var serverName = 'sql-${nameSuffix}'
var databaseName = 'kis'
var privateEndpointName = 'pe-${serverName}'

resource sqlServer 'Microsoft.Sql/servers@2023-08-01-preview' = {
  name: serverName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    administratorLogin: sqlAdminLogin
    administratorLoginPassword: '@Microsoft.KeyVault(SecretUri=${reference(keyVaultId, '2023-07-01').vaultUri}secrets/${sqlAdminPasswordSecretName}/)'
    publicNetworkAccess: 'Disabled'
    minimalTlsVersion: '1.2'
    version: '12.0'
  }
}

resource kisDb 'Microsoft.Sql/servers/databases@2023-08-01-preview' = {
  parent: sqlServer
  name: databaseName
  location: location
  tags: tags
  sku: {
    name: 'GP_Gen5_2'
    tier: 'GeneralPurpose'
    family: 'Gen5'
    capacity: 2
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    zoneRedundant: false
    requestedBackupStorageRedundancy: 'Local'
  }
}

resource sqlPrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-09-01' = {
  name: privateEndpointName
  location: location
  tags: tags
  properties: {
    subnet: {
      id: dataSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'sqlServer'
        properties: {
          privateLinkServiceId: sqlServer.id
          groupIds: [
            'sqlServer'
          ]
        }
      }
    ]
  }
}

output sqlServerName string = sqlServer.name
output sqlServerFqdn string = sqlServer.properties.fullyQualifiedDomainName
output sqlDatabaseName string = kisDb.name
output sqlServerPrincipalId string = sqlServer.identity.principalId

@description('Source-SQL module implementation marker.')
output moduleStatus string = 'source-sql-implemented'
