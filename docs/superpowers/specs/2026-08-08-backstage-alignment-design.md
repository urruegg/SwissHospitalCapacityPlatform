---
Version: 1.0.1
Date: 2026-08-08
Author: Copilot coding agent (autopilot, delegated)
Status: Draft
Previous Version: 1.0.0 (reviews section: seat-keyed sessions with translated name/persp, not English-only records)
---

# Backstage-plane alignment + BVA v2.0.0 re-baseline — design & assumptions

## 1. Context

The Curavias `apps/hcc-app-fluent` **backstage** plane (plus one start-plane menu
rename) needs a content + layout alignment pass so its wording, spacing tokens,
person roster and BVA numbers match the shipped start plane and the recalculated
[`docs/BVA.md` v2.0.0](../../BVA.md) evidence base. Experience-lane only; no
data-lane or infra changes. Governance: never self-merge, never self-approve a
SIT/PROD deploy.

## 2. The six asks (as scoped)

1. **Start menu rename** — `Value` -> `Stage` (`start.frontier.nav.value`), all 4
   locales.
2. **Backstage menu renames** — `Digital Feedback Loop` -> `Feedback Loop`,
   `DevSecOps loop` -> `DevSecOps`, `Review sessions` -> `Review`,
   `Product Owner Agent` -> `Product Owner`, `90-day roadmap` -> `Roadmap`. All 4
   locales.
3. **Section spacing (item 2)** — the gap between the company-intro section
   (`## We didn't just build a Frontier Firm...`) and the BVA section
   (`## We ran a BVA on ourselves...`) must use the standard vertical token.
4. **Business case (item 3)** — fix header->body + card-title spacing; **remove the
   `Executive decision` card**; re-baseline every BVA number to v2.0.0; establish
   **named-constant variables** so start + backstage share one source of truth.
5. **Review sessions (item 4)** — 3-column table (`SESSION` / `DATE` /
   `Perspective challenged`); harmonize titles + perspectives to the start-plane
   "What we heard" vocabulary; change the venue line to
   `Held at the Microsoft Innovation Hub, Zurich, and with hospital teams
   directly.`; rebuild the person cards (photo + name + role + link) to the exact
   9-person authoritative roster.
6. **First-frontier spacing (item 5) + general standardization (item 6)** — fix the
   subtext->cards gap; token standardization; translate touched labels.

## 3. Key decisions (autonomous)

- **BVA single source of truth.** New module
  `apps/hcc-app-fluent/src/data/bva/bva-figures.ts` exports v2.0.0 canonical
  constants; `bva-evidence.ts` consumes them. This satisfies the "establish
  variables" ask and keeps start + backstage numbers aligned. A later sprint can
  publish the `bva_*` gold tables in Fabric and bind the app to them (out of scope
  here).
- **v2.0.0 canonical figures** (from `docs/BVA.md` + `data/master-data/bva`):
  one-time `780,000` (Frontier) / `1,300,000` (ROM); annual run `1,250,000`;
  3-year TCO `4,530,000` (Frontier) / `5,050,000` (ROM); 3-year gross benefit
  `11,460,000`; 3-year net value `6,930,000`; **3-year ROI `153%`**; payback
  `~3.6 months`; gross annual benefit `3,820,000`; net annual benefit
  `2,570,000`. Sensitivity: Conservative `TCO 4,860,000 / ROI 60%`, Base
  `TCO 4,530,000 / ROI 153%`, Upside `TCO 4,390,000 / ROI 242%`.
- **Headline KPI mapping.** `Net Value Realized (3yr)` -> `6.93M` CHF;
  `ROI %` -> `153`, target label -> `Net annual benefit CHF 2.57M`.
- **Plan-vs-actual reframed** to the "recalculated TCO is lower" story: 3-year TCO
  plan (ROM) `5,050,000` -> actual (Frontier) `4,530,000`, variance `-10.3%`. The
  card title i18n `tcoTitle` changes `Annualised TCO` -> `3-year TCO`.
- **Sensitivity `Base ROM` -> `Base (Frontier-informed)`.** The scenario id stays
  `base-rom` for stability; only the label + numbers update (ROM 127% becomes the
  Frontier 153% base).
- **Executive-decision card removal.** Removing `bva-final-card` also removes both
  its CTAs (launch + rail). The launch/roadmap link is preserved by the standalone
  90-day/Roadmap backstage section; the Product Owner rail remains reachable from
  the Product-Owner tab. Unused imports/functions/styles are cleaned.
- **Review sessions are seat-keyed, chrome + records translated.** The 6 sessions
  are keyed to the start-plane "What we heard" seats (COO/CIO/Ops/CTO/CISO/IT);
  their session name + harmonized perspective are i18n keys
  (`reviews.sessions.<seat>.{name,persp}`) translated in en + de (fr/it fall back
  to en). Column headers, the venue note and section chrome are i18n. New key
  `reviews.colDate`; the table is 3 columns (Session / Date / Perspective
  challenged). Dates stay ISO literal data in the component.
- **9-person roster.** The 8 start-plane challenger reviewers (Rebekka Hatzung,
  Emanuel Furler, Christian Ernst, Dr. Regula Adams, Dr. med. Marco Rossi, Petrus
  Jallo, Rene Raeber, Daniel von Bueren) render with their existing photo assets;
  Marco Weber (Cloud & AI Solution Engineer) has no photo -> initials fallback.
  Michael Doring-Wermelinger, Rebekka's old placeholder role, and the "AMA review
  panel" tile are removed.
- **Translation scope (item 6).** Fully translate the nav renames + all touched
  review/BVA chrome across en/de/fr/it. The large set of pre-existing hardcoded
  English constants in `BackstageNarrativeSections.tsx` (FOCUS_DOMAINS challenge
  quotes, PO_CLASSES, DevSecOps legend) is **documented deferred debt** — a full
  backstage-narrative localization is a separate, larger task and out of scope for
  this alignment pass.

## 4. Verification gates (mandatory)

`tsc --noEmit` exit 0; `vitest` on all touched files; mojibake scan 0; axe
wcag2aa 0 serious+critical on the backstage narrative sections; visual check at
`localhost:5173/backstage`.
