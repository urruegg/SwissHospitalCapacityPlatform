@description('Location for all resources.')
param location string

@description('Resource name suffix, e.g. ihzhhpf-sit or ihzhhpf-prod.')
param nameSuffix string

@description('Resource tags applied to all resources.')
param tags object

@description('Log Analytics retention in days.')
@minValue(30)
@maxValue(730)
param logAnalyticsRetentionInDays int = 90

@description('Optional explicit Key Vault name. When empty (default), a deterministic per-(subscription, RG) name is generated. Set this only to sidestep a soft-delete + purge-protection name collision on a same-RG region rebuild (e.g. the Sprint 19 Switzerland North greenfield, where the decommissioned westus2 RG left kv-ihzhhpf-prod-i62t purge-protected until 2026-10-16).')
@maxLength(24)
param keyVaultName string = ''

@description('When true, provisions a private endpoint for the Key Vault into the specified VNet subnet plus the Azure-managed `privatelink.vaultcore.azure.net` private DNS zone, and flips the vault to `publicNetworkAccess=Disabled`. Required in PROD switzerlandnorth to give the AAD-only vault a reachable data plane while satisfying the MCAPSGov policy that force-disables Key Vault public network access (ADR-0039, extends ADR-0029 Option A + ADR-0037). Ignored (public, no PE) when false.')
param enableKeyVaultPrivateEndpoint bool = false

@description('Resource ID of the VNet that hosts the Key Vault private-endpoint subnet + is linked to the private DNS zone. Ignored when enableKeyVaultPrivateEndpoint=false.')
param vnetResourceId string = ''

@description('Name of the subnet inside vnetResourceId that hosts the Key Vault private endpoint. Ignored when enableKeyVaultPrivateEndpoint=false.')
param keyVaultPrivateEndpointSubnetName string = 'snet-data'

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-${nameSuffix}'
  location: location
  tags: tags
  properties: {
    retentionInDays: logAnalyticsRetentionInDays
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

// Key Vault names are globally unique across all Azure and soft-delete-locked for 90 days.
// Add a short, deterministic per-(subscription, RG) suffix so ihzhhpf-based names don't collide.
var globalUniquenessSuffix = take(uniqueString(subscription().subscriptionId, resourceGroup().id), 4)
var effectiveKeyVaultName = empty(keyVaultName) ? 'kv-${nameSuffix}-${globalUniquenessSuffix}' : keyVaultName

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: effectiveKeyVaultName
  location: location
  tags: tags
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
    enableSoftDelete: true
    enablePurgeProtection: true
    // Required so ARM can resolve keyVault.getSecret() parameter references at deploy time (Sprint 00 source-SQL enable).
    enabledForTemplateDeployment: true
    // Pin publicNetworkAccess explicitly. The tenant-wide MCAPSGov
    // KeyVault_PublicNetwork_Modify policy (Modify effect, enforced at the
    // Tenant Root Management Group) forces this to Disabled unconditionally,
    // with or without a private endpoint -- confirmed live: SIT has no PE for
    // this vault yet is Disabled, and stays reachable for Bicep's own
    // getSecret()/getKeyVaultSecret() references because ARM resolves those
    // via a policy-exempt, trusted first-party channel, not the public data
    // plane. Hardcoding here (instead of tying it to enableKeyVaultPrivateEndpoint)
    // removes the perpetual what-if drift the previous conditional caused
    // (Bicep requested Enabled, policy silently re-disabled it every deploy).
    // enableKeyVaultPrivateEndpoint still controls whether the PE + private DNS
    // zone below are provisioned -- that is a genuine SIT/PROD topology
    // difference, unlike this property. See ADR-0039.
    publicNetworkAccess: 'Disabled'
    softDeleteRetentionInDays: 90
  }
}

// ============================================================================
// Key Vault private endpoint + private DNS zone (ADR-0039, extends ADR-0029
// Option A). Mirrors the Cosmos PE pattern in infra/modules/cosmos/csa.bicep.
//
// Required in PROD switzerlandnorth because the MCAPSGov policy force-disables
// Key Vault public network access subscription-wide; without a PE the AAD-only
// vault has no reachable data plane at all. The zone name is Azure-managed and
// MUST be exactly privatelink.vaultcore.azure.net for auto-registration to work.
// ============================================================================

var keyVaultPrivateEndpointName = 'pe-${effectiveKeyVaultName}'
var keyVaultPrivateDnsZoneName = 'privatelink.vaultcore.azure.net'

resource keyVaultPrivateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = if (enableKeyVaultPrivateEndpoint) {
  name: keyVaultPrivateDnsZoneName
  location: 'global'
  tags: tags
}

resource keyVaultPrivateDnsZoneVnetLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = if (enableKeyVaultPrivateEndpoint) {
  parent: keyVaultPrivateDnsZone
  name: '${last(split(vnetResourceId, '/'))}-link'
  location: 'global'
  tags: tags
  properties: {
    registrationEnabled: false
    virtualNetwork: {
      id: vnetResourceId
    }
  }
}

resource keyVaultPrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-11-01' = if (enableKeyVaultPrivateEndpoint) {
  name: keyVaultPrivateEndpointName
  location: location
  tags: tags
  properties: {
    subnet: {
      id: '${vnetResourceId}/subnets/${keyVaultPrivateEndpointSubnetName}'
    }
    privateLinkServiceConnections: [
      {
        name: '${keyVaultPrivateEndpointName}-conn'
        properties: {
          privateLinkServiceId: keyVault.id
          groupIds: [
            'vault'
          ]
        }
      }
    ]
  }
}

resource keyVaultPrivateDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-11-01' = if (enableKeyVaultPrivateEndpoint) {
  parent: keyVaultPrivateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'privatelink-vaultcore-azure-net'
        properties: {
          privateDnsZoneId: keyVaultPrivateDnsZone.id
        }
      }
    ]
  }
}

output keyVaultName string = keyVault.name
output logAnalyticsWorkspaceName string = logAnalyticsWorkspace.name
output logAnalyticsWorkspaceResourceId string = logAnalyticsWorkspace.id
