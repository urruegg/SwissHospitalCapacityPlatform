import {
  Badge,
  Body1,
  Card,
  Caption1,
  Text,
  Title3,
  makeStyles,
  mergeClasses,
  tokens,
} from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { useSurfaceStyles } from '../../../theme/design-system/recipes';
import { NINETY_DAY_PHASES } from './start-content';
import { START_NARRATIVE_NARROW_MEDIA_QUERY } from './start-layout';

const useStyles = makeStyles({
  root: {
    display: 'grid',
    gap: tokens.spacingVerticalM,
    minWidth: 0,
  },
  roadmap: {
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
  phase: {
    minWidth: 0,
  },
  phaseCard: {
    height: '100%',
    display: 'grid',
    gap: tokens.spacingVerticalS,
    alignContent: 'start',
    backgroundColor: tokens.colorNeutralBackground2,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    boxShadow: 'none',
  },
  phaseHeader: {
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: tokens.spacingHorizontalS,
    flexWrap: 'wrap',
  },
  outcomes: {
    display: 'grid',
    gap: tokens.spacingVerticalXS,
    margin: 0,
    paddingLeft: tokens.spacingHorizontalL,
  },
  rom: {
    color: tokens.colorNeutralForeground3,
  },
});

export function NinetyDaySection() {
  const styles = useStyles();
  const surface = useSurfaceStyles();
  const { t } = useTranslation();

  return (
    <div className={styles.root}>
      <ol className={styles.roadmap} aria-label={t('start.frontier.ninetyDay.roadmapLabel')}>
        {NINETY_DAY_PHASES.map((phase) => (
          <li key={phase.id} className={styles.phase} data-testid="ninety-day-phase">
            <Card className={mergeClasses(surface.surfaceCard, styles.phaseCard)}>
              <div className={styles.phaseHeader}>
                <Title3 as="h3">{t(phase.titleKey)}</Title3>
                <Badge appearance="tint" color="brand">
                  {t(phase.rangeKey)}
                </Badge>
              </div>
              <Body1>{t(phase.bodyKey)}</Body1>
              <ul className={styles.outcomes}>
                {phase.outcomeKeys.map((outcomeKey) => (
                  <li key={outcomeKey}>
                    <Text>{t(outcomeKey)}</Text>
                  </li>
                ))}
              </ul>
              <Caption1 className={styles.rom}>
                {t('start.frontier.ninetyDay.romLabel')}
              </Caption1>
            </Card>
          </li>
        ))}
      </ol>
    </div>
  );
}
