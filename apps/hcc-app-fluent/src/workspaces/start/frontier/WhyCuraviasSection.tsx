import { makeStyles, mergeClasses, tokens } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { SHOWCASE_ACCENT, useShowcaseStyles } from '../../shared/narrative/showcase-styles';
import { VISION_MARK_STEPS, VISION_PILLS, VISION_WORD_ROWS } from './start-content';

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalL, minWidth: 0 },
  // Etymology term cell (cura / via / curavias) — a proper noun rendered verbatim.
  term: { color: tokens.colorNeutralForeground1, fontWeight: tokens.fontWeightSemibold, fontStyle: 'italic' },

  // Logo journey (Start -> Care -> Success).
  markSteps: {
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'stretch',
    gap: tokens.spacingHorizontalM,
    listStyleType: 'none',
    margin: `${tokens.spacingVerticalXS} 0`,
    padding: 0,
  },
  markStep: {
    position: 'relative',
    flex: '1 1 0',
    minWidth: '80px',
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
    padding: tokens.spacingHorizontalS,
    borderRadius: tokens.borderRadiusMedium,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground2,
    textAlign: 'center',
    ':not(:first-child)::before': {
      content: '"→"',
      position: 'absolute',
      left: '-14px',
      top: '50%',
      transform: 'translateY(-50%)',
      color: tokens.colorNeutralForeground3,
    },
  },
  markStepOn: {
    border: `1px solid ${SHOWCASE_ACCENT.green}`,
    backgroundColor: tokens.colorNeutralBackground1,
    boxShadow: tokens.shadow2,
  },
  markStepLabel: { fontSize: tokens.fontSizeBase300, fontWeight: tokens.fontWeightSemibold, color: tokens.colorNeutralForeground1 },
  markStepLabelOn: { color: SHOWCASE_ACCENT.green },
  markStepCaption: { fontSize: tokens.fontSizeBase200, color: tokens.colorNeutralForeground3 },

  vmHeading: {
    margin: 0,
    fontSize: tokens.fontSizeBase500,
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorNeutralForeground1,
  },
  statementTag: {
    fontSize: tokens.fontSizeBase200,
    fontWeight: tokens.fontWeightSemibold,
    textTransform: 'uppercase',
    letterSpacing: '0.06em',
  },
  statementPrimary: {
    margin: 0,
    fontSize: tokens.fontSizeBase400,
    fontWeight: tokens.fontWeightSemibold,
    lineHeight: 1.4,
    color: tokens.colorNeutralForeground1,
  },
  statementEcho: {
    margin: 0,
    fontSize: tokens.fontSizeBase200,
    fontStyle: 'italic',
    lineHeight: 1.45,
    color: tokens.colorNeutralForeground3,
  },

  timeCurrency: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
    paddingLeft: tokens.spacingHorizontalM,
    borderLeft: `3px solid ${SHOWCASE_ACCENT.green}`,
  },
  timeCurrencyPrimary: { margin: 0, fontSize: tokens.fontSizeBase300, lineHeight: 1.5, color: tokens.colorNeutralForeground2 },
  timeCurrencyEcho: { margin: 0, fontSize: tokens.fontSizeBase200, fontStyle: 'italic', color: tokens.colorNeutralForeground3 },

  pillRow: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalS,
    listStyleType: 'none',
    margin: 0,
    padding: 0,
  },
  pill: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '6px',
    padding: `${tokens.spacingVerticalXS} ${tokens.spacingHorizontalM}`,
    borderRadius: tokens.borderRadiusCircular,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
    fontSize: tokens.fontSizeBase200,
  },
  pillLabel: { color: tokens.colorNeutralForeground1, fontWeight: tokens.fontWeightSemibold },
  pillSep: { color: tokens.colorNeutralForeground4 },
  pillEcho: { color: tokens.colorNeutralForeground3 },
});

/**
 * Sprint 40 START polish — the mockup's "Why Curavias exists" (vision & mission)
 * section. It renders four beats beneath StartView's SectionHeader (which supplies the
 * eyebrow / title / lead): the cura + via etymology table and the three-step logo-journey
 * mark (word/mark split), the "Our vision & mission" statements, the time-currency line,
 * and the three advisory / human / Swiss guarantee pills.
 *
 * Localisation follows the challenger's Approach B: the chrome (headings, column labels,
 * captions) localises en/de, while the vision statement, mission statement, time-currency
 * line and pills are deliberate EN|DE bilingual brand copy — carried as identical
 * `{primary,echo}` / `{label,echo}` keys that render the same in every locale (de omits
 * those leaf keys so they fall back to the shared English brand copy).
 */
export function WhyCuraviasSection() {
  const styles = useStyles();
  const sc = useShowcaseStyles();
  const { t } = useTranslation();
  const base = 'start.frontier.vision';

  return (
    <div className={styles.root}>
      <div className={sc.split}>
        <div className={sc.staticCard} style={{ borderLeftColor: SHOWCASE_ACCENT.navy }}>
          <h3 className={sc.cardTitle}>{t(`${base}.word.heading`)}</h3>
          <table className={sc.table} data-testid="vision-word-table" aria-label={t(`${base}.word.label`)}>
            <thead>
              <tr>
                <th scope="col" className={sc.th}>{t(`${base}.word.columns.latin`)}</th>
                <th scope="col" className={sc.th}>{t(`${base}.word.columns.meaning`)}</th>
                <th scope="col" className={sc.th}>{t(`${base}.word.columns.product`)}</th>
              </tr>
            </thead>
            <tbody>
              {VISION_WORD_ROWS.map((row) => (
                <tr key={row.id} data-testid="vision-word-row">
                  <th scope="row" className={mergeClasses(sc.td, styles.term)}>{row.id}</th>
                  <td className={sc.td}>{t(row.meaningKey)}</td>
                  <td className={sc.td}>{t(row.productKey)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className={sc.staticCard} style={{ borderLeftColor: SHOWCASE_ACCENT.green }}>
          <h3 className={sc.cardTitle}>{t(`${base}.mark.heading`)}</h3>
          <p className={sc.cardBody}>{t(`${base}.mark.intro`)}</p>
          <ol className={styles.markSteps} data-testid="vision-mark" aria-label={t(`${base}.mark.label`)}>
            {VISION_MARK_STEPS.map((step) => (
              <li
                key={step.id}
                data-testid={`vision-mark-step-${step.id}`}
                aria-current={step.highlighted ? 'step' : undefined}
                className={mergeClasses(styles.markStep, step.highlighted && styles.markStepOn)}
              >
                <span className={mergeClasses(styles.markStepLabel, step.highlighted && styles.markStepLabelOn)}>
                  {t(step.labelKey)}
                </span>
                <span className={styles.markStepCaption}>{t(step.captionKey)}</span>
              </li>
            ))}
          </ol>
          <p className={sc.note}>{t(`${base}.mark.note`)}</p>
        </div>
      </div>

      <h3 className={styles.vmHeading}>{t(`${base}.vmHeading`)}</h3>

      <div className={sc.split}>
        <div className={sc.staticCard} style={{ borderLeftColor: SHOWCASE_ACCENT.navy }} data-testid="vision-statement">
          <span className={styles.statementTag} style={{ color: SHOWCASE_ACCENT.navy }}>{t(`${base}.vision.tag`)}</span>
          <p className={styles.statementPrimary}>{t(`${base}.vision.primary`)}</p>
          <p className={styles.statementEcho}>{t(`${base}.vision.echo`)}</p>
        </div>
        <div className={sc.staticCard} style={{ borderLeftColor: SHOWCASE_ACCENT.green }} data-testid="mission-statement">
          <span className={styles.statementTag} style={{ color: SHOWCASE_ACCENT.green }}>{t(`${base}.mission.tag`)}</span>
          <p className={styles.statementPrimary}>{t(`${base}.mission.primary`)}</p>
          <p className={styles.statementEcho}>{t(`${base}.mission.echo`)}</p>
        </div>
      </div>

      <div className={styles.timeCurrency} data-testid="vision-time-currency">
        <p className={styles.timeCurrencyPrimary}>{t(`${base}.timeCurrency`)}</p>
        <p className={styles.timeCurrencyEcho}>{t(`${base}.timeCurrencyEcho`)}</p>
      </div>

      <ul className={styles.pillRow} aria-label={t(`${base}.pillRowLabel`)}>
        {VISION_PILLS.map((pill) => (
          <li key={pill.id} className={styles.pill} data-testid="vision-pill">
            {pill.flag && <span aria-hidden="true">🇨🇭</span>}
            <span className={styles.pillLabel}>{t(pill.labelKey)}</span>
            <span className={styles.pillSep} aria-hidden="true">·</span>
            <span className={styles.pillEcho}>{t(pill.echoKey)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
