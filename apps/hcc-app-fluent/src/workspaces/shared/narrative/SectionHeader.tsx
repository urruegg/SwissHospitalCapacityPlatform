import type { ReactNode } from 'react';
import { Body1, Caption1, makeStyles, tokens } from '@fluentui/react-components';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
    scrollMarginTop: '72px',
  },
  headRow: {
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: tokens.spacingHorizontalL,
    flexWrap: 'wrap',
  },
  headText: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
    flexGrow: 1,
    minWidth: 0,
  },
  header: {
    margin: 0,
    fontSize: tokens.fontSizeBase500,
    lineHeight: tokens.lineHeightBase500,
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorNeutralForeground1,
  },
  headerLg: {
    margin: 0,
    fontSize: tokens.fontSizeBase600,
    lineHeight: tokens.lineHeightBase600,
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorNeutralForeground1,
  },
  eyebrow: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: tokens.fontSizeBase200,
    fontWeight: tokens.fontWeightBold,
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
    color: '#12765F',
    '::before': {
      content: '""',
      width: '22px',
      height: '3px',
      borderRadius: '2px',
      backgroundColor: '#17B890',
    },
  },
  tagline: {
    color: tokens.colorBrandForeground1,
    fontWeight: tokens.fontWeightSemibold,
  },
  description: {
    color: tokens.colorNeutralForeground2,
  },
  tools: {
    display: 'flex',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalS,
  },
});

interface SectionHeaderProps {
  /** Anchor id — the scrollspy target and `TabList` value. */
  id: string;
  header: string;
  tagline: string;
  description: string;
  /** 'eyebrow' renders the tagline as an uppercase kicker above the title (Backstage). */
  variant?: 'default' | 'eyebrow';
  /** Optional right-aligned controls (e.g. the DFL play/pause + mode toggle). */
  tools?: ReactNode;
}

/** Self-describing header for a vertical-narrative section: header + tagline + description. */
export function SectionHeader({ id, header, tagline, description, tools, variant = 'default' }: SectionHeaderProps) {
  const s = useStyles();
  const isEyebrow = variant === 'eyebrow';
  return (
    <header className={s.root} data-testid={`section-header-${id}`}>
      <div className={s.headRow}>
        <div className={s.headText}>
          {isEyebrow ? (
            <>
              <span className={s.eyebrow}>{tagline}</span>
              <h2 id={`${id}-title`} className={s.headerLg}>{header}</h2>
            </>
          ) : (
            <>
              <h2 id={`${id}-title`} className={s.header}>{header}</h2>
              <Caption1 className={s.tagline}>{tagline}</Caption1>
            </>
          )}
          <Body1 className={s.description}>{description}</Body1>
        </div>
        {tools && <div className={s.tools}>{tools}</div>}
      </div>
    </header>
  );
}
