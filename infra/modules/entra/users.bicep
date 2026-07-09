// Sprint 12 — Entra demo org: user personas.
//
// Creates one Entra user per row of the persona catalog
// (data/synthetic/personas.csv → design spec §6). Passwords are NEVER stored in
// the repo or in a parameter file: a temporary password is passed as a secure
// parameter at apply time and users must reset it on first sign-in
// (forceChangePasswordNextSignIn = true). See the T4 refusal rules in the plan.
//
// Requires the Microsoft Graph Bicep extension (see bicepconfig.json).

targetScope = 'subscription'

extension microsoftGraphV1_0

@description('Persona rows. Each item: { upn, displayName, appRole, defaultHospital, mailNickname }.')
param personas array

@description('Domain the personas must belong to. UPNs using any other domain are rejected (refusal rule).')
param allowedUpnDomain string = 'mngenvmcap164444.onmicrosoft.com'

@description('Temporary initial password. Provided securely at apply time; never committed. Users must reset on first sign-in.')
@secure()
param temporaryPassword string

// Refusal guard: fail the build/deployment if any UPN uses a non-approved domain.
var offendingUpns = filter(personas, persona => !endsWith(toLower(persona.upn), '@${allowedUpnDomain}'))

// Enforce the refusal rule at deploy time: if any persona uses a domain other than
// allowedUpnDomain this assertion fails and no users are created (T4 refusal rule).
assert noForeignUpnDomains = length(offendingUpns) == 0

resource users 'Microsoft.Graph/users@v1.0' = [
  for persona in personas: {
    accountEnabled: true
    displayName: persona.displayName
    mailNickname: persona.mailNickname
    userPrincipalName: persona.upn
    usageLocation: 'CH'
    passwordProfile: {
      password: temporaryPassword
      forceChangePasswordNextSignIn: true
    }
  }
]

@description('Refusal-rule assertion: no persona may use a domain other than allowedUpnDomain.')
output upnDomainGuard array = offendingUpns

@description('Created user object IDs, keyed by upn/appRole for downstream group membership + assignments.')
output userIds array = [
  for (persona, i) in personas: {
    upn: persona.upn
    appRole: persona.appRole
    id: users[i].id
  }
]
