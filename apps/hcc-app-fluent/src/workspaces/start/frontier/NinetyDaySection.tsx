import {
  Badge,
  Body1,
  Caption1,
  Text,
  Title3,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import {
  useShowcaseStyles,
  SHOWCASE_ACCENT,
  type ShowcaseAccent,
} from '../../shared/narrative/showcase-styles';
import { NINETY_DAY_PHASES, type NinetyDayPhaseId } from './start-content';
import { START_NARRATIVE_NARROW_MEDIA_QUERY } from './start-layout';

// Per-phase left accent (blueprint progression: frame navy, build teal, operate green).
const PHASE_ACCENT: Record<NinetyDayPhaseId, ShowcaseAccent> = {
  'frame-ground': 'navy',
  'build-prove': 'teal',
  'operate-scale': 'green',
};

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
    display: 'flex',
  },
  phaseBand: {
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: tokens.spacingHorizontalS,
    flexWrap: 'wrap',
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusMedium,
    // Mockup phase-top: green -> teal wash.
    backgroundImage:
      'linear-gradient(120deg, rgba(23, 184, 144, 0.12), rgba(31, 169, 214, 0.06))',
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
  const sc = useShowcaseStyles();
  const { t } = useTranslation();

  return (
    <div className={styles.root}>
      <ol className={styles.roadmap} aria-label={t('start.frontier.ninetyDay.roadmapLabel')}>
        {NINETY_DAY_PHASES.map((phase) => (
          <li key={phase.id} className={styles.phase} data-testid="ninety-day-phase">
            <div
              className={sc.staticCard}
              style={{ borderLeftColor: SHOWCASE_ACCENT[PHASE_ACCENT[phase.id]] }}
            >
              <div className={styles.phaseBand}>
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
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
