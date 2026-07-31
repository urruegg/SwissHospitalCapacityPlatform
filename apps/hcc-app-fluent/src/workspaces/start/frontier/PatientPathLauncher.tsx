import {
  Badge,
  Body1,
  Caption1,
  Card,
  Text,
  Title3,
  makeStyles,
  mergeClasses,
  tokens,
} from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useRoleLens } from '../../../context/role-context';
import { useSurfaceStyles } from '../../../theme/design-system/recipes';
import { LAUNCHER_TILES, type LauncherTile } from '../role-launcher';
import { PATIENT_PATH_OPERATIONAL_STOPS } from './start-content';

const PATIENT_PATH_JOURNEY_STOP_COUNT = PATIENT_PATH_OPERATIONAL_STOPS.length + 1;

const useStyles = makeStyles({
  root: {
    display: 'grid',
    gap: tokens.spacingVerticalL,
    minWidth: 0,
  },
  journeyViewport: {
    overflowX: 'auto',
    paddingBottom: tokens.spacingVerticalXS,
  },
  journey: {
    position: 'relative',
    display: 'grid',
    gridTemplateColumns: `repeat(${PATIENT_PATH_JOURNEY_STOP_COUNT}, minmax(128px, 1fr))`,
    gap: tokens.spacingHorizontalS,
    minWidth: '840px',
    listStyleType: 'none',
    margin: 0,
    padding: `${tokens.spacingVerticalXXL} ${tokens.spacingHorizontalS}`,
    ':before': {
      content: '""',
      position: 'absolute',
      left: tokens.spacingHorizontalS,
      right: tokens.spacingHorizontalS,
      top: 'calc(50% - 28px)',
      height: '56px',
      borderRadius: tokens.borderRadiusCircular,
      background: `linear-gradient(90deg, ${tokens.colorBrandBackground2}, ${tokens.colorPaletteTealBackground2}, ${tokens.colorBrandBackground2})`,
      border: `1px solid ${tokens.colorBrandStroke2}`,
    },
    '@media (max-width: 720px)': {
      gridTemplateColumns: '1fr',
      minWidth: 0,
      padding: `${tokens.spacingVerticalS} 0 ${tokens.spacingVerticalS} ${tokens.spacingHorizontalXXL}`,
      ':before': {
        left: tokens.spacingHorizontalS,
        right: 'auto',
        top: 0,
        bottom: 0,
        width: '40px',
        height: 'auto',
      },
    },
  },
  stop: {
    position: 'relative',
    zIndex: 1,
    minWidth: 0,
  },
  stopHigh: {
    transform: 'translateY(-18px)',
    '@media (max-width: 720px)': {
      transform: 'none',
    },
  },
  stopLow: {
    transform: 'translateY(18px)',
    '@media (max-width: 720px)': {
      transform: 'none',
    },
  },
  stopLink: {
    display: 'grid',
    height: '100%',
    color: 'inherit',
    textDecorationLine: 'none',
    borderRadius: tokens.borderRadiusXLarge,
    ':focus-visible': {
      outlineStyle: 'solid',
      outlineWidth: tokens.strokeWidthThick,
      outlineColor: tokens.colorStrokeFocus2,
      outlineOffset: '3px',
    },
  },
  stopCard: {
    height: '100%',
    minHeight: '154px',
    display: 'grid',
    gap: tokens.spacingVerticalXS,
    alignContent: 'start',
    minWidth: 0,
  },
  stopTitle: {
    overflowWrap: 'anywhere',
  },
  agentLine: {
    color: tokens.colorNeutralForeground3,
    overflowWrap: 'anywhere',
  },
  recoveryCard: {
    backgroundColor: tokens.colorPaletteGreenBackground1,
    borderTopColor: tokens.colorPaletteGreenBorder1,
    borderRightColor: tokens.colorPaletteGreenBorder1,
    borderBottomColor: tokens.colorPaletteGreenBorder1,
    borderLeftColor: tokens.colorPaletteGreenBorder1,
  },
  advisoryGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, minmax(0, 1fr))',
    gap: tokens.spacingHorizontalM,
    '@media (max-width: 720px)': {
      gridTemplateColumns: '1fr',
    },
  },
  advisoryCard: {
    gridColumn: '1 / -1',
    display: 'grid',
    gap: tokens.spacingVerticalS,
    padding: tokens.spacingHorizontalL,
    borderRadius: tokens.borderRadiusXLarge,
    backgroundColor: tokens.colorNeutralBackground2,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  advisoryHeader: {
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: tokens.spacingHorizontalS,
    flexWrap: 'wrap',
  },
  advisoryLink: {
    color: tokens.colorBrandForegroundLink,
    fontWeight: tokens.fontWeightSemibold,
    width: 'fit-content',
    ':focus-visible': {
      outlineStyle: 'solid',
      outlineWidth: tokens.strokeWidthThick,
      outlineColor: tokens.colorStrokeFocus2,
      outlineOffset: '3px',
    },
  },
  footer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: tokens.spacingHorizontalM,
    flexWrap: 'wrap',
    paddingTop: tokens.spacingVerticalM,
    borderTop: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  footerCopy: {
    display: 'grid',
    gap: tokens.spacingVerticalXXS,
  },
  chips: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalXS,
  },
});

function tileFor(boardKey: string): LauncherTile {
  const tile = LAUNCHER_TILES.find((candidate) => candidate.boardKey === boardKey);
  if (!tile) {
    throw new Error(`PatientPathLauncher requires the "${boardKey}" launcher tile.`);
  }
  return tile;
}

export function PatientPathLauncher() {
  const styles = useStyles();
  const surface = useSurfaceStyles();
  const { t } = useTranslation();
  const { capabilities } = useRoleLens();
  const operationalStops = PATIENT_PATH_OPERATIONAL_STOPS.map((stop) => ({
    ...stop,
    tile: tileFor(stop.boardKey),
  }));
  const crisisTile = LAUNCHER_TILES.find((tile) => tile.requiresCsaNav);

  return (
    <div className={styles.root}>
      <div className={styles.journeyViewport}>
        <ol className={styles.journey} aria-label={t('start.patientPath.journeyLabel')}>
          {operationalStops.map(({ bodyKey, tile }, index) => (
            <li
              key={tile.boardKey}
              className={mergeClasses(
                styles.stop,
                index % 2 === 0 ? styles.stopHigh : styles.stopLow,
              )}
              data-testid="patient-path-stop"
            >
              <Link
                className={styles.stopLink}
                to={tile.route}
                aria-label={t('start.patientPath.openRoleBoard', {
                  role: t(tile.labelKey),
                })}
              >
                <Card className={mergeClasses(surface.surfaceCard, styles.stopCard)}>
                  <Badge appearance="tint" color="brand">
                    {t('start.patientPath.operationalBadge')}
                  </Badge>
                  <Title3 as="h3" className={styles.stopTitle}>
                    {t(tile.labelKey)}
                  </Title3>
                  <Body1>{t(bodyKey)}</Body1>
                  <Caption1 className={styles.agentLine}>
                    {tile.agent} · {tile.ceiling}
                  </Caption1>
                </Card>
              </Link>
            </li>
          ))}

          <li
            className={mergeClasses(styles.stop, styles.stopLow)}
            data-testid="patient-path-stop"
          >
            <Card
              className={mergeClasses(
                surface.surfaceCard,
                styles.stopCard,
                styles.recoveryCard,
              )}
            >
              <Badge appearance="tint" color="success">
                {t('start.patientPath.destinationBadge')}
              </Badge>
              <Title3 as="h3" className={styles.stopTitle}>
                {t('start.patientPath.recoveryTitle')}
              </Title3>
              <Body1>{t('start.patientPath.recoveryBody')}</Body1>
              <Caption1 className={styles.agentLine}>
                {t('start.patientPath.recoveryCaption')}
              </Caption1>
            </Card>
          </li>
        </ol>
      </div>

      <div className={styles.advisoryGrid}>
        <article
          className={styles.advisoryCard}
          role="note"
          aria-label={t('start.patientPath.dataQuality.ariaLabel')}
        >
          <div className={styles.advisoryHeader}>
            <Title3 as="h3">{t('start.patientPath.dataQuality.title')}</Title3>
            <Badge appearance="tint" color="informative">
              {t('start.patientPath.advisoryBadge')}
            </Badge>
          </div>
          <Body1>{t('start.patientPath.dataQuality.body')}</Body1>
          <Caption1 className={styles.agentLine}>data-quality-agent</Caption1>
        </article>

        {capabilities.nav.csa && crisisTile ? (
          <article
            className={styles.advisoryCard}
            role="note"
            aria-label={t('start.patientPath.crisis.ariaLabel')}
            data-testid="patient-path-csa-advisory"
          >
            <div className={styles.advisoryHeader}>
              <Title3 as="h3">{t(crisisTile.labelKey)}</Title3>
              <Badge appearance="tint" color="warning">
                {t('start.patientPath.advisoryBadge')}
              </Badge>
            </div>
            <Body1>{t('start.patientPath.crisis.body')}</Body1>
            <Link
              className={styles.advisoryLink}
              to={crisisTile.route}
              aria-label={t('start.patientPath.openRoleBoard', {
                role: t(crisisTile.labelKey),
              })}
            >
              {t('start.patientPath.crisis.cta')}
            </Link>
          </article>
        ) : null}
      </div>

      <footer
        className={styles.footer}
        role="contentinfo"
        aria-label={t('start.patientPath.humanDecision.ariaLabel')}
      >
        <div className={styles.footerCopy}>
          <Text weight="semibold">{t('start.patientPath.humanDecision.title')}</Text>
          <Body1>{t('start.patientPath.humanDecision.body')}</Body1>
        </div>
        <div className={styles.chips} aria-label={t('start.patientPath.evidenceLabel')}>
          <Badge appearance="tint" color="informative">
            {t('start.patientPath.evidenceChip')}
          </Badge>
          <Badge appearance="tint" color="brand">
            {t('start.patientPath.goldenThreadChip')}
          </Badge>
        </div>
      </footer>
    </div>
  );
}
