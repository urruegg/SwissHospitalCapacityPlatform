# Sprint 19 — PROD Switzerland North rebuild: baseline execution record

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-23 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | — (new evidence artefact) |

Execution record for the Phase 1–4 baseline slice of the DR-style teardown +
Switzerland North greenfield rebuild ([ADR-0037](../../../adr/0037-prod-region-switzerland-north-greenfield.md),
issue [#239](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/239)).
Runbook: [`sprint-19-prod-switzerland-north-dr-rebuild-runbook.md`](../../../runbooks/sprint-19-prod-switzerland-north-dr-rebuild-runbook.md).

Approval: `approved-to-apply` granted in-session by repo OWNER @urruegg
(2026-07-23). Teardown (Phase 0) evidence recorded on #239.

## Key Vault name-collision fix

The deterministic `uniqueString(subscription().subscriptionId, resourceGroup().id)`
seed used for globally-unique names resolves to the **same `i62t` token** as the
decommissioned **westus2** `rg-ihzhhpf-prod` — because both the subscription and
the resource-group name are identical. That left `kv-ihzhhpf-prod-i62t`
**soft-deleted and purge-protected until 2026-10-16**; the name is globally
reserved and cannot be purged early, so reusing it would fail the deploy.

Fix (additive, backward-compatible):

- `infra/modules/platform-foundation/main.bicep` — new optional `keyVaultName`
  param (`@maxLength(24)`). Empty (default) keeps the auto-generated
  deterministic name, so **SIT is unchanged**.
- `infra/main.bicep` — new optional `keyVaultNameOverride` param, forwarded to
  `platform-foundation`.
- `infra/environments/prod-swn.bicepparam` — sets
  `keyVaultNameOverride = 'kv-ihzhhpf-prod-swn1'`.

Event Hubs / Service Bus namespaces reuse the same seed
(`evh-/sb-ihzhhpf-prod-i62t`) but have **no soft-delete**, so those names freed
when the old RG was deleted in Phase 0 — only the Key Vault collided.

## Baseline what-if

`az deployment group what-if` → `Succeeded`, 33 changes: **31 Create, 1 Ignore,
1 Unsupported, 0 Delete**. `az bicep build-params` exit 0.

## Apply

`az deployment group create -n sprint19-prod-swn-baseline -g rg-ihzhhpf-prod`
→ **provisioningState: Succeeded**.

The first attempt failed on a ~2-second ARM eventual-consistency race: the
parent `agent-host-prod` deployment read the agent-host managed identity via an
`existing` reference (for the Cosmos `sqlRoleAssignment`) ~2s after the nested
`agent-host-container-app` deployment created it (`ResourceNotFound`). The MI
and both Container Apps were already `Succeeded`; the idempotent re-run cleared
it with no resource changes.

## Runtime verification

| Endpoint | Result |
|----------|--------|
| `ca-agent-host-ihzhhpf-prod …/healthz` | 200 |
| `ca-agent-host-ihzhhpf-prod …/agents` | 200 |
| `ca-app-fluent-ihzhhpf-prod …/` | 200 |

## Resources deployed (`rg-ihzhhpf-prod`, switzerlandnorth)

`crihzhhpfprod` (ACR) · `log-ihzhhpf-prod` · `appi-ihzhhpf-prod` ·
`kv-ihzhhpf-prod-swn1` · `id-platform-ihzhhpf-prod` ·
`id-ca-agent-host-ihzhhpf-prod` · `id-ca-app-fluent-ihzhhpf-prod` ·
`ai-ihzhhpf-prod` (Foundry) · `cosmos-ihzhhpf-prod` (agenthost db + 3 containers) ·
`cosmos-csa-ihzhhpf-prod` (csa db + 4 vector containers) ·
`evh-ihzhhpf-prod-i62t` · `sb-ihzhhpf-prod-i62t` ·
`cae-ihzhhpf-prod` · `cae-app-fluent-ihzhhpf-prod` ·
`ca-agent-host-ihzhhpf-prod` · `ca-app-fluent-ihzhhpf-prod`.

## Scope assertion

Deployment scoped entirely to `rg-ihzhhpf-prod`. No `rg-ihzhhpf-sit`, no shared
`curavias.ch` DNS zone, and no shared Entra app `ihzhhpf-app` were touched.

## Remaining gated phases

- **P5** — Foundry project + 3 models (gpt-5 / gpt-5-mini / o3) + 8 agents via
  the v2 `/agents` API (`allowProjectManagement=true` PATCH first).
- **P6** — Fabric F2 co-located in switzerlandnorth + workspace + lakehouse /
  notebooks / semantic model + simulator.
- **P7** — DNS re-point `app.curavias.ch` → new swn Container App fqdn + managed
  cert; update Entra `ihzhhpf-app` PROD redirect URI.
- **P8** — E2E verification + PROD evidence doc.

Each remains `approved-to-apply`-gated per the runbook.
