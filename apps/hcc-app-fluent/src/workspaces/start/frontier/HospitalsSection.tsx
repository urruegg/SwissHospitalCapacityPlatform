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
import { FRONTIER_AGENTS, FRONTIER_HOSPITALS } from './start-content';
import { START_NARRATIVE_NARROW_MEDIA_QUERY } from './start-layout';

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
  hospitalCard: {
    height: '100%',
    display: 'grid',
    gap: tokens.spacingVerticalS,
    alignContent: 'start',
    backgroundColor: tokens.colorNeutralBackground2,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    boxShadow: 'none',
  },
  hospitalArticle: {
    minWidth: 0,
  },
  focus: {
    color: tokens.colorBrandForeground1,
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
    backgroundColor: tokens.colorNeutralBackground2,
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
  const surface = useSurfaceStyles();
  const { t } = useTranslation();

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
            <Card className={mergeClasses(surface.surfaceCard, styles.hospitalCard)}>
              <Badge appearance="tint" color="brand">
                {t('start.frontier.hospitals.syntheticBadge')}
              </Badge>
              <Title3 as="h3">{t(hospital.nameKey)}</Title3>
              <Body1>{t(hospital.profileKey)}</Body1>
              <Caption1 className={styles.focus}>{t(hospital.focusKey)}</Caption1>
            </Card>
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
