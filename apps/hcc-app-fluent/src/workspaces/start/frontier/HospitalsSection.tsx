import { Body1, Caption1, Text, Title3, makeStyles, tokens } from '@fluentui/react-components';
import {
  BuildingBankRegular,
  BuildingHomeRegular,
  BuildingMultipleRegular,
  BotRegular,
  ChatRegular,
  PersonHeartRegular,
  StethoscopeRegular,
  type FluentIcon,
} from '@fluentui/react-icons';
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
  FRONTIER_HOSPITAL_ROLES,
  type FrontierAgentId,
  type FrontierHospitalId,
  type FrontierHospitalRoleId,
  type FrontierHospitalRoleKind,
} from './start-content';
import { START_NARRATIVE_NARROW_MEDIA_QUERY } from './start-layout';

// Per-site left accent + header glyph (mockup: distinct hue + building icon
// per synthetic hospital archetype).
const HOSPITAL_ACCENT: Record<FrontierHospitalId, ShowcaseAccent> = {
  curanova: 'teal',
  curalp: 'green',
  vialta: 'navy',
};

const HOSPITAL_GLYPH: Record<FrontierHospitalId, FluentIcon> = {
  curanova: BuildingBankRegular,
  curalp: BuildingMultipleRegular,
  vialta: BuildingHomeRegular,
};

// Per-role icon (mockup `.row-mini`): bed side / ops side / agents / product owner.
const ROLE_ICON: Record<FrontierHospitalRoleId, FluentIcon> = {
  bedside: PersonHeartRegular,
  opsside: StethoscopeRegular,
  agents: BotRegular,
  po: ChatRegular,
};

// Per-role accent family (mockup: human=navy, agent=green, po=violet).
const ROLE_ACCENT: Record<FrontierHospitalRoleKind, ShowcaseAccent> = {
  human: 'navy',
  agent: 'green',
  po: 'violet',
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
  cardHead: {
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: tokens.spacingHorizontalM,
    minWidth: 0,
  },
  headText: {
    display: 'grid',
    gap: tokens.spacingVerticalXXS,
    minWidth: 0,
  },
  glyphTile: {
    display: 'grid',
    placeItems: 'center',
    width: '42px',
    height: '42px',
    borderRadius: tokens.borderRadiusLarge,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground2,
    fontSize: '20px',
    flexShrink: 0,
  },
  facts: {
    color: tokens.colorNeutralForeground2,
    fontWeight: tokens.fontWeightSemibold,
    overflowWrap: 'anywhere',
    marginTop: tokens.spacingVerticalXXS,
  },
  roleRows: {
    display: 'grid',
    gap: tokens.spacingVerticalXS,
    marginTop: tokens.spacingVerticalXS,
  },
  roleRow: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalS,
    padding: `${tokens.spacingVerticalXS} ${tokens.spacingHorizontalS}`,
    borderRadius: tokens.borderRadiusMedium,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    borderLeftWidth: '3px',
    backgroundColor: tokens.colorNeutralBackground2,
    minWidth: 0,
  },
  roleIcon: {
    fontSize: '16px',
    flexShrink: 0,
    display: 'inline-grid',
    placeItems: 'center',
  },
  roleLabel: {
    fontSize: tokens.fontSizeBase200,
    color: tokens.colorNeutralForeground1,
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
        {FRONTIER_HOSPITALS.map((hospital) => {
          const Glyph = HOSPITAL_GLYPH[hospital.id];
          const accentHex = SHOWCASE_ACCENT[HOSPITAL_ACCENT[hospital.id]];
          return (
            <article
              key={hospital.id}
              className={styles.hospitalArticle}
              data-testid="frontier-hospital-card"
            >
              <button
                type="button"
                className={sc.accentCard}
                style={{ borderLeftColor: accentHex }}
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
                <span className={styles.cardHead}>
                  <span className={styles.headText}>
                    <span className={sc.cardTitle}>{t(hospital.nameKey)}</span>
                    <span className={sc.cardBody}>{t(hospital.profileKey)}</span>
                  </span>
                  <span
                    className={styles.glyphTile}
                    style={{ color: accentHex }}
                    data-testid="frontier-hospital-glyph"
                  >
                    <Glyph aria-hidden />
                  </span>
                </span>
                <Caption1 className={styles.facts} data-testid="frontier-hospital-facts">
                  {t(hospital.factsKey)}
                </Caption1>
                <span className={styles.roleRows}>
                  {FRONTIER_HOSPITAL_ROLES.map((role) => {
                    const RoleIcon = ROLE_ICON[role.roleId];
                    return (
                      <span
                        key={role.roleId}
                        className={styles.roleRow}
                        style={{ borderLeftColor: SHOWCASE_ACCENT[ROLE_ACCENT[role.kind]] }}
                        data-testid="frontier-hospital-role"
                      >
                        <span
                          className={styles.roleIcon}
                          style={{ color: SHOWCASE_ACCENT[ROLE_ACCENT[role.kind]] }}
                        >
                          <RoleIcon aria-hidden />
                        </span>
                        <span className={styles.roleLabel}>
                          {t(`start.frontier.hospitals.sites.${hospital.id}.roles.${role.roleId}`)}
                        </span>
                      </span>
                    );
                  })}
                </span>
              </button>
            </article>
          );
        })}
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
