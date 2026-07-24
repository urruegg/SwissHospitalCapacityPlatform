// Sprint 16 T1 — CSA Cosmos DB for NoSQL account + 4 containers for the
// what-if scenario catalogue and agent memory. Sprint 26 WS-C adds 2 more
// containers (`proposed_actions`, `plans`) for the decision/coordination tier.
//
// Grounds design spec §4 (docs/superpowers/specs/2026-07-09-sprint-16-csa-design.md):
//   scenarios       PK /scenarioId  vector DiskANN       on /descriptionEmbedding
//   agent-memory    PK /threadId    vector DiskANN       on /contentEmbedding (sharded by /threadId)
//   response-levers PK /leverId     vector quantizedFlat on /descriptionEmbedding
//   simulation-runs PK /runId       (no vector)
//
// Sprint 26 WS-C adds 2 more containers for the decision/coordination tier per
// design spec §3.3 / §3.4 (docs/superpowers/specs/2026-07-23-sprint-26-decision-ontology-actionable-insight-design.md):
//   proposed_actions PK /plan_id      (no vector) — HITL-gated proposed levers
//   plans            PK /episode_key (no vector) — CapacityEpisode golden-thread
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

@description('Total shared throughput (RU/s) for the database in autoscale max mode. Small demo default. Applies to `simulation-runs` (no vector index).')
@minValue(1000)
@maxValue(10000)
param databaseMaxThroughput int = 1000

@description('Dedicated per-container throughput (RU/s) in autoscale max mode for vector-indexed containers. Cosmos requires vector containers to use dedicated (not shared) throughput.')
@minValue(1000)
@maxValue(10000)
param vectorContainerMaxThroughput int = 1000

@description('When true, provisions a private endpoint into the specified VNet subnet plus the Azure-managed `privatelink.documents.azure.com` private DNS zone. Required in SIT because MCAPSGov policies enforce publicNetworkAccess=Disabled on Cosmos.')
param enablePrivateEndpoint bool = false

@description('Resource ID of the VNet that hosts the private endpoint subnet + will be linked to the private DNS zone. Ignored when enablePrivateEndpoint=false.')
param vnetResourceId string = ''

@description('Name of the subnet inside vnetResourceId that will host the Cosmos private endpoint. Ignored when enablePrivateEndpoint=false.')
param privateEndpointSubnetName string = 'snet-data'

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
    // Pin publicNetworkAccess explicitly (matches infra/modules/agent-host/cosmos.bicep).
    // Disabled when a private endpoint is provisioned (SIT — also what the MCAPSGov
    // Modify-effect policy enforces); Enabled for the public/network-off scope
    // (PROD eastus2, synthetic-only per ADR-0013). Without this the API defaults to
    // Enabled and every redeploy shows a spurious what-if drift on this property.
    publicNetworkAccess: enablePrivateEndpoint ? 'Disabled' : 'Enabled'
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
    options: {
      autoscaleSettings: {
        maxThroughput: vectorContainerMaxThroughput
      }
    }
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
    options: {
      autoscaleSettings: {
        maxThroughput: vectorContainerMaxThroughput
      }
    }
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
    options: {
      autoscaleSettings: {
        maxThroughput: vectorContainerMaxThroughput
      }
    }
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

resource proposedActionsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-12-01-preview' = {
  parent: database
  name: 'proposed_actions'
  properties: {
    resource: {
      id: 'proposed_actions'
      partitionKey: {
        paths: [
          '/plan_id'
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

resource plansContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-12-01-preview' = {
  parent: database
  name: 'plans'
  properties: {
    resource: {
      id: 'plans'
      partitionKey: {
        paths: [
          '/episode_key'
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

// ============================================================================
// Private endpoint + private DNS zone (Concept 1 network plumbing).
//
// Required in SIT because MCAPSGov policies enforce publicNetworkAccess=Disabled
// on all Cosmos accounts. Without this the account is unreachable from Fabric,
// Container Apps, and any client outside the VNet.
//
// Zone name is Azure-managed and MUST be exactly privatelink.documents.azure.com
// for the private-endpoint auto-registration to work.
//
// Sprint 19: the zone + VNet link are now created ONCE in the network module
// (infra/modules/network/main.bicep) so both this PE and the agent-host Cosmos
// PE can attach zone groups without a creation-ordering race. This module only
// references the zone with `existing`. Ordering is guaranteed because this
// module depends on the network module via vnetResourceId.
// ============================================================================

var privateEndpointName = 'pe-${accountName}'
var privateDnsZoneName = 'privatelink.documents.azure.com'

resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' existing = {
  name: privateDnsZoneName
}

resource privateEndpoint 'Microsoft.Network/privateEndpoints@2023-11-01' = if (enablePrivateEndpoint) {
  name: privateEndpointName
  location: location
  tags: tags
  properties: {
    subnet: {
      id: '${vnetResourceId}/subnets/${privateEndpointSubnetName}'
    }
    privateLinkServiceConnections: [
      {
        name: '${privateEndpointName}-conn'
        properties: {
          privateLinkServiceId: account.id
          groupIds: [
            'Sql'
          ]
        }
      }
    ]
  }
}

resource privateDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-11-01' = if (enablePrivateEndpoint) {
  parent: privateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'privatelink-documents-azure-com'
        properties: {
          privateDnsZoneId: privateDnsZone.id
        }
      }
    ]
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
  proposedActionsContainer.name
  plansContainer.name
]
