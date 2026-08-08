import {
  Badge,
  Caption1,
  Text,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import {
  useShowcaseStyles,
  SHOWCASE_ACCENT,
  type ShowcaseAccent,
} from '../../shared/narrative/showcase-styles';
import { useCopilotRail } from '../../../copilot-rail/rail-context';
import { startInsight, startReco } from './start-rail';
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
  },
  outcomeItem: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: tokens.spacingHorizontalXS,
  },
  rom: {
    color: tokens.colorNeutralForeground3,
  },
  disclaimer: {
    color: tokens.colorNeutralForeground3,
  },
});

export function NinetyDaySection() {
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
      <ol className={styles.roadmap} aria-label={t('start.frontier.ninetyDay.roadmapLabel')}>
        {NINETY_DAY_PHASES.map((phase) => (
          <li key={phase.id} className={styles.phase} data-testid="ninety-day-phase">
            <button
              type="button"
              className={sc.accentCard}
              style={{ borderLeftColor: SHOWCASE_ACCENT[PHASE_ACCENT[phase.id]] }}
              onClick={() =>
                rail?.openWithReco(
                  startInsight(`ninety-day-${phase.id}`, t(phase.titleKey)),
                  startReco(
                    t(phase.titleKey),
                    t(phase.bodyKey),
                    phase.outcomeKeys.map((outcomeKey) => t(outcomeKey)),
                    ['hcp:NinetyDayRoadmap'],
                  ),
                )
              }
            >
              <div className={styles.phaseBand}>
                <span className={sc.cardTitle}>{t(phase.titleKey)}</span>
                <Badge appearance="tint" color="brand">
                  {t(phase.rangeKey)}
                </Badge>
              </div>
              <span className={sc.cardBody}>{t(phase.bodyKey)}</span>
              <div className={styles.outcomes}>
                {phase.outcomeKeys.map((outcomeKey) => (
                  <span key={outcomeKey} className={styles.outcomeItem}>
                    <Text aria-hidden="true">•</Text>
                    <Text>{t(outcomeKey)}</Text>
                  </span>
                ))}
              </div>
              <Caption1 className={styles.rom}>
                {t('start.frontier.ninetyDay.romLabel')}
              </Caption1>
            </button>
          </li>
        ))}
      </ol>
      <Caption1 className={styles.disclaimer} data-testid="ninety-day-disclaimer">
        {t('start.frontier.ninetyDay.disclaimer')}
      </Caption1>
    </div>
  );
}
