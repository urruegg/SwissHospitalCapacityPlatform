import { Caption1, Text, Title3, makeStyles, tokens } from '@fluentui/react-components';
import {
  BuildingBankRegular,
  BuildingHomeRegular,
  BuildingMultipleRegular,
  BotRegular,
  ChatRegular,
  PersonHeartRegular,
  StethoscopeRegular,
  DataTrendingRegular,
  DoorArrowRightRegular,
  BedRegular,
  BeakerRegular,
  WrenchRegular,
  PeopleTeamRegular,
  CheckmarkCircleRegular,
  type FluentIcon,
} from '@fluentui/react-icons';
import { useTranslation } from 'react-i18next';
import {
  useShowcaseStyles,
  SHOWCASE_ACCENT,
  type ShowcaseAccent,
} from '../../shared/narrative/showcase-styles';
import { useCopilotRail } from '../../../copilot-rail/rail-context';
import { enrichWithLiveAnswer, startInsight, startReco } from './start-rail';
import {
  FRONTIER_ROSTER,
  FRONTIER_HOSPITALS,
  FRONTIER_HOSPITAL_ROLES,
  type FrontierRosterId,
  type FrontierRosterKind,
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

// Per-roster-chip icon (mockup "The agent team behind every hospital"): one
// Fluent glyph per runtime agent + the PO grounded Q&A rail.
const ROSTER_ICON: Record<FrontierRosterId, FluentIcon> = {
  ooa: DataTrendingRegular,
  dca: DoorArrowRightRegular,
  bmca: BedRegular,
  csa: BeakerRegular,
  orsa: WrenchRegular,
  sba: PeopleTeamRegular,
  'data-quality': CheckmarkCircleRegular,
  po: ChatRegular,
};

// Per-roster-chip accent (mockup: runtime agents = green, PO rail = violet).
const ROSTER_ACCENT: Record<FrontierRosterKind, ShowcaseAccent> = {
  agent: 'green',
  po: 'violet',
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
  roleGroup: {
    display: 'grid',
    gap: tokens.spacingVerticalXS,
    minWidth: 0,
  },
  services: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalXS,
    paddingLeft: tokens.spacingHorizontalXL,
    minWidth: 0,
  },
  serviceChip: {
    display: 'inline-flex',
    alignItems: 'center',
    paddingTop: tokens.spacingVerticalXXS,
    paddingBottom: tokens.spacingVerticalXXS,
    paddingLeft: tokens.spacingHorizontalS,
    paddingRight: tokens.spacingHorizontalS,
    borderRadius: tokens.borderRadiusCircular,
    border: `1px solid ${SHOWCASE_ACCENT.navy}`,
    color: SHOWCASE_ACCENT.navy,
    backgroundColor: tokens.colorNeutralBackground1,
    fontSize: tokens.fontSizeBase100,
    fontWeight: tokens.fontWeightSemibold,
    lineHeight: tokens.lineHeightBase100,
    overflowWrap: 'anywhere',
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
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'center',
    gap: tokens.spacingHorizontalS,
  },
  rosterTag: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalXS,
    paddingTop: tokens.spacingVerticalXXS,
    paddingBottom: tokens.spacingVerticalXXS,
    paddingLeft: tokens.spacingHorizontalS,
    paddingRight: tokens.spacingHorizontalS,
    borderRadius: tokens.borderRadiusCircular,
    border: `1px solid ${SHOWCASE_ACCENT.green}`,
    color: SHOWCASE_ACCENT.green,
    fontSize: tokens.fontSizeBase200,
    fontWeight: tokens.fontWeightSemibold,
    whiteSpace: 'nowrap',
  },
  rosterTagDot: {
    width: '6px',
    height: '6px',
    borderRadius: tokens.borderRadiusCircular,
    backgroundColor: SHOWCASE_ACCENT.green,
    flexShrink: 0,
  },
  roster: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))',
    gap: tokens.spacingHorizontalS,
    listStyleType: 'none',
    margin: 0,
    padding: 0,
  },
  rosterItem: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalS,
    paddingTop: tokens.spacingVerticalS,
    paddingBottom: tokens.spacingVerticalS,
    paddingLeft: tokens.spacingHorizontalM,
    paddingRight: tokens.spacingHorizontalM,
    borderRadius: tokens.borderRadiusLarge,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    borderLeftWidth: '4px',
    backgroundColor: tokens.colorNeutralBackground1,
    boxShadow: tokens.shadow2,
    minWidth: 0,
  },
  rosterIcon: {
    fontSize: '18px',
    flexShrink: 0,
    display: 'inline-grid',
    placeItems: 'center',
  },
  rosterText: {
    display: 'inline',
    minWidth: 0,
    overflowWrap: 'anywhere',
    fontSize: tokens.fontSizeBase200,
    color: tokens.colorNeutralForeground2,
    lineHeight: tokens.lineHeightBase200,
  },
  rosterAbbr: {
    color: tokens.colorNeutralForeground1,
  },
  rosterNote: {
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
                onClick={() => {
                  rail?.openWithReco(
                    startInsight(`hospitals-${hospital.id}`, t(hospital.nameKey)),
                    startReco(
                      t(hospital.nameKey),
                      t(hospital.profileKey),
                      [t(hospital.focusKey)],
                      ['hcp:HospitalNetwork'],
                    ),
                  );
                  if (rail) {
                    void enrichWithLiveAnswer(t(hospital.profileKey), rail).catch((error) => {
                      console.error('PO agent live enrichment failed', error);
                    });
                  }
                }}
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
                    const services =
                      role.roleId === 'opsside'
                        ? t(hospital.servicesKey)
                            .split(/\s*\u00b7\s*/)
                            .filter(Boolean)
                            .slice(0, 4)
                        : [];
                    return (
                      <span key={role.roleId} className={styles.roleGroup}>
                        <span
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
                            {t(
                              `start.frontier.hospitals.sites.${hospital.id}.roles.${role.roleId}`,
                            )}
                          </span>
                        </span>
                        {services.length > 0 ? (
                          <span
                            className={styles.services}
                            data-testid="frontier-hospital-services"
                            aria-label={t('start.frontier.hospitals.servicesLabel')}
                          >
                            {services.map((service) => (
                              <span
                                key={service}
                                className={styles.serviceChip}
                                data-testid="frontier-hospital-service"
                              >
                                {service}
                              </span>
                            ))}
                          </span>
                        ) : null}
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
            {t('start.frontier.hospitals.roster.title')}
          </Title3>
          <span className={styles.rosterTag}>
            <span className={styles.rosterTagDot} aria-hidden />
            {t('start.frontier.hospitals.roster.tag')}
          </span>
        </div>
        <ul className={styles.roster}>
          {FRONTIER_ROSTER.map((entry) => {
            const RosterIcon = ROSTER_ICON[entry.id];
            const accent = SHOWCASE_ACCENT[ROSTER_ACCENT[entry.kind]];
            return (
              <li
                key={entry.id}
                className={styles.rosterItem}
                style={{ borderLeftColor: accent }}
                data-testid="frontier-agent-roster-item"
              >
                <span className={styles.rosterIcon} style={{ color: accent }}>
                  <RosterIcon aria-hidden />
                </span>
                <span className={styles.rosterText}>
                  <Text weight="semibold" className={styles.rosterAbbr}>
                    {t(entry.abbrKey)}
                  </Text>{' '}
                  <span>{`\u2014 ${t(entry.descKey)}`}</span>
                </span>
              </li>
            );
          })}
        </ul>
        <Caption1 className={styles.rosterNote}>
          {t('start.frontier.hospitals.roster.note')}
        </Caption1>
      </section>
    </div>
  );
}
