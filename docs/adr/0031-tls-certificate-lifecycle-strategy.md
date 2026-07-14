# ADR-0031 — TLS certificate lifecycle strategy for custom hostnames

| Field | Value |
| ----- | ----- |
| **Status** | **Accepted (2026-07-14)** |
| **Date** | 2026-07-14 |
| **Deciders** | @urruegg |
| **Superseded by** | — |
| **Scope** | Any Azure Container Apps custom hostname in SIT and PROD (`appsit.curavias.ch`, `app.curavias.ch`, future subdomains). |
| **Related** | [ADR-0030 curavias.ch DNS strategy](0030-curavias-dns-strategy.md), [`infra/modules/apps/hcc-app-fluent/main.bicep`](../../infra/modules/apps/hcc-app-fluent/main.bicep) |

> Follow-up to ADR-0030. That ADR made the DNS zone + custom-hostname
> decision; this one decides **where the TLS certificate for those hostnames
> is issued, stored, and renewed**. The choice affects operational overhead,
> audit posture, portability across services, and the path to real-enterprise
> PROD.

---

## Context

Sprint 13.1 Phase 2 (2026-07-14) landed `https://appsit.curavias.ch` on the
`ca-app-fluent-ihzhhpf-sit` Container App using an **Azure Container Apps
managed certificate**:

- Bicep declares `Microsoft.App/managedEnvironments/managedCertificates` named
  `cert-appsit-curavias-ch`
- Azure validates domain ownership via the `asuid.appsit` TXT record
- A cert is auto-issued by **DigiCert (GeoTrust TLS RSA CA G1)** in commercial
  regions today (historically Let's Encrypt in some regions)
- Azure auto-renews the cert ~30 days before expiry
- The private key is Azure-managed; not exportable, not visible to the tenant

This is optimal for **demo / SIT / dev**, but a Swiss healthcare PROD deployment
raises different questions:

- Do we need audit logging of "who / when accessed the cert"? Swiss DSG-relevant.
- Do we want cert governance policy (approved CAs, renewal cadence, revocation)?
- Do we want the same cert to front App Gateway / APIM / other services later?
- Do we want to use an org-managed CA (DigiCert Enterprise, Sectigo, internal)?
- Do we want manual override / emergency rotation?

For **demo PROD** (aligned with [ADR-0013](0013-temporary-us-region-demo-scope.md))
the answers are mostly *no / not yet*. For **realistic enterprise PROD** the
answers become mostly *yes*.

## Decision drivers

| Driver | Weight | Managed cert | Key Vault cert |
| ------ | ------ | ------------ | -------------- |
| Zero ops overhead | High for demo | ✓ | ✗ |
| Cost | Low overall | ✓ ($0) | ~ (small KV cost) |
| Time to value | High for demo | ✓ (fast) | ~ (depends on CA order) |
| Swiss DSG audit trail on cert access | Medium in demo, High in PROD | ✗ | ✓ |
| Portable across Azure services (App GW, APIM, App Service) | Low in demo, Medium in PROD | ✗ | ✓ |
| Bring-your-own CA (DigiCert Enterprise, internal) | Low in demo, Situational in PROD | ✗ | ✓ |
| Emergency revocation / rotation | Low in demo, Situational in PROD | ~ (Azure-managed only) | ✓ (customer-controlled) |
| Cert versioning / history | Low in demo | ✗ | ✓ |

## Considered options

### Option 1 — Managed cert everywhere (SIT + PROD)

- Provisioned by Azure Container Apps as `managedCertificates`
- Auto-renewed, zero ops
- **Chosen for SIT** (already deployed, working)
- **Not chosen for the long-term PROD posture** because audit trail + custom
  CA flexibility become non-negotiable in a regulated healthcare production
  scenario

### Option 2 — Key Vault-backed cert everywhere (SIT + PROD)

- Cert stored as a PFX secret in Key Vault
- ACA CAE imports it as `Microsoft.App/managedEnvironments/certificates`
  (not `managedCertificates`) via `certificateKeyVaultProperties`
- Requires: managed identity with `Key Vault Secrets User` on KV, imported
  PFX, potentially an out-of-band CA order
- **Full portability, full audit**
- **Not chosen for demo scope** — introduces cert-governance decisions we
  do not have policy for yet (which CA? what renewal cadence? whose
  incident-response process?)

### Option 3 — Hybrid: managed cert in SIT + demo PROD; Key Vault-backed cert in real-enterprise PROD

- SIT stays on managed cert (zero ops, matches demo scope)
- Demo PROD (initial promotion) also stays on managed cert
- Real-enterprise PROD switches to Key Vault-backed cert when the org has
  a defined cert governance policy
- Bicep supports both paths via a single opt-in param
- **Chosen** — matches the platform's demo-first posture ([ADR-0013](0013-temporary-us-region-demo-scope.md))
  while keeping the door open for enterprise PROD without a schema change

## Decision

**Adopt Option 3 (hybrid).**

Implementation:

1. `infra/modules/apps/hcc-app-fluent/main.bicep` accepts a new optional
   parameter `existingCustomDomainCertificateResourceId string = ''`:
   - **Empty** (SIT + demo PROD): use the ACA-managed cert path — behaviour
     identical to today's Phase 2 deploy.
   - **Non-empty**: skip the `managedCertificates` resource; the CA's
     `customDomains[0].certificateId` points at the passed-in resource ID.
     The caller is expected to have provisioned that certificate resource
     out-of-band — typically a `Microsoft.App/managedEnvironments/certificates`
     imported from Key Vault via `certificateKeyVaultProperties` (see PROD
     switch runbook when needed). This design also allows a customer to bring
     a pre-provisioned managedCertificates resource under their own naming.
2. Bicep changes in this PR do not fully wire the KV import — that lands
   in a dedicated PR when PROD actually needs it. The scaffold guarantees
   the switch is a bicepparam change, not a Bicep refactor.
3. **No changes to SIT posture today** — `appFluentEnableCustomDomainCert = true`
   combined with an unset `existingCustomDomainCertificateResourceId` keeps
   the current ACA-managed cert path.

## Trigger for revisiting

Move to Key Vault-backed cert (Option 2) when **any** of these hold for PROD:

- The customer / hospital consortium has a defined cert governance policy
  and wants approval / rotation on their terms.
- Swiss DSG audit review flags "cert access without full audit trail" as a
  gap.
- We introduce App Gateway, APIM, or App Service in the topology and want
  a single shared cert.
- We migrate off DigiCert / GeoTrust as the default CA to an org-approved
  CA.
- We need multi-region (Switzerland North + Europe West) cert distribution
  with tenant-controlled versioning.

The revisit will not require a new ADR — this ADR sets the switching
criteria; the follow-up PR fills in the actual KV cert import.

## Consequences

### Positive

- **Zero ops for demo scope**: SIT + demo PROD both benefit from Azure's
  auto-renew on the managed cert.
- **Future-proof**: Bicep is ready for the KV switch — no re-architecture
  needed.
- **Explicit switching criteria**: Clear signals for when to move; not an
  open-ended "someday".
- **Consistent SIT + PROD posture in demo mode**: identical cert lifecycle
  in both.

### Negative

- **Limited audit trail today**: If Swiss DSG review happens during demo
  window, we need to explain that ACA managed cert access is logged only
  in the Azure control-plane (not in a customer-visible audit store).
- **DigiCert-issued default**: If an org insists on Let's Encrypt or a
  specific CA, we cannot honour that without switching to KV-backed.
- **No manual rotation on demand**: Emergency cert revocation requires
  waiting for Azure's cycle or triggering a Bicep re-deploy that
  regenerates the managed cert (adds ~15-30 min).

### Neutral

- Cost is negligible either way; managed cert is $0, KV storage is <$1/mo
  for a single cert.
- Deploy-time impact is similar: managed cert takes ~15-30 min to issue;
  KV-backed cert deploy is faster (cert already exists) but the CA order
  process ahead of time takes days.

## Rollback

Not applicable — this ADR sets the decision. If a later PR flips to
Key Vault-backed and something breaks:

1. Set `existingCustomDomainCertificateResourceId = ''` in the affected bicepparam.
2. Re-deploy. The managed cert path re-engages; cert is re-issued within
   ~15-30 min.
3. Old KV secret remains in KV until explicitly deleted (audit trail
   preserved for the switching event).

## Cross-references

- [ADR-0013](0013-temporary-us-region-demo-scope.md) — demo scope in `westus2`
- [ADR-0030](0030-curavias-dns-strategy.md) — DNS strategy for `curavias.ch`
- Microsoft docs on ACA custom domains:
  <https://learn.microsoft.com/azure/container-apps/custom-domains-managed-certificates>
- Microsoft docs on Key Vault certificates on Container Apps:
  <https://learn.microsoft.com/azure/container-apps/environment-custom-dns-suffix>
