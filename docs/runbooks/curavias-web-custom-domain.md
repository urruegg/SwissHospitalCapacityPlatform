# Runbook — Curavias web custom-domain binding (curavias.ch + www)

> **Scope:** bind the PROD Azure Static Web App (`stapp-ihzhhpf-prod`) to the apex
> `curavias.ch` and `www.curavias.ch`. PROD-only (ADR-0030). Every apply is
> approval-gated (AGENTS.md §4 — requires an `approved-to-apply` comment + PROD
> environment reviewer).

## Prerequisites

- `curavias.ch` is an Azure DNS zone, delegated from GoDaddy (see
  `curavias-dns-godaddy-delegation.md`, ADR-0030).
- `enableCuraviasWebModule = true` in `infra/environments/prod.bicepparam` (already set).
- The Astro content has been deployed at least once via `curavias-web-deploy.yml`.

## Why apex needs an alias A record

A zone apex (`curavias.ch`) cannot be a CNAME. Azure Static Web Apps apex domains are
bound with an **Azure DNS alias A record** whose `targetResource` is the SWA resource id.
`www.curavias.ch` uses a normal **CNAME** to the SWA default hostname. The
`dns/curavias.bicep` module supports both via `aliasARecords` and `cnameRecords`.

## Two-step procedure

### Step 1 — provision hosting (custom domains OFF)

Deploy infra with `curaviasWebEnableCustomDomains = false` (default). This creates the
SWA + media storage without domain validation. Note the outputs:

- `curaviasWebStaticWebAppName` → e.g. `stapp-ihzhhpf-prod`
- `curaviasWebDefaultHostname`  → e.g. `<generated>.azurestaticapps.net`

### Step 2 — records + validation + binding

1. Add the DNS records by passing to `dns/curavias.bicep`:
   - `aliasARecords`: `[ { name: '@', targetResourceId: '<SWA resourceId>', ttl: 3600 } ]`
   - `cnameRecords`:  `[ { name: 'www', target: '<curaviasWebDefaultHostname>', ttl: 3600 } ]`
   - `txtRecords`:    the apex validation token TXT emitted by SWA when the custom
     domain is created with `validation: 'dns-txt-token'`.
2. Flip `curaviasWebEnableCustomDomains = true` and re-run the **approval-gated**
   PROD infra deploy. SWA validates ownership and issues managed TLS certs for both
   hostnames.
3. Verify: `https://curavias.ch` and `https://www.curavias.ch` serve the site over TLS.

## Rollback

Set `curaviasWebEnableCustomDomains = false` and redeploy to unbind the custom domains;
the SWA default hostname keeps serving. DNS records can be left in place or removed by
passing empty arrays to the DNS module.

## Zone-ownership note

The `curavias.ch` zone currently lives in `rg-ihzhhpf-sit`. When PROD gets its own RG,
refactor `dns/curavias.bicep` to an `existing` zone reference so PROD only adds records
and the zone stays SIT-owned (tracked in ADR-0030 follow-ups).
