// Sprint 12 — Entra demo org: app registration + service principal.
//
// Declares the single ihzhhpf-app registration (one per tenant, shared across
// the SIT and PROD slots per design decision D-6) with the full appRoles catalog
// folded in from app-roles.bicep, plus its service principal (needed as the
// resourceId for group-based appRole assignments in assignments.bicep).
//
// Requires the Microsoft Graph Bicep extension (see bicepconfig.json). Graph
// resources are provisioned at tenant scope by the extension regardless of the
// deployment target scope.

targetScope = 'subscription'

extension microsoftGraphV1_0

@description('Solution short name (copilot-instructions.md §8), used to build the app uniqueName.')
param solutionShort string = 'ihzhhpf'

@description('Environment tag: sit or prod. Used only in the friendly displayName; the app is shared across slots.')
@allowed([
  'sit'
  'prod'
])
param env string

@description('SPA redirect URIs for the Sprint 13 app + Sprint 15 BVA report (env-specific slot URLs).')
param spaRedirectUris array

@description('Full appRoles array, produced by app-roles.bicep.')
param appRoles array

var appUniqueName = '${solutionShort}-app'

resource app 'Microsoft.Graph/applications@v1.0' = {
  uniqueName: appUniqueName
  displayName: '${appUniqueName} (${env})'
  signInAudience: 'AzureADMyOrg'
  appRoles: appRoles
  spa: {
    redirectUris: spaRedirectUris
  }
  requiredResourceAccess: [
    {
      resourceAppId: '00000003-0000-0000-c000-000000000000' // Microsoft Graph
      resourceAccess: [
        {
          id: 'e1fe6dd8-ba31-4d61-89e7-88639da4683d' // User.Read (delegated)
          type: 'Scope'
        }
      ]
    }
  ]
}

resource servicePrincipal 'Microsoft.Graph/servicePrincipals@v1.0' = {
  appId: app.appId
  appRoleAssignmentRequired: true
}

@description('Application (client) ID of the app registration.')
output appId string = app.appId

@description('Directory object ID of the application.')
output appObjectId string = app.id

@description('Directory object ID of the service principal (resourceId for appRole assignments).')
output servicePrincipalId string = servicePrincipal.id
