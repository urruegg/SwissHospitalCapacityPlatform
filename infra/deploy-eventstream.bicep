targetScope = 'resourceGroup'

// Sprint 10 T1 (S10.1) — narrow deploy scope for the Fabric Eventstream module only.
//
// Why this exists: on 2026-07-06 the full-scope what-if on infra/main.bicep flagged 15
// Modify changes on unrelated resources (config drift between the live SIT state and the
// current Bicep declarations — ACR security policies, KV public network access, ASP SKU,
// VNet subnets, etc.). Deploying main.bicep to enable the eventstream would have
// reconciled all that drift as a side effect. Restructure per Sprint 10 T1 plan
// Option 3 keeps the eventstream enable surgical.
//
// Inline params (not a .bicepparam file) because:
//   1. Values are fixed for the SIT deploy (workspace + lakehouse GUIDs from checkpoint §2.2).
//   2. This template is a one-time enable — not part of the recurring infra/main.bicep flow.
//   3. Avoids editing sit.bicepparam and re-triggering the full-scope drift.
//
// Drift reconciliation for the other 15 resources is tracked as S10.15 (raised alongside
// this template) and out of scope here.
//
// PROD replication: when PROD needs Eventstream, either author deploy-eventstream-prod.bicep
// with equivalent inline params or (preferred) reconcile drift on main.bicep + PROD's
// bicepparam and fold the eventstream module back into main.bicep.

@description('Fabric workspace ID hosting the Eventstream. SIT default per checkpoint §2.2.')
param workspaceId string = 'f3af9733-9503-4e92-98f9-a901d96f1c87'

@description('Destination Lakehouse ID inside the workspace. SIT lh_ihzhhpf_sit per checkpoint §2.2.')
param destinationLakehouseId string = '30594c20-46ba-40ea-91fa-4701b105e0b9'

@description('Event Hubs namespace fully-qualified hostname.')
param eventHubNamespace string = 'evh-ihzhhpf-sit.servicebus.windows.net'

@description('Event Hub name for capacity events (Sprint 09 v2 T2.1).')
param eventHubName string = 'evh-capacity-events-sit'

@description('Deployment region — westus2 per ADR-0013 demo-scope carve-out.')
@allowed([
  'westus2'
  'switzerlandnorth'
])
param location string = 'westus2'

module eventstream 'modules/data-platform/fabric-eventstream/main.bicep' = {
  name: 'sprint10-t1-eventstream'
  params: {
    workspaceId: workspaceId
    eventHubNamespace: eventHubNamespace
    eventHubName: eventHubName
    // eventHubConsumerGroup uses module default (cg-fabric-eventstream)
    location: location
    demoScope: true
    // eventstreamDisplayName + description use module defaults (es-ihzhhpf-events)
    destinationLakehouseId: destinationLakehouseId
    // destinationTablePrefix uses module default (bronze_eventstream)
  }
}

@description('Manifest consumed by post-deploy/configure-eventstream.ps1.')
output eventstreamManifest object = eventstream.outputs.eventstreamManifest

@description('Human-readable status.')
output moduleStatus string = eventstream.outputs.moduleStatus

@description('Path to companion PS1 that materialises the Eventstream via Fabric REST.')
output postDeployScriptPath string = eventstream.outputs.postDeployScriptPath
