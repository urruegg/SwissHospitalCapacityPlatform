// Sprint 12 — Entra demo org: subscription-scope orchestrator.
//
// Chains the Entra provisioning modules for the ihzhhpf-app demo organisation:
//   app-roles      → the 17-role catalog (2 super + operational/governance)
//   app-registration → the app + service principal, appRoles folded in
//   users          → 23 personas (design spec §6)
//   security-groups → one group per role, members set from personas
//   assignments    → group-based app-role assignments to the service principal
//
// Deploy with: az deployment sub create --location westus2 \
//   --template-file infra/modules/entra/main.bicep \
//   --parameters infra/modules/entra/parameters/sit.bicepparam \
//   --parameters temporaryPassword=<secure-value>
//
// Every apply is a `deploy`-ceiling action gated behind an `approved-to-apply`
// comment (AGENTS.md §4). adoption-telemetry.bicep is deployed separately (it
// targets tenant-scoped Azure AD diagnostic settings).
//
// Requires the Microsoft Graph Bicep extension (see bicepconfig.json).

targetScope = 'subscription'

@description('Solution short name, per copilot-instructions.md §8 naming convention.')
param solutionShort string = 'ihzhhpf'

@description('Environment tag: sit or prod. The app + identities are shared across slots; env scoping is in-app (design spec §4).')
@allowed([
  'sit'
  'prod'
])
param env string

@description('SPA redirect URIs (Sprint 13 app + Sprint 15 BVA report) for this env slot.')
param spaRedirectUris array

@description('Persona rows. Each item: { upn, displayName, appRole, defaultHospital, mailNickname }.')
param personas array = []

@description('Temporary initial password for created personas. Provided securely at apply time; never committed.')
@secure()
param temporaryPassword string = ''

var appIdentifier = '${solutionShort}-app'

module appRoles './app-roles.bicep' = {
  name: 'appRoles-${env}'
  params: {
    appIdentifier: appIdentifier
  }
}

module appReg './app-registration.bicep' = {
  name: 'appReg-${env}'
  params: {
    solutionShort: solutionShort
    env: env
    spaRedirectUris: spaRedirectUris
    appRoles: appRoles.outputs.roles
  }
}

module users './users.bicep' = {
  name: 'users-${env}'
  params: {
    personas: personas
    temporaryPassword: temporaryPassword
  }
}

module securityGroups './security-groups.bicep' = {
  name: 'groups-${env}'
  params: {
    roleValues: appRoles.outputs.roleValues
    userIds: users.outputs.userIds
  }
}

module assignments './assignments.bicep' = {
  name: 'assignments-${env}'
  params: {
    appIdentifier: appIdentifier
    servicePrincipalId: appReg.outputs.servicePrincipalId
    groupIds: securityGroups.outputs.groupIds
  }
}

output appId string = appReg.outputs.appId
output appObjectId string = appReg.outputs.appObjectId
output servicePrincipalId string = appReg.outputs.servicePrincipalId
output roleCount int = length(appRoles.outputs.roleValues)
output personaCount int = length(personas)
