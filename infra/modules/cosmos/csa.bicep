// Sprint 16 T1 — CSA Cosmos DB for NoSQL account + 4 containers for the
// what-if scenario catalogue and agent memory.
//
// Grounds design spec §4 (docs/superpowers/specs/2026-07-09-sprint-16-csa-design.md):
//   scenarios       PK /scenarioId  vector DiskANN       on /descriptionEmbedding
//   agent-memory    PK /threadId    vector DiskANN       on /contentEmbedding (sharded by /threadId)
//   response-levers PK /leverId     vector quantizedFlat on /descriptionEmbedding
//   simulation-runs PK /runId       (no vector)
//
// This Cosmos account is SEPARATE from the Sprint 13 conversations/audit Cosmos
// (ADR-0007) — different concern, different account.
//
// Consistency: Session (read-your-writes for agent memory).
// Auth: RBAC data-plane only (Cosmos DB Built-in Data Contributor) — no keys.

@description('Location for the Cosmos account. Demo scope is westus2 per ADR-0013.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
@minLength(3)
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Cosmos SQL database name.')
param databaseName string = 'csa'

@description('Object ID of the Sprint 13 agent-host managed identity. When set, receives Cosmos DB Built-in Data Contributor scoped to this account (least privilege). Empty string skips the assignment.')
param agentHostMiPrincipalId string = ''

@description('Total shared throughput (RU/s) for the database in autoscale max mode. Small demo default.')
@minValue(1000)
@maxValue(10000)
param databaseMaxThroughput int = 1000

// Cosmos account names must be globally unique, 3-44 chars, lowercase.
var accountName = toLower('cosmos-csa-${nameSuffix}')

// Vector dimension for the embedding model (text-embedding-3-small = 1536).
var vectorDimensions = 1536

// Cosmos DB Built-in Data Contributor role (data-plane RBAC).
// Fixed built-in id, verified against Azure docs:
// https://learn.microsoft.com/azure/cosmos-db/how-to-setup-rbac
var cosmosDataContributorRoleId = '00000000-0000-0000-0000-000000000002'

resource account 'Microsoft.DocumentDB/databaseAccounts@2024-12-01-preview' = {
  name: accountName
  location: location
  tags: tags
  kind: 'GlobalDocumentDB'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    databaseAccountOfferType: 'Standard'
    disableLocalAuth: true
    minimalTlsVersion: 'Tls12'
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
    capabilities: [
      {
        name: 'EnableNoSQLVectorSearch'
      }
    ]
  }
}

resource database 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-12-01-preview' = {
  parent: account
  name: databaseName
  properties: {
    resource: {
      id: databaseName
    }
    options: {
      autoscaleSettings: {
        maxThroughput: databaseMaxThroughput
      }
    }
  }
}

resource scenariosContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-12-01-preview' = {
  parent: database
  name: 'scenarios'
  properties: {
    resource: {
      id: 'scenarios'
      partitionKey: {
        paths: [
          '/scenarioId'
        ]
        kind: 'Hash'
      }
      vectorEmbeddingPolicy: {
        vectorEmbeddings: [
          {
            path: '/descriptionEmbedding'
            dataType: 'float32'
            distanceFunction: 'cosine'
            dimensions: vectorDimensions
          }
        ]
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [
          {
            path: '/*'
          }
        ]
        excludedPaths: [
          {
            path: '/descriptionEmbedding/*'
          }
        ]
        vectorIndexes: [
          {
            path: '/descriptionEmbedding'
            type: 'diskANN'
          }
        ]
      }
    }
  }
}

resource agentMemoryContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-12-01-preview' = {
  parent: database
  name: 'agent-memory'
  properties: {
    resource: {
      id: 'agent-memory'
      partitionKey: {
        paths: [
          '/threadId'
        ]
        kind: 'Hash'
      }
      vectorEmbeddingPolicy: {
        vectorEmbeddings: [
          {
            path: '/contentEmbedding'
            dataType: 'float32'
            distanceFunction: 'cosine'
            dimensions: vectorDimensions
          }
        ]
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [
          {
            path: '/*'
          }
        ]
        excludedPaths: [
          {
            path: '/contentEmbedding/*'
          }
        ]
        vectorIndexes: [
          {
            path: '/contentEmbedding'
            type: 'diskANN'
          }
        ]
      }
    }
  }
}

resource responseLeversContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-12-01-preview' = {
  parent: database
  name: 'response-levers'
  properties: {
    resource: {
      id: 'response-levers'
      partitionKey: {
        paths: [
          '/leverId'
        ]
        kind: 'Hash'
      }
      vectorEmbeddingPolicy: {
        vectorEmbeddings: [
          {
            path: '/descriptionEmbedding'
            dataType: 'float32'
            distanceFunction: 'cosine'
            dimensions: vectorDimensions
          }
        ]
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [
          {
            path: '/*'
          }
        ]
        excludedPaths: [
          {
            path: '/descriptionEmbedding/*'
          }
        ]
        vectorIndexes: [
          {
            path: '/descriptionEmbedding'
            type: 'quantizedFlat'
          }
        ]
      }
    }
  }
}

resource simulationRunsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-12-01-preview' = {
  parent: database
  name: 'simulation-runs'
  properties: {
    resource: {
      id: 'simulation-runs'
      partitionKey: {
        paths: [
          '/runId'
        ]
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [
          {
            path: '/*'
          }
        ]
        excludedPaths: []
      }
    }
  }
}

// Least-privilege data-plane RBAC for the Sprint 13 agent-host managed identity,
// scoped to this account only. No account keys are used (disableLocalAuth=true).
resource agentHostDataContributor 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2024-12-01-preview' = if (!empty(agentHostMiPrincipalId)) {
  parent: account
  name: guid(account.id, agentHostMiPrincipalId, cosmosDataContributorRoleId)
  properties: {
    roleDefinitionId: '${account.id}/sqlRoleDefinitions/${cosmosDataContributorRoleId}'
    principalId: agentHostMiPrincipalId
    scope: account.id
  }
}

@description('Cosmos account name.')
output accountName string = account.name

@description('Cosmos account document endpoint.')
output documentEndpoint string = account.properties.documentEndpoint

@description('Cosmos SQL database name.')
output databaseName string = database.name

@description('Container names provisioned by this module.')
output containerNames array = [
  scenariosContainer.name
  agentMemoryContainer.name
  responseLeversContainer.name
  simulationRunsContainer.name
]
