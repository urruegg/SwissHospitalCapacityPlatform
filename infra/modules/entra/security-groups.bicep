// Sprint 12 — Entra demo org: security groups (one per app role).
//
// Creates one mail-disabled security group per app-role value (convention:
// group displayName == app-role value). Group membership is set here from the
// created user object IDs: each group contains exactly the personas whose
// app_role matches the group's role value. App-role *assignment* of the group
// to the service principal is handled in assignments.bicep.
//
// Requires the Microsoft Graph Bicep extension (see bicepconfig.json).

targetScope = 'subscription'

extension microsoftGraphV1_0

@description('Ordered role values (from app-roles.bicep), one security group per value.')
param roleValues array

@description('Created user object IDs: array of { upn, appRole, id } (from users.bicep).')
param userIds array = []

resource groups 'Microsoft.Graph/groups@v1.0' = [
  for roleValue in roleValues: {
    uniqueName: roleValue
    displayName: roleValue
    description: 'Security group backing the ${roleValue} app role (group-based assignment).'
    mailEnabled: false
    mailNickname: replace(roleValue, '.', '-')
    securityEnabled: true
    members: {
      relationships: map(filter(userIds, member => member.appRole == roleValue), member => member.id)
    }
  }
]

@description('Created group object IDs, keyed by role value, for appRole assignment in assignments.bicep.')
output groupIds array = [
  for (roleValue, i) in roleValues: {
    value: roleValue
    id: groups[i].id
  }
]
