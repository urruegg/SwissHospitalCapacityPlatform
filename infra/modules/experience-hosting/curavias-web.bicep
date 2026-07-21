// Sprint 24 — Curavias product landing page hosting (ADR-0030 DNS, PROD-only).
//
// Provisions the Azure Static Web App that serves apps/curavias-web (Astro static
// output) plus a dedicated Storage account for media artefacts (images/video that
// are too large or too binary for the repo). Custom-domain binding for curavias.ch
// (apex) and www.curavias.ch is a gated two-step, mirroring the app-fluent pattern:
//   (1) deploy with enableCustomDomains=false to create the SWA + storage,
//   (2) add the DNS records (dns/curavias.bicep) + GoDaddy delegation,
//   (3) flip enableCustomDomains=true so the SWA validates ownership + issues certs.
// No secrets cross module boundaries; the SWA deployment token is read at deploy time
// by the workflow, never emitted here.

@description('Location for the media storage account. The Static Web App itself is a global resource; pass a supported control-plane region (e.g. westeurope).')
param location string

@description('Static Web App control-plane region. SWA is only available in a subset of regions; westeurope is the closest to Switzerland.')
@allowed([
  'westeurope'
  'northeurope'
  'eastus2'
  'eastasia'
])
param staticWebAppLocation string = 'westeurope'

@description('Resource name suffix, e.g. ihzhhpf-prod.')
@minLength(3)
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Static Web App SKU. Standard is required for custom domains with SLA + enterprise features.')
@allowed([
  'Free'
  'Standard'
])
param staticWebAppSku string = 'Standard'

@description('Object ID of the identity (e.g. the media-publisher managed identity or the deploy service principal) that uploads media to the storage account. Empty string skips the role assignment.')
param mediaPublisherPrincipalId string = ''

@description('Principal type for the media publisher role assignment.')
@allowed([
  'ServicePrincipal'
  'User'
  'Group'
])
param mediaPublisherPrincipalType string = 'ServicePrincipal'

@description('When true, bind the custom domains in `customDomains` to the Static Web App. Keep false on the first deploy; flip true only after the DNS records + GoDaddy delegation are in place so SWA can validate ownership.')
param enableCustomDomains bool = false

@description('Custom domains to bind when enableCustomDomains is true. Apex (curavias.ch) must use dns-txt-token validation; subdomains (www.curavias.ch) use cname-delegation. Example: [ { name: "curavias.ch", validation: "dns-txt-token" }, { name: "www.curavias.ch", validation: "cname-delegation" } ].')
param customDomains array = []

// Storage account name: lowercase alphanumeric, <= 24 chars, globally unique.
// nameSuffix "ihzhhpf-prod" -> "stmediaihzhhpfprod" (18 chars).
var storageAccountName = toLower('stmedia${replace(nameSuffix, '-', '')}')

// Storage Blob Data Contributor built-in role. GUID verified against Azure RBAC docs.
var storageBlobDataContributorRoleId = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'

resource mediaStorage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: true
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    publicNetworkAccess: 'Enabled'
    allowSharedKeyAccess: true
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: mediaStorage
  name: 'default'
  properties: {
    cors: {
      corsRules: [
        {
          allowedOrigins: [
            'https://curavias.ch'
            'https://www.curavias.ch'
          ]
          allowedMethods: [ 'GET', 'HEAD', 'OPTIONS' ]
          allowedHeaders: [ '*' ]
          exposedHeaders: [ '*' ]
          maxAgeInSeconds: 3600
        }
      ]
    }
  }
}

// Public-read container: only non-PHI, brand-approved marketing media is ever stored here.
resource mediaContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'media'
  properties: {
    publicAccess: 'Blob'
  }
}

resource mediaPublisherRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(mediaPublisherPrincipalId)) {
  name: guid(mediaStorage.id, mediaPublisherPrincipalId, storageBlobDataContributorRoleId)
  scope: mediaStorage
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataContributorRoleId)
    principalId: mediaPublisherPrincipalId
    principalType: mediaPublisherPrincipalType
  }
}

resource staticSite 'Microsoft.Web/staticSites@2023-12-01' = {
  name: 'stapp-${nameSuffix}'
  location: staticWebAppLocation
  tags: tags
  sku: {
    name: staticWebAppSku
    tier: staticWebAppSku
  }
  properties: {
    // Deployed by the curavias-web-deploy workflow via deployment token (no linked repo).
    provider: 'Custom'
    allowConfigFileUpdates: true
    stagingEnvironmentPolicy: 'Enabled'
    enterpriseGradeCdnStatus: 'Disabled'
  }
}

resource staticSiteDomains 'Microsoft.Web/staticSites/customDomains@2023-12-01' = [for domain in (enableCustomDomains ? customDomains : []): {
  parent: staticSite
  name: domain.name
  properties: {
    validationMethod: domain.validation
  }
}]

@description('Curavias web hosting module implementation marker.')
output moduleStatus string = 'curavias-web-implemented'

@description('Static Web App name.')
output staticWebAppName string = staticSite.name

@description('Static Web App default hostname (e.g. <name>.azurestaticapps.net). Used as the CNAME target for www.curavias.ch.')
output staticWebAppDefaultHostname string = staticSite.properties.defaultHostname

@description('Media storage account name.')
output mediaStorageAccountName string = mediaStorage.name

@description('Public base URL for media blobs.')
output mediaBaseUrl string = '${mediaStorage.properties.primaryEndpoints.blob}media'
