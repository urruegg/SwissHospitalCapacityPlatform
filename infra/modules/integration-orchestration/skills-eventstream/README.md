# `skills-eventstream` Bicep module

> Sprint 23 · WS-A4 · design D4 · scaffold-only Bicep + REST-API post-deploy

## Purpose

Provisions the **skills-events** Microsoft Fabric Eventstream — the near-real-time lane
(design [D4](../../../../docs/superpowers/specs/2026-07-23-sprint-23-org-skills-refactor-design.md))
that carries **only** the three skills events which must move faster than the next batch
master-data load:

- `credential-expiry`
- `consent-grant-or-revoke`
- `newly-confirmed-assertion`

Everything else (HRIS/LMS master data) flows through the batch/ADLS landing-zone lane
(WS-A1..A3). Events land at `Files/bronze/skills-events/` (Lakehouse table
`bronze_skills_events`), the entry point for the
[`data-platform/notebooks/skills-events`](../../../../data-platform/notebooks/skills-events/README.md)
bronze → silver → gold chain (the silver notebook is the PHI/consent gate).

## Source transport — `sourceMode`

| `sourceMode` | Status | Description |
|--------------|--------|-------------|
| `CustomEndpoint` (**default**) | **Live-deployable today** | Mirrors the working `es-capacity-events-sit` topology. Fabric exposes an Event-Hub-compatible ingestion endpoint on the Eventstream; the Container Apps publisher (NFR-SKILL-001) POSTs `DC-SKILL-EVENT-v1` envelopes to it. No out-of-band connection required. This is the ADR-0013 demo-scope path. |
| `EventHub` | **Un-parked for PROD swn** ([ADR-0043](../../../../docs/adr/0043-preview-tier-permitted-in-prod-swn-for-demo.md)) | Consumes a dedicated skills-events Event Hub → Eventstream. **GA in Switzerland North** (Eventstream + Event Hubs both GA; PROD namespace `evh-ihzhhpf-prod-i62t` exists in-region), so it does not consume the preview exception. Requires a **Fabric-managed connection** to the EH namespace (`POST /v1/connections`) that does not exist yet; the post-deploy script refuses to wire an EH source until it does. Fed by a **simulator** until the live publisher lands. The GA-only gate is reserved for a real go-live (real-PHI) cut-over. |

The demo carve-out (CustomEndpoint) and the target-state (EventHub) share one Bicep source;
flip `sourceMode` when the managed connection is provisioned. The EventHub flip is un-parked for
PROD Switzerland North per [ADR-0043](../../../../docs/adr/0043-preview-tier-permitted-in-prod-swn-for-demo.md).
See design spec §6 open items.

## Why this module is scaffold-only

The `Microsoft.Fabric` ARM/Bicep provider only exposes `Microsoft.Fabric/capacities`.
Fabric items — workspaces, lakehouses, eventstreams — are **not** first-class ARM resources;
they are provisioned exclusively via the Fabric REST API (same rationale as the sibling
[`data-platform/fabric-eventstream`](../../data-platform/fabric-eventstream/README.md) module
and ADR-0014). This module therefore:

1. Declares the design-D4 parameters as first-class Bicep inputs so parent composition
   (`infra/main.bicep`) and `az deployment group what-if` stay accurate.
2. Emits an `eventstreamManifest` output consumed by the companion post-deploy script.
3. Creates **no ARM resources** (its what-if footprint is additive/empty).

## Parameters

| Name | Type | Default | Purpose |
|------|------|---------|---------|
| `workspaceId` | `string` (GUID) | `''` | Fabric workspace that hosts the Eventstream. Required at post-deploy time. |
| `sourceMode` | `string` (`CustomEndpoint` \| `EventHub`) | `CustomEndpoint` | Source transport (see table above). |
| `eventHubNamespace` | `string` | `''` | EH namespace host. Only used when `sourceMode=EventHub`. |
| `eventHubName` | `string` | `''` | EH name. Only used when `sourceMode=EventHub`. |
| `eventHubConsumerGroup` | `string` | `cg-skills-eventstream` | Consumer group. Only used when `sourceMode=EventHub`. |
| `location` | `string` (`switzerlandnorth` \| `westus2`) | — | Region. `westus2` is the ADR-0013 demo carve-out. |
| `demoScope` | `bool` | `false` | `true` under ADR-0013 (US region, synthetic data, no PHI). |
| `eventstreamDisplayName` | `string` | `es-ihzhhpf-skills-events` | Eventstream item display name. |
| `destinationLakehouseId` | `string` | `''` | Destination Lakehouse GUID. Empty ⇒ source-only (warning emitted). |
| `destinationTablePrefix` | `string` | `bronze_skills_events` | Destination Delta table name. |

## Outputs

| Name | Type | Purpose |
|------|------|---------|
| `eventstreamManifest` | `object` | Consumed by `post-deploy/configure-skills-eventstream.ps1`. |
| `allowedEventKinds` | `array` | The exactly-three D4 event kinds. |
| `moduleStatus` | `string` | Signals scaffold-only to parent orchestration. |
| `postDeployScriptPath` | `string` | Repo-relative path to the companion PS1. |

## Post-deploy invocation

```powershell
# 1. Capture the manifest from the Bicep module output (or hand-author it from the params).
az deployment group show `
  -g rg-ihzhhpf-sit -n skills-eventstream-sit `
  --query properties.outputs.eventstreamManifest.value -o json > skills-eventstream-manifest.json

# 2. Dry-run (validates the three-kind guardrail + prints the topology).
./post-deploy/configure-skills-eventstream.ps1 -ManifestPath ./skills-eventstream-manifest.json -DryRun

# 3. Live create (CustomEndpoint source). Idempotent; -Force replaces an existing item.
./post-deploy/configure-skills-eventstream.ps1 `
  -ManifestPath ./skills-eventstream-manifest.json `
  -WorkspaceId f3af9733-... -DestinationLakehouseId 30594c20-...

# 4. Live create (EventHub source, PROD swn / ADR-0043). Requires the dedicated skills-events
#    hub (auto-provisioned by the eventhubs module) + a Fabric-managed connection GUID.
./post-deploy/configure-skills-eventstream.ps1 `
  -ManifestPath ./skills-eventstream-manifest.json `
  -WorkspaceId <prod-swn-ws> -DestinationLakehouseId <prod-swn-lh> `
  -ConnectionId <fabric-managed-connection-guid>
```

### EventHub-source publish (simulator, until the live connector lands)

```powershell
# Publish synthetic DC-SKILL-EVENT-v1 records to the dedicated per-domain hub (MI Data Sender).
cd data-platform/scripts/skills-events
$env:PYTHONPATH="."
python publish_skill_events.py --dry-run   # offline validation, sends nothing
python publish_skill_events.py `
  --namespace evh-ihzhhpf-prod-i62t.servicebus.windows.net --eventhub skills-events
```

The script is **idempotent** (skips when the display name already exists) and **async-safe**
(Fabric item creation returns 202; the script resolves the id by display-name lookup with retry).

## Guardrails

- **Narrow scope (D4):** the script asserts the manifest carries **exactly** the three allowed
  event kinds and refuses otherwise. Broadening the set is a design change.
- **PHI gate is downstream:** the Eventstream lands raw synthetic envelopes; the PHI/consent
  gate + kind allow-list enforcement is performed by the **silver skills-events notebook**
  (deny-by-default quarantine), per `guardrails.phiGateEnforcedBy`.
- **No secrets committed:** the CustomEndpoint ingestion connection string (SharedAccessKey)
  is retrieved at publish-time via `GET …/eventstreams/{id}/sources/{sourceId}/connection`
  and stored in Key Vault — never in the repo.

## Runtime dependencies (must exist before the post-deploy script runs)

1. **Fabric workspace + destination lakehouse** — provisioned by `data-platform/fabric` +
   `configure-fabric.ps1`.
2. **(EventHub sourceMode only) dedicated skills-events Event Hub entity** — the
   `data-foundation/eventhubs` module auto-provisions a per-domain `skills-events` hub +
   `cg-skills-eventstream` consumer group inside the environment's namespace whenever the skills
   lane runs in `sourceMode=EventHub` (parent derives `enableSkillsEventHub`). The envelope is thus
   isolated by functional domain from the capacity `events` rail.
3. **(EventHub sourceMode only) Fabric-managed connection** to the Event Hubs namespace — created
   out-of-band via `POST /v1/connections`; its GUID is passed to the post-deploy script via
   `-ConnectionId`. The script refuses a live EventHub wire without it.
4. **(EventHub sourceMode only) a publisher** — until the live HRIS/LMS connector lands, the
   [`publish_skill_events.py`](../../../../data-platform/scripts/skills-events/publish_skill_events.py)
   **simulator** emits synthetic `DC-SKILL-EVENT-v1` records (one AMQP message per record, routed by
   the `eventKind` property) to the dedicated hub via Managed Identity (`Data Sender`).

## Swiss-region variant path

`location` is constrained to `['switzerlandnorth', 'westus2']` so one source serves both the
ADR-0013 SIT demo (`westus2`/`eastus2` per enabled capacity) and the PROD Switzerland North
deployment (`switzerlandnorth`). SIT and PROD do **not** share input services — each environment
uses its own Event Hubs namespace (`evh-ihzhhpf-sit-y26y` vs `evh-ihzhhpf-prod-i62t`). When flipping
PROD swn to `sourceMode=EventHub` set `demoScope=false`, re-run the post-deploy script against the
PROD-swn workspace, and confirm the silver PHI gate is enforced. Per
[ADR-0043](../../../../docs/adr/0043-preview-tier-permitted-in-prod-swn-for-demo.md) the flip is
un-parked (GA-in-swn); the GA-only gate is reserved for a real go-live cut-over.

## Known limitations

- **No what-if visibility on the Eventstream item itself** — `what-if` shows the module
  parameter/output shape but nothing about the downstream Fabric REST calls. The script's
  `-DryRun` mode covers the REST call chain.
- **Preview posture** — the Fabric REST APIs exercised here are subject to Fabric preview
  terms (ADR-0014).
