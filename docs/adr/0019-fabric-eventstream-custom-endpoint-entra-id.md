# ADR-0019 — Fabric Eventstream ingest via Custom Endpoint + Entra ID (MCAPS baseline forced pivot)

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-07-08 |
| **Author** | Urs Rüegg |
| **Supersedes (scoped)** | Design spec §4.2 ingest topology for Sprint 09 v2 T2.2 and Sprint 10 T1 (S10.1) — for the SIT MCAPS-hosted demo scope only; the original Azure Event Hubs → Fabric Eventstream design remains the target once the sunset conditions in §Sunset criteria are met. |

## Context

Sprint 09 v2 T2 stood up an Azure Event Hubs namespace (`evh-ihzhhpf-sit-y26y`) with a single hub `events` and three consumer groups (`cg-fabric-eventstream`, `cg-bm-copilot-agent`, `cg-csa-agent`) as the ingest surface. Sprint 10 T1 (S10.1) was to add a Fabric Eventstream on top, using Fabric's built-in *Azure Event Hubs* source connector.

During T1 execution on 2026-07-07/08 we hit two independent, hard blockers when trying to create the Fabric source connection:

1. **Fabric connector auth constraint.** The Fabric *Azure Event Hubs* source connector (Basic and Extended feature levels) only supports **Shared Access Key** authentication today. OAuth 2.0 appears in the connection dropdown but is rejected at runtime with `Unable to connect to the data source ... credentials invalid`. Verified against [add-source-azure-event-hubs](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-source-azure-event-hubs#configure-an-azure-event-hubs-connector) and confirmed by testing hub-scope `Azure Event Hubs Data Receiver` + tenant-admin OAuth token in the portal.

2. **MCAPS tenant Modify policy.** The MCAPS sandbox tenant (`MngEnvMCAP164444`) enforces `disableLocalAuth=true` on Event Hubs namespaces via a `Microsoft.Authorization/policies/modify` effect at management-group scope. Every attempt to set `disableLocalAuth=false` on `evh-ihzhhpf-sit-y26y` — via `az resource update`, direct ARM PATCH, or Bicep — is auto-reverted to `true` within seconds. Confirmed by the activity log showing a `policies/modify` event immediately after each `namespaces/write`. We cannot exempt, disable, or override this policy (Microsoft owns the definition).

The intersection of (1) and (2) means SAS ingest is architecturally impossible in this tenant, and OAuth ingest is not supported by the connector. The only remaining first-class Fabric ingest path with Entra ID authentication is the **Custom Endpoint source** on Eventstream, where producers push directly to a Fabric-hosted EH-compatible endpoint using Entra ID tokens.

## Decision

For the SIT MCAPS-hosted demo scope only, pivot the Sprint 10 T1 ingest architecture:

- **Sink:** Fabric Eventstream `es-capacity-events-sit` (`7b65dfa1-c523-412f-93b2-a78eaa2788fa`) in workspace `ws-ihzhhpf-sit-data` (`f3af9733-9503-4e92-98f9-a901d96f1c87`) with a **Custom Endpoint source** named `capacity-events-source`.
- **Producer:** the existing sim-capacity producer (`apps/sim-capacity/src/emitters/eventhub_emitter.py`) retargets to the Fabric endpoint via env-var change only — the `azure-eventhub` AMQP client + `DefaultAzureCredential` work unchanged against the Custom Endpoint.
- **Producer identity:** the existing User-Assigned Managed Identity `id-ca-sim-capacity-ihzhhpf-sit` (Entra objectId `b646f093-cbbc-496f-8a65-376b39ff04d3`) assigned as **Contributor** on the workspace via Fabric REST.
- **No new Service Principal or SAS key is introduced.** This preserves [.github/copilot-instructions.md](../../.github/copilot-instructions.md) §4 ("no long-lived client secrets").
- **Azure EH becomes vestigial for the ingest path.** `evh-ihzhhpf-sit-y26y`, its `events` hub, and the three consumer groups stay provisioned during Sprint 10 (avoids churn against the drift baseline), and are re-evaluated in Sprint 11 hygiene for deletion or repurposing.
- **Agent subscribers** (BM-Copilot, CSA) subscribe to **Fabric-side outputs** (Lakehouse Delta or KQL DB) that the Eventstream lands to, not to Azure EH consumer groups. Their MI role assignments on the Azure EH hub remain in place until the vestigial resources are decided in Sprint 11.

Scope boundary (all conditions must hold; violating any one auto-invalidates the exception):

1. **Tenant:** `1337187a-4c41-4da9-8fca-731bba7a4329` (MCAPS `MngEnvMCAP164444`) only.
2. **Environment:** SIT only. PROD is out of scope (PROD hosts no Fabric Eventstream on MCAPS today; when it does, the sunset check below applies).
3. **Data:** Synthetic only per [ADR-0016](0016-no-phi-in-mvp-demo-scope.md).
4. **Duration:** Time-limited by the sunset criteria below.

## Sunset criteria

Revisit and restore the original Azure EH → Fabric Eventstream design when either:

1. Fabric ships **Managed Identity** support for the Azure Event Hubs source connector (public preview or GA), removing the SAS-only constraint. Verify by re-running the T1 golden-task fixture against the new connector option. **OR**
2. We exit the MCAPS tenant to a customer-owned tenant where the `disableLocalAuth=true` Modify policy does not apply, restoring the ability to use SAS as documented. Track exit under the tenant-migration ADR family.

On sunset:

- Author a superseding ADR (e.g. ADR-00NN) documenting the reversal.
- Revert [`infra/environments/sit.bicepparam`](../../infra/environments/sit.bicepparam) — `simCapacityEventHubNamespace` and `simCapacityEventHubName` back to the Azure EH values (namespace resolved from data-foundation module output, name `demand-encounters` or the current design-spec name).
- Delete the Fabric Custom Endpoint source and reassign it to *Azure Event Hubs* source in Eventstream authoring.
- Move this ADR to **Superseded** and link the superseder.

## Consequences

**Positive:**

- Unblocks Sprint 10 T1 in the MCAPS tenant.
- No new Service Principal or SAS key — the security posture in [.github/copilot-instructions.md](../../.github/copilot-instructions.md) §4 stays intact.
- No producer code change; only env-var reconfiguration via [`infra/environments/sit.bicepparam`](../../infra/environments/sit.bicepparam) and the Container App restart that follows CI.
- The Custom Endpoint pattern is what Microsoft documents as the *Entra ID* path in [connect-using-managed-identity](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/connect-using-managed-identity) and [custom-endpoint-entra-id-auth](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/custom-endpoint-entra-id-auth) — supported, not a workaround.

**Negative / risks:**

- The Azure EH namespace, hub, and consumer groups become vestigial for ingest until the Sprint 11 hygiene decision. They still accrue Standard-tier billing (~USD 22/month for the namespace at the base capacity) — accepted per [ADR-0013](0013-temporary-us-region-demo-scope.md) demo scope.
- Agent MI role assignments on the Azure EH hub become vestigial too. Removing them prematurely would create rollback friction if we sunset this ADR before Sprint 11 hygiene; keeping them is a small least-privilege noise.
- Custom Endpoint is a Fabric-scoped surface, so producers cannot use a private endpoint into the customer VNet the way Azure EH would allow. Not an issue for the demo (public network access is fine per [ADR-0013](0013-temporary-us-region-demo-scope.md)); becomes an issue when we exit MCAPS to a PHI-capable tenant — that is one of the sunset triggers.
- Fabric Custom Endpoint identity is a Fabric-owned SPN; there is no ARM role assignment to point at from `main.bicep`. Producer workspace membership is granted via Fabric REST from a post-deploy step, not from Bicep, which is documented in the runbook but is a small IaC drift with our normal pattern.

**Governance actions triggered by this ADR:**

- [`infra/environments/sit.bicepparam`](../../infra/environments/sit.bicepparam) — `simCapacityEventHubNamespace` and `simCapacityEventHubName` updated to the Fabric Custom Endpoint values, comment references this ADR.
- [`docs/superpowers/specs/2026-07-06-sprint-10-t1-eventstream-design.md`](../superpowers/specs/2026-07-06-sprint-10-t1-eventstream-design.md) — updated design brief cross-linking this ADR (follow-up PR).
- Sprint 11 backlog — tracker issue for the Azure EH vestigial cleanup decision (delete namespace + hub + consumer groups + agent role assignments, or repurpose).
- `docs/PRD.md` and `docs/DATA.md` — no immediate change; the ingest boundary shifts from Azure EH to Fabric Custom Endpoint but data contracts and downstream Lakehouse landing are unchanged.

## References

- [.github/copilot-instructions.md](../../.github/copilot-instructions.md) §4 — no long-lived secrets
- [ADR-0013](0013-temporary-us-region-demo-scope.md) — demo scope, sunset triggers overlap
- [ADR-0016](0016-no-phi-in-mvp-demo-scope.md) — synthetic-only data
- [`infra/environments/sit.bicepparam`](../../infra/environments/sit.bicepparam) — the Bicep param file this ADR governs
- [`apps/sim-capacity/src/emitters/eventhub_emitter.py`](../../apps/sim-capacity/src/emitters/eventhub_emitter.py) — producer emitter unchanged
- Microsoft Learn — [add-source-azure-event-hubs](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-source-azure-event-hubs) — SAS-only constraint on the Azure EH source connector
- Microsoft Learn — [custom-endpoint-entra-id-auth](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/custom-endpoint-entra-id-auth) — Entra ID auth for Custom Endpoint (chosen pattern)
