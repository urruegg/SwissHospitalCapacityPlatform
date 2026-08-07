import { useRef, useState, type KeyboardEvent } from 'react';
import { makeStyles, mergeClasses, tokens } from '@fluentui/react-components';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { SHOWCASE_ACCENT, useShowcaseStyles } from '../../shared/narrative/showcase-styles';
import { CHALLENGER_PERSONAS, type ChallengerPersonaId } from './start-content';

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalL, minWidth: 0 },
  tablist: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalL,
    marginTop: tokens.spacingVerticalL,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  tab: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-start',
    gap: '1px',
    padding: `${tokens.spacingVerticalXS} 0 ${tokens.spacingVerticalS}`,
    marginBottom: '-1px',
    background: 'transparent',
    border: 'none',
    borderBottom: '2px solid transparent',
    cursor: 'pointer',
    textAlign: 'left',
    color: 'inherit',
    ':hover': { borderBottomColor: tokens.colorNeutralStroke1 },
    ':focus-visible': {
      outline: `2px solid ${tokens.colorStrokeFocus2}`,
      outlineOffset: '2px',
      borderRadius: tokens.borderRadiusSmall,
    },
  },
  tabSelected: { borderBottomColor: SHOWCASE_ACCENT.green },
  tabTag: { fontWeight: tokens.fontWeightSemibold, color: tokens.colorNeutralForeground2 },
  tabTagSelected: { color: tokens.colorNeutralForeground1 },
  tabSub: { fontSize: tokens.fontSizeBase200, color: tokens.colorNeutralForeground3 },
  pane: { borderLeftWidth: '4px' },
  who: { display: 'flex', flexDirection: 'column', gap: '2px', marginBottom: tokens.spacingVerticalS },
  whoName: { fontSize: tokens.fontSizeBase400, fontWeight: tokens.fontWeightSemibold, color: tokens.colorNeutralForeground1 },
  whoMeta: { fontSize: tokens.fontSizeBase200, color: tokens.colorNeutralForeground3 },
  quote: {
    margin: 0,
    paddingLeft: tokens.spacingHorizontalM,
    borderLeft: `3px solid ${tokens.colorNeutralStroke1}`,
    fontSize: tokens.fontSizeBase400,
    fontStyle: 'italic',
    lineHeight: 1.5,
    color: tokens.colorNeutralForeground1,
  },
  gloss: {
    marginTop: tokens.spacingVerticalXS,
    fontSize: tokens.fontSizeBase200,
    color: tokens.colorNeutralForeground3,
    lineHeight: 1.4,
  },
  heading: {
    margin: 0,
    marginTop: tokens.spacingVerticalM,
    fontSize: tokens.fontSizeBase300,
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorNeutralForeground1,
  },
  para: { margin: 0, fontSize: tokens.fontSizeBase200, color: tokens.colorNeutralForeground2, lineHeight: 1.5 },
  narrative: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXS, minWidth: 0 },
  list: {
    margin: 0,
    marginTop: tokens.spacingVerticalXS,
    paddingLeft: '1.1rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    fontSize: tokens.fontSizeBase200,
    color: tokens.colorNeutralForeground2,
    lineHeight: 1.45,
  },
  disclaimer: { marginTop: tokens.spacingVerticalS },
});

/**
 * Sprint 40 START polish — the mockup's "The room pushed back" section. Six real,
 * dated review-session challengers are presented as a tabbed deep-dive: pick a seat
 * (COO / CIO / CTO / CISO / Hospital Operations / IT-Cantonal) and read the actual
 * question, how it was addressed, the value delivered and what changed in the product.
 * Section chrome is localised (en/de); the authentic attributed quotes are kept
 * verbatim (original language plus the mockup's English gloss) and never translated.
 * The eyebrow / title / lead are supplied by StartView's SectionHeader wrapper, so this
 * component renders only the tab strip, the selected pane and the synthetic disclaimer.
 *
 * The tab strip is a native ARIA tablist (role tablist/tab/tabpanel with roving tabindex
 * and arrow-key selection-follows-focus) rather than a Fluent TabList, so the section
 * stays free of the Tabster dummy-sentinel `aria-hidden-focus` violation and meets the
 * NFR-UX-001 axe AA gate.
 */
export function ChallengerSection() {
  const styles = useStyles();
  const sc = useShowcaseStyles();
  const { t } = useTranslation();
  const [selected, setSelected] = useState<ChallengerPersonaId>('coo');
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);

  const selectAt = (index: number) => {
    const clamped = (index + CHALLENGER_PERSONAS.length) % CHALLENGER_PERSONAS.length;
    const next = CHALLENGER_PERSONAS[clamped];
    setSelected(next.id);
    tabRefs.current[clamped]?.focus();
  };

  const onTabKeyDown = (event: KeyboardEvent<HTMLButtonElement>, index: number) => {
    switch (event.key) {
      case 'ArrowRight':
      case 'ArrowDown':
        event.preventDefault();
        selectAt(index + 1);
        break;
      case 'ArrowLeft':
      case 'ArrowUp':
        event.preventDefault();
        selectAt(index - 1);
        break;
      case 'Home':
        event.preventDefault();
        selectAt(0);
        break;
      case 'End':
        event.preventDefault();
        selectAt(CHALLENGER_PERSONAS.length - 1);
        break;
      default:
        break;
    }
  };

  const persona = CHALLENGER_PERSONAS.find((p) => p.id === selected) ?? CHALLENGER_PERSONAS[0];
  const base = `start.frontier.challenger.personas.${persona.id}`;
  const list = (suffix: string): string[] => {
    const value = t(`${base}.${suffix}`, { returnObjects: true }) as unknown;
    return Array.isArray(value) ? (value as string[]) : [];
  };

  const paneId = `challenger-pane-${persona.id}`;
  const tabId = (id: ChallengerPersonaId) => `challenger-tab-${id}`;

  return (
    <div className={styles.root}>
      <div className={styles.tablist} role="tablist" aria-label={t('start.frontier.challenger.tablistLabel')}>
        {CHALLENGER_PERSONAS.map((p, index) => {
          const isSelected = p.id === selected;
          return (
            <button
              key={p.id}
              ref={(node) => {
                tabRefs.current[index] = node;
              }}
              id={tabId(p.id)}
              type="button"
              role="tab"
              aria-selected={isSelected}
              aria-controls={isSelected ? paneId : undefined}
              tabIndex={isSelected ? 0 : -1}
              data-testid={`challenger-tab-${p.id}`}
              className={mergeClasses(styles.tab, isSelected && styles.tabSelected)}
              onClick={() => setSelected(p.id)}
              onKeyDown={(event) => onTabKeyDown(event, index)}
            >
              <span className={mergeClasses(styles.tabTag, isSelected && styles.tabTagSelected)}>
                {t(`start.frontier.challenger.personas.${p.id}.tag`)}
              </span>
              <span className={styles.tabSub}>{t(`start.frontier.challenger.personas.${p.id}.sub`)}</span>
            </button>
          );
        })}
      </div>

      <div
        className={mergeClasses(sc.split)}
        role="tabpanel"
        id={paneId}
        aria-labelledby={tabId(persona.id)}
        aria-label={t(`${base}.name`)}
        data-testid={paneId}
      >
        <div className={styles.narrative}>
          <div className={styles.who}>
            <span className={styles.whoName}>{t(`${base}.name`)}</span>
            <span className={styles.whoMeta}>{t(`${base}.org`)}</span>
            <span className={styles.whoMeta}>{t(`${base}.meta`)}</span>
          </div>
          <blockquote className={styles.quote}>{t(`${base}.quote`)}</blockquote>
          {persona.hasGloss && <p className={styles.gloss}>{t(`${base}.gloss`)}</p>}
          <h4 className={styles.heading}>{t('start.frontier.challenger.headings.addressed')}</h4>
          {list('addressed').map((paragraph, index) => (
            <p key={index} className={styles.para}>
              {paragraph}
            </p>
          ))}
        </div>

        <div
          className={mergeClasses(sc.staticCard, styles.pane)}
          style={{ borderLeftColor: SHOWCASE_ACCENT[persona.accent] }}
        >
          <h4 className={styles.heading}>{t('start.frontier.challenger.headings.value')}</h4>
          <ul className={styles.list}>
            {list('value').map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
          <h4 className={styles.heading}>{t('start.frontier.challenger.headings.adapted')}</h4>
          <ul className={styles.list}>
            {list('adapted').map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
          <p className={sc.note}>{t(`${base}.evidence`)}</p>
        </div>
      </div>

      <p className={mergeClasses(sc.note, styles.disclaimer)} data-testid="challenger-disclaimer">
        {t('start.frontier.challenger.disclaimer')}{' '}
        <Link to="/backstage">{t('start.frontier.challenger.disclaimerLinkLabel')}</Link>.
      </p>
    </div>
  );
}
