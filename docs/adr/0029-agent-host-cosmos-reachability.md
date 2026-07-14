# ADR-0029 — Agent-host Cosmos reachability in SIT (choose PE + VNet integration or co-locate on CSA Cosmos)

| Field | Value |
| ----- | ----- |
| **Status** | **Accepted (2026-07-14) — Option A** |
| **Date** | 2026-07-13 (Proposed) → 2026-07-14 (Accepted, implemented, verified) |
| **Deciders** | @urruegg |
| **Superseded by** | — |
| **Scope** | SIT. PROD inherits Option A when PROD RG is provisioned (see §Implementation trail → Guidance for PROD promotion). |

> Sprint 13.1 recovery deploy revealed a runtime reachability gap between
> `ca-agent-host-ihzhhpf-sit` and `cosmos-ihzhhpf-sit`. This ADR documents the
> gap, presents three options, and records the final decision. **Status flipped
> Proposed → Accepted on 2026-07-14 with Option A chosen** after a fresh
> inspection of the SIT infrastructure revealed that the required VNet + private
> DNS zone + PE pattern already exists (used by `cosmos-csa-ihzhhpf-sit`), so
> Option A's implementation is materially smaller than initially estimated.
> Implementation plan: [`docs/superpowers/plans/2026-07-14-cae-vnet-integration-cosmos-pe.md`](../superpowers/plans/2026-07-14-cae-vnet-integration-cosmos-pe.md).
> Referenced by
> [`infra/modules/agent-host/main.bicep`](../../infra/modules/agent-host/main.bicep),
> [`infra/modules/agent-host/cosmos.bicep`](../../infra/modules/agent-host/cosmos.bicep),
> [`infra/modules/agent-host/container-app.bicep`](../../infra/modules/agent-host/container-app.bicep),
> the Sprint 13 design spec, and the
> [Sprints 11-16 review checklist](../sprints/2026-07-10-sprints-11-16-review-checklist.md).

## Context

The Sprint 13.1 recovery deploy (run
[`29240688046`](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29240688046))
successfully landed `ca-agent-host-ihzhhpf-sit`, `cae-ihzhhpf-sit`, and the
`cosmos-ihzhhpf-sit` account with its 3 required containers
(`conversations`, `audit`, `approval-events`) on 2026-07-13.

Post-deploy verification surfaced a runtime reachability gap:

| Fact | Value | Source |
| --- | --- | --- |
| `cosmos-ihzhhpf-sit.publicNetworkAccess` | `Disabled` | `az cosmosdb show` |
| `cosmos-ihzhhpf-sit` private endpoints | 0 (none) | `az network private-endpoint list` filter by `privateLinkServiceId` |
| `cosmos-ihzhhpf-sit` virtualNetworkRules | `[]` | `az cosmosdb show` |
| `cosmos-ihzhhpf-sit` ipRules | `[]` | `az cosmosdb show` |
| `cae-ihzhhpf-sit` VNet integration | `null` | `az containerapp env show --query properties.vnetConfiguration` |
| MCAPS policy assignment | `CosmosDB_PublicNetwork_Modify` (Modify, Compliant) | `az policy state list` |

The Bicep declares `publicNetworkAccess: 'Enabled'` in
[`infra/modules/agent-host/cosmos.bicep`](../../infra/modules/agent-host/cosmos.bicep),
but the MCAPS `CosmosDB_PublicNetwork_Modify` policy assignment
(`MCAPSGovDeployPolicies`) silently reverts every apply back to `Disabled`.
This is by design at the tenant governance layer and cannot be overridden from
this repository.

**Implication:** the placeholder image
(`mcr.microsoft.com/dotnet/samples:aspnetapp`) currently running in the
agent-host CA never calls Cosmos, so the deploy is healthy today. When the
**real** agent-host image lands (Sprint 13.1 follow-up work: `agent-host-build.yml`
push to ACR + image ref in `sit.bicepparam`), its first `POST /agents/*/chat`
call will fail at
[`persistence.write('conversations', ...)`](../../apps/hcc-agent-host/src/orchestrator/dispatch.py) —
the container has no network path to Cosmos.

Reference precedent in the same RG:
[`cosmos-csa-ihzhhpf-sit`](Sprint 16) is also `publicNetworkAccess: Disabled`
(same policy) and reaches its callers via **2 private endpoints** with a
`privatelink.documents.azure.com` DNS zone linked to
`vnet-platform-ihzhhpf-sit`. Its callers are Foundry-hosted agents (`csa-agent`,
`bm-copilot`), which run inside the VNet by default.

## Decision — **Accepted: Option A** (2026-07-14)

**Option A — Add private endpoint on `cosmos-ihzhhpf-sit` + VNet-integrate `cae-ihzhhpf-sit`** is chosen. The initial recommendation in the Proposed version was Option C (env-var toggle to skip Cosmos in SIT), but a fresh inspection of the SIT infrastructure on 2026-07-14 revealed that the required substrate already exists:

| Substrate | State on 2026-07-14 | Impact on Option A effort |
| --- | --- | --- |
| `vnet-platform-ihzhhpf-sit` (`10.60.0.0/16`) | Exists in `rg-ihzhhpf-sit` | No new VNet needed |
| Subnets: `snet-app` (`10.60.1.0/24`), `snet-data` (`10.60.2.0/24`) | Exist with NSGs | Add ONE new subnet for CAE (delegated) |
| Private DNS zone `privatelink.documents.azure.com` | Exists, VNet-linked, 3 records | No new zone — PE auto-registers via `privateDnsZoneGroup` |
| CSA Cosmos PE pattern (`pe-cosmos-csa-ihzhhpf-sit` in `snet-data`, `groupIds: ['Sql']`) | Exists and working | Mirror the pattern for `cosmos-ihzhhpf-sit` |
| CAE VNet integration precedent in this repo | Not yet — this is new for the platform | Bicep pattern documented in the implementation plan |

The Option A effort estimate drops from "2–3 days + destructive CAE recreate" to **~1 day of Bicep work + 1 destructive apply** (still destructive on the CAE, but confined and testable). This tips the balance decisively toward Option A because it preserves ADR-0007 §2 posture, restores full HITL evidence persistence, and is directly reusable for PROD.

Option C's rationale (fast SIT unblock via env-var toggle) is no longer needed because:

1. SIT is now stable end-to-end via PR #199 + #201 + #202 — no urgent operational pressure to defer
2. The demo showcase requires functional Cosmos writes (HITL evidence, conversation history) for a credible walk-through with Spital Zollikerberg on 2026-07-17
3. Option A gives us PROD readiness "for free" — the same Bicep serves both envs

Implementation is tracked in [`docs/superpowers/plans/2026-07-14-cae-vnet-integration-cosmos-pe.md`](../superpowers/plans/2026-07-14-cae-vnet-integration-cosmos-pe.md) and gated behind an explicit `approved-to-apply` per AGENTS.md §4 (destructive CAE recreate).

### Original option summary (kept for context)

Three options were evaluated in the Proposed version:

### Option A — Add private endpoint + VNet-integrate `cae-ihzhhpf-sit`

Provision a private endpoint on `cosmos-ihzhhpf-sit` pointing at
`vnet-platform-ihzhhpf-sit`, link the private DNS zone
`privatelink.documents.azure.com`, and update `cae-ihzhhpf-sit` to use a
VNet-integrated deployment (delegated subnet).

- **Effort:** ~2-3 days. New Bicep sub-module (`agent-host/private-endpoint.bicep`),
  update `container-app.bicep` to declare `vnetConfiguration`, potentially
  recreate the CAE (VNet integration is set at env creation; migrating an
  existing CAE means delete + recreate).
- **Cost:** small ongoing (private endpoint + PIP). No new SKU changes.
- **Risk:** CAE recreation is **destructive** — the running `ca-agent-host` +
  `ca-app-fluent` would be deleted and recreated. Requires an
  `approved-to-apply` gate. Interim outage 5-10 min.
- **PROD readiness:** ✅ this is the standard pattern; matches
  ADR-0007 §2's stable-schema-contract expectation.
- **Reversibility:** low — CAE recreation is a one-way step; going back to a
  public CAE would recreate again.

### Option B — Reuse `cosmos-csa-ihzhhpf-sit` for agent-host

Delete `cosmos-ihzhhpf-sit` and move the 3 agent-host containers under the
existing `cosmos-csa-ihzhhpf-sit` account (which already has 2 PEs + DNS
linking). Introduce a schema separation via database naming: keep CSA under
its existing DB, add `agenthost` DB alongside on the same account.

- **Effort:** ~1 day. Update `cosmos.bicep` to `existing` and reference the
  CSA account; move 3 container declarations. Coordinate delete of the
  old account (which has no data yet — placeholder image never wrote).
- **Cost:** slightly less than Option A (no new PE) but adds shared-account
  contention risk between CSA and agent-host.
- **Risk:** mixes two workloads' data on one account. Complicates RBAC scoping
  and separate scaling/backup profiles. Violates ADR-0007's implied
  one-account-per-workload posture.
- **PROD readiness:** ⚠️ compromises separation of concerns. Would need
  reversal for PROD.
- **Reversibility:** medium — reverts by restoring dedicated
  `cosmos-ihzhhpf-sit` account.

### Option C — Add private endpoint on `cosmos-ihzhhpf-sit` **only**; keep CAE public (SIT scope)

Add PE + DNS wiring on `cosmos-ihzhhpf-sit`, but **do not** VNet-integrate
`cae-ihzhhpf-sit`. Instead, expose Cosmos to the CAE via VNet-service-endpoint
allow-list on a small dedicated subnet the CAE outbound traffic uses (Container
Apps outbound egresses through a per-env-owned IP that can be allow-listed via
`ipRules`). Alternatively (and simpler): **skip Cosmos writes for SIT** — set an
env var `COSMOS_MODE=inmemory` and let the agent-host use its in-memory
`CosmosPersistence` stand-in
([`apps/hcc-agent-host/src/persistence/cosmos_client.py`](../../apps/hcc-agent-host/src/persistence/cosmos_client.py)),
parallel to how [ADR-0028](0028-defer-managed-redis-in-sit-demo-scope.md)
handles Redis.

- **Effort:** ~30 min (env-var toggle) or ~4-6 hours (PE + ipRules approach).
- **Cost:** USD 0 (env-var path) or small (PE-only path).
- **Risk:** **agent-host conversation/audit history is lost on container
  restart** — same trade-off we already accepted for Redis grounding in
  ADR-0028. HITL evidence would need a different persistence path (perhaps
  the CSA Cosmos with a small `hitl-approvals` container).
- **PROD readiness:** ⚠️ SIT-only pattern. PROD must use Option A.
- **Reversibility:** high — flip an env var / add PE later.

### Original recommendation (overridden by 2026-07-14 decision above)

**~~Adopt Option C (env-var toggle variant)~~ — SUPERSEDED by Option A per the 2026-07-14 decision above.**

The Option C recommendation stood on 2026-07-13 based on the assumption that Option A required 2–3 days + substantial new infrastructure (VNet, private DNS zone, PE pattern). The 2026-07-14 infrastructure inspection showed the substrate already exists, dropping Option A to ~1 day. See the 2026-07-14 Decision section above.

For historical reference, the original Option C plan was:

1. Add an `agentHostEnableCosmos bool = true` param on
   [`infra/main.bicep`](../../infra/main.bicep) mirroring the ADR-0028 pattern.
2. Pin it `false` in [`infra/environments/sit.bicepparam`](../../infra/environments/sit.bicepparam)
   with a comment linking here.
3. Update [`infra/modules/agent-host/main.bicep`](../../infra/modules/agent-host/main.bicep) to
   optionally instantiate the Cosmos sub-module.
4. Update [`infra/modules/agent-host/container-app.bicep`](../../infra/modules/agent-host/container-app.bicep) so
   `COSMOS_ENDPOINT` is only injected when `cosmosEndpoint` is non-empty.
5. If the agent-host runtime later needs durable state in SIT, split HITL
   `approval-events` off onto the CSA Cosmos (Option B partial reuse) rather
   than pursuing full Option A in SIT.

For **PROD** — Option A remains the plan, tied to
[issue #179](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/179).

## Rationale

| # | Criterion | Option A (PE + VNet) | Option B (reuse CSA) | **Option C (env-var, chosen)** |
| --- | --- | --- | --- | --- |
| 1 | Effort in SIT | 2-3 days + destructive CAE recreate | 1 day + destructive Cosmos delete | 30 min |
| 2 | Ongoing cost | Small (PE + PIP) | Slight savings | USD 0 |
| 3 | Aligned with ADR-0007 | ✅ | ⚠️ (mixes workloads) | ⚠️ (SIT-only deviation, documented) |
| 4 | Aligned with ADR-0028 posture | ⚠️ (heavier posture) | ⚠️ | ✅ (mirror pattern) |
| 5 | Blast radius of change | High (CAE recreation) | High (Cosmos delete) | Low (Bicep flag + env var) |
| 6 | PROD readiness | ✅ | ⚠️ | ⚠️ (SIT-only) |
| 7 | Reversibility | Low | Medium | **High** |

## Consequences (if Option C adopted)

**Positive:**

- Agent-host runs end-to-end in SIT with placeholder+ real image alike.
- No destructive changes to `cae-ihzhhpf-sit` or `cosmos-ihzhhpf-sit`.
- Mirror of the ADR-0028 pattern: explicit toggle, documented deviation,
  low-risk reversibility.
- HITL evidence is captured in-memory during a single container run; enough
  for a canned demo but not for real gating.

**Negative:**

- **HITL evidence is not persisted** across container restarts — a real
  hospital-workflow deployment would fail the HITL evidence-persistence
  requirement in [ADR-0007 §7](0007-mvp-agent-runtime-and-hitl-release-gates.md).
- Conversation history is not durable — the "same conversation across sessions"
  affordance the app-shell relies on won't work across restarts.
- Two ADR-scoped deviations from ADR-0007 for SIT (Redis + Cosmos) now exist.
  Cumulatively they turn SIT into a "cache-only" demo. Documented, but the
  demo narrative should call this out.

## Follow-ups (assuming Option C is adopted)

1. **Sprint 13.2 mini-sprint** — implement the ADR-0028-parallel toggle for
   Cosmos: `agentHostEnableCosmos` param + conditional module + env-var
   suppression.
2. **PROD promotion checklist** (issue #179): both `agentHostEnableRedis` and
   `agentHostEnableCosmos` must be `true` for PROD, and the Option A PE + VNet
   posture must be implemented before flipping.
3. **HITL runtime story** — if any Sprint 13.6+ demo needs to exercise an
   HITL gate against `approval-events`, decide between: (a) adding a small
   PE-covered `agenthost` DB on `cosmos-csa-ihzhhpf-sit`, or (b) sticking with
   in-memory for the demo but scripting the HITL narrative accordingly.
4. **PROD PE + VNet Bicep** — build the reusable module today so PROD
   promotion is a flag-flip, not a design exercise.

## Evidence

- **Failed reachability chain** (observed 2026-07-13):
  - `cosmos-ihzhhpf-sit.publicNetworkAccess`: `Disabled` (policy-enforced)
  - `cosmos-ihzhhpf-sit` PE count: 0
  - `cae-ihzhhpf-sit` VNet integration: `null`
- **MCAPS policy assignment**:

  ```text
  Effect    State       Name                     Def
  --------  ----------  -----------------------  ----------------------------
  modify    Compliant   MCAPSGovDeployPolicies   CosmosDB_PublicNetwork_Modify
  modify    Compliant   MCAPSGovDeployPolicies   CosmosDB_LocalAuth_Modify
  ```

- **Deploy run**: [`29240688046`](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29240688046)
  succeeded 2026-07-13T09:57Z; the Cosmos + agent-host CA are provisioned but
  not runtime-connected.

## Open questions for the decider

**All resolved on 2026-07-14 by the Accepted-Option-A decision above.**

1. ~~Confirm Option C is the right SIT posture given the HITL evidence consequence.~~ — Answered: no. HITL evidence persistence matters for the demo credibility. Option A restores full posture.
2. ~~If not: pick Option A (destructive recreate, ~2-3 days) or Option B (workload consolidation on CSA Cosmos, ~1 day).~~ — Answered: **Option A**. Effort reduced to ~1 day because VNet + private DNS zone + PE pattern already exist. Option B rejected because it violates ADR-0007 one-account-per-workload posture.
3. ~~Confirm this ADR should also cover PROD, or split PROD into a separate ADR at PROD promotion time.~~ — Answered: **this ADR covers PROD by extension**. Same Bicep pattern applies. PROD promotion issue [#179](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/179) inherits the Option A implementation without a new ADR.

## Implementation trail (2026-07-14)

Recorded here so PROD promotion has the complete diagnostic history and doesn't re-discover the same failure modes. Option A implementation on SIT took **five deploy iterations + one non-Bicep destructive step** before landing green.

### Iteration table

| # | PR / action | Deploy run | Blocker | Fix that unblocked next iteration |
| - | ----------- | ---------- | ------- | --------------------------------- |
| 1 | [PR #205](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/205) initial Option A Bicep (subnet + PE + CAE `vnetConfiguration`) | [29325801157](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29325801157) | `SubscriptionIsNotRegistered` on `Microsoft.App` + `Microsoft.ContainerService`. CAE VNet integration silently requires the `Microsoft.ContainerService` RP because the CAE internally provisions AKS-managed infrastructure when `infrastructureSubnetId` is set. | [PR #206](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/206) — add both RPs to the workflow registration guard + `az provider register` ad-hoc for SIT sub. |
| 2 | (Retry after PR #206) | [29327123189](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29327123189) | `ManagedEnvironmentV1SubnetDelegationNotAllowed`: "consumption-only environment must not have delegations". This wording was **misleading** — the actual cause was that ARM refuses to reconfigure a v1 (consumption-only) CAE with `infrastructureSubnetId` **at all**, regardless of delegation. See also iteration 5 for the reversal of the naive fix. | [PR #207](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/207) — removed the delegation, which was wrong but appeared to match the error. |
| 3 | (Retry after PR #207) | [29329094217](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29329094217) | `ManagedEnvironmentCannotAddVnetToExistingEnv`: "Adding a subnet to managed environment cae-ihzhhpf-sit is not allowed". This finally revealed the real rule: **VNet integration on a CAE is immutable after environment creation**. Bicep `Modify` on an existing CAE is refused at the RP level. | **Manual destructive step (with explicit `approved-to-apply`)**: `az containerapp delete ca-agent-host-ihzhhpf-sit` + `az containerapp env delete cae-ihzhhpf-sit`. Recreated cleanly by next Bicep deploy. |
| 4 | (Retry after manual delete, still on PR #207 Bicep with no delegation) | [29330572239](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29330572239) | `ManagedEnvironmentSubnetDelegationError`: "The subnet of the environment MUST be delegated to `Microsoft.App/environments`". The delegation IS required on a fresh modern-API CAE with `infrastructureSubnetId`. Iteration 2's error was a red herring; the true rule is "delegation required". | [PR #208](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/208) — restore the `Microsoft.App/environments` delegation on `snet-cae`. |
| 5 | (Retry after PR #208) | [29332192702](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29332192702) | CAE PUT was accepted (delegation now correct), then failed **inside the CAE's internal cluster provisioning** with `SubscriptionNotRegisteredForFeature` on `Microsoft.Network/AllowBringYourOwnPublicIpAddress`. VNet-integrated CAEs internally provision a public IP for the managed AKS load balancer; the subscription-level **feature flag** (not RP) was not registered. | [PR #209](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/209) — add feature-registration loop to both SIT + PROD workflows + `az feature register` ad-hoc for SIT sub. |
| 6 | (Retry after PR #209 + delete of the Failed CAE from iteration 5) | [29334633463](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29334633463) | ✅ **Green (6m12s)**. All architectural components proven. | — |

### Total effort

- **Bicep PRs**: 5 (#205, #206, #207, #208, #209)
- **Destructive manual steps**: 2 (delete of live v1 CAE + delete of Failed CAE after iteration 5). Both under explicit `approved-to-apply`.
- **Ad-hoc `az` commands** (idempotent, non-destructive): 2 (`az provider register Microsoft.ContainerService`, `az feature register Microsoft.Network/AllowBringYourOwnPublicIpAddress`)
- **Successful deploys**: 2 (Option A itself, then [PR #210](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/210) which added the Cosmos DB Built-in Data Contributor RBAC on run [29336946152](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/29336946152))
- **Wall-clock**: ~2 hours of iterative diagnosis
- **Original estimate** (before substrate discovery): 2–3 days
- **Revised estimate** (after substrate discovery, before iteration): ~1 day
- **Actual**: within revised estimate, but with more iteration than expected

### Guidance for PROD promotion

Do this in order for a first-time PROD deploy:

1. **Pre-flight the subscription**: run `az provider register --namespace Microsoft.App --wait`, `az provider register --namespace Microsoft.ContainerService --wait`, `az feature register --namespace Microsoft.Network --name AllowBringYourOwnPublicIpAddress`, then `az provider register --namespace Microsoft.Network --wait`. **PRs #206 + #209 make the workflow do this automatically**, but running once ahead of time saves ~1 iteration.
2. **Ensure `snet-cae` subnet has the `Microsoft.App/environments` delegation** in the network module (already correct post PR #208 revert).
3. **Deploy Option A Bicep clean** — because the CAE does not exist yet in PROD, ARM accepts the `vnetConfiguration` on the first create. No delete-and-recreate dance needed.
4. **Deploy PR #210 RBAC in the same run OR immediately after** — the Cosmos DB Built-in Data Contributor role is inline in `agent-host/main.bicep` and lands together with the CAE.
5. **Run the same 10-check verification** used for SIT (private DNS resolves inside the CA, PE connection Approved, private DNS records auto-registered, MI principalId matches role assignment).

### Post-mortem — what would have avoided the iteration cost

- **A more thorough pre-flight probe** at the start would have surfaced items 1, 4, and 5 as separate failures with clearer signal. For PROD I'll add a "pre-flight" workflow step that registers RPs + features + validates subnet delegation in a single dry-run.
- **The Microsoft error `ManagedEnvironmentV1SubnetDelegationNotAllowed`** is documented misleadingly. Would have been faster to try the delete-and-recreate path first (iteration 3), and only reach for the "remove delegation" hypothesis after that failed. Lesson: when an ARM error mentions "must not have X" but the operation is on a resource that is architecturally frozen (v1 CAE with legacy shape), prefer the "recreate the resource" hypothesis over the "modify the property to match the error message" hypothesis.

### Cross-references

- [`docs/superpowers/plans/2026-07-14-cae-vnet-integration-cosmos-pe.md`](../superpowers/plans/2026-07-14-cae-vnet-integration-cosmos-pe.md) — original implementation plan (task-by-task; some tasks superseded by the manual delete path).
- [`docs/runbooks/curavias-dns-godaddy-delegation.md`](../runbooks/curavias-dns-godaddy-delegation.md) — related Sprint 13.1 DNS work; separate from ADR-0029 but shares the same deploy window.
