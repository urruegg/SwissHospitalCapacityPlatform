// Sprint 23 WS-A1 (#255) — ADLS Gen2 landing zone for Curavias org/skills master data.
//
// Grounds design D5: the on-demand ingestion pipeline (Container Apps Jobs, WS-A3)
// writes synthetic HR/LMS/skills-manager/work-id extracts here; a Fabric OneLake
// shortcut (WS-A2 runbook) surfaces the container into the lakehouse Bronze layer.
//
// Landing convention (folders are virtual in ADLS Gen2 — created on first upload,
// not provisionable in Bicep):
//   landing/curavias-org-skills/<source>/<yyyy-mm-dd>/<extract>.csv
// where <source> ∈ { successfactors, lms, skills-manager, work-id }.
//
// No secrets cross the module boundary. Access is RBAC-only (shared-key disabled);
// the pipeline managed identity is granted Storage Blob Data Contributor.

@description('Location for the storage account.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
@minLength(3)
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Object ID of the ingestion pipeline managed identity that writes extracts to the landing container. When set, receives Storage Blob Data Contributor scoped to the account. Empty string skips the role assignment.')
param pipelinePrincipalId string = ''

@description('Principal type for the pipeline role assignment.')
@allowed([
  'ServicePrincipal'
  'User'
  'Group'
])
param pipelinePrincipalType string = 'ServicePrincipal'

@description('Resource ID of the Log Analytics workspace for blob diagnostic settings. Empty string skips diagnostics (SIT). Populated in PROD per the copilot-instructions §3 "diagnostics for every production resource" rule.')
param logAnalyticsWorkspaceId string = ''

// Storage account name: lowercase alphanumeric, <= 24 chars, globally unique.
// nameSuffix "ihzhhpf-sit"  -> "stmasterdataihzhhpfsit"  (22 chars)
// nameSuffix "ihzhhpf-prod" -> "stmasterdataihzhhpfprod" (23 chars)
var storageAccountName = toLower('stmasterdata${replace(nameSuffix, '-', '')}')

// Storage Blob Data Contributor built-in role. GUID verified against Azure RBAC docs.
var storageBlobDataContributorRoleId = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'

// ADLS Gen2 = StorageV2 + hierarchical namespace enabled.
resource landingStorage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    isHnsEnabled: true
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    // Tenant-wide MCAPSGov StorageAccount_PublicNetwork_Modify policy forces
    // this Disabled unconditionally; declare it to match and stop the
    // perpetual what-if drift (mirrors infra/modules/agent-host/cosmos.bicep).
    publicNetworkAccess: 'Disabled'
    allowSharedKeyAccess: false
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: landingStorage
  name: 'default'
}

// The `landing` filesystem (ADLS Gen2 container). Source/date subfolders are
// created by the pipeline on upload, not here.
resource landingFilesystem 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'landing'
  properties: {
    publicAccess: 'None'
  }
}

resource pipelineWriterRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(pipelinePrincipalId)) {
  name: guid(landingStorage.id, pipelinePrincipalId, storageBlobDataContributorRoleId)
  scope: landingStorage
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataContributorRoleId)
    principalId: pipelinePrincipalId
    principalType: pipelinePrincipalType
    description: 'Sprint 23 WS-A1 (#255) — ingestion pipeline MI writes synthetic org/skills extracts to landing/curavias-org-skills/.'
  }
}

// PROD-only blob diagnostics -> Log Analytics (skipped when workspace ID empty).
resource blobDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (!empty(logAnalyticsWorkspaceId)) {
  name: 'diag-blob-${storageAccountName}'
  scope: blobService
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      {
        category: 'StorageWrite'
        enabled: true
      }
      {
        category: 'StorageDelete'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'Transaction'
        enabled: true
      }
    ]
  }
}

@description('Masterdata landing module implementation marker.')
output moduleStatus string = 'masterdata-landing-implemented'

@description('ADLS Gen2 landing storage account name.')
output storageAccountName string = landingStorage.name

@description('Landing filesystem (container) name.')
output landingContainerName string = landingFilesystem.name

@description('DFS (ADLS Gen2) endpoint for the landing storage account.')
output dfsEndpoint string = landingStorage.properties.primaryEndpoints.dfs
