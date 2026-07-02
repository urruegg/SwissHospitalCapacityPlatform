targetScope = 'resourceGroup'

@description('Suffix appended to resource names (e.g. ihzhhpf-sit).')
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

@secure()
@description('SQL admin password. Pass via keyVault.getSecret() from the caller.')
param sqlAdminPassword string

@description('SQL admin login.')
param sqlAdminLogin string = 'sqladmin'

@description('Optional. Resource ID of the existing privatelink.database.windows.net private DNS zone. Leave empty to wire DNS externally (e.g. via hub network).')
param privateDnsZoneId string = ''

var serverName = 'sql-${nameSuffix}'
var databaseName = 'kis'
var privateEndpointName = 'pe-${serverName}'

// TODO(ADR-0006): swap to GA Microsoft.Sql/servers API before PROD enables.
// TODO: add 'administrators' block for Entra group SQL admin once platform-identity slice is in place.
resource sqlServer 'Microsoft.Sql/servers@2023-08-01-preview' = {
  name: serverName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    administratorLogin: sqlAdminLogin
    administratorLoginPassword: sqlAdminPassword
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
    // TDE is enabled by default on Azure SQL DB; acceptable for synthetic SIT data.
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

resource sqlPrivateDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-09-01' = if (!empty(privateDnsZoneId)) {
  parent: sqlPrivateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'privatelink-database-windows-net'
        properties: {
          privateDnsZoneId: privateDnsZoneId
        }
      }
    ]
  }
}

output sqlServerName string = sqlServer.name
output sqlServerFqdn string = sqlServer.properties.fullyQualifiedDomainName
output sqlDatabaseName string = kisDb.name
output sqlServerPrincipalId string = sqlServer.identity.principalId

output sqlPrivateDnsWarning string = empty(privateDnsZoneId) ? 'WARN: privateDnsZoneId not supplied. Configure the privatelink.database.windows.net DNS zone group externally before clients can resolve the SQL FQDN.' : 'ok'

@description('Source-SQL module implementation marker.')
output moduleStatus string = 'source-sql-implemented'
