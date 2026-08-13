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
import {
  BedRegular,
  CheckmarkCircleRegular,
  ChevronRightRegular,
  HeartPulseRegular,
  HomeRegular,
  PeopleRegular,
  SyringeRegular,
  type FluentIcon,
} from '@fluentui/react-icons';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useCopilotRail } from '../../../copilot-rail/rail-context';
import { useRoleLens } from '../../../context/role-context';
import { useShowcaseStyles, SHOWCASE_ACCENT, type ShowcaseAccent } from '../../shared/narrative/showcase-styles';
import { LAUNCHER_TILES, type LauncherTile } from '../role-launcher';
import { enrichWithLiveAnswer, startInsight, startReco } from './start-rail';
import { DC_INSIGHT_BEATS, PATIENT_PATH_OPERATIONAL_STOPS, type DcInsightBeatId } from './start-content';

const BEAT_ACCENT: Record<DcInsightBeatId, ShowcaseAccent> = {
  signal: 'teal',
  understanding: 'teal',
  recommendation: 'green',
  action: 'amber',
  coordination: 'violet',
};

// Sprint 44 UI polish — each patient-path stop renders a Fluent UI icon in a
// coloured circular node (replaces the former hand-authored SVG glyph paths) to
// align with the Fluent Card/Badge/Icon language used by the other charts.
const NODE_PRESENTATION: Record<string, { color: string; Icon: FluentIcon }> = {
  occupancy: { color: '#33546B', Icon: HeartPulseRegular },
  'bed-manager': { color: '#3C6E8E', Icon: BedRegular },
  'or-steering': { color: '#24708F', Icon: SyringeRegular },
  staffing: { color: '#1E7D68', Icon: PeopleRegular },
  discharge: { color: '#1F7A50', Icon: HomeRegular },
};

const RECOVERY_NODE_COLOR = '#218A5A';

const useStyles = makeStyles({
  root: {
    display: 'grid',
    gap: tokens.spacingVerticalL,
    minWidth: 0,
  },
  banners: {
    display: 'grid',
    gap: tokens.spacingVerticalS,
  },
  bannerCard: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalM,
    padding: `${tokens.spacingVerticalS} ${tokens.spacingHorizontalL}`,
    borderRadius: tokens.borderRadiusXLarge,
    backgroundColor: tokens.colorNeutralBackground2,
    borderLeft: '4px solid transparent',
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    flexWrap: 'wrap',
  },
  bannerBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: '44px',
    height: '26px',
    paddingLeft: tokens.spacingHorizontalXS,
    paddingRight: tokens.spacingHorizontalXS,
    borderRadius: tokens.borderRadiusMedium,
    fontSize: tokens.fontSizeBase200,
    fontWeight: tokens.fontWeightBold,
    letterSpacing: '0.04em',
    color: tokens.colorNeutralForegroundOnBrand,
  },
  bannerCopy: {
    display: 'flex',
    alignItems: 'baseline',
    gap: tokens.spacingHorizontalXS,
    flexWrap: 'wrap',
    flexGrow: 1,
    minWidth: 0,
  },
  bannerDot: {
    color: tokens.colorNeutralForeground3,
  },
  bannerEvidence: {
    display: 'inline-flex',
    alignItems: 'center',
    padding: `2px ${tokens.spacingHorizontalS}`,
    borderRadius: tokens.borderRadiusCircular,
    fontSize: tokens.fontSizeBase200,
    fontWeight: tokens.fontWeightSemibold,
    backgroundColor: tokens.colorNeutralBackground3,
    color: tokens.colorNeutralForeground2,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  bannerLink: {
    color: tokens.colorBrandForegroundLink,
    fontWeight: tokens.fontWeightSemibold,
    fontSize: tokens.fontSizeBase200,
    textDecorationLine: 'none',
    ':hover': { textDecorationLine: 'underline' },
    ':focus-visible': {
      outlineStyle: 'solid',
      outlineWidth: tokens.strokeWidthThick,
      outlineColor: tokens.colorStrokeFocus2,
      outlineOffset: '2px',
    },
  },
  bannerTriggerButton: {
    display: 'inline',
    background: 'none',
    border: 'none',
    padding: 0,
    margin: 0,
    font: 'inherit',
    fontWeight: tokens.fontWeightSemibold,
    color: 'inherit',
    textAlign: 'left',
    cursor: 'pointer',
    ':hover': { color: tokens.colorBrandForegroundLink },
    ':focus-visible': {
      outlineStyle: 'solid',
      outlineWidth: tokens.strokeWidthThick,
      outlineColor: tokens.colorStrokeFocus2,
      outlineOffset: '2px',
    },
  },
  journeyViewport: {
    overflowX: 'auto',
    paddingBottom: tokens.spacingVerticalXS,
  },
  journey: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'stretch',
    gap: tokens.spacingHorizontalXS,
    listStyleType: 'none',
    margin: 0,
    padding: `${tokens.spacingVerticalM} ${tokens.spacingHorizontalXS}`,
    minWidth: 0,
    '@media (max-width: 720px)': {
      flexDirection: 'column',
      alignItems: 'stretch',
      minWidth: 0,
    },
  },
  stop: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    gap: tokens.spacingHorizontalXS,
    flexGrow: 1,
    flexBasis: 0,
    minWidth: '116px',
    '@media (max-width: 720px)': {
      flexDirection: 'column',
      flexBasis: 'auto',
    },
  },
  stopCard: {
    flexGrow: 1,
    flexBasis: 0,
    minWidth: 0,
    alignItems: 'center',
    textAlign: 'center',
    rowGap: tokens.spacingVerticalS,
    padding: tokens.spacingVerticalM,
    '@media (max-width: 720px)': {
      width: '100%',
    },
  },
  connector: {
    flexShrink: 0,
    fontSize: '22px',
    color: tokens.colorNeutralForeground4,
    '@media (max-width: 720px)': {
      transform: 'rotate(90deg)',
    },
  },
  stopLink: {
    display: 'grid',
    justifyItems: 'center',
    gap: tokens.spacingVerticalS,
    color: 'inherit',
    textDecorationLine: 'none',
    borderRadius: tokens.borderRadiusMedium,
    ':focus-visible': {
      outlineStyle: 'solid',
      outlineWidth: tokens.strokeWidthThick,
      outlineColor: tokens.colorStrokeFocus2,
      outlineOffset: '3px',
    },
  },
  node: {
    width: '56px',
    height: '56px',
    borderRadius: tokens.borderRadiusCircular,
    display: 'grid',
    placeItems: 'center',
    boxShadow: tokens.shadow8,
    border: '3px solid #ffffff',
  },
  agentBadge: {
    // Applied to a Fluent Badge whose background is a fixed deep node hex, so
    // white text is the theme-independent AA-safe choice (the Curavias brand
    // ramp resolves colorNeutralForegroundOnBrand to a dark tone here).
    color: '#ffffff',
    letterSpacing: '0.04em',
  },
  stopTitle: {
    fontSize: tokens.fontSizeBase300,
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorNeutralForeground1,
    overflowWrap: 'anywhere',
  },
  evidenceChip: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: `${tokens.spacingVerticalXXS} ${tokens.spacingHorizontalS}`,
    borderRadius: tokens.borderRadiusMedium,
    fontSize: tokens.fontSizeBase200,
    fontWeight: tokens.fontWeightSemibold,
    backgroundColor: tokens.colorNeutralBackground3,
    color: tokens.colorNeutralForeground2,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    overflowWrap: 'anywhere',
    lineHeight: tokens.lineHeightBase200,
  },
  stopBody: {
    fontSize: tokens.fontSizeBase200,
    color: tokens.colorNeutralForeground3,
    maxWidth: '160px',
  },
  agentLine: {
    color: tokens.colorNeutralForeground3,
    overflowWrap: 'anywhere',
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
  advisoryTitleButton: {
    display: 'inline',
    background: 'none',
    border: 'none',
    padding: 0,
    margin: 0,
    font: 'inherit',
    color: 'inherit',
    textAlign: 'left',
    cursor: 'pointer',
    ':hover': {
      color: tokens.colorBrandForegroundLink,
    },
    ':focus-visible': {
      outlineStyle: 'solid',
      outlineWidth: tokens.strokeWidthThick,
      outlineColor: tokens.colorStrokeFocus2,
      outlineOffset: '2px',
    },
  },
  beatList: {
    display: 'grid',
    gap: tokens.spacingVerticalS,
    marginTop: tokens.spacingVerticalXS,
  },
  beatRow: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: tokens.spacingHorizontalS,
  },
  beatCopy: {
    fontSize: tokens.fontSizeBase200,
    color: tokens.colorNeutralForeground2,
    lineHeight: tokens.lineHeightBase200,
  },
  kpiRow: {
    display: 'flex',
    alignItems: 'baseline',
    gap: tokens.spacingHorizontalS,
    marginTop: tokens.spacingVerticalXS,
  },
  kpiValue: {
    fontSize: '34px',
    fontWeight: tokens.fontWeightBold,
    color: tokens.colorNeutralForeground3,
  },
  kpiTarget: {
    // Deep, theme-adaptive green (AA on both light card + dark surface).
    // SHOWCASE_ACCENT.green (#17b890) only reaches 2.53:1 on white.
    color: tokens.colorPaletteGreenForeground1,
  },
  pillRow: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalXS,
    marginTop: tokens.spacingVerticalXS,
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
  const sc = useShowcaseStyles();
  const { t } = useTranslation();
  const { capabilities } = useRoleLens();
  let rail: ReturnType<typeof useCopilotRail> | null = null;
  try {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    rail = useCopilotRail();
  } catch {
    rail = null;
  }
  const operationalStops = PATIENT_PATH_OPERATIONAL_STOPS.map((stop) => ({
    ...stop,
    tile: tileFor(stop.boardKey),
  }));
  const crisisTile = LAUNCHER_TILES.find((tile) => tile.requiresCsaNav);
  const showCrisisLink = Boolean(capabilities.nav.csa && crisisTile);

  return (
    <div className={styles.root}>
      <div
        className={styles.banners}
        data-testid="patient-path-banners"
        aria-label={t('start.patientPath.bannersAriaLabel')}
      >
        <article
          className={styles.bannerCard}
          style={{ borderLeftColor: SHOWCASE_ACCENT.red }}
          role="note"
          aria-label={t('start.patientPath.crisis.ariaLabel')}
          data-testid="patient-path-csa-advisory"
        >
          <span className={styles.bannerBadge} style={{ backgroundColor: SHOWCASE_ACCENT.red }}>
            {t('start.patientPath.crisis.badge')}
          </span>
          <span className={styles.bannerCopy}>
            {showCrisisLink && crisisTile ? (
              <>
                <Text weight="semibold">{t('start.patientPath.crisis.bannerLabel')}</Text>
                <Caption1 className={styles.bannerDot}>· {t('start.patientPath.crisis.bannerDot')}</Caption1>
                <Link
                  className={styles.bannerLink}
                  to={crisisTile.route}
                  aria-label={t('start.patientPath.openRoleBoard', { role: t(crisisTile.labelKey) })}
                  onClick={() => {
                    rail?.openWithReco(
                      startInsight('patient-path-crisis', t(crisisTile.labelKey)),
                      startReco(
                        t(crisisTile.labelKey),
                        t('start.patientPath.crisis.body'),
                        [crisisTile.agent, crisisTile.ceiling],
                        ['hcp:PatientPath:crisis'],
                      ),
                    );
                    if (rail) {
                      void enrichWithLiveAnswer(t('start.patientPath.crisis.body'), rail).catch((error) => {
                        console.error('PO agent live enrichment failed', error);
                      });
                    }
                  }}
                >
                  {t('start.patientPath.crisis.cta')}
                </Link>
              </>
            ) : (
              <>
                <button
                  type="button"
                  className={styles.bannerTriggerButton}
                  data-testid="patient-path-crisis-trigger"
                  onClick={() => {
                    rail?.openWithReco(
                      startInsight('patient-path-crisis', t('start.patientPath.crisis.bannerLabel')),
                      startReco(
                        t('start.patientPath.crisis.bannerLabel'),
                        t('start.patientPath.crisis.body'),
                        [],
                        ['hcp:PatientPath:crisis'],
                      ),
                    );
                    if (rail) {
                      void enrichWithLiveAnswer(t('start.patientPath.crisis.body'), rail).catch((error) => {
                        console.error('PO agent live enrichment failed', error);
                      });
                    }
                  }}
                >
                  {t('start.patientPath.crisis.bannerLabel')}
                </button>
                <Caption1 className={styles.bannerDot}>· {t('start.patientPath.crisis.bannerDot')}</Caption1>
              </>
            )}
          </span>
          <span className={styles.bannerEvidence}>{t('start.patientPath.crisis.evidence')}</span>
          <Badge appearance="tint" color="warning">
            {t('start.patientPath.advisoryBadge')}
          </Badge>
        </article>

        <article
          className={styles.bannerCard}
          style={{ borderLeftColor: SHOWCASE_ACCENT.teal }}
          role="note"
          aria-label={t('start.patientPath.dataQuality.ariaLabel')}
        >
          <span className={styles.bannerBadge} style={{ backgroundColor: SHOWCASE_ACCENT.teal }}>
            {t('start.patientPath.dataQuality.badge')}
          </span>
          <span className={styles.bannerCopy}>
            <button
              type="button"
              className={styles.bannerTriggerButton}
              data-testid="patient-path-data-quality-trigger"
              onClick={() => {
                rail?.openWithReco(
                  startInsight('patient-path-data-quality', t('start.patientPath.dataQuality.title')),
                  startReco(
                    t('start.patientPath.dataQuality.title'),
                    t('start.patientPath.dataQuality.body'),
                    [],
                    ['hcp:DataQuality'],
                  ),
                );
                if (rail) {
                  void enrichWithLiveAnswer(t('start.patientPath.dataQuality.body'), rail).catch((error) => {
                    console.error('PO agent live enrichment failed', error);
                  });
                }
              }}
            >
              {t('start.patientPath.dataQuality.bannerLabel')}
            </button>
            <Caption1 className={styles.bannerDot}>· {t('start.patientPath.dataQuality.bannerDot')}</Caption1>
          </span>
          <span className={styles.bannerEvidence}>{t('start.patientPath.dataQuality.evidence')}</span>
          <Badge appearance="tint" color="informative">
            {t('start.patientPath.advisoryBadge')}
          </Badge>
        </article>
      </div>

      <div className={styles.journeyViewport}>
        <ol
          className={styles.journey}
          data-testid="patient-path-flow"
          aria-label={t('start.patientPath.journeyLabel')}
        >
          {operationalStops.map(({ bodyKey, tile, stepKey, evidenceKey }) => {
            const presentation = NODE_PRESENTATION[tile.boardKey];
            const nodeColor = presentation?.color ?? tokens.colorBrandBackground;
            const acronym = tile.agent.replace('-agent', '').toUpperCase();
            const StopIcon = presentation?.Icon ?? CheckmarkCircleRegular;
            return (
              <li key={tile.boardKey} className={styles.stop} data-testid="patient-path-stop">
                <Card className={styles.stopCard} appearance="outline">
                  <Link
                    className={styles.stopLink}
                    to={tile.route}
                    aria-label={t('start.patientPath.openRoleBoard', { role: t(tile.labelKey) })}
                    onClick={() => {
                      rail?.openWithReco(
                        startInsight(`patient-path-${tile.boardKey}`, t(tile.labelKey)),
                        startReco(t(tile.labelKey), t(bodyKey), [tile.agent, tile.ceiling], [
                          `hcp:PatientPath:${tile.boardKey}`,
                        ]),
                      );
                      if (rail) {
                        void enrichWithLiveAnswer(t(bodyKey), rail).catch((error) => {
                          console.error('PO agent live enrichment failed', error);
                        });
                      }
                    }}
                  >
                    <span
                      className={styles.node}
                      style={{ backgroundColor: nodeColor, color: '#ffffff' }}
                      data-testid="patient-path-node"
                    >
                      <StopIcon fontSize={26} />
                    </span>
                    <Badge
                      className={styles.agentBadge}
                      appearance="filled"
                      size="large"
                      style={{ backgroundColor: nodeColor }}
                    >
                      {acronym}
                    </Badge>
                    <span className={styles.stopTitle}>{t(stepKey)}</span>
                    <span
                      className={styles.evidenceChip}
                      style={{ borderColor: nodeColor }}
                      data-testid="patient-path-evidence"
                    >
                      {t(evidenceKey)}
                    </span>
                  </Link>
                </Card>
                <ChevronRightRegular className={styles.connector} aria-hidden />
              </li>
            );
          })}

          <li className={styles.stop} data-testid="patient-path-stop">
            <Card className={styles.stopCard} appearance="outline">
              <span
                className={styles.node}
                style={{ backgroundColor: RECOVERY_NODE_COLOR, color: '#ffffff' }}
                data-testid="patient-path-node"
              >
                <CheckmarkCircleRegular fontSize={28} />
              </span>
              <Badge appearance="tint" color="success">
                {t('start.patientPath.destinationBadge')}
              </Badge>
              <Title3 as="h3" className={styles.stopTitle}>
                {t('start.patientPath.recoveryTitle')}
              </Title3>
              <Caption1 className={styles.agentLine}>{t('start.patientPath.recoveryCaption')}</Caption1>
            </Card>
          </li>
        </ol>
      </div>

      <div
        className={styles.banners}
        data-testid="patient-path-foundation"
        aria-label={t('start.patientPath.foundationAriaLabel')}
      >
        <article
          className={styles.bannerCard}
          style={{ borderLeftColor: SHOWCASE_ACCENT.green }}
          role="note"
          aria-label={t('start.patientPath.productOwner.ariaLabel')}
          data-testid="patient-path-product-owner-advisory"
        >
          <span className={styles.bannerBadge} style={{ backgroundColor: SHOWCASE_ACCENT.green }}>
            {t('start.patientPath.productOwner.badge')}
          </span>
          <span className={styles.bannerCopy}>
            <button
              type="button"
              className={styles.bannerTriggerButton}
              data-testid="patient-path-product-owner-trigger"
              onClick={() => {
                rail?.openWithReco(
                  startInsight('patient-path-product-owner', t('start.patientPath.productOwner.title')),
                  startReco(
                    t('start.patientPath.productOwner.title'),
                    t('start.patientPath.productOwner.body'),
                    [],
                    ['hcp:ProductOwner'],
                  ),
                );
                if (rail) {
                  void enrichWithLiveAnswer(t('start.patientPath.productOwner.body'), rail).catch((error) => {
                    console.error('PO agent live enrichment failed', error);
                  });
                }
              }}
            >
              {t('start.patientPath.productOwner.bannerLabel')}
            </button>
            <Caption1 className={styles.bannerDot}>· {t('start.patientPath.productOwner.bannerDot')}</Caption1>
          </span>
          <span className={styles.bannerEvidence}>{t('start.patientPath.productOwner.evidence')}</span>
          <Badge appearance="tint" color="informative">
            {t('start.patientPath.advisoryBadge')}
          </Badge>
        </article>

        <article
          className={styles.bannerCard}
          style={{ borderLeftColor: SHOWCASE_ACCENT.violet }}
          role="note"
          aria-label={t('start.patientPath.signals.ariaLabel')}
          data-testid="patient-path-signals-advisory"
        >
          <span className={styles.bannerBadge} style={{ backgroundColor: SHOWCASE_ACCENT.violet }}>
            {t('start.patientPath.signals.badge')}
          </span>
          <span className={styles.bannerCopy}>
            <button
              type="button"
              className={styles.bannerTriggerButton}
              data-testid="patient-path-signals-trigger"
              onClick={() => {
                rail?.openWithReco(
                  startInsight('patient-path-signals', t('start.patientPath.signals.title')),
                  startReco(
                    t('start.patientPath.signals.title'),
                    t('start.patientPath.signals.body'),
                    [],
                    ['hcp:ExternalSignal'],
                  ),
                );
                if (rail) {
                  void enrichWithLiveAnswer(t('start.patientPath.signals.body'), rail).catch((error) => {
                    console.error('PO agent live enrichment failed', error);
                  });
                }
              }}
            >
              {t('start.patientPath.signals.bannerLabel')}
            </button>
            <Caption1 className={styles.bannerDot}>· {t('start.patientPath.signals.bannerDot')}</Caption1>
          </span>
          <span className={styles.bannerEvidence}>{t('start.patientPath.signals.evidence')}</span>
          <Badge appearance="tint" color="informative">
            {t('start.patientPath.advisoryBadge')}
          </Badge>
        </article>
      </div>

      <div className={sc.split} data-testid="patient-path-dc-insight">
        <button
          type="button"
          className={sc.accentCard}
          style={{ borderLeftColor: SHOWCASE_ACCENT.teal }}
          data-testid="patient-path-dc-insight-card"
          onClick={() => {
            rail?.openWithReco(
              startInsight('patient-path-dc-insight', t('start.patientPath.dcInsight.title')),
              startReco(
                t('start.patientPath.dcInsight.title'),
                t('start.patientPath.dcInsight.beats.signal.body'),
                DC_INSIGHT_BEATS.map((beat) => `${t(beat.labelKey)} — ${t(beat.bodyKey)}`),
                ['hcp:DcInsightPattern'],
              ),
            );
            if (rail) {
              void enrichWithLiveAnswer(t('start.patientPath.dcInsight.beats.signal.body'), rail).catch((error) => {
                console.error('PO agent live enrichment failed', error);
              });
            }
          }}
        >
          <span className={sc.cardTitle}>{t('start.patientPath.dcInsight.title')}</span>
          <div className={styles.beatList}>
            {DC_INSIGHT_BEATS.map((beat, index) => (
              <div key={beat.id} className={styles.beatRow}>
                <span
                  className={sc.numBadge}
                  style={{ backgroundColor: SHOWCASE_ACCENT[BEAT_ACCENT[beat.id]] }}
                  aria-hidden="true"
                >
                  {index + 1}
                </span>
                <span className={styles.beatCopy}>
                  <Text weight="bold">{t(beat.labelKey)}</Text> — {t(beat.bodyKey)}
                </span>
              </div>
            ))}
          </div>
        </button>

        <button
          type="button"
          className={sc.accentCard}
          style={{ borderLeftColor: SHOWCASE_ACCENT.green }}
          data-testid="patient-path-worked-example-card"
          onClick={() => {
            rail?.openWithReco(
              startInsight('patient-path-worked-example', t('start.patientPath.workedExample.eyebrow')),
              startReco(
                t('start.patientPath.workedExample.eyebrow'),
                t('start.patientPath.workedExample.sub'),
                [
                  t('start.patientPath.workedExample.pillAdvisory'),
                  t('start.patientPath.workedExample.pillAuditable'),
                ],
                ['hcp:CapacityForecast'],
              ),
            );
            if (rail) {
              void enrichWithLiveAnswer(t('start.patientPath.workedExample.sub'), rail).catch((error) => {
                console.error('PO agent live enrichment failed', error);
              });
            }
          }}
        >
          <Caption1>{t('start.patientPath.workedExample.eyebrow')}</Caption1>
          <div className={styles.kpiRow}>
            <span className={styles.kpiValue}>{t('start.patientPath.workedExample.kpiFrom')}</span>
            <Text aria-hidden="true">→</Text>
            <span className={mergeClasses(styles.kpiValue, styles.kpiTarget)}>
              {t('start.patientPath.workedExample.kpiTo')}
            </span>
          </div>
          <span className={sc.cardBody}>{t('start.patientPath.workedExample.sub')}</span>
          <div className={styles.pillRow}>
            <Badge appearance="tint" color="informative">
              {t('start.patientPath.workedExample.pillAdvisory')}
            </Badge>
            <Badge appearance="tint" color="success">
              {t('start.patientPath.workedExample.pillAuditable')}
            </Badge>
          </div>
        </button>
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
          <Badge appearance="tint" color="success">
            {t('start.patientPath.goldenThreadChip')}
          </Badge>
        </div>
      </footer>
    </div>
  );
}
