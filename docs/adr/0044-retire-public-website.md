# ADR-0044: Retire the public Curavias website (`apps/curavias-web` / curavias.ch)

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-25 |
| **Author** | Urs Rüegg |
| **Decision-makers** | @urruegg |
| **Supersedes** | The public-web scope of the Sprint 24 product-marketing + webpage epic (#261): `FR-WEB-001` to `FR-WEB-005` in [docs/PRD.md](../PRD.md) are withdrawn. |
| **Related** | [ADR-0030](0030-curavias-dns-strategy.md) (curavias.ch DNS zone — retained for the Fluent app), [ADR-0013](0013-temporary-us-region-demo-scope.md), [ADR-0016](0016-no-phi-in-mvp-demo-scope.md), [issue #275](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/275) |

## Context

Sprint 24 (epic #261) added a public, PROD-only Astro landing page for the
Curavias showcase (`apps/curavias-web`), hosted on Azure Static Web Apps at
`curavias.ch` / `www.curavias.ch`, provisioned by the
`infra/modules/experience-hosting/curavias-web.bicep` module (toggled by
`enableCuraviasWebModule` in `prod.bicepparam`) and deployed by the
`curavias-web-deploy.yml` workflow.

The site never went live:

* The custom-domain binding was never flipped on
  (`curaviasWebEnableCustomDomains = false` — the two-step binding stayed on
  step 1).
* The apex/`www` DNS records were never wired into `infra/main.bicep`; only the
  Fluent-app records (`app.curavias.ch` CNAME + `asuid.app` TXT) are populated
  in the shared `curavias.ch` zone.
* Requirements `FR-WEB-001..005` were tracked **Open — deferred** (#275).

The showcase is served end-to-end through the in-app experience
(`hcc-app-fluent` at `app.curavias.ch`); a separate marketing landing page adds
maintenance and legal-clearance surface (trademark / Swiss-cross, tracked as an
open item under `FR-WEB-005`) without advancing the demo. The product owner
decided to retire the public website rather than carry it as deferred scope.

## Decision

1. **Retire the public Curavias website in full.** Remove the app, its hosting
   infrastructure, its deploy workflow, and its runbooks:
   * `apps/curavias-web/**`
   * `.github/workflows/curavias-web-deploy.yml`
   * `infra/modules/experience-hosting/curavias-web.bicep`
   * `infra/main.bicep`: the `curaviasWeb` module block, the
     `enableCuraviasWebModule` / `curaviasWebMediaPublisherPrincipalId` /
     `curaviasWebEnableCustomDomains` params, and the three `curaviasWeb*`
     outputs + `curaviasWeb` module-status entry.
   * `infra/environments/prod.bicepparam`: the three `curaviasWeb*` params.
   * `infra/modules/dns/curavias.bicep`: the website-only, never-wired
     `aliasARecords` param + alias-A resource.
   * `docs/runbooks/curavias-web-custom-domain.md`,
     `docs/runbooks/curavias-web-media-library.md`.
2. **Withdraw `FR-WEB-001..005`** in [docs/PRD.md](../PRD.md), marking them
   Retired and linking this ADR (the IDs are kept for traceability, not reused).
3. **Retain the shared `curavias.ch` DNS zone** and its Fluent-app records — the
   zone serves `hcc-app-fluent` (`app.curavias.ch`), not the website. ADR-0030
   remains in force for the zone.
4. **Keep the `product-marketing-agent`.** Its `FR-MKT-*` charter (stringent,
   brand-aligned messaging across channels) stands; only its retired
   website-copy deliverable is dropped.

## Consequences

* **Positive:** Removes unshipped scope, one deployable surface, one workflow,
  and the trademark/Swiss-cross legal-clearance exposure carried by `FR-WEB-005`.
  Reduces the PROD infra surface and CI matrix.
* **Neutral:** No live Azure resource is affected — the Static Web App and media
  storage were never provisioned in a running environment; the toggle stayed
  `false`. The `curavias.ch` zone and Fluent-app hostname are untouched.
* **Negative / residual:** There is no standalone public marketing page for the
  Curavias showcase; product messaging is delivered in-app and via the
  `product-marketing-agent`. If a public page is wanted later, it must be
  re-proposed as fresh scope (new FR IDs; `FR-WEB-*` are retired, not revived).

## Migration

* Consumers that referenced `FR-WEB-001..005` (the `product-marketing-agent`
  golden task and `docs/CURAVIAS-PRODUCT-STATUS.md`) are updated in the same PR.
* No Azure teardown is required. Should the module ever have been deployed, the
  removal is the standard "remove-from-template → what-if → apply" path against
  PROD, gated by `approved-to-apply`.
