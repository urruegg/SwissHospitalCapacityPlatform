# CSA Fabric Mirroring — setup runbook (Sprint 16 T2)

Replicates the CSA Cosmos DB account (`cosmos-csa-ihzhhpf-sit`, provisioned by
[`infra/modules/cosmos/`](../../../infra/modules/cosmos/README.md)) into Fabric
OneLake so the four CSA containers surface as Delta tables in the Fabric SQL
analytics endpoint, joinable with Gold capacity data — **no RU consumption for
mirroring reads**.

> **Gated.** Enabling Mirroring is a `deploy`-class action. Post the enablement
> plan as a PR/issue comment and wait for `@urruegg` to reply
> `approved-to-apply` per [AGENTS.md §4](../../../AGENTS.md#4-confirmation-rule-for-deploy--delete)
> before enabling. Synthetic-only data (ADR-0016).

## Preview caveat

Fabric Mirroring for **external** Azure Cosmos DB is in **preview** and is not
available in sovereign clouds. The demo scope is `westus2` per
[ADR-0013](../../adr/0013-temporary-us-region-demo-scope.md), which accepts
preview features.

## Enablement steps (after `approved-to-apply`)

1. In the Fabric workspace `ws-ihzhhpf-sit-data`, create a **Mirrored Azure
   Cosmos DB** item named `fabric-mirrored-csa`.
2. Point it at the `cosmos-csa-ihzhhpf-sit` account using the agent-host managed
   identity (Workload Identity Federation — no keys; `disableLocalAuth=true`).
3. Select all four containers: `scenarios`, `agent-memory`, `response-levers`,
   `simulation-runs`.
4. Start replication.

## Verification

- Confirm the four Delta tables appear in the Fabric SQL analytics endpoint
  **within 15 minutes** of the first write to a mirrored container (design spec
  §12 Mirroring smoke).
- Run a BI join against Gold capacity data to confirm the analytics surface.

## Fallback

If Mirroring is blocked at go-live, activate the documented Spark change-feed job
[`fallback-change-feed-copy.py`](fallback-change-feed-copy.py) (kept as an inert
stub until needed), which copies the Cosmos change feed into Fabric Bronze with
the same schema. Publishing that job is itself a gated `deploy` action.
