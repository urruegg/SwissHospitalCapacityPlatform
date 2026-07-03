# `fabric-eventstream` Bicep module

**Sprint 09 v2.0.0 · T2.2 · scaffold-only + REST-API post-deploy**

## Purpose

Provisions a Microsoft Fabric Eventstream that consumes from the Sprint 09 v2.0.0 Event Hub
(via consumer group `cg-fabric-eventstream` — T2.1) and appends raw event envelopes into a
Fabric Lakehouse at `Files/bronze/eventstream/`. This is the entry point for the
bronze → silver → gold notebook chain described in design spec §4.6.

Grounds design spec [§4.2 (Event Hubs topology)](../../../../docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md#42-event-hubs-topology).

## Why this module is scaffold-only

The `Microsoft.Fabric` ARM/Bicep provider only exposes `Microsoft.Fabric/capacities`
(API versions `2023-11-01` and `2025-01-15-preview`, verified via ARM provider metadata
on 2026-07-03). **Fabric items — workspaces, lakehouses, mirrors, and eventstreams — are
not first-class ARM resources.** They are provisioned exclusively via the Fabric REST API.

Per Sprint 09 v2.0.0 T2.2 guardrails and ADR-0014, the module therefore:

1. Declares design-spec §4.2 parameters as first-class Bicep inputs so that parent
   composition (`infra/main.bicep`) and `az deployment group what-if` remain accurate.
2. Emits an `eventstreamManifest` output that the companion PowerShell post-deploy
   script consumes.
3. Does **not** create the Eventstream from ARM. The parent orchestration must invoke
   `post-deploy/configure-eventstream.ps1` after the Bicep deployment completes.

This mirrors the pattern already established by `data-platform/fabric/main.bicep` +
`post-deploy/configure-fabric.ps1` for workspace + lakehouse + mirror (Sprint 08).

**When Microsoft ships a first-class ARM/Bicep type for Fabric Eventstream,** this module
should be rewritten to declare the resource directly. Track the resource-type ledger in
ADR-0014 (preview-resource-type gating) and open a Sprint 10+ follow-up when
`Microsoft.Fabric/workspaces/eventstreams` (or equivalent) shows up in the ARM
provider metadata.

## Parameters

| Name | Type | Default | Purpose |
|------|------|---------|---------|
| `workspaceId` | `string` (GUID, required) | — | Fabric workspace ID that hosts the Eventstream. Obtain via `GET /v1/workspaces` after workspace creation (see `configure-fabric.ps1` output). |
| `eventHubNamespace` | `string` (required) | — | Fully-qualified EH namespace hostname (e.g. `evh-ihzhhpf-sit-xxxx.servicebus.windows.net`). Wired from `data-foundation/eventhubs` module output. |
| `eventHubName` | `string` (required) | — | Event Hub name inside the namespace. Design spec §4.2 uses a single hub with routing by `eventKind`. |
| `eventHubConsumerGroup` | `string` | `cg-fabric-eventstream` | Consumer group the Eventstream subscribes to. Provisioned by Sprint 09 v2.0.0 T2.1. |
| `location` | `string` (`switzerlandnorth` \| `westus2`) | — | Deployment region. `switzerlandnorth` is the ADR-0003 default; `westus2` is the ADR-0013 demo-scope carve-out. |
| `demoScope` | `bool` | `false` | Set to `true` when deployed under ADR-0013 carve-out (US region, synthetic data only, no PHI). Documented in the output manifest so post-deploy can enforce the PHI-gate policy. |
| `eventstreamDisplayName` | `string` | `es-ihzhhpf-events` | Display name for the Eventstream item in the Fabric workspace. |
| `eventstreamDescription` | `string` | Sprint 09 v2.0.0 description | Item description. |
| `destinationLakehouseId` | `string` | `''` | Destination Lakehouse GUID. Empty defers destination wiring — Eventstream is created source-only and the post-deploy script emits a warning. |
| `destinationTablePrefix` | `string` | `bronze_eventstream` | Table name prefix under the Lakehouse. |

## Outputs

| Name | Type | Purpose |
|------|------|---------|
| `eventstreamManifest` | `object` | Consumed by `post-deploy/configure-eventstream.ps1`. Contains `provisioningMode`, `workspaceId`, `eventstream`, `source`, `destination`, and `guardrails` blocks. |
| `moduleStatus` | `string` | `fabric-eventstream-scaffold-only-see-post-deploy-script` — signals to parent orchestration that Bicep alone is insufficient. |
| `postDeployScriptPath` | `string` | Repo-relative path to the companion PS1. |

## Runtime dependencies (must exist before the post-deploy script runs)

1. **Fabric workspace + lakehouse** — provisioned by `data-platform/fabric` +
   `configure-fabric.ps1` (Sprint 00 / Sprint 08).
2. **Fabric-managed connection to the Event Hubs namespace** — created out-of-band via
   the Fabric portal or `POST /v1/connections`. Design spec §4.2 uses Fabric-managed
   connection auth (no connection strings). The connection ID must be substituted into
   the post-deploy PS1 (`<REQUIRES-FABRIC-MANAGED-CONNECTION-ID>` placeholder).
3. **Consumer group `cg-fabric-eventstream`** — provisioned by T2.1 in
   `infra/modules/data-foundation/eventhubs/main.bicep`.

## Swiss-region variant path

The `location` param is constrained to `['switzerlandnorth', 'westus2']` so a single
Bicep source can serve both the ADR-0013 demo-scope deployment (`westus2` today) and the
eventual Swiss-region flip when Fabric IQ reaches Swiss GA (`switzerlandnorth`, gated by
OPS-RISK-01 / ADR-0013). When flipping:

- Update `sit.bicepparam` and `prod.bicepparam` `location` values.
- Re-run the post-deploy script against the new-region workspace.
- Update `demoScope=false` in `sit.bicepparam` at flip time and confirm PHI-gate policy
  is enabled in silver notebook (T2.3).

The event-hub source, notebook chain, simulator, and semantic model in the rest of the
sprint are region-agnostic per design spec §4.9.

## Post-deploy invocation

```powershell
# Capture manifest from Bicep deployment outputs
az deployment group show `
  -g rg-ihzhhpf-sit `
  -n fabric-eventstream-sit `
  --query properties.outputs.eventstreamManifest.value `
  -o json > eventstream-manifest.json

# Materialise via Fabric REST API
./infra/modules/data-platform/fabric-eventstream/post-deploy/configure-eventstream.ps1 `
  -ManifestPath ./eventstream-manifest.json `
  -DryRun   # remove to actually POST
```

The PS1 must be edited to inject the Fabric-managed connection ID until it is passed
as a parameter (deferred to a Sprint 10 refinement — the connection ID cannot be
discovered via ARM).

## Known limitations

- **No what-if visibility on the Eventstream item itself.** `az deployment group what-if`
  will show the parameter/output shape of this module but nothing about the downstream
  Fabric REST calls. Coverage of the REST call chain is the responsibility of the
  post-deploy script's `-DryRun` mode.
- **Preview resource-type disclosure.** Even though this module does not declare a
  preview ARM type today, the Fabric REST APIs it exercises are themselves subject to
  Fabric preview terms (see ADR-0014). Consumers must accept ADR-0014 preview posture.
