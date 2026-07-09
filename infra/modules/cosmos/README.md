# CSA Cosmos DB (`cosmos-csa-ihzhhpf-sit`)

> **Version** 1.0.0 · **Date** 2026-07-09 · **Author** Urs Rüegg · **Status** Draft for review · **Previous Version** n/a (new — Sprint 16 T1)

Sprint 16 T1 provisions an **Azure Cosmos DB for NoSQL** account that backs the
CSA what-if scenario catalogue and per-run agent memory. Grounds
[design spec §4](../../../docs/superpowers/specs/2026-07-09-sprint-16-csa-design.md#4-persistence--cosmos-db-for-nosql--fabric-mirroring).

> **Separate account.** This Cosmos is **distinct** from the Sprint 13
> conversations/audit Cosmos ([ADR-0007](../../../docs/adr/0007-mvp-agent-runtime-and-hitl-release-gates.md)):
> different concern, different account, different RBAC scope.

## Containers

| Container | Partition key | Vector policy | Purpose |
| --------- | ------------- | ------------- | ------- |
| `scenarios` | `/scenarioId` | `diskANN` on `/descriptionEmbedding` (cosine, 1536-dim) | What-if scenario catalogue |
| `agent-memory` | `/threadId` | `diskANN` on `/contentEmbedding` (sharded by `/threadId`) | Per-run agent memory, one document per turn |
| `response-levers` | `/leverId` | `quantizedFlat` on `/descriptionEmbedding` | Doctrine-aligned mitigation library (< 100 items) |
| `simulation-runs` | `/runId` | (none) | Run metadata + result references |

**Vector index rationale** — DiskANN for `scenarios` and `agent-memory`
(high-throughput, low-latency, cost-efficient at scale, dynamic updates);
`quantizedFlat` for `response-levers` because the library is small.

## Configuration

- **Consistency**: `Session` (read-your-writes for agent memory).
- **Auth**: data-plane **RBAC only** — `disableLocalAuth = true`, no account
  keys. The Sprint 13 agent-host managed identity receives **Cosmos DB Built-in
  Data Contributor** scoped to the account (least privilege). Supply its
  `principalId` via `agentHostMiPrincipalId` at apply time.
- **TLS**: minimum 1.2.
- **Capability**: `EnableNoSQLVectorSearch`.
- **RU budget**: database-shared autoscale, max `1000` RU/s (demo default —
  `databaseMaxThroughput`). Mirroring reads consume **no** RU.
- **Region**: `westus2` for the demo scope per
  [ADR-0013](../../../docs/adr/0013-temporary-us-region-demo-scope.md) (accepts
  preview features such as external-Cosmos Fabric Mirroring). Returns to
  `switzerlandnorth` at Swiss GA.

## Deploy (gated)

Cosmos provisioning is a `deploy`-ceiling action. Per
[AGENTS.md §4](../../../AGENTS.md#4-confirmation-rule-for-deploy--delete), post
the `what-if` output as a PR comment and wait for `@urruegg` to reply
`approved-to-apply` (label `cosmos-provision`) before applying.

```bash
# Plan (safe)
az deployment group what-if \
  --resource-group rg-ihzhhpf-sit \
  --template-file infra/modules/cosmos/main.bicep \
  --parameters infra/modules/cosmos/parameters/sit.bicepparam \
  --parameters agentHostMiPrincipalId=<agent-host-mi-principalId>

# Apply (only after `approved-to-apply`)
az deployment group create \
  --resource-group rg-ihzhhpf-sit \
  --template-file infra/modules/cosmos/main.bicep \
  --parameters infra/modules/cosmos/parameters/sit.bicepparam \
  --parameters agentHostMiPrincipalId=<agent-host-mi-principalId>
```

## Deletion

Cosmos **deletion is blocked during the MVP** (design spec §11). Deletion
requires portal action + `delete-confirmed` label + explicit `approved-to-apply`.
