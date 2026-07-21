# Curavias Web — Media Library Runbook

> Sprint 24, Phase 6 (issue #267). Governs how marketing media for the Curavias
> product site (`apps/curavias-web`) is stored, published, and referenced.

## Current state (source of truth)

The landing page is **fully self-contained**: every graphic on the site is
inline SVG or the brand icon shipped in-repo at
`apps/curavias-web/public/brand/curavias-icon.svg`. **No raster (PNG/JPG/WebP)
or photographic assets are shipped today**, so the media library starts empty.

This runbook establishes the process and env wiring so that future raster or
diagram assets have a governed home — without checking large binaries into git.

## Where media lives

| Layer | Resource | Notes |
| --- | --- | --- |
| In-repo (versioned) | `apps/curavias-web/public/**` | Small brand SVGs, favicons, `robots.txt`. Committed. |
| Media library (blob) | Storage `stmediaihzhhpfprod`, container `media` (public-read `Blob`) | Raster/photo/diagram assets. Provisioned by `infra/modules/experience-hosting/curavias-web.bicep`. |

Public base URL (module output `mediaBaseUrl`):

```text
https://stmediaihzhhpfprod.blob.core.windows.net/media
```

Only **non-PHI, brand-approved** marketing media is ever stored in this
container (public read access). Never place synthetic patient data, screenshots
of real data, or unlicensed marks here.

## Referencing media from the site

The site reads an optional build-time base URL. When unset, in-repo assets are
used and no external media is fetched.

1. Set `PUBLIC_MEDIA_BASE_URL` (see `apps/curavias-web/.env.example`).
2. Reference an asset as `` `${import.meta.env.PUBLIC_MEDIA_BASE_URL}/hero.webp` ``
   inside an `.astro` component, guarded by a fallback to an in-repo asset.

Keep the fallback so a missing env never breaks a build.

## Uploading assets (manual, gated)

Publishing to the PROD media library touches a PROD resource and is therefore
**human-gated** (`approved-to-apply`). Run only after the storage account exists
(infra applied) and with a brand-approved asset set:

```bash
# Auth via the same OIDC/WIF identity used by the deploy workflow, or an
# az login with Storage Blob Data Contributor on stmediaihzhhpfprod.
az storage blob upload-batch \
  --account-name stmediaihzhhpfprod \
  --auth-mode login \
  --destination media \
  --source ./media-staging \
  --overwrite true
```

Record the uploaded asset names + licence in the inventory below.

## Asset inventory

| Asset | Type | Status | Source / licence |
| --- | --- | --- | --- |
| `curavias-icon.svg` | Brand mark (in-repo) | Shipped | Curavias brandkit (`docs/brandkit`) |
| _(raster/photo assets)_ | — | None yet | — |

## Brand Central / stock (tracked, pending)

Official Curavias marks and any licensed stock photography are **pending a
Brand Central sign-in** and legal clearance (see issue #268). Until approved:

- Do **not** ship official marks or stock imagery to the media library.
- Use placeholder SVG / neutral illustrations only.
- Track outstanding items on issue #267 and the risk register.

**Acceptance (Phase 6):** site references the media base URL via a guarded env,
in-repo SVG committed, Brand Central items tracked, no unlicensed marks shipped.
