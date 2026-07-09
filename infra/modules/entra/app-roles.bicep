// Sprint 12 — Entra demo org: app-role catalog (pure computation, no side effects).
//
// This module emits the full appRoles array that app-registration.bicep folds
// into the Microsoft.Graph/applications resource. It declares no resources and
// needs no extension — it exists so the role catalog is reviewable in one place
// and so the appRole GUIDs are deterministic (seeded from the app identifier +
// role value), which keeps `what-if` diffs stable across re-plans.
//
// Role catalog: 2 super roles (HCC.SuperAdmin, HCC.GuestReadOnly) + the
// operational/governance roles referenced by the persona catalog
// (docs/superpowers/specs/2026-07-09-sprint-12-org-design.md §6). See the module
// README for the note on the "15 vs 17" role-count reconciliation.

targetScope = 'subscription'

@description('Stable identifier used to seed deterministic appRole GUIDs (typically the app uniqueName, e.g. ihzhhpf-app).')
param appIdentifier string

// Two super roles (design spec §5).
var superRoles = [
  {
    value: 'HCC.SuperAdmin'
    displayName: 'HCC.SuperAdmin'
    description: 'Full read/write across all roles, hospitals, and environments. Only 1-2 assignees; not used for daily ops; PIM planned in a hardening sprint.'
  }
  {
    value: 'HCC.GuestReadOnly'
    displayName: 'HCC.GuestReadOnly'
    description: 'Read-only across all roles for demo tours. Cannot invoke agents; cannot open the CSA wizard; cannot mutate state.'
  }
]

// Operational + governance roles referenced by the persona catalog (design spec §6).
var operationalRoles = [
  {
    value: 'HCC.OperationsLead'
    displayName: 'HCC.OperationsLead'
    description: 'Hospital operations lead: cross-department capacity oversight for a single hospital context.'
  }
  {
    value: 'HCC.BedManager'
    displayName: 'HCC.BedManager'
    description: 'Bed management copilot user: bed state, assignment, and occupancy actions.'
  }
  {
    value: 'HCC.FlowManager'
    displayName: 'HCC.FlowManager'
    description: 'Patient-flow manager: transfers, admissions/discharge coordination across wards.'
  }
  {
    value: 'HCC.EDLead'
    displayName: 'HCC.EDLead'
    description: 'Emergency department lead: ED census, boarding, and admission pressure.'
  }
  {
    value: 'HCC.ORCoordinator'
    displayName: 'HCC.ORCoordinator'
    description: 'Operating-room coordinator: OR schedule and steering copilot user.'
  }
  {
    value: 'HCC.StaffingCoordinator'
    displayName: 'HCC.StaffingCoordinator'
    description: 'Staffing balance coordinator: shift and staffing-to-demand balancing.'
  }
  {
    value: 'HCC.DischargeCoordinator'
    displayName: 'HCC.DischargeCoordinator'
    description: 'Discharge coordinator: discharge readiness and downstream placement.'
  }
  {
    value: 'HCC.CrisisManager'
    displayName: 'HCC.CrisisManager'
    description: 'Crisis / scenario manager: surge and crisis-scenario copilot user.'
  }
  {
    value: 'HCC.Executive'
    displayName: 'HCC.Executive'
    description: 'Executive: aggregated cross-hospital capacity and value reporting.'
  }
  {
    value: 'HCC.CantonalViewer'
    displayName: 'HCC.CantonalViewer'
    description: 'Cantonal viewer: read-only aggregated cross-provider view (B2B invite deferred post-sprint).'
  }
  {
    value: 'HCC.PlatformAdmin'
    displayName: 'HCC.PlatformAdmin'
    description: 'Platform administrator: platform configuration and operations (non-super).'
  }
  {
    value: 'HCC.OntologySteward'
    displayName: 'HCC.OntologySteward'
    description: 'Ontology steward: semantic model and ontology governance.'
  }
  {
    value: 'HCC.AIGovernance'
    displayName: 'HCC.AIGovernance'
    description: 'AI governance: agent evaluation, safety, and responsible-AI oversight.'
  }
  {
    value: 'HCC.DemoOperator'
    displayName: 'HCC.DemoOperator'
    description: 'Demo operator: drives demo tours with a SIT demo override on hospital context.'
  }
  {
    value: 'HCC.Auditor'
    displayName: 'HCC.Auditor'
    description: 'Auditor: read-only access to governance evidence and audit trails.'
  }
]

var roleCatalog = concat(superRoles, operationalRoles)

@description('Full appRoles array for the Microsoft.Graph/applications resource.')
output roles array = [
  for role in roleCatalog: {
    id: guid(appIdentifier, role.value)
    displayName: role.displayName
    description: role.description
    value: role.value
    allowedMemberTypes: [
      'User'
    ]
    isEnabled: true
  }
]

@description('Ordered list of role values, reused by security-groups and assignments.')
output roleValues array = [for role in roleCatalog: role.value]
