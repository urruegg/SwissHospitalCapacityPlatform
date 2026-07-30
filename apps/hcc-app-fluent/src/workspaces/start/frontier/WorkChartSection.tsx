import {
  Badge,
  Body1,
  Card,
  Caption1,
  Title3,
  makeStyles,
  mergeClasses,
  tokens,
} from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { useSurfaceStyles } from '../../../theme/design-system/recipes';
import { WORK_MODES } from './start-content';
import { START_NARRATIVE_NARROW_MEDIA_QUERY } from './start-layout';

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
  },
  modeCard: {
    height: '100%',
    display: 'grid',
    gap: tokens.spacingVerticalS,
    alignContent: 'start',
    backgroundColor: tokens.colorNeutralBackground2,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    boxShadow: 'none',
  },
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
  mapping: {
    color: tokens.colorNeutralForeground2,
  },
});

export function WorkChartSection() {
  const styles = useStyles();
  const surface = useSurfaceStyles();
  const { t } = useTranslation();

  return (
    <div className={styles.root}>
      <ol className={styles.flow} aria-label={t('start.frontier.workChart.flowLabel')}>
        {WORK_MODES.map((mode) => (
          <li key={mode.id} className={styles.flowItem} data-testid="work-chart-mode">
            <Card className={mergeClasses(surface.surfaceCard, styles.modeCard)}>
              <Badge appearance="tint" color="brand">
                {t('start.frontier.workChart.modeBadge')}
              </Badge>
              <Title3 as="h3">{t(mode.titleKey)}</Title3>
              <Body1>{t(mode.bodyKey)}</Body1>
            </Card>
          </li>
        ))}
      </ol>

      <aside
        className={styles.principle}
        role="note"
        aria-label={t('start.frontier.workChart.principle.title')}
      >
        <div className={styles.principleHeader}>
          <Title3 as="h3">{t('start.frontier.workChart.principle.title')}</Title3>
          <Badge appearance="filled" color="brand">
            {t('start.frontier.workChart.principle.badge')}
          </Badge>
        </div>
        <Body1>{t('start.frontier.workChart.principle.body')}</Body1>
        <Caption1 className={styles.mapping}>
          {t('start.frontier.workChart.principle.curaviasMap')}
        </Caption1>
      </aside>
    </div>
  );
}
