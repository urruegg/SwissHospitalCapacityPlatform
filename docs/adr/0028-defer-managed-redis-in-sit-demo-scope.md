# ADR-0028 — Defer Azure Managed Redis in SIT demo scope (agent-host uses in-memory cache)

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-07-13 |
| **Deciders** | @urruegg |
| **Superseded by** | — |
| **Scope** | SIT only. PROD retains Managed Redis per [ADR-0007](0007-mvp-agent-runtime-and-hitl-release-gates.md) §1. |

> Sprint 13.1 mini-sprint completion ADR. Deviates from
> [ADR-0007 §1](0007-mvp-agent-runtime-and-hitl-release-gates.md) for the SIT
> demo scope by making the Managed Redis module optional and disabling it in
> `infra/environments/sit.bicepparam`. Referenced by
> [`infra/main.bicep`](../../infra/main.bicep),
> [`infra/modules/agent-host/main.bicep`](../../infra/modules/agent-host/main.bicep),
> [`infra/modules/agent-host/container-app.bicep`](../../infra/modules/agent-host/container-app.bicep),
> [`infra/environments/sit.bicepparam`](../../infra/environments/sit.bicepparam),
> and the [Sprints 11-16 review checklist](../sprints/2026-07-10-sprints-11-16-review-checklist.md).

## Context

Sprint 13 T5 authored an Azure Managed Redis module
([`infra/modules/agent-host/redis.bicep`](../../infra/modules/agent-host/redis.bicep))
to back the agent-host grounding cache per [ADR-0007 §1](0007-mvp-agent-runtime-and-hitl-release-gates.md).
The module targets `Microsoft.Cache/redisEnterprise` (`Balanced_B0` SKU, port
10000, TLS ≥ 1.2, `accessKeysAuthentication: Disabled` for Entra-MI-only auth
per ADR-0007). This replaced the retired classic `Microsoft.Cache/redis` type
per PR #190.

On 2026-07-13, the Sprint 13.1 SIT recovery deploy failed at the Redis
allocation step:

```text
Deploy chain: deploy-sit-29101177996
              → agent-host-sit
              → agent-host-redis
              → redis-ihzhhpf-sit (Balanced_B0)

Error: AllocationFailed
Message: Request failed due to insufficient capacity. Retry using a different
         Azure Managed Redis size, region or contact Azure support for
         assistance.
```

Root-cause investigation against the ARM provider SKU catalog
(`https://management.azure.com/subscriptions/.../providers/Microsoft.Cache/skus`
at `api-version=2024-10-01`) confirmed that:

1. **`Balanced_B0` is not listed** for `Microsoft.Cache/redisEnterprise` in any
   region for our MCAPS demo subscription. Balanced/Memory-Optimized/Compute-Optimized/
   Flash-Optimized are the marketing tier names for Azure Managed Redis, but at
   the ARM API level our subscription only sees the older `Enterprise_E*` and
   `EnterpriseFlash_F*` naming.
2. `westus2` (our SIT region per [ADR-0013](0013-temporary-us-region-demo-scope.md))
   offers: `Enterprise_E1`, `Enterprise_E5`, `Enterprise_E10..E400`,
   `EnterpriseFlash_F300..F1500`. No `Balanced_*` anywhere.
3. Both `az bicep build` and `az deployment group what-if` accept `Balanced_B0`
   as a valid SKU string; the failure surfaces only at deploy-time allocation.

Three options were considered:

- **Option 1** — swap SKU to `Enterprise_E1` (the smallest tier actually
  offered in `westus2`). Estimated cost impact: ~USD 200/month vs ~USD 110/month
  target for `Balanced_B0` (vs ~USD 16/month for the retired classic).
- **Option 2** — make the Redis module optional and skip it in SIT. Runtime
  impact for the demo: **none** — the agent-host Python code
  ([`apps/hcc-agent-host/src/cache/redis_client.py`](../../apps/hcc-agent-host/src/cache/redis_client.py))
  ships with an **in-memory** `RedisCache` implementation and never imports the
  live `redis` package, never reads `REDIS_HOST`/`REDIS_PORT` env vars. Grep of
  `apps/hcc-agent-host/` for `import redis` and `os.environ.get("REDIS_HOST")`
  returns zero hits.
- **Option 3** — move SIT to a region offering `Balanced_B0`. Cross-cutting
  scope change; conflicts with [ADR-0013](0013-temporary-us-region-demo-scope.md).

## Decision

**Adopt Option 2.**

1. Introduce `param enableRedisModule bool = true` on
   [`infra/modules/agent-host/main.bicep`](../../infra/modules/agent-host/main.bicep).
   Default keeps PROD behaviour aligned with ADR-0007.
2. Wrap the Redis sub-module invocation in `if (enableRedisModule)`. When
   disabled, the container-app module receives empty `redisHostName` and
   `redisPort: 0`.
3. Update [`infra/modules/agent-host/container-app.bicep`](../../infra/modules/agent-host/container-app.bicep)
   so the `REDIS_HOST` and `REDIS_PORT` env vars are **only** injected when
   `redisHostName` is non-empty (Bicep `empty()` check + `concat()`).
4. Expose the toggle to top-level via `param agentHostEnableRedis bool = true`
   on [`infra/main.bicep`](../../infra/main.bicep), passed through to the
   agent-host module.
5. Pin `agentHostEnableRedis = false` in
   [`infra/environments/sit.bicepparam`](../../infra/environments/sit.bicepparam)
   for the SIT demo scope.
6. Leave [`infra/environments/prod.bicepparam`](../../infra/environments/prod.bicepparam)
   unchanged — inherits the default `true`, so PROD stays ADR-0007-compliant.

## Rationale

| # | Criterion | Option 1 (Enterprise_E1) | **Option 2 — chosen** | Option 3 (region move) |
| --- | --- | --- | --- | --- |
| 1 | Deploy success in westus2 | Likely (E1 is in the SKU catalog) | **Certain** (nothing to allocate) | Certain (in a different region) |
| 2 | SIT monthly cost (list price) | ~USD 200 | **USD 0** | Similar to Option 1 |
| 3 | Effort | 1-line Bicep + BCP037 warning cleanup + PR | 3 Bicep files + ADR + PR | Multi-day: move VNet, Fabric capacity, EH namespace, Cosmos, ACR, LA workspace, …; conflicts with [ADR-0013](0013-temporary-us-region-demo-scope.md) |
| 4 | Demo functionality | Identical (Python code is in-memory anyway) | **Identical** (Python code is in-memory anyway) | Identical |
| 5 | ADR-0007 alignment | Preserved | Documented deviation (this ADR, SIT scope only) | Preserved |
| 6 | Reversibility | Change SKU string later | **Flip `agentHostEnableRedis: true` in sit.bicepparam + re-deploy** | Multi-day migration back |
| 7 | PROD readiness | Redis running with a mismatched SKU; needs re-sizing | Redis flag off in SIT only; flip on in PROD | Depends on target PROD region |

Option 2 wins on cost (zero), effort (bounded), risk (zero cross-cutting
impact), and reversibility (one bicepparam flip). The demo-scope alignment with
[ADR-0013](0013-temporary-us-region-demo-scope.md) is preserved.

## Consequences

**Positive:**

- Sprint 13.1 SIT recovery deploy unblocks with no infrastructure cost for a
  Redis cluster the agent-host does not currently talk to.
- The `enableRedisModule` toggle is a **first-class, version-controlled**
  parameter — the "no Redis in SIT" decision is explicit, not accidental.
- Path to PROD is unchanged: PROD keeps the default `agentHostEnableRedis: true`
  and provisions Managed Redis per ADR-0007. When PROD lands in a region that
  offers a suitable SKU, ADR-0028 does not need to be reversed — it only
  covers SIT.

**Negative:**

- SIT deviates from ADR-0007 §1 (Redis is the runtime grounding cache). The
  deviation is scoped and documented in this ADR, but a reader of ADR-0007
  alone would believe Redis is always deployed.
- If a future feature adds session-state code that expects a live Redis client
  (e.g., cross-replica sticky sessions, distributed HITL locks), the SIT
  demo will need `agentHostEnableRedis: true` flipped back on **and** a working
  SKU in the deploy region.
- Sprint 15 BVA cost model rows referencing Redis show USD 0 in the SIT slice
  — cosmetic, and easy to explain: "the SIT slice reflects ADR-0028; the PROD
  slice reflects ADR-0007".

## Reversibility

To restore Managed Redis in SIT:

1. Ensure the target Redis Enterprise SKU is offered in the target region for
   the target subscription:

   ```powershell
   az rest --method get `
     --url "https://management.azure.com/subscriptions/<sub>/providers/Microsoft.Cache/skus?api-version=2024-10-01" `
     --query "value[?resourceType=='redisEnterprise' && locations[0]=='<region>'].name" -o tsv
   ```

2. If the SKU string in `infra/modules/agent-host/redis.bicep` differs from
   what the region offers, update it in a small preparatory PR (single-line
   `sku.name` change) and cover the BCP037 warnings on `highAvailability` and
   `accessKeysAuthentication` if the Bicep type schema still complains.

3. Flip `param agentHostEnableRedis = true` in
   [`infra/environments/sit.bicepparam`](../../infra/environments/sit.bicepparam).

4. Merge and re-trigger `cd-infra-deploy-sit.yml` (approval-gated per the
   existing `sit` GitHub Environment protection rule).

The Python `RedisCache` class then still runs in-memory. Wiring the live
`redis` client is a **separate** follow-up PR — the flag change alone does not
make the container talk to Redis.

## Follow-ups

1. **Sprint 15 BVA cost model annotation** — mark the "Cache for Redis" row in
   the SIT cost slice as N/A per ADR-0028; keep the row for PROD scope. Track
   in a separate small doc PR.
2. **Optional: wire a live Redis client** in
   [`apps/hcc-agent-host/src/cache/redis_client.py`](../../apps/hcc-agent-host/src/cache/redis_client.py)
   for PROD. This is currently untracked work; the in-memory fallback
   `RedisCache` class remains the interface. When wired, add a feature-flag
   env var (e.g., `REDIS_MODE=inmemory|live`) so SIT can force in-memory even
   if a Redis endpoint were later provisioned.
3. **Bicep type staleness** —
   [`infra/modules/agent-host/redis.bicep`](../../infra/modules/agent-host/redis.bicep)
   currently emits `BCP037` warnings on `highAvailability` (should be under
   `properties.encryption`?) and `accessKeysAuthentication` (should be under
   `databases.geoReplication.modules`?). Not blocking, but worth a cleanup PR
   before re-enabling Redis.
4. **PROD promotion checklist** — the item "verify `agentHostEnableRedis`
   posture per environment" should be added to the PROD promotion issue
   ([#179](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/179)).

## Evidence

- **Failed SIT deploy** — `deploy-sit-29101177996` (run
  [`29101177996`](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29101177996)):
  `AllocationFailed` on `redis-ihzhhpf-sit` (Balanced_B0).
- **Provider SKU catalog query** — the query above returned only
  `Enterprise_E*` and `EnterpriseFlash_F*` for `westus2`; no `Balanced_*`
  anywhere in the subscription's catalog.
- **Python code audit** — grep of `apps/hcc-agent-host/` for
  `import redis|Redis\(|redis\.from_url|from redis` and
  `REDIS_HOST|REDIS_PORT|redis_url|os\.environ.*REDIS`: **0** hits outside of
  the in-memory `RedisCache` class file itself.
- **What-if with `agentHostEnableRedis = false`** — plan reduced from
  `4 to create` (agent-host CA + CAE + Redis cluster + Redis database) to
  `2 to create` (agent-host CA + CAE only). `status: Succeeded`,
  `0 deletes`.
