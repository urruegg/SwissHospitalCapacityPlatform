# ADR-0030 — curavias.ch DNS strategy: full Azure DNS delegation + Container Apps managed certs

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-07-13 |
| **Deciders** | @urruegg |
| **Superseded by** | — |
| **Scope** | Public-facing hostnames for the platform on SIT and PROD. Private-endpoint DNS (Cosmos, Storage, etc.) uses Azure-owned zones and is out of scope. |

> Sprint 13.1 mini-sprint decision. Records how the freshly-registered
> `curavias.ch` domain is used for public custom hostnames on Azure Container
> Apps, why we chose full Azure DNS delegation over GoDaddy-hosted DNS, and why
> the domain is intentionally decoupled from the MCAPS Entra tenant.

## Context

The platform has been running on Azure-provided Container Apps hostnames
(e.g. `ca-app-fluent-ihzhhpf-sit.ashysky-8f51a689.westus2.azurecontainerapps.io`).
These are correct but ugly, brittle to CAE recreation (see the ADR-0029
Option A track), and make MSAL redirect URIs churn with every infrastructure
change.

`curavias.ch` was registered at GoDaddy on 2026-07-13 (registrar), fresh + no
existing records, no email, no other services. The intended endpoints are:

- `app.curavias.ch` — PROD hcc-app-fluent Container App
- `appsit.curavias.ch` — SIT hcc-app-fluent Container App

Not in scope for this ADR:

- Public hostname on the agent-host CA (backend API — Azure-provided hostname
  is fine per the brainstorm; deferred until we have a UX reason to change).
- Adding `curavias.ch` as a **verified custom domain in Entra ID** (MCAPS
  restricts tenant custom domains AND ties the domain to the tenant, which is
  incompatible with the tenant-migration risk called out in ADR-0012).

## Decision

**Adopt full Azure DNS delegation ("Option C" in the brainstorm) + Azure
Container Apps managed certificates.**

1. Delegate the entire `curavias.ch` zone from GoDaddy to Azure DNS by setting
   NS records at GoDaddy that point at the Azure DNS name servers.
2. Zone is provisioned in [`infra/modules/dns/curavias.bicep`](../../infra/modules/dns/curavias.bicep)
   and lives in `rg-ihzhhpf-sit` for Sprint 13.1. When PROD is provisioned in
   its own RG, the module must be refactored to use an `existing` zone
   reference from PROD (or the zone moved to a shared RG). Tracked as a
   follow-up in this ADR.
3. Records are populated from Container Apps Bicep outputs — no hand-typed
   FQDNs, no secret material crossing module boundaries. Each hostname adds:
   - CNAME `<label>` → CA's `properties.configuration.ingress.fqdn`
   - TXT `asuid.<label>` → CA's `properties.customDomainVerificationId`
4. TLS certificates via
   [`Microsoft.App/managedEnvironments/managedCertificates`](https://learn.microsoft.com/azure/container-apps/custom-domains-managed-certificates)
   — free Let's Encrypt cert auto-issued + auto-renewed. No GoDaddy cert
   product needed. No self-signed certificates anywhere.
5. Container App ingress binds the custom hostname via `configuration.ingress.customDomains[]`
   with `bindingType: 'SniEnabled'` referencing the managed cert.
6. Deploy is a **two-phase** flow via the `appFluentEnableCustomDomainCert`
   param (default `false`):
   - Phase 1 (first deploy): create DNS zone + records only; skip cert
     issuance because NS delegation is not yet live.
   - Phase 2 (after NS delegation + propagation): flip the flag to `true`,
     redeploy; managed cert validates ownership + issues cert + CA binds.
   Runbook: [`docs/runbooks/curavias-dns-godaddy-delegation.md`](../runbooks/curavias-dns-godaddy-delegation.md).
7. `curavias.ch` is **not** used as an Entra verified custom domain.
   MSAL redirect URIs (application-level, not tenant-level) may use the
   hostnames — that requires no tenant verification, only Entra app
   registration config in
   [`infra/modules/entra/parameters/sit.bicepparam`](../../infra/modules/entra/parameters/sit.bicepparam).

## Rationale

Three shapes were evaluated in the brainstorm on 2026-07-13:

| # | Option | Hostname shape | DNS management | Recommendation |
| --- | --- | --- | --- | --- |
| A | Keep root at GoDaddy, add CNAMEs manually | `appsit.curavias.ch` | Click-ops in GoDaddy admin UI | Fastest for a single hostname, but not IaC. |
| B | Delegate a subdomain (e.g. `azure.curavias.ch`) to Azure DNS | `appsit.azure.curavias.ch` (deeper) | Bicep for the delegated subdomain | Partial IaC, hostname aesthetics compromise. |
| C | Delegate the full root `curavias.ch` to Azure DNS (**chosen**) | `appsit.curavias.ch` (clean) | Bicep for the entire zone | Full IaC + clean hostnames, safe because the domain is fresh + empty. |

Option C wins because:

- The domain is fresh and empty at GoDaddy — no existing records (email, MX,
  landing page, TXT verifications) to migrate. Delegating the root loses
  nothing.
- Bicep-managed records make hostname additions declarative and auditable
  (see also ADR-0010 — policy-as-code + release evidence).
- The hostname shape matches the intent stated by the decider (`app.curavias.ch`,
  `appsit.curavias.ch`), no compromise on hierarchy depth.
- Delegation is reversible: point NS back at GoDaddy's defaults at any time.

Rationale for **managed certs** over the "self-signed if we don't have a
GoDaddy cert" alternative that was briefly raised in the discussion:

| Aspect | Self-signed | Managed cert (Let's Encrypt) — **chosen** |
| --- | --- | --- |
| Cost | USD 0 | **USD 0** |
| Browser trust | ❌ "Not secure" warning every session | ✅ Trusted globally (Let's Encrypt is a widely-trusted CA) |
| MSAL sign-in | ❌ Some MSAL flows reject invalid certs | ✅ Works |
| Cert renewal | Manual | Automatic (Azure renews 30 days before expiry) |
| Ops burden | Rotation + secret management | None |
| Demo optics | Warning banners during a live pitch | Clean green padlock |

Rationale for **NOT using curavias.ch as an Entra tenant custom domain**:

- MCAPS-provided tenants (per ADR-0012) restrict tenant-level custom domain
  addition — organisational Entra policies would block us from binding
  `curavias.ch` as a verified domain.
- Even if allowed, tying the domain to the current Entra tenant would
  couple `curavias.ch` to the MCAPS tenant identity. If the platform later
  migrates tenants (see ADR-0012 tenant-migration risks), we'd need to
  detach the domain + reverify on the new tenant — high friction, error-prone.
- Keeping `curavias.ch` at the DNS/application layer only (no tenant
  coupling) means tenant migration re-provisions Azure resources in a new
  sub, we re-run the DNS module, we re-point NS at GoDaddy → done. The
  domain itself is portable.

## Consequences

**Positive:**

- Clean `https://appsit.curavias.ch` and (later) `https://app.curavias.ch` URLs
  for the demo and for MSAL redirects.
- Full IaC: hostname additions become a bicepparam edit + redeploy, no
  click-ops.
- Zero cert cost and zero cert operational burden.
- Domain portable across tenant migrations — no MCAPS-tenant coupling.
- MSAL redirect URIs anchor on stable hostnames — no churn on CAE
  recreation (the CNAME target changes, but the public hostname stays).

**Negative:**

- Two-phase deploy for the first cert issuance (Phase 1 DNS-only, Phase 2
  cert). Documented in the runbook. Not automatable further without
  Azure-side changes (Managed Cert resource is synchronous).
- Zone lives in `rg-ihzhhpf-sit` for Sprint 13.1 (co-located with SIT).
  When PROD is provisioned in a separate RG, the module needs a small
  refactor (use `existing` reference for the zone in PROD). Follow-up 1.
- Adds ~USD 0.50/month for the Azure DNS zone at demo scale. Trivial.

## Follow-ups

1. **PROD refactor** — when PROD RG is provisioned, refactor
   [`infra/modules/dns/curavias.bicep`](../../infra/modules/dns/curavias.bicep)
   to accept `manageZone: bool` (SIT owns, PROD consumes via `existing`),
   or move the zone to a dedicated shared RG (`rg-ihzhhpf-shared`) that both
   env deploys reference. Choice depends on how many other cross-env shared
   resources emerge by the time PROD lands.
2. **Entra MSAL redirect URIs** — update
   [`infra/modules/entra/parameters/sit.bicepparam`](../../infra/modules/entra/parameters/sit.bicepparam)
   `spaRedirectUris` to include `https://appsit.curavias.ch` (SIT) and
   `https://app.curavias.ch` (PROD). Separate PR after Phase 2 confirms the
   cert is live (avoids updating the app-registration before its intended
   surface is reachable). Requires a manual Entra module apply (subscription
   scope, per ADR-0027 §Reversibility).
3. **Agent-host public hostname** — deferred. Backend API, users never see
   the URL. If a UX reason emerges (e.g. exposing `/chat` from an external
   client that isn't the Fluent app), add `agenthost-sit.curavias.ch` +
   `agenthost.curavias.ch` in a follow-up.
4. **PROD promotion (issue [#179](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/179))**
   — after Follow-up 1 lands, flip `appFluentEnableCustomDomainCert: true`
   in PROD `bicepparam` and approve PROD deploy.

## Evidence

- Fresh domain confirmation: user statement 2026-07-13 pm — "the current
  curavias.ch domain is a fresh empty domain".
- Cert story confirmation: user acceptance of managed certs 2026-07-13 pm
  after clarifying the GoDaddy-cert misunderstanding.
- Bicep what-if against SIT (first deploy, `appFluentEnableCustomDomainCert = false`):
  `status: Succeeded`, `3 creates` (zone + CNAME + TXT), `0 deletes`.

## References

- [Azure Container Apps custom domains + managed certificates](https://learn.microsoft.com/azure/container-apps/custom-domains-managed-certificates)
- [Azure DNS zone delegation](https://learn.microsoft.com/azure/dns/dns-domain-delegation)
- [Let's Encrypt (via Azure Container Apps)](https://letsencrypt.org/)
- [ADR-0012](0012-tenant-migration-to-mcap164444.md) — tenant migration constraints
- [ADR-0013](0013-temporary-us-region-demo-scope.md) — demo scope in westus2
- [ADR-0027](0027-mcaps-demo-users-full-group-membership.md) — MCAPS demo-user model (why the tenant coupling would be risky)
