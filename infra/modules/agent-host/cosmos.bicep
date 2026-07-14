@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

// Sprint 13 T5 — Cosmos DB for the agent-host (ADR-0007 §2). Containers:
// conversations (PK conversationId), audit (PK correlationId), approval-events
// (PK correlationId). Serverless capacity for the demo scope (ADR-0013).

resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: 'cosmos-${nameSuffix}'
  location: location
  tags: tags
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    enableAutomaticFailover: false
    disableLocalAuth: true
    // ADR-0029 Option A — Cosmos data-plane is reached exclusively via the
    // private endpoint provisioned in `./cosmos-pe.bicep`. MCAPS
    // `CosmosDB_PublicNetwork_Modify` policy already forces this to Disabled
    // at deploy time; declaring it here matches deployed state and removes
    // silent drift.
    publicNetworkAccess: 'Disabled'
    capabilities: [
      {
        name: 'EnableServerless'
      }
    ]
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
  }
}

resource database 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-05-15' = {
  parent: cosmosAccount
  name: 'agenthost'
  properties: {
    resource: {
      id: 'agenthost'
    }
  }
}

var containers = [
  {
    name: 'conversations'
    partitionKey: '/conversationId'
  }
  {
    name: 'audit'
    partitionKey: '/correlationId'
  }
  {
    name: 'approval-events'
    partitionKey: '/correlationId'
  }
]

resource containerResources 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = [
  for container in containers: {
    parent: database
    name: container.name
    properties: {
      resource: {
        id: container.name
        partitionKey: {
          paths: [
            container.partitionKey
          ]
          kind: 'Hash'
        }
      }
    }
  }
]

output cosmosAccountName string = cosmosAccount.name
output cosmosAccountResourceId string = cosmosAccount.id
output cosmosEndpoint string = cosmosAccount.properties.documentEndpoint
