# Curavias — Fluent UI Color System (Brand Kit extension)

### Fluent 2 / Fluent UI v9 colour schema — **primary = Success Green `#17B890`**, secondary = Curavias Blue `#365B7D`

| Field | Value |
| --- | --- |
| **Prepared for** | Urs Rüegg — Sr Solution Engineer Hub, Microsoft |
| **Primary brand** | Success Green `#17B890` = `brand[80]` (Fluent `colorBrandBackground`) |
| **Secondary brand** | Curavias Blue `#365B7D` (icon panel / wordmark; nav, headers, white-text actions) |
| **Status** | Draft v2.0 — green-primary re-base |
---

## 1. Overview

Green is now the **primary brand colour** (it best fits Curavias — care, health, the *journey to success*). Curavias Blue becomes the **secondary** brand (it stays the icon panel and wordmark). `#17B890` sits at `brand[80]`.

> **Accessibility rule baked into the theme:** green `#17B890` is bright — **white text on it fails WCAG AA (2.53:1)**. Curavias green surfaces therefore use **dark text** (`#0E0F11`, 7.57:1 AAA). For a solid button with **white** text, use **secondary blue** `#365B7D` (7.12:1 AAA). Green **text/links** on white use `brand[50] #12765F` (5.55:1 AA).

## 2. Colour ramps (10 → 160)

| Step | Green (PRIMARY) | Blue | Red | Amber | Teal | Violet | Grey |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **10** | `#0B1D1D` | `#0E141B` | `#200B10` | `#201B0E` | `#0C1C24` | `#121626` | `#0E0F11` |
| **20** | `#0D332D` | `#141E29` | `#3C0B11` | `#3D2E0C` | `#0F303D` | `#1C2243` | `#171A1C` |
| **30** | `#0F493E` | `#1A2837` | `#570A11` | `#59420A` | `#124457` | `#272E60` | `#212427` |
| **40** | `#10604E` | `#1F3245` | `#730911` | `#765508` | `#145870` | `#313B7D` | `#2D3134` |
| **50** | `#12765F` | `#253D53` | `#8F0812` | `#926806` | `#176C8A` | `#3B479A` | `#3B4045` |
| **60** | `#148C6F` | `#2B4761` | `#AB0812` | `#AF7B04` | `#1A81A3` | `#4553B6` | `#4B5258` |
| **70** | `#15A280` | `#30516F` | `#C70713` | `#CB8F02` | `#1C95BD` | `#5060D3` | `#5E666E` |
| **80** | `#17B890` | `#365B7D` | `#E30613` | `#E8A200` | `#1FA9D6` | `#5A6CF0` | `#6C767F` |
| **90** | `#39C2A0` | `#537290` | `#E62A35` | `#EBAF25` | `#3FB5DB` | `#7281F2` | `#808A93` |
| **100** | `#56CAAE` | `#6D87A0` | `#E94A54` | `#EDBB46` | `#5CC0E0` | `#8794F3` | `#969EA6` |
| **110** | `#73D3BB` | `#859BB0` | `#EC6971` | `#EFC666` | `#78CAE5` | `#9BA6F4` | `#ACB3B9` |
| **120** | `#8FDBC9` | `#9EAFC0` | `#EF878E` | `#F2D185` | `#93D4EA` | `#AFB7F6` | `#C2C7CB` |
| **130** | `#AAE3D5` | `#B5C2CF` | `#F2A4AA` | `#F4DBA3` | `#ADDEEE` | `#C2C8F7` | `#D6D9DC` |
| **140** | `#C5EBE2` | `#CCD5DE` | `#F5C1C5` | `#F6E6C1` | `#C7E7F2` | `#D5D9F8` | `#E3E6E8` |
| **150** | `#E0F2EF` | `#E3E8EC` | `#F7DEE0` | `#F8F0DE` | `#E1F1F7` | `#E8EAFA` | `#F1F2F3` |
| **160** | `#FAFAFB` | `#FAFAFB` | `#FAFAFB` | `#FAFAFB` | `#FAFAFB` | `#FAFAFB` | `#FBFBFB` |

## 3. Semantic token mapping (Fluent v9)

`createLightTheme(curaviasBrand)` sets brand tokens; the theme file overrides on-brand text + status tokens (`curavias-theme.ts`).

| Fluent token | Value | Use |
| --- | --- | --- |
| `colorBrandBackground` | `#17B890` | Primary buttons/selection — **dark text on top** |
| `colorBrandBackgroundHover` | `#15A280` | Primary hover |
| `colorBrandBackgroundPressed` | `#148C6F` | Primary pressed |
| `colorNeutralForegroundOnBrand` | `#0E0F11` | **Dark** text/icon on green (override) |
| `colorBrandForegroundLink` | `#12765F` | Green links/text on white (accessible) |
| `secondary · background` | `#365B7D` | Nav, headers, **white-text** buttons (blue) |
| `secondary · foreground` | `#537290` | Secondary text/links on white |
| `colorNeutralForeground1` | `#2E4C68` | Primary text (Ink) |
| `colorNeutralForeground2` | `#6B7A88` | Secondary text (Slate) |
| `colorStatusSuccessForeground1` | `#12765F` | Success text (green) |
| `colorStatusSuccessBackground3` | `#17B890` | Success fill (dark text) |
| `colorStatusDangerForeground1` | `#E62A35` | Error text |
| `colorStatusDangerBackground3` | `#E30613` | Error/critical fill (white text) |
| `colorStatusWarningForeground1` | `#EBAF25` | Warning text |
| `custom · info` | `#1FA9D6` | Informational chips (teal) |
| `custom · accent` | `#5A6CF0` | Decorative / data-viz (violet) |

## 4. Data-visualization palette (Power BI & charts)

`curavias-powerbi-theme.json` ships these `dataColors` (green leads); KPI status **good=`#17B890` · neutral=`#E8A200` · bad=`#E30613`**.

| # | HEX |
| --- | --- |
| 1 | `#17B890` |
| 2 | `#365B7D` |
| 3 | `#1C95BD` |
| 4 | `#5A6CF0` |
| 5 | `#E30613` |
| 6 | `#E8A200` |
| 7 | `#8FDBC9` |
| 8 | `#9EAFC0` |

## 5. Accessibility (WCAG contrast)
| Pair | Ratio | Verdict |
| --- | --- | --- |
| White text on Green[80] | 2.53:1 | Fail |
| **Dark** text on Green[80] — use this | 7.57:1 | AAA |
| White text on Blue[80] (secondary) | 7.12:1 | AAA |
| Green[50] link on white | 5.55:1 | AA |
| Ink #2E4C68 on white | 8.94:1 | AAA |
| White text on Danger[80] | 4.88:1 | AA |

**Takeaway:** never put white text on Curavias green — use dark text on green, or blue for white-text actions.

## 6. Usage & do/don'ts

- **Primary = green**: primary buttons, active/selected, success — always with **dark text**.
- **Secondary = blue**: top nav, headers, any solid **white-text** CTA; the logo wordmark.
- **Swiss red** = **error/critical only** in UI (also the logo's care cross — keep it for danger so it retains alarm meaning).
- **Teal** = info/tips; **Violet** = decorative & data-viz; **Amber** = warning.
- Don't fill large surfaces with saturated green — use `150/160` tints or neutral.

## 7. Files
| File | Purpose |
| --- | --- |
| `curavias-theme.ts` | Fluent v9 BrandVariants (green) + light/dark themes + on-brand & status overrides |
| `curavias-tokens.json` | All ramps + semantic aliases + data-viz (source of truth) |
| `curavias-tokens.css` | CSS `--cv-*` custom properties |
| `curavias-powerbi-theme.json` | Power BI theme (green-led) |
| `curavias-color-swatches.png` | Visual reference of all ramps |

## 8. Note on the logo
The wordmark stays **Ink/Blue** (now the *secondary* brand) — coherent, since green now drives the success node and UI primary actions. If you'd like the **wordmark in green** to foreground the new primary, I can produce that logo variant.

## 9. Integration

```tsx
import { FluentProvider } from '@fluentui/react-components';
import { curaviasLightTheme } from './curavias-theme';
<FluentProvider theme={curaviasLightTheme}><App /></FluentProvider>
```
