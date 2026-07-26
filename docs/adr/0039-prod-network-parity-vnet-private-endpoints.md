# ADR-0039: PROD Network Parity — VNet + Cosmos & Key Vault Private Endpoints (Switzerland North)

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-24 |
| **Author** | Urs Rüegg |
| **Decision-makers** | @urruegg |
| **Extends** | [ADR-0037](0037-prod-region-switzerland-north-greenfield.md) (PROD switzerlandnorth greenfield — this ADR expands its network scope) |
| **Inherits pattern from** | [ADR-0029](0029-agent-host-cosmos-reachability.md) (agent-host ↔ Cosmos reachability, Option A: add PE + VNet-integrate the CAE) |
| **Consulted** | Live `az` against sub `66a9953a-df37-4c51-856c-9971b9bf3e03` (2026-07-22); [ADR-0013](0013-temporary-us-region-demo-scope.md) demo scope; issue [#311](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/311) |

## Context

The Sprint 19 PROD greenfield rebuild ([ADR-0037](0037-prod-region-switzerland-north-greenfield.md))
deliberately shipped a **public, network-off** baseline slice (`enableNetworkModule=false`),
mirroring the earlier eastus2 first slice: synthetic data only, no PHI
([ADR-0013](0013-temporary-us-region-demo-scope.md)/[ADR-0016](0016-no-phi-in-mvp-demo-scope.md)),
with VNet + private endpoints named as an explicit later hardening item.

Post-rebuild verification (issue [#311](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/311))
surfaced two coupled gaps:

1. **PROD Key Vault `kv-ihzhhpf-prod-swn1` has no reachable data plane.** The vault is
   AAD-only (RBAC, zero secrets/keys — intentional; the platform is AAD-only and the
   only `getSecret` consumer, source-SQL, is disabled in PROD). But the MCAPSGov
   Modify-effect policy **force-disables `publicNetworkAccess`** subscription-wide — a
   manual `--public-network-access Enabled` silently reverts. With public access
   disabled and **no** private endpoint, the vault is unreachable from any network,
   including the operator's laptop, and cannot be data-plane verified.

2. **PROD Cosmos (`cosmos-csa-ihzhhpf-prod`) is public-in-Bicep but policy-locked.** The
   same policy family (`CosmosDB_PublicNetwork_Modify`) force-disables Cosmos public
   access, so the account is unreachable at runtime without a private endpoint —
   exactly the SIT condition that [ADR-0029](0029-agent-host-cosmos-reachability.md)
   resolved with Option A.

SIT already runs the full network stack (`enableNetworkModule=true`): a platform VNet,
a Cosmos private endpoint, and a VNet-integrated agent-host CAE. PROD should reach the
same posture for parity and to give both the KV and Cosmos a reachable (private) data
plane.

### The immutability constraint (why this is partly destructive)

[ADR-0029](0029-agent-host-cosmos-reachability.md)'s "Guidance for PROD promotion"
assumed a **greenfield** PROD where the CAE did not yet exist, so ARM would accept
`vnetConfiguration` on first create. **That assumption no longer holds:** the swn
rebuild already created `cae-ihzhhpf-prod` as a **public** CAE hosting
`ca-agent-host-ihzhhpf-prod` + `ca-signal-runner-ihzhhpf-prod`. VNet integration is
**immutable after CAE creation** (`ManagedEnvironmentCannotAddVnetToExistingEnv`, SIT
iteration 3), so enabling it now requires a **one-time destructive delete + recreate**
of `cae-ihzhhpf-prod` and its two container apps (~5-10 min outage).

The separate `cae-app-fluent-ihzhhpf-prod` (hosting `ca-app-fluent` and the
`app.curavias.ch` custom domain) is **not** VNet-wired and is **unaffected**.

## Decision

**Accepted: bring PROD switzerlandnorth to SIT network parity, plus add a Key Vault
private endpoint.**

1. **Enable the network module for PROD** (`enableNetworkModule=true`) with a
   non-overlapping address space `10.70.0.0/16` (SIT is `10.60.0.0/16`; same
   subscription, different RGs — non-overlap preserves a future peering option).
   This creates `vnet-platform-ihzhhpf-prod` (`snet-app`, `snet-data`, delegated
   `snet-cae`), the Cosmos private endpoint (`privatelink.documents.azure.com`), and
   VNet-integrates the agent-host CAE — inheriting [ADR-0029](0029-agent-host-cosmos-reachability.md)
   Option A wholesale.
2. **Add a Key Vault private endpoint** (new) — `privatelink.vaultcore.azure.net` zone
   plus a PE into `snet-data` and a DNS zone group, gated by a dedicated
   `enableKeyVaultPrivateEndpoint` flag (PROD=true). The vault flips to
   `publicNetworkAccess=Disabled` to match the enforced policy state and eliminate the
   perpetual what-if drift. Mirrors the Cosmos PE pattern in
   `infra/modules/cosmos/csa.bicep`.
3. **Accept the one-time destructive CAE recreate** for `cae-ihzhhpf-prod` (+
   `ca-agent-host` + `ca-signal-runner`), executed as a **separate `approved-to-apply`-gated
   deploy** (what-if → explicit OWNER approval). The Bicep + ADR artefacts land first,
   non-destructively.

### Scoping choices

+ **Dedicated KV-PE flag, not `enableNetworkModule`.** Gating the KV PE on its own
  `enableKeyVaultPrivateEndpoint` flag keeps this change **PROD-only** and avoids an
  unplanned SIT KV change on the next SIT deploy. Extending the same flag to SIT for
  parity is a trivial follow-up (set it true in `sit.bicepparam`).
+ **KV PE is non-destructive on its own.** Adding a PE + flipping
  `publicNetworkAccess=Disabled` does not recreate the vault. Only the CAE VNet
  integration is destructive.

## Consequences

### Positive

+ PROD KV and Cosmos gain a reachable **private** data plane; both match the
  policy-enforced `publicNetworkAccess=Disabled` state (no more what-if drift).
+ Full SIT↔PROD network parity; the agent-host reaches Cosmos over private link.
+ The SIT-discovered gotchas are **already pre-solved** for PROD: `Microsoft.App` +
  `Microsoft.ContainerService` RP registration and the
  `AllowBringYourOwnPublicIpAddress` feature are handled by `cd-infra-deploy-prod.yml`;
  the `snet-cae` `Microsoft.App/environments` delegation is in the network module. PROD
  should therefore avoid SIT iterations 1, 4, and 5.

### Negative / risks

+ **One-time ~5-10 min agent-host outage** during the destructive CAE recreate
  (`cae-ihzhhpf-prod` + `ca-agent-host` + `ca-signal-runner`). `app.curavias.ch` stays
  up (separate CAE).
+ **Operator KV/Cosmos access still requires an in-VNet path.** A private endpoint makes
  the vault reachable only from inside the VNet; interactive verification from a laptop
  needs a jumpbox/Bastion (not in scope here — a follow-up if interactive access is
  required). The agent-host, running in-VNet, is unaffected.
+ Expands ADR-0037's deliberately-lean PROD scope; recorded here as the amendment.

## Implementation notes

**Bicep (this PR — non-destructive artefacts):**

+ `infra/modules/platform-foundation/main.bicep` — new `enableKeyVaultPrivateEndpoint`
  / `vnetResourceId` / `keyVaultPrivateEndpointSubnetName` params; conditional
  `privatelink.vaultcore.azure.net` zone + VNet link + PE (`groupIds: ['vault']`) + DNS
  zone group; `publicNetworkAccess` now `Disabled` when the PE is on.
+ `infra/main.bicep` — new top-level `enableKeyVaultPrivateEndpoint` param wired into
  `platformFoundation`; new `networkCaeSubnetPrefix` param plumbed into the network
  module (required because a non-default VNet prefix moves the CAE subnet out of the
  hardcoded `10.60.4.0/23` default).
+ `infra/environments/prod-swn.bicepparam` — `enableNetworkModule=true`,
  `enableKeyVaultPrivateEndpoint=true`, `10.70.0.0/16` address space.

**Gated deploy sequence (separate, `approved-to-apply`):**

1. `what-if` the PROD deploy; confirm the plan deletes/recreates `cae-ihzhhpf-prod` +
   its two apps and adds the KV + Cosmos PEs.
2. OWNER comments `approved-to-apply`.
3. Manual destructive step (explicit approval): delete `ca-agent-host-ihzhhpf-prod`,
   `ca-signal-runner-ihzhhpf-prod`, `cae-ihzhhpf-prod`.
4. Redeploy via `cd-infra-deploy-prod` — ARM creates the fresh VNet-integrated CAE and
   both apps clean.
5. Run the ADR-0029 10-check verification (private DNS resolves in-CA, PE connection
   Approved, DNS auto-registration, MI role bind present).

## Applied & verified (2026-07-24)

The network parity described here was applied to `rg-ihzhhpf-prod` and verified
live on 2026-07-24. Verification confirmed VNet `vnet-platform-ihzhhpf-prod`
(`10.70.0.0/16`); the platform Cosmos, CSA Cosmos, and Key Vault private
endpoints all in `Approved` state; `cae-ihzhhpf-prod` VNet-integrated on
`snet-cae` with `provisioningState Succeeded`; and `kv-ihzhhpf-prod-swn1` with
`publicNetworkAccess=Disabled`. See the sprint evidence record:
[`2026-07-24-network-parity-verification.md`](../sprints/sprint-19/evidence/2026-07-24-network-parity-verification.md).

## Cross-references

+ [ADR-0029](0029-agent-host-cosmos-reachability.md) — Option A pattern + the five-iteration
  SIT implementation trail this PROD promotion inherits.
+ [ADR-0037](0037-prod-region-switzerland-north-greenfield.md) — the PROD greenfield baseline
  this ADR amends.
+ Issue [#311](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/311) — PROD CD
  repoint + KV/network follow-up tracking.
