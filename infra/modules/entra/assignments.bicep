// Sprint 12 — Entra demo org: group-based app-role assignments.
//
// Assigns each security group to the app registration's service principal with
// the matching app role, so members of the group receive the role in the app's
// `roles` claim. Uses group-based assignment (principal = group), never direct
// user-to-app-role, per design spec §2.1 + §4.
//
// The appRole GUIDs are recomputed deterministically from the same seed used in
// app-roles.bicep (guid(appIdentifier, roleValue)), so no cross-module wiring of
// role IDs is required.
//
// Requires the Microsoft Graph Bicep extension (see bicepconfig.json).

targetScope = 'subscription'

extension microsoftGraphV1_0

@description('App uniqueName used to seed deterministic appRole GUIDs (must match app-roles.bicep appIdentifier).')
param appIdentifier string

@description('Service principal object ID of the app registration (resourceId of the assignment).')
param servicePrincipalId string

@description('Created group object IDs: array of { value, id } (from security-groups.bicep).')
param groupIds array

resource groupAppRoleAssignments 'Microsoft.Graph/appRoleAssignedTo@v1.0' = [
  for group in groupIds: {
    appRoleId: guid(appIdentifier, group.value)
    principalId: group.id
    resourceId: servicePrincipalId
  }
]

@description('Number of group-based app-role assignments created.')
output assignmentCount int = length(groupIds)
