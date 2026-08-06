import { Badge, Body1, Caption1, Text, Title3, makeStyles, tokens } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import {
  useShowcaseStyles,
  SHOWCASE_ACCENT,
  type ShowcaseAccent,
} from '../../shared/narrative/showcase-styles';
import { useCopilotRail } from '../../../copilot-rail/rail-context';
import { startInsight, startReco } from './start-rail';
import {
  FRONTIER_AGENTS,
  FRONTIER_HOSPITALS,
  type FrontierAgentId,
  type FrontierHospitalId,
} from './start-content';
import { START_NARRATIVE_NARROW_MEDIA_QUERY } from './start-layout';

// Per-site left accent (mockup: distinct hue per synthetic hospital).
const HOSPITAL_ACCENT: Record<FrontierHospitalId, ShowcaseAccent> = {
  curanova: 'teal',
  curalp: 'green',
  vialta: 'navy',
};

// Per-agent chip accent (mockup: colored agent roster chips).
const AGENT_ACCENT: Record<FrontierAgentId, ShowcaseAccent> = {
  'ooa-agent': 'green',
  'bmca-agent': 'navy',
  'dca-agent': 'teal',
  'orsa-agent': 'violet',
  'sba-agent': 'amber',
  'csa-agent': 'red',
  'data-quality-agent': 'slate',
};

const useStyles = makeStyles({
  root: {
    display: 'grid',
    gap: tokens.spacingVerticalXL,
    minWidth: 0,
  },
  hospitals: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, minmax(0, 1fr))',
    gap: tokens.spacingHorizontalM,
    [START_NARRATIVE_NARROW_MEDIA_QUERY]: {
      gridTemplateColumns: '1fr',
    },
  },
  hospitalArticle: {
    minWidth: 0,
    display: 'flex',
  },
  focus: {
    color: SHOWCASE_ACCENT.green,
    fontWeight: tokens.fontWeightSemibold,
  },
  facts: {
    color: tokens.colorNeutralForeground2,
    fontWeight: tokens.fontWeightSemibold,
    overflowWrap: 'anywhere',
  },
  rosterSection: {
    display: 'grid',
    gap: tokens.spacingVerticalM,
  },
  rosterHeader: {
    display: 'grid',
    gap: tokens.spacingVerticalXXS,
  },
  roster: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
    gap: tokens.spacingHorizontalS,
    listStyleType: 'none',
    margin: 0,
    padding: 0,
  },
  rosterItem: {
    display: 'grid',
    gap: tokens.spacingVerticalXXS,
    padding: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusLarge,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    borderLeftWidth: '4px',
    backgroundColor: tokens.colorNeutralBackground1,
    boxShadow: tokens.shadow2,
    minWidth: 0,
  },
  agentName: {
    overflowWrap: 'anywhere',
  },
  agentRole: {
    color: tokens.colorNeutralForeground3,
  },
});

export function HospitalsSection() {
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
      <section
        className={styles.hospitals}
        aria-label={t('start.frontier.hospitals.sitesLabel')}
      >
        {FRONTIER_HOSPITALS.map((hospital) => (
          <article
            key={hospital.id}
            className={styles.hospitalArticle}
            data-testid="frontier-hospital-card"
          >
            <button
              type="button"
              className={sc.accentCard}
              style={{ borderLeftColor: SHOWCASE_ACCENT[HOSPITAL_ACCENT[hospital.id]] }}
              onClick={() =>
                rail?.openWithReco(
                  startInsight(`hospitals-${hospital.id}`, t(hospital.nameKey)),
                  startReco(
                    t(hospital.nameKey),
                    t(hospital.profileKey),
                    [t(hospital.focusKey)],
                    ['hcp:HospitalNetwork'],
                  ),
                )
              }
            >
              <Badge appearance="tint" color="brand">
                {t('start.frontier.hospitals.syntheticBadge')}
              </Badge>
              <span className={sc.cardTitle}>{t(hospital.nameKey)}</span>
              <span className={sc.cardBody}>{t(hospital.profileKey)}</span>
              <Caption1 className={styles.facts} data-testid="frontier-hospital-facts">
                {t(hospital.factsKey)}
              </Caption1>
              <Caption1 className={styles.focus}>{t(hospital.focusKey)}</Caption1>
            </button>
          </article>
        ))}
      </section>

      <section
        className={styles.rosterSection}
        aria-labelledby="frontier-agent-roster-title"
      >
        <div className={styles.rosterHeader}>
          <Title3 as="h3" id="frontier-agent-roster-title">
            {t('start.frontier.hospitals.rosterTitle')}
          </Title3>
          <Body1>{t('start.frontier.hospitals.rosterBody')}</Body1>
        </div>
        <ul className={styles.roster}>
          {FRONTIER_AGENTS.map((agent) => (
            <li
              key={agent.id}
              className={styles.rosterItem}
              style={{ borderLeftColor: SHOWCASE_ACCENT[AGENT_ACCENT[agent.id]] }}
              data-testid="frontier-agent-roster-item"
            >
              <Text weight="semibold" className={styles.agentName}>
                {t(agent.nameKey)}
              </Text>
              <Caption1 className={styles.agentRole}>{t(agent.roleKey)}</Caption1>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
