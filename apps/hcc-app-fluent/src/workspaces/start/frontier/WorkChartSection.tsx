import { Badge, makeStyles, tokens } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { useShowcaseStyles, SHOWCASE_ACCENT, type ShowcaseAccent } from '../../shared/narrative/showcase-styles';
import { useCopilotRail } from '../../../copilot-rail/rail-context';
import { startInsight, startReco } from './start-rail';
import { WORK_MODES, type WorkModeId } from './start-content';
import { START_NARRATIVE_NARROW_MEDIA_QUERY } from './start-layout';

// Per-mode left-accent (Frontier-Firm operating model: humans navy, agents green, on-demand violet).
const MODE_ACCENT: Record<WorkModeId, ShowcaseAccent> = {
  humans: 'navy',
  agents: 'green',
  'on-demand': 'violet',
};

const useStyles = makeStyles({
  root: {
    display: 'grid',
    gap: tokens.spacingVerticalL,
    minWidth: 0,
  },
  flow: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, minmax(0, 1fr))',
    gap: tokens.spacingHorizontalM,
    listStyleType: 'none',
    margin: 0,
    padding: 0,
    [START_NARRATIVE_NARROW_MEDIA_QUERY]: {
      gridTemplateColumns: '1fr',
    },
  },
  flowItem: {
    minWidth: 0,
    display: 'flex',
  },
  badge: { alignSelf: 'flex-start' },
  principle: {
    display: 'grid',
    gap: tokens.spacingVerticalS,
    padding: tokens.spacingHorizontalL,
    borderRadius: tokens.borderRadiusXLarge,
    border: `1px solid ${tokens.colorBrandStroke2}`,
    backgroundColor: tokens.colorBrandBackground2,
  },
  principleHeader: {
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: tokens.spacingHorizontalM,
    flexWrap: 'wrap',
  },
  principleTitle: {
    margin: 0,
    fontSize: tokens.fontSizeBase400,
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorNeutralForeground1,
  },
  principleBody: {
    margin: 0,
    fontSize: tokens.fontSizeBase300,
    color: tokens.colorNeutralForeground2,
    lineHeight: 1.5,
  },
  mapping: {
    fontSize: tokens.fontSizeBase200,
    color: tokens.colorNeutralForeground2,
  },
});

export function WorkChartSection() {
  const styles = useStyles();
  const sc = useShowcaseStyles();
  const { t } = useTranslation();
  let rail: ReturnType<typeof useCopilotRail> | null = null;
  try {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    rail = useCopilotRail();
  } catch {
    rail = null;
  }

  return (
    <div className={styles.root}>
      <ol className={styles.flow} aria-label={t('start.frontier.workChart.flowLabel')}>
        {WORK_MODES.map((mode) => {
          const accent = SHOWCASE_ACCENT[MODE_ACCENT[mode.id]];
          return (
            <li key={mode.id} className={styles.flowItem} data-testid="work-chart-mode">
              <button
                type="button"
                className={sc.accentCard}
                style={{ borderLeftColor: accent }}
                onClick={() =>
                  rail?.openWithReco(
                    startInsight(`work-chart-${mode.id}`, t(mode.titleKey)),
                    startReco(
                      t(mode.titleKey),
                      t(mode.bodyKey),
                      [t('start.frontier.workChart.principle.title')],
                      ['hcp:OperatingModel'],
                    ),
                  )
                }
              >
                <Badge className={styles.badge} appearance="tint" color="brand">
                  {t('start.frontier.workChart.modeBadge')}
                </Badge>
                <span className={sc.cardTitle} data-testid="work-chart-mode-title">
                  {t(mode.titleKey)}
                </span>
                <span className={sc.cardBody}>{t(mode.bodyKey)}</span>
              </button>
            </li>
          );
        })}
      </ol>

      <aside
        className={styles.principle}
        role="note"
        aria-label={t('start.frontier.workChart.principle.title')}
      >
        <div className={styles.principleHeader}>
          <h3 className={styles.principleTitle}>{t('start.frontier.workChart.principle.title')}</h3>
          <Badge appearance="filled" color="brand">
            {t('start.frontier.workChart.principle.badge')}
          </Badge>
        </div>
        <p className={styles.principleBody}>{t('start.frontier.workChart.principle.body')}</p>
        <span className={styles.mapping}>{t('start.frontier.workChart.principle.curaviasMap')}</span>
      </aside>
    </div>
  );
}
