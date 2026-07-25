// Sprint 28 WS-INF (#377) — Azure AI Search: the GA substrate beneath the shared
// Foundry IQ Knowledge Layer (design D2, ADR-0043). Hosts the hybrid vector +
// keyword indexes the PO Agent's Class A corpus knowledge source retrieves over.
//
// Posture: system-assigned managed identity (so Search can pull from OneLake /
// Storage without keys), RBAC-only data plane (local API keys disabled — no
// secrets cross the module boundary), semantic ranker enabled for hybrid
// retrieval. Diagnostics -> Log Analytics in PROD (skipped in SIT).
//
// The control-plane ARM apiVersion is pinned below. The DATA-PLANE agentic-
// retrieval REST version (some features Preview per design R2) is pinned in the
// companion runbook `../foundry-iq-knowledge-base/knowledge-base-rest.md` and
// surfaced as an output so the runtime wires a single, reviewed version.

@description('Location for the Azure AI Search service. PROD = switzerlandnorth (ADR-0037); SIT = westus2 (ADR-0013).')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
@minLength(3)
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Search SKU. `standard` supports hybrid vector + keyword + semantic ranker (design D2).')
@allowed([
  'basic'
  'standard'
  'standard2'
  'standard3'
])
param sku string = 'standard'

@description('Replica count (query throughput / SLA). 1 for SIT demo scope; raise in PROD as needed.')
@minValue(1)
@maxValue(12)
param replicaCount int = 1

@description('Partition count (index size / write throughput).')
@allowed([
  1
  2
  3
  4
  6
  12
])
param partitionCount int = 1

@description('Resource ID of the Log Analytics workspace for diagnostic settings. Empty string skips diagnostics (SIT). Populated in PROD per copilot-instructions §3.')
param logAnalyticsWorkspaceId string = ''

// Search service name: 2-60 chars, lowercase letters/digits/dashes, no leading/
// trailing/consecutive dashes. nameSuffix "ihzhhpf-sit" -> "srch-ihzhhpf-sit".
var searchServiceName = toLower('srch-${nameSuffix}')

resource search 'Microsoft.Search/searchServices@2024-06-01-preview' = {
  name: searchServiceName
  location: location
  tags: tags
  sku: {
    name: sku
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    replicaCount: replicaCount
    partitionCount: partitionCount
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
    // RBAC-only data plane: disable admin/query API keys so no secret is ever
    // needed. Callers (Foundry IQ, the PO Agent runtime MI) use Entra roles.
    disableLocalAuth: true
    semanticSearch: 'standard'
    networkRuleSet: {
      ipRules: []
    }
  }
}

resource searchDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (!empty(logAnalyticsWorkspaceId)) {
  name: 'diag-${searchServiceName}'
  scope: search
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      {
        category: 'OperationLogs'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

@description('Azure AI Search module implementation marker.')
output moduleStatus string = 'knowledge-layer-ai-search-implemented'

@description('Azure AI Search service name.')
output searchServiceName string = search.name

@description('Azure AI Search service resource ID.')
output searchServiceId string = search.id

@description('Azure AI Search query endpoint.')
output searchEndpoint string = 'https://${search.name}.search.windows.net'

@description('Principal ID of the Search system-assigned managed identity (grant it read on OneLake / corpus storage).')
output searchPrincipalId string = search.identity.principalId

@description('Pinned data-plane agentic-retrieval REST api-version (see the knowledge-base runbook). Single reviewed value the runtime consumes.')
output pinnedSearchRestApiVersion string = '2024-05-01-preview'
