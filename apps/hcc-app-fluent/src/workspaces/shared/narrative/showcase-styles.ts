import { makeStyles, tokens } from '@fluentui/react-components';

/**
 * Sprint 40 START polish — shared "showcase" card language, lifted verbatim from
 * the polished BACKSTAGE narrative surface so START and Backstage share one visual
 * vocabulary (elevation + 4px colored left accent + hover + focus, evidence panels,
 * stat tiles, and the backstage table treatment). Accent colors are passed per-use
 * via inline `style={{ borderLeftColor, ... }}` (matching backstage's accent-hex
 * approach); this module owns only the structural/elevation styles.
 */
export const useShowcaseStyles = makeStyles({
  // Elevated, accent-left content card that doubles as a rail button.
  accentCard: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
    padding: tokens.spacingHorizontalL,
    borderRadius: tokens.borderRadiusLarge,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    borderLeftWidth: '4px',
    backgroundColor: tokens.colorNeutralBackground1,
    boxShadow: tokens.shadow2,
    textAlign: 'left',
    fontFamily: 'inherit',
    color: 'inherit',
    width: '100%',
    cursor: 'pointer',
    transitionProperty: 'box-shadow, transform',
    transitionDuration: tokens.durationNormal,
    ':hover': { boxShadow: tokens.shadow4 },
    ':focus-visible': {
      outlineStyle: 'solid',
      outlineWidth: '2px',
      outlineColor: tokens.colorStrokeFocus2,
      outlineOffset: '2px',
    },
  },
  // Same card language but non-interactive (no pointer/hover), for static content.
  staticCard: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
    padding: tokens.spacingHorizontalL,
    borderRadius: tokens.borderRadiusLarge,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    borderLeftWidth: '4px',
    backgroundColor: tokens.colorNeutralBackground1,
    boxShadow: tokens.shadow2,
  },
  cardTitle: {
    margin: 0,
    fontSize: tokens.fontSizeBase400,
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorNeutralForeground1,
  },
  cardBody: { fontSize: tokens.fontSizeBase200, color: tokens.colorNeutralForeground2, lineHeight: 1.45 },

  // Evidence panel (the "in numbers" surface).
  panel: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalS,
    padding: tokens.spacingHorizontalL,
    borderRadius: tokens.borderRadiusLarge,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
    boxShadow: tokens.shadow2,
  },
  panelTitle: {
    margin: 0,
    fontSize: tokens.fontSizeBase500,
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorNeutralForeground1,
  },
  note: { fontSize: tokens.fontSizeBase200, color: tokens.colorNeutralForeground3, lineHeight: 1.4 },

  // Two-column narrative + evidence composition.
  split: {
    display: 'grid',
    gridTemplateColumns: '1.05fr 0.95fr',
    gap: tokens.spacingHorizontalL,
    alignItems: 'start',
    '@media screen and (max-width: 900px)': { gridTemplateColumns: '1fr' },
  },

  // Stat tiles.
  statGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: tokens.spacingHorizontalM,
  },
  statCell: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusLarge,
    backgroundColor: tokens.colorNeutralBackground2,
  },
  statValue: { fontSize: tokens.fontSizeBase600, fontWeight: tokens.fontWeightBold, color: '#365B7D' },
  statSub: { fontSize: tokens.fontSizeBase200, color: tokens.colorNeutralForeground3 },

  // Backstage table treatment (replaces raw <table>s).
  table: { width: '100%', borderCollapse: 'collapse' },
  th: {
    textAlign: 'left',
    padding: '6px 8px',
    color: tokens.colorNeutralForeground3,
    fontWeight: tokens.fontWeightSemibold,
    textTransform: 'uppercase',
    fontSize: '11px',
    letterSpacing: '0.04em',
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  td: {
    padding: '8px',
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    color: tokens.colorNeutralForeground2,
    verticalAlign: 'top',
    fontSize: tokens.fontSizeBase200,
  },
  tdName: { color: tokens.colorNeutralForeground1, fontWeight: tokens.fontWeightSemibold },

  // Number / glyph badge tiles.
  numBadge: {
    display: 'grid',
    placeItems: 'center',
    width: '28px',
    height: '28px',
    borderRadius: tokens.borderRadiusCircular,
    color: '#FFFFFF',
    fontSize: tokens.fontSizeBase200,
    fontWeight: tokens.fontWeightBold,
    flexShrink: 0,
  },
  glyphTile: {
    display: 'grid',
    placeItems: 'center',
    width: '40px',
    height: '40px',
    borderRadius: tokens.borderRadiusLarge,
    fontSize: '22px',
    flexShrink: 0,
  },

  // Header row for a card (badge/glyph + title).
  cardHead: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalM },
});

/** Canonical accent hexes (matching the mockup + backstage decorative palette). */
export const SHOWCASE_ACCENT = {
  green: '#17B890',
  navy: '#365B7D',
  teal: '#1FA9D6',
  violet: '#5A6CF0',
  amber: '#E8A200',
  red: '#E30613',
  slate: '#6B7A88',
} as const;

export type ShowcaseAccent = keyof typeof SHOWCASE_ACCENT;
