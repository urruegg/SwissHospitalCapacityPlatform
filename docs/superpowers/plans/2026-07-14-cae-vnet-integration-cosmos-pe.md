# CAE VNet integration + Cosmos private endpoint — Implementation Plan (ADR-0029 Option A)

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the Cosmos reachability gap between `ca-agent-host-ihzhhpf-sit` and `cosmos-ihzhhpf-sit` by (a) provisioning a Private Endpoint on the Cosmos account in the existing `snet-data` subnet, (b) VNet-integrating `cae-ihzhhpf-sit` into a new delegated subnet so Container Apps traffic resolves the Cosmos FQDN to the private IP.

**Architecture:** Mirror the working `cosmos-csa-ihzhhpf-sit` PE pattern (existing PE in `snet-data`, existing private DNS zone `privatelink.documents.azure.com`). Add a new `Microsoft.App/environments`-delegated subnet `snet-cae` to `vnet-platform-ihzhhpf-sit`. Update the agent-host Container Apps Environment (CAE) Bicep to reference the delegated subnet — this triggers a **destructive CAE recreate** (also recreates the child `ca-agent-host-ihzhhpf-sit`). CAE FQDN changes; the curavias.ch CNAME auto-updates via Bicep output → managed cert re-validates on next Phase 2 apply.

**Tech Stack:** Bicep (`Microsoft.Network/virtualNetworks/subnets` with `Microsoft.App/environments` delegation, `Microsoft.Network/privateEndpoints`, `Microsoft.Network/privateEndpoints/privateDnsZoneGroups`, `Microsoft.App/managedEnvironments` with `vnetConfiguration`). Azure CLI for post-deploy verification.

**Reference precedent in this repo:**

- `pe-cosmos-csa-ihzhhpf-sit` in `snet-data` with `groupIds: ['Sql']`
- `privatelink.documents.azure.com` private DNS zone linked to `vnet-platform-ihzhhpf-sit` (3 record sets, 1 VNet link)
- `vnet-platform-ihzhhpf-sit` with subnets `snet-app` (`10.60.1.0/24`) and `snet-data` (`10.60.2.0/24`) — both with NSGs

---

## File Structure

Modified files map to logical responsibilities:

| File | Responsibility | Change |
| --- | --- | --- |
| [`infra/modules/network/main.bicep`](../../../infra/modules/network/main.bicep) | VNet + subnet declarations | **Add `snet-cae`** subnet with `Microsoft.App/environments` delegation, no NSG (CAE forbids NSG on delegated subnet), address `10.60.3.0/23` (CAE needs `/23` minimum for infrastructure) |
| [`infra/modules/network/main.bicep`](../../../infra/modules/network/main.bicep) | Outputs | **Export `caeSubnetId`** for consumption by agent-host module |
| [`infra/modules/agent-host/cosmos.bicep`](../../../infra/modules/agent-host/cosmos.bicep) | Cosmos account + database + containers | **No change** — MCAPS policy already forces `publicNetworkAccess: Disabled` |
| [`infra/modules/agent-host/cosmos-pe.bicep`](../../../infra/modules/agent-host/cosmos-pe.bicep) *(new)* | Private endpoint + DNS zone group for the agent-host Cosmos | **New file** — mirror the CSA Cosmos PE pattern |
| [`infra/modules/agent-host/container-app.bicep`](../../../infra/modules/agent-host/container-app.bicep) | CAE + agent-host CA | **Add `vnetConfiguration` block** on the CAE resource referencing the new subnet. Add `caeSubnetId` param + default empty (safe fallback). Destructive on existing CAE. |
| [`infra/modules/agent-host/main.bicep`](../../../infra/modules/agent-host/main.bicep) | Orchestrator | Wire the new `cosmos-pe` sub-module + pass `caeSubnetId` param through to `container-app.bicep` |
| [`infra/main.bicep`](../../../infra/main.bicep) | Top-level | Read the network module output `caeSubnetId` + pass through to agent-host module. No new top-level param. |
| [`infra/environments/sit.bicepparam`](../../../infra/environments/sit.bicepparam) | SIT env values | **No new params** — the plan is Bicep-only (no new bicepparam values needed since VNet integration is on/off via presence of the subnet output, not a user flag) |
| [`docs/adr/0029-agent-host-cosmos-reachability.md`](../../adr/0029-agent-host-cosmos-reachability.md) | Decision record | **Already updated** — Proposed → Accepted (Option A) in this branch |

---

## Task 1: Add `snet-cae` delegated subnet + output the subnet ID

**Files:**

- Modify: [`infra/modules/network/main.bicep`](../../../infra/modules/network/main.bicep)

**Rationale:** Container Apps Environment VNet integration requires a **dedicated** subnet with `Microsoft.App/environments` service delegation. Subnet must be at least `/23` for a **workload-profiles** CAE (per Microsoft docs); our existing `cae-ihzhhpf-sit` is a **consumption-only** CAE which accepts `/27` — verify at apply time via `what-if`. Address plan: use `10.60.4.0/23` (avoids collisions with existing `snet-app` `.1.0/24` and `snet-data` `.2.0/24`; leaves `.3.0/24` free for future).

- [ ] **Step 1: Read current network module** to confirm subnet declaration pattern
- [ ] **Step 2: Add `snet-cae` subnet** with:

  ```bicep
  {
    name: 'snet-cae'
    properties: {
      addressPrefix: '10.60.4.0/23'
      delegations: [
        {
          name: 'Microsoft.App.environments'
          properties: {
            serviceName: 'Microsoft.App/environments'
          }
        }
      ]
      // NO networkSecurityGroup — Azure Container Apps forbids NSG on delegated subnets
      // (or requires specific NSG rules; keep clean for now)
    }
  }
  ```

- [ ] **Step 3: Add output `caeSubnetId`** returning the subnet resource ID
- [ ] **Step 4: `az bicep build --file infra/main.bicep`** — must exit 0 (only pre-existing BCP037 warnings from `redis.bicep` and BCP422 from `data-platform` are acceptable)
- [ ] **Step 5: Commit**: `feat(network): add snet-cae delegated subnet for CAE VNet integration (ADR-0029)`

## Task 2: Create the Cosmos private-endpoint module

**Files:**

- Create: [`infra/modules/agent-host/cosmos-pe.bicep`](../../../infra/modules/agent-host/cosmos-pe.bicep)

**Rationale:** New module mirrors the `pe-cosmos-csa-ihzhhpf-sit` pattern (verified 2026-07-14 via `az network private-endpoint show`). One resource per: PE, private DNS zone group. Consumes existing zone `privatelink.documents.azure.com` via `existing` reference.

- [ ] **Step 1: Write the module** with params `location`, `nameSuffix`, `tags`, `cosmosAccountResourceId`, `subnetResourceId`, `privateDnsZoneResourceId`
- [ ] **Step 2: Define the PE** with `privateLinkServiceConnections[0].groupIds: ['Sql']`, name `pe-cosmos-<nameSuffix>`
- [ ] **Step 3: Define the `privateDnsZoneGroups` child resource** referencing the existing `privatelink.documents.azure.com` zone
- [ ] **Step 4: Emit outputs**: `privateEndpointName`, `privateEndpointFqdn` (from `customDnsConfigs[0].fqdn`)
- [ ] **Step 5: `az bicep build --file infra/modules/agent-host/cosmos-pe.bicep`** — exit 0 required
- [ ] **Step 6: Commit** with the same PR

## Task 3: Wire `vnetConfiguration` into the CAE Bicep

**Files:**

- Modify: [`infra/modules/agent-host/container-app.bicep`](../../../infra/modules/agent-host/container-app.bicep) — CAE resource + new `caeSubnetId` param

**Rationale:** CAE VNet integration is declared at CAE creation time. Adding `vnetConfiguration` to an existing CAE is a **destructive change** — ARM cannot patch VNet integration on a running CAE, so the CAE is deleted and recreated. Child resources (agent-host CA) are recreated too. Bicep dependencies re-emit the CA on the new CAE, so no manual re-provisioning needed.

- [ ] **Step 1: Add `caeSubnetId` param** with default `''` (empty = no VNet integration = current behaviour; safe for other envs)
- [ ] **Step 2: Add `vnetConfiguration` conditional** in the CAE resource:

  ```bicep
  vnetConfiguration: empty(caeSubnetId) ? null : {
    infrastructureSubnetId: caeSubnetId
    internal: false  // external ingress is still allowed
  }
  ```

- [ ] **Step 3: Verify `az bicep build`** — no new warnings introduced
- [ ] **Step 4: Confirm** (via docs check) that `internal: false` preserves the current public ingress FQDN on `.westus2.azurecontainerapps.io`

## Task 4: Wire the PE module + subnet plumbing in the agent-host orchestrator

**Files:**

- Modify: [`infra/modules/agent-host/main.bicep`](../../../infra/modules/agent-host/main.bicep) — add cosmos-pe module invocation + `caeSubnetId` param pass-through
- Modify: [`infra/main.bicep`](../../../infra/main.bicep) — read network output + pass `caeSubnetId` to agent-host module

**Rationale:** Keep the CAE VNet integration and the PE creation on the same deploy — they land together atomically. `caeSubnetId` flows: `network.outputs.caeSubnetId` → `main.bicep` → `agentHost` module → `containerApp` sub-module.

- [ ] **Step 1: In `infra/modules/agent-host/main.bicep`** — add `param caeSubnetId string = ''` and pass it into the `containerApp` module invocation
- [ ] **Step 2: In the same file** — invoke the new `cosmos-pe.bicep` module conditionally on `!empty(caeSubnetId)` (PE only makes sense when VNet integration is in place)
- [ ] **Step 3: Pass `cosmosAccountResourceId`, `subnetResourceId`, `privateDnsZoneResourceId`** to the PE module. The private DNS zone name is fixed (`privatelink.documents.azure.com`); the resource ID resolves via `resourceId('Microsoft.Network/privateDnsZones', 'privatelink.documents.azure.com')`
- [ ] **Step 4: In `infra/main.bicep`** — read `network.outputs.caeSubnetId` (may need to add the output on the network module in Task 1) and pass to `agentHost` module
- [ ] **Step 5: `az bicep build --file infra/main.bicep`** — exit 0

## Task 5: What-if + PR draft

**Files:**

- Create: `.scratch/whatif-adr0029-option-a.ps1` — reusable what-if runner
- Do NOT commit `.scratch/` (gitignored per prior work)

- [ ] **Step 1: Run `az deployment group what-if`** against `rg-ihzhhpf-sit` with `sit.bicepparam`
- [ ] **Step 2: Verify plan shape**:
  - `+ snet-cae` (new subnet on existing VNet)
  - `+ pe-cosmos-ihzhhpf-sit` (new PE)
  - `+ pe-cosmos-ihzhhpf-sit/default` (private DNS zone group)
  - `~ cae-ihzhhpf-sit` (Modify — vnetConfiguration added; ARM MAY show this as Replace = destructive)
  - `~ ca-agent-host-ihzhhpf-sit` (Modify — inherits new CAE; also may be Replace)
  - `+ 1 A record in privatelink.documents.azure.com/cosmos-ihzhhpf-sit` (added by the DNS zone group)
  - `0 deletes` explicitly — private DNS zone stays intact
- [ ] **Step 3: Flag destructive replaces prominently in the PR body** — CAE + CA WILL be recreated; downtime ~5-15 min
- [ ] **Step 4: Open PR** with title `feat(network): implement ADR-0029 Option A — CAE VNet integration + Cosmos private endpoint`
- [ ] **Step 5: PR body** covers: deploy plan, downtime window, rollback (revert PR + redeploy — CAE recreates without VNet), verification checklist, PROD readiness note

## Task 6: `approved-to-apply` gate + destructive deploy

**Blocked on:** explicit human `approved-to-apply` in the PR thread (AGENTS.md §4 — destructive Container App recreation).

- [ ] **Step 1: Wait for explicit `approved-to-apply` comment on the PR** from `@urruegg` (or another authorised approver — cannot be the agent itself per AGENTS.md §4)
- [ ] **Step 2: Merge PR** — auto-triggers `cd-infra-deploy-sit`
- [ ] **Step 3: Approve at `sit` env gate**
- [ ] **Step 4: Monitor deploy** — expect ~5-15 min for CAE recreate, another ~2 min for CA revision cold start
- [ ] **Step 5: On failure** — capture the failed operation via `az deployment operation group list --name deploy-sit-<runid>` and open a hotfix PR (matches the pattern used in PR #197 + #199)

## Task 7: Post-deploy verification

**Files:**

- Ad-hoc PowerShell — no committed script

- [ ] **Step 1: Verify subnet exists**: `az network vnet subnet show -g rg-ihzhhpf-sit --vnet-name vnet-platform-ihzhhpf-sit -n snet-cae --query "{name: name, delegation: delegations[0].serviceName}" -o json`
- [ ] **Step 2: Verify PE + DNS record**:

  ```powershell
  az network private-endpoint show -g rg-ihzhhpf-sit -n pe-cosmos-ihzhhpf-sit --query "{state: provisioningState, subnet: subnet.id, groupIds: privateLinkServiceConnections[0].groupIds}" -o json
  az network private-dns record-set a list -g rg-ihzhhpf-sit -z privatelink.documents.azure.com -o table
  ```

- [ ] **Step 3: Verify CAE VNet integration**: `az containerapp env show -g rg-ihzhhpf-sit -n cae-ihzhhpf-sit --query "properties.vnetConfiguration" -o json` — non-null with `infrastructureSubnetId` set
- [ ] **Step 4: Verify CA healthy after recreate**: `az containerapp show -g rg-ihzhhpf-sit -n ca-agent-host-ihzhhpf-sit --query "{state: properties.provisioningState, running: properties.runningStatus, fqdn: properties.configuration.ingress.fqdn}" -o json`
- [ ] **Step 5: End-to-end Cosmos write test** from inside the CA — exec into the container and run:

  ```bash
  # Inside the running CA replica
  curl -X POST https://ca-agent-host-....azurecontainerapps.io/agents/bmca-agent/chat \
    -H "content-type: application/json" \
    -d '{"prompt":"Wie viele Betten sind auf USZ 3B belegt?","conversationId":"e2e-test-adr0029","callerObjectId":"urruegg"}'
  ```

  Expected: HTTP 200 with a grounded reply, AND a new document in `cosmos-ihzhhpf-sit/agenthost/conversations` container. If Cosmos write fails: rollback (see Task 8).
- [ ] **Step 6: If Phase 2 cert was already live before the recreate** — trigger a cert re-issuance:

  ```powershell
  az containerapp env certificate list -g rg-ihzhhpf-sit -n cae-ihzhhpf-sit --managed-certificates-only -o table
  # If the cert lists provisioningState = Failed, recreate:
  az containerapp env certificate delete -g rg-ihzhhpf-sit -n cae-ihzhhpf-sit --certificate cert-appsit-curavias-ch -y
  # Then re-run cd-infra-deploy-sit to re-issue via Bicep
  ```

## Task 8: Rollback procedure (documented, not executed)

Trigger: any of Task 7 steps fail OR unforeseen impact on live workloads.

- [ ] **Step 1: Revert the PR** — GitHub UI or `gh pr revert <number>`
- [ ] **Step 2: Approve `cd-infra-deploy-sit` on the revert commit** — CAE reverts to public (non-VNet) mode. PE + subnet stay orphaned (safe — no cost, no exposure)
- [ ] **Step 3: (Optional) Clean up orphans**: delete `pe-cosmos-ihzhhpf-sit` and `snet-cae` manually via `az resource delete` — requires `approved-to-apply`
- [ ] **Step 4: Post-mortem** — record what failed under `docs/reviews/YYYY-MM-DD-adr0029-post-mortem.md`

## Task 9: Update audit doc (governance)

**Files:**

- Modify: [`docs/sprints/2026-07-10-sprints-11-16-review-checklist.md`](../../sprints/2026-07-10-sprints-11-16-review-checklist.md)

- [ ] **Step 1: Flip S13.6 from ⚠️ partial → ✅ done** with evidence links to the successful deploy run + the E2E Cosmos write test
- [ ] **Step 2: Update Sprint 13 tally** — was `8/1/0/2/1`, now `9/0/0/2/1`
- [ ] **Step 3: Update Overall tally** accordingly
- [ ] **Step 4: Version bump** — `1.6.0` → `1.7.0`

---

## Testing strategy

- **Bicep build**: passes on every task (fast feedback)
- **What-if before apply**: mandatory — validates plan shape without side effects (Task 5)
- **Post-deploy smoke test**: HTTP 200 on `/healthz` + `/agents` (already-passing baseline) + a new POST to `/agents/bmca-agent/chat` that lands a document in Cosmos (new)
- **No unit tests needed for Bicep** — infrastructure declarative, verified via what-if + post-deploy queries

## Risk register

| Risk | Likelihood | Mitigation |
| --- | --- | --- |
| CAE recreate takes longer than 15 min | Medium | Baseline this window in the PR — no user-facing impact (SIT is demo scope) |
| CA revision fails cold-start on new CAE | Low | Same image + env — should be identical; Task 5 what-if flags any config drift |
| Private DNS zone group conflicts with existing record | Very low | Zone allows multiple A records; PE auto-adds one for the cosmos-ihzhhpf-sit account |
| Managed cert (Phase 2) invalidated by CAE recreate | High if Phase 2 is live | Task 7 Step 6 explicitly handles this — delete + re-issue |
| MCAPS policy blocks the subnet delegation | Low (no policy precedent) | Test in what-if; fallback to `az network vnet subnet update` post-deploy if Bicep rejects |
| Address space conflict (10.60.4.0/23 overlaps something) | Very low | Existing VNet uses .1.0/24 + .2.0/24; .4.0/23 is unused per Task 1 Step 1 inspection |

## Dependencies

- **Depends on:** Phase 1 DNS deploy landed (PR #201 — already merged, deploy pending user approval on run 29287994405). Not a hard blocker — Option A can land before Phase 1 without conflict.
- **Blocks:** S13.6 DoD closure. Blocks proceeding to PROD promotion of ADR-0029 Option A.
- **Related:** ADR-0028 Redis (no interaction — Redis still off in SIT). ADR-0030 curavias.ch DNS (CNAME auto-updates via Bicep output when CA FQDN changes; Phase 2 cert may need re-validation).

## Estimated effort

- Task 1: 30 min (subnet Bicep)
- Task 2: 45 min (new PE module + private DNS zone group)
- Task 3: 20 min (CAE vnetConfiguration)
- Task 4: 30 min (wire modules)
- Task 5: 20 min (what-if + PR)
- Task 6: 20 min real + ~15 min deploy wait
- Task 7: 30 min verification
- Task 9: 15 min audit doc

**Total: ~4 hours of focused work** + 1 deploy window with your `approved-to-apply` gate.
