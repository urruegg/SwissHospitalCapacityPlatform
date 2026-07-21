# Curavias → Power BI Theme Token Mapping

| Field | Value |
|-------|-------|
| **Version** | 1.0.1 |
| **Date** | 2026-07-21 |
| **Author** | Urs Rüegg |
| **Status** | Draft for review |
| **Previous Version** | 1.0.0 (helvion→curavias brand rename) |
| **Theme file** | [curavias.json](curavias.json) |
| **Design spec** | [docs/superpowers/specs/2026-07-09-powerbi-demoable-redesign-design.md](../../../../docs/superpowers/specs/2026-07-09-powerbi-demoable-redesign-design.md) §8 |

This document maps the Curavias brand tokens (design spec §8) to the Power BI
theme JSON keys used in [`curavias.json`](curavias.json). Sprint 13 reuses it to
derive the Fluent theme tokens for the React app, so the mapping is kept
human-readable and one-to-one with the theme file.

## Colour tokens

| Curavias token | Value | Power BI theme key(s) |
|---------------|-------|-----------------------|
| Curavias Red | `#E30613` | `dataColors[0]`, `bad` (negative / over-threshold KPI accent) |
| Curavias Blue | `#365B7D` | `dataColors[1]`, `tableAccent`, `maximum`, `hyperlink`, KPI headline |
| Ink | `#2E4C68` | `foreground` (primary text) |
| Slate | `#6B7A88` | `foregroundNeutralSecondary` (chart axis, subdued text) |
| White | `#FFFFFF` | `background` (page + card backgrounds) |
| Rainbow — warm tip | `#FF9A2E` | `dataColors[2]`, `neutral`, `center` |
| Rainbow — coral | `#FF5A4E` | `dataColors[3]` |
| Rainbow — magenta | `#F0398F` | `dataColors[4]` |
| Rainbow — violet | `#9A4FF0` | `dataColors[5]`, `visitedHyperlink` |
| Rainbow — azure | `#3E7BF6` | `dataColors[6]` |
| Rainbow — cool base | `#23C57E` | `dataColors[7]`, `good` |

Derived neutrals (not brand primaries, tuned for readability against the palette):

| Purpose | Value | Power BI theme key |
|---------|-------|--------------------|
| Light surface | `#F3F5F7` | `backgroundLight` |
| Neutral surface | `#DCE1E6` | `backgroundNeutral` |
| Tertiary text | `#9BA7B2` | `foregroundNeutralTertiary`, `null` |
| Gauge minimum | `#DCE7F0` | `minimum` |

## Typography tokens

| Curavias role | Font | Power BI `textClasses` key |
|--------------|------|----------------------------|
| Wordmark / KPI headline | Segoe UI (Bold-weighted at render) | `callout` |
| Section title | Segoe UI Semibold | `title` |
| Subhead / descriptor (uppercase) | Segoe UI Semibold | `header` |
| Body / chart labels | Segoe UI | `label` |

## Notes

- The rainbow gradient (`dataColors[2..7]`) drives categorical charts (donut, bar,
  funnel) so multi-category visuals stay on-brand.
- `bad`/`neutral`/`good` map to Curavias Red / warm-orange / cool-green so RAG
  states inherit the brand palette instead of the default Power BI traffic colours.
- The theme replaces the default `CY26SU05` base theme via `report.json`
  (`themeCollection.baseTheme` → `curavias`).
