// Sprint 28 WS-INF (#377) — ADLS Gen2 landing zone for the Curavias product
// corpus (PRDs, ADRs, design specs, runbooks) that grounds the PO Agent's
// Class A answers (design D2, ADR-0043).
//
// The daily corpus-refresh Container Apps Job (see
// `../../experience-hosting/po-agent-runtime/main.bicep`) writes synthetic,
// no-PHI product documents here; the Azure AI Search service (its knowledge
// source) reads them via the Search system-assigned MI. A Fabric OneLake shortcut
// (companion runbook) can also surface the container for medallion notebooks.
//
// Landing convention (folders are virtual in ADLS Gen2 — created on first upload,
// not provisionable in Bicep):
//   landing/curavias-product-corpus/<source>/<yyyy-mm-dd>/<doc>.md
// where <source> ∈ { prd, adr, design, runbook }.
//
// No secrets cross the module boundary. Access is RBAC-only (shared-key disabled):
// the refresh-job MI gets Storage Blob Data Contributor; the Search service MI
// gets Storage Blob Data Reader.

@description('Location for the storage account.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
@minLength(3)
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Object ID of the corpus-refresh job managed identity that writes documents to the landing container. When set, receives Storage Blob Data Contributor scoped to the account. Empty string skips the role assignment.')
param refreshJobPrincipalId string = ''

@description('Object ID of the Azure AI Search system-assigned managed identity. When set, receives Storage Blob Data Reader so the knowledge source can index the corpus without keys. Empty string skips the role assignment.')
param searchPrincipalId string = ''

@description('Principal type for the corpus-refresh job role assignment.')
@allowed([
  'ServicePrincipal'
  'User'
  'Group'
])
param refreshJobPrincipalType string = 'ServicePrincipal'

@description('Resource ID of the Log Analytics workspace for blob diagnostic settings. Empty string skips diagnostics (SIT). Populated in PROD per copilot-instructions §3.')
param logAnalyticsWorkspaceId string = ''

// Storage account name: lowercase alphanumeric, <= 24 chars, globally unique.
// nameSuffix "ihzhhpf-sit"  -> "stcorpusihzhhpfsit"  (18 chars)
// nameSuffix "ihzhhpf-prod" -> "stcorpusihzhhpfprod" (19 chars)
var storageAccountName = toLower('stcorpus${replace(nameSuffix, '-', '')}')

// Built-in role IDs. GUIDs verified against Azure RBAC docs.
var storageBlobDataContributorRoleId = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
var storageBlobDataReaderRoleId = '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'

// ADLS Gen2 = StorageV2 + hierarchical namespace enabled.
resource corpusStorage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
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
    publicNetworkAccess: 'Enabled'
    allowSharedKeyAccess: false
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: corpusStorage
  name: 'default'
}

// The `landing` filesystem (ADLS Gen2 container). Source/date subfolders are
// created by the refresh job on upload, not here.
resource landingFilesystem 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'landing'
  properties: {
    publicAccess: 'None'
  }
}

resource refreshJobWriterRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(refreshJobPrincipalId)) {
  name: guid(corpusStorage.id, refreshJobPrincipalId, storageBlobDataContributorRoleId)
  scope: corpusStorage
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataContributorRoleId)
    principalId: refreshJobPrincipalId
    principalType: refreshJobPrincipalType
    description: 'Sprint 28 WS-INF (#377) — corpus-refresh job MI writes synthetic product docs to landing/curavias-product-corpus/.'
  }
}

resource searchReaderRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(searchPrincipalId)) {
  name: guid(corpusStorage.id, searchPrincipalId, storageBlobDataReaderRoleId)
  scope: corpusStorage
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataReaderRoleId)
    principalId: searchPrincipalId
    principalType: 'ServicePrincipal'
    description: 'Sprint 28 WS-INF (#377) — Azure AI Search MI reads the corpus for the Foundry IQ knowledge source (no keys).'
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

@description('Corpus landing module implementation marker.')
output moduleStatus string = 'knowledge-layer-corpus-landing-implemented'

@description('ADLS Gen2 corpus storage account name.')
output storageAccountName string = corpusStorage.name

@description('Landing filesystem (container) name.')
output landingContainerName string = landingFilesystem.name

@description('DFS (ADLS Gen2) endpoint for the corpus storage account.')
output dfsEndpoint string = corpusStorage.properties.primaryEndpoints.dfs
