import {
  createLightTheme,
  createDarkTheme,
  type BrandVariants,
  type Theme,
} from '@fluentui/react-components';

/**
 * Sprint 13 T1 — Fluent UI v9 theme derived from the Helvion brand tokens.
 *
 * Source of truth for the token values:
 * `data-platform/reports/capacity-dashboard.Report/themes/helvion-token-mapping.md`
 * (landed in the Power BI M1 redesign). Kept one-to-one with that mapping so the
 * React app and the Power BI report stay visually consistent.
 */

// Helvion Blue (#365B7D) anchors the Fluent brand ramp. The ramp below is a
// perceptual interpolation from near-white to near-black through the brand hue.
export const helvionBrand: BrandVariants = {
  10: '#020304',
  20: '#111a24',
  30: '#182b3d',
  40: '#1e3750',
  50: '#254564',
  60: '#2c5279',
  70: '#365b7d', // Helvion Blue — primary brand
  80: '#4a6d8d',
  90: '#5e7f9d',
  100: '#7291ad',
  110: '#86a3bd',
  120: '#9bb5cd',
  130: '#b0c7dc',
  140: '#c6d9ec',
  150: '#dceafb',
  160: '#f0f6ff',
};

/** Raw Helvion palette tokens re-exported for card/KPI accents (see mapping doc). */
export const helvionTokens = {
  red: '#E30613', // bad / over-threshold
  blue: '#365B7D', // primary brand / KPI headline
  ink: '#2E4C68', // primary text
  slate: '#6B7A88', // subdued text / axis
  white: '#FFFFFF', // surfaces
  warm: '#FF9A2E', // neutral / center
  coral: '#FF5A4E',
  magenta: '#F0398F',
  violet: '#9A4FF0',
  azure: '#3E7BF6',
  cool: '#23C57E', // good
  lightSurface: '#F3F5F7',
  neutralSurface: '#DCE1E6',
} as const;

/** RAG accents mirror the Power BI `bad`/`neutral`/`good` mapping. */
export const ragColors = {
  bad: helvionTokens.red,
  neutral: helvionTokens.warm,
  good: helvionTokens.cool,
} as const;

/** Categorical series colours (dataColors[2..7] in the Power BI theme). */
export const categoricalColors = [
  helvionTokens.warm,
  helvionTokens.coral,
  helvionTokens.magenta,
  helvionTokens.violet,
  helvionTokens.azure,
  helvionTokens.cool,
] as const;

export const helvionLightTheme: Theme = createLightTheme(helvionBrand);
export const helvionDarkTheme: Theme = createDarkTheme(helvionBrand);
