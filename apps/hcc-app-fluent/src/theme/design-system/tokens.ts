import { tokens as fluent } from '@fluentui/react-components';

/** Semantic tokens: name the decisions Fluent leaves open so screens stop hand-rolling them. */
export const space = {
  xs: '4px',
  s: '8px',
  m: '12px',
  l: '16px',
  xl: '24px',
  xxl: '32px',
} as const;

export const radii = {
  control: fluent.borderRadiusMedium,
  card: fluent.borderRadiusLarge,
  pill: fluent.borderRadiusCircular,
} as const;

export const elevation = {
  flat: fluent.shadow2,
  card: fluent.shadow4,
  raised: fluent.shadow8,
  overlay: fluent.shadow16,
  dialog: fluent.shadow28,
} as const;

export const motion = {
  durationFast: fluent.durationFaster,
  durationNormal: fluent.durationNormal,
  durationSlow: fluent.durationSlow,
  easyEase: fluent.curveEasyEase,
  decelerate: fluent.curveDecelerateMid,
} as const;

export const density = { rowHeight: '44px', compactRowHeight: '36px' } as const;
export const zIndex = { base: 0, sticky: 100, drawer: 400, overlay: 800 } as const;
export const focus = { ringWidth: '2px', ringOffset: '2px' } as const;

export const dsTokens = { space, radii, elevation, motion, density, zIndex, focus } as const;
