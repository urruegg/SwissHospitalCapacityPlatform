# Curavias — Brand Guidelines (Brand Kit v2)

### Swiss Hospital Capacity Copilot — the official brand kit for solution branding

| Field | Value |
| --- | --- |
| **Product name** | **Curavias** |
| **Meaning** | *cura* (care) + *via* (path) = **"the care pathway"** |
| **Domain** | curavias.ch |
| **Descriptor** | Swiss Hospital Capacity Copilot |
| **Tagline** | *Every patient's path, in Swiss hands.* |
| **Powered by** | Microsoft |
| **Version** | Brand Kit v2 (green-primary) |

---

## 1. Vision & Mission

**Vision (North Star).** A Switzerland where every hospital steers **all** of its capacity — beds, operating rooms, staff, rooms and equipment — as **one intelligent, real-time system**. Where every patient reaches the right place at the right time, clinicians are freed from firefighting, and hospitals can **foresee and rehearse** tomorrow's pressure before it arrives — from a single ward to the whole canton.

**Mission.** Curavias gives Swiss hospitals **one trustworthy AI Hospital Command Center for capacity** — an ontology-grounded copilot and what-if simulation platform that **forecasts** demand, **coordinates** discharge, **steers** beds, OR, staff, rooms and equipment, and **rehearses** crises — with **Swiss data residency, grounded and auditable AI, and Swiss precision.**

---

## 2. The Idea Behind the Mark

Curavias means **"the care pathway."** The icon shows a **three-step patient journey rising to success**:

> **Start** (entry into care) → **Care** (the Swiss/medical cross) → **Success** (a green check — the patient made well).

This is the platform's whole purpose in one glyph: moving every patient along a clear pathway to a successful outcome. Swissness comes from the diagonal white / federal-blue split and the Swiss cross (à la MeteoSwiss).

---

## 3. Logo System

| Asset | File | Use |
| --- | --- | --- |
| **App icon** | `icon/curavias-icon.svg` | App tile, PWA, store listings (Swiss cross + journey) |
| **Standalone symbol** | `logo/curavias-symbol.svg` | Avatars, favicons-in-context, watermarks |
| **Horizontal logo** | `logo/curavias-logo.svg` | Default logo (symbol + wordmark + descriptor) |
| **Logo with tagline** | `logo/curavias-logo-tagline.svg` | Hero, cover, presentations |
| **Favicons / app tiles** | `icon/favicons/curavias-{16…1024}.png` | Browser/app icons |

**Usage.** Keep clear space around the logo (≥ the height of the symbol's success node). Place on white or very light backgrounds. Don't recolour the journey nodes, stretch/skew the mark, or crowd it. SVG is the scalable master; PNG are previews. For production, convert the wordmark to outlines.

---

## 4. Colour System (Fluent UI conformant)

**Primary = Success Green `#17B890`** (the journey's success). **Secondary = Curavias Blue `#365B7D`** (the icon panel and wordmark). Full 16-step ramps, Fluent v9 tokens, Power BI theme and the accessibility model are in **`color/Curavias-Fluent-Color-System.md`** and shipped as code in `color/`.

| Role | HEX | Notes |
| --- | --- | --- |
| **Primary — Green** | `#17B890` | Primary buttons, active/selected, success — **always dark text on green** |
| **Secondary — Blue** | `#365B7D` | Nav, headers, white-text CTAs, wordmark |
| Danger — Swiss Red | `#E30613` | Error/critical only (also the logo care-cross) |
| Warning — Amber | `#E8A200` | Warnings (added for completeness) |
| Info — Teal | `#1FA9D6` | Informational chips/tips |
| Accent — Violet | `#5A6CF0` | Decorative / data-viz |
| Text — Ink / Slate | `#2E4C68` / `#6B7A88` | Primary / secondary text |

> **Critical accessibility rule:** green `#17B890` is bright — **white text on it fails WCAG AA (2.5:1)**. Use **dark text on green** (7.6:1 AAA); use **blue** for any solid **white-text** button. Green **links** on white use the darker `brand[50]`. This is pre-wired in `color/curavias-theme.ts`.

Colour deliverables in `color/`: `curavias-theme.ts` (Fluent v9 theme), `curavias-tokens.json`, `curavias-tokens.css`, `curavias-powerbi-theme.json`, `curavias-color-swatches.png`.

---

## 5. Typography

- **Wordmark & headings:** Segoe UI Bold (Microsoft's brand typeface). Fallbacks: Helvetica Neue, Arial.
- **Descriptor:** Segoe UI Semibold, uppercase, letter-spaced.
- **Body / UI:** Segoe UI (Fluent default).

---

## 6. Legal & Clearance Notes

1. **Swiss coat of arms.** Use the **Swiss cross / flag** (as in the assets), **not the federal shield** — the shield is reserved for the Confederation. Ensure the brand is not misleading as to official origin; obtain **legal review** before public release.
2. **Name / domain.** `curavias.ch` is registered; complete **trademark clearance** (CH/EU, healthcare-IT & software classes) before production use.
3. **Microsoft / Copilot.** The mark is original (inspired by, not copied from, Microsoft assets). Use of "Copilot" and "Powered by Microsoft" follows Microsoft brand & partner guidelines.

---

## 7. Kit Contents

```
brandkitv2/
├─ Curavias-Brand-Guidelines.(md|docx)   ← this document
├─ README.(md|docx)                       ← quick index
├─ logo/     curavias-logo, -logo-tagline, -symbol  (.svg + .png)
├─ icon/     curavias-icon (.svg + .png) + favicons/ (16–1024 px)
└─ color/    curavias-theme.ts, -tokens.json, -tokens.css,
             curavias-powerbi-theme.json, curavias-color-swatches.png,
             Curavias-Fluent-Color-System.(md|docx)
```

*Brand Kit v2 supersedes the earlier "Helvion" concept and the C-series icon explorations (kept under `../branding/` for reference only).*
