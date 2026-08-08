import { useEffect, type ReactNode } from 'react';
import { Tab, TabList, makeStyles, mergeClasses, tokens } from '@fluentui/react-components';
import { SectionHeader } from './SectionHeader';
import { useScrollSpy } from './useScrollSpy';

export interface NarrativeSection {
  key: string;
  label: string;
  render: () => ReactNode;
  full?: boolean;
}

interface NarrativeShellProps {
  /** Intro title. Omit (with introDescription) to render no intro section — the shell starts at the first `sections` entry. */
  introTitle?: string;
  introDescription?: string;
  sections: NarrativeSection[];
  /** Deep-link target (route param / hash) scrolled to on mount. */
  initialKey?: string;
  navLabel?: string;
  /** Eyebrow/kicker rendered above the intro title. */
  introEyebrow?: string;
  /** Anchor id + nav label for the intro rendered as the first section. */
  introKey?: string;
  introNavLabel?: string;
  /** The first N sections share one screen (grouped, some space between); the rest fill the viewport one-per-screen. */
  leadingGroupCount?: number;
  /** Extra intro content rendered under the description (e.g. disclaimer, mode badge). */
  introExtra?: ReactNode;
  /** Prefix for the nav tab test ids (`${prefix}-${key}`). Defaults to `backstage-nav`. */
  navTestIdPrefix?: string;
}

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
  },
  introExtra: {
    marginTop: tokens.spacingVerticalM,
  },
  navBar: {
    position: 'sticky',
    top: 0,
    zIndex: 10,
    backgroundColor: tokens.colorNeutralBackground2,
    paddingTop: tokens.spacingVerticalXS,
    paddingBottom: tokens.spacingVerticalXS,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  navInner: {
    width: '100%',
    maxWidth: '1280px',
    marginLeft: 'auto',
    marginRight: 'auto',
    boxSizing: 'border-box',
    paddingLeft: 'clamp(16px, 4vw, 48px)',
    paddingRight: 'clamp(16px, 4vw, 48px)',
  },
  sections: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXXL,
    width: '100%',
    maxWidth: '1280px',
    marginLeft: 'auto',
    marginRight: 'auto',
    boxSizing: 'border-box',
    paddingLeft: 'clamp(16px, 4vw, 48px)',
    paddingRight: 'clamp(16px, 4vw, 48px)',
    paddingTop: tokens.spacingVerticalL,
  },
  section: {
    scrollMarginTop: '88px',
  },
  sectionFull: {
    minHeight: 'calc(100svh - 150px)',
  },
  leadGroup: {
    minHeight: 'calc(100svh - 120px)',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    gap: tokens.spacingVerticalXXL,
  },
});

function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

export function scrollToSection(key: string) {
  if (typeof document === 'undefined') return;
  const el = document.getElementById(key);
  el?.scrollIntoView({ behavior: prefersReducedMotion() ? 'auto' : 'smooth', block: 'start' });
}

/** A vertical scroll narrative: sticky section nav (scrollspy) + stacked sections, intro first. */
export function NarrativeShell({
  introTitle,
  introDescription,
  sections,
  initialKey,
  navLabel,
  introEyebrow,
  introKey = 'company',
  introNavLabel = 'Company',
  leadingGroupCount,
  introExtra,
  navTestIdPrefix = 'backstage-nav',
}: NarrativeShellProps) {
  const s = useStyles();
  const introSection: NarrativeSection = {
    key: introKey,
    label: introNavLabel,
    render: () => (
      <>
        <SectionHeader
          id={introKey}
          variant="eyebrow"
          header={introTitle ?? ''}
          tagline={introEyebrow ?? ''}
          description={introDescription ?? ''}
        />
        {introExtra && <div className={s.introExtra}>{introExtra}</div>}
      </>
    ),
  };
  const allSections = introTitle ? [introSection, ...sections] : sections;
  const ids = allSections.map((section) => section.key);
  const active = useScrollSpy(ids);
  const selected = active || ids[0];
  const groupKeys =
    leadingGroupCount && leadingGroupCount > 0
      ? allSections.slice(0, leadingGroupCount).map((section) => section.key)
      : [];
  const scrollTargetFor = (key: string) =>
    groupKeys.length > 1 && groupKeys.includes(key) ? groupKeys[0] : key;

  useEffect(() => {
    if (!initialKey || !ids.includes(initialKey) || typeof window === 'undefined') return undefined;
    const timer = window.setTimeout(() => scrollToSection(scrollTargetFor(initialKey)), 60);
    return () => window.clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialKey]);

  return (
    <div className={s.root}>
      <div className={s.navBar}>
        <div className={s.navInner}>
          <TabList
            selectedValue={selected}
            aria-label={navLabel}
            onTabSelect={(_e, d) => scrollToSection(scrollTargetFor(String(d.value)))}
          >
            {allSections.map((section) => (
              <Tab key={section.key} value={section.key} data-testid={`${navTestIdPrefix}-${section.key}`}>
                {section.label}
              </Tab>
            ))}
          </TabList>
        </div>
      </div>
      <div className={s.sections}>
        {leadingGroupCount && leadingGroupCount > 0 ? (
          <>
            <div className={s.leadGroup}>
              {allSections.slice(0, leadingGroupCount).map((section) => (
                <section
                  key={section.key}
                  id={section.key}
                  className={s.section}
                  data-testid={`widget-${section.key}`}
                >
                  {section.render()}
                </section>
              ))}
            </div>
            {allSections.slice(leadingGroupCount).map((section) => (
              <section
                key={section.key}
                id={section.key}
                data-full={section.full ? 'true' : undefined}
                className={mergeClasses(s.section, section.full ? s.sectionFull : undefined)}
                data-testid={`widget-${section.key}`}
              >
                {section.render()}
              </section>
            ))}
          </>
        ) : (
          allSections.map((section) => (
            <section
              key={section.key}
              id={section.key}
              className={s.section}
              data-testid={`widget-${section.key}`}
            >
              {section.render()}
            </section>
          ))
        )}
      </div>
    </div>
  );
}
