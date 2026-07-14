// Sprint 12 completion — SIT groups + assignments only.
//
// Same as sit.bicepparam but with personas cleared to bypass the Microsoft.Graph/users
// read-only limitation (confirmed by Microsoft Learn: users is read-only in the Graph
// Bicep extension at v1.0 and beta). MCAPS tenant restriction: no real user provisioning.
// The 17 HCC.* security groups + 17 group→role assignments still deploy — group
// membership is added out-of-band via `az ad group member add` for admin@ + urruegg@.
//
// Reference: partial-deploy state 2026-07-13 (deployment: entra-sit-20260713103046)
//   ✅ ihzhhpf-app (sit) — appId 52681a08-c792-44b1-b6b5-01cb560d450f
//   ✅ Service principal — id 667b8c54-c741-4832-b1e7-fe75eea5163c
//   ✅ 17 app roles embedded in app
//   ❌ 23 users (blocked by extension design; MCAPS decision: skip user creation)
//   ⏸️ 17 groups (this deployment)
//   ⏸️ 17 assignments (this deployment)
using '../main.bicep'

param solutionShort = 'ihzhhpf'
param env = 'sit'
param spaRedirectUris = [
  // Sprint 13.1 ADR-0030 custom hostname — must stay in sync with sit.bicepparam.
  // This groups-only variant is used for identity-only slice deploys; still
  // needs the correct redirect URIs on the shared ihzhhpf-app registration.
  'https://appsit.curavias.ch'
  'https://ca-app-fluent-ihzhhpf-sit.ashysky-8f51a689.westus2.azurecontainerapps.io'
  'https://app-platform-ihzhhpf-sit.azurewebsites.net'
  'http://localhost:5173'
]
// PERSONAS INTENTIONALLY EMPTY — see file-header rationale.
param personas = []
