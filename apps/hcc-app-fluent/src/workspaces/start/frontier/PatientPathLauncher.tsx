import {
  Badge,
  Body1,
  Caption1,
  Text,
  Title3,
  makeStyles,
  mergeClasses,
  tokens,
} from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useCopilotRail } from '../../../copilot-rail/rail-context';
import { useRoleLens } from '../../../context/role-context';
import { useShowcaseStyles, SHOWCASE_ACCENT, type ShowcaseAccent } from '../../shared/narrative/showcase-styles';
import { LAUNCHER_TILES, type LauncherTile } from '../role-launcher';
import { enrichWithLiveAnswer, startInsight, startReco } from './start-rail';
import { DC_INSIGHT_BEATS, PATIENT_PATH_OPERATIONAL_STOPS, type DcInsightBeatId } from './start-content';

const PATIENT_PATH_JOURNEY_STOP_COUNT = PATIENT_PATH_OPERATIONAL_STOPS.length + 1;

const BEAT_ACCENT: Record<DcInsightBeatId, ShowcaseAccent> = {
  signal: 'teal',
  understanding: 'teal',
  recommendation: 'green',
  action: 'amber',
  coordination: 'violet',
};

const NODE_PRESENTATION: Record<string, { color: string; glyph: string }> = {
  occupancy: { color: '#33546B', glyph: 'occupancy' },
  'bed-manager': { color: '#3C6E8E', glyph: 'bed-manager' },
  'or-steering': { color: '#24708F', glyph: 'or-steering' },
  staffing: { color: '#1E7D68', glyph: 'staffing' },
  discharge: { color: '#1F7A50', glyph: 'discharge' },
};

const RECOVERY_NODE_COLOR = '#218A5A';

const GLYPH_PATHS: Record<string, string> = {
  occupancy: 'M2 12h4l3 8 4-16 3 8h4',
  'bed-manager': 'M3 18V8m0 5h13a4 4 0 0 1 4 4v1M7 12V10.5A1.5 1.5 0 0 1 8.5 9h2',
  'or-steering': 'M12 3v3M12 18v3M3 12h3M18 12h3M12 8.5A3.5 3.5 0 1 0 12 15.5A3.5 3.5 0 0 0 12 8.5Z',
  staffing: 'M9 5a2.6 2.6 0 1 0 0 5.2A2.6 2.6 0 0 0 9 5ZM3.5 19c0-3 2.5-5.4 5.5-5.4s5.5 2.4 5.5 5.4M16 8.6a2.1 2.1 0 1 0 0 4.2M16.5 13.4c2.3.2 4 2.1 4 4.4',
  discharge: 'M13 4h6v16h-6M10.5 12H20m0 0-3.2-3.2M20 12l-3.2 3.2',
  recovery: 'M4 12.5l4.5 4.5L20 6',
};

function NodeGlyph({ id }: { id: string }) {
  return (
    <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true" focusable="false">
      <path
        d={GLYPH_PATHS[id] ?? GLYPH_PATHS.recovery}
        fill="none"
        stroke="#ffffff"
        strokeWidth="1.9"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

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
    position: 'relative',
    display: 'grid',
    gridTemplateColumns: `repeat(${PATIENT_PATH_JOURNEY_STOP_COUNT}, minmax(132px, 1fr))`,
    gap: tokens.spacingHorizontalS,
    minWidth: '900px',
    listStyleType: 'none',
    margin: 0,
    padding: `${tokens.spacingVerticalXXL} ${tokens.spacingHorizontalM}`,
    '@media (max-width: 720px)': {
      gridTemplateColumns: '1fr',
      minWidth: 0,
      padding: `${tokens.spacingVerticalS} 0`,
      gap: tokens.spacingVerticalM,
    },
  },
  wave: {
    position: 'absolute',
    left: tokens.spacingHorizontalM,
    right: tokens.spacingHorizontalM,
    top: 'calc(50% - 40px)',
    height: '80px',
    width: 'auto',
    zIndex: 0,
    pointerEvents: 'none',
    '@media (max-width: 720px)': {
      display: 'none',
    },
  },
  stop: {
    position: 'relative',
    zIndex: 1,
    minWidth: 0,
    display: 'grid',
    justifyItems: 'center',
    textAlign: 'center',
    gap: tokens.spacingVerticalXS,
  },
  stopHigh: {
    alignSelf: 'start',
    '@media (max-width: 720px)': { alignSelf: 'auto' },
  },
  stopLow: {
    alignSelf: 'end',
    marginTop: '58px',
    '@media (max-width: 720px)': { marginTop: 0, alignSelf: 'auto' },
  },
  stopLink: {
    display: 'grid',
    justifyItems: 'center',
    gap: tokens.spacingVerticalXS,
    color: 'inherit',
    textDecorationLine: 'none',
    borderRadius: tokens.borderRadiusXLarge,
    padding: tokens.spacingVerticalXXS,
    ':focus-visible': {
      outlineStyle: 'solid',
      outlineWidth: tokens.strokeWidthThick,
      outlineColor: tokens.colorStrokeFocus2,
      outlineOffset: '3px',
    },
  },
  node: {
    width: '60px',
    height: '60px',
    borderRadius: tokens.borderRadiusCircular,
    display: 'grid',
    placeItems: 'center',
    boxShadow: tokens.shadow8,
    border: '3px solid #ffffff',
  },
  agentBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: '40px',
    height: '20px',
    paddingLeft: '6px',
    paddingRight: '6px',
    borderRadius: tokens.borderRadiusMedium,
    fontSize: '11px',
    fontWeight: tokens.fontWeightBold,
    letterSpacing: '0.04em',
    // Badge background is always a fixed deep node hex, so white text is the
    // theme-independent AA-safe choice. The Curavias brand ramp resolves
    // colorNeutralForegroundOnBrand to a dark tone (fails contrast here).
    color: '#ffffff',
  },
  stopTitle: {
    fontSize: tokens.fontSizeBase200,
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorNeutralForeground1,
    overflowWrap: 'anywhere',
  },
  evidenceChip: {
    display: 'inline-flex',
    alignItems: 'center',
    padding: `2px ${tokens.spacingHorizontalS}`,
    borderRadius: tokens.borderRadiusCircular,
    fontSize: '11px',
    fontWeight: tokens.fontWeightSemibold,
    backgroundColor: tokens.colorNeutralBackground3,
    color: tokens.colorNeutralForeground2,
    border: '1px solid transparent',
    overflowWrap: 'anywhere',
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
  const showCrisisBanner = Boolean(capabilities.nav.csa && crisisTile);

  return (
    <div className={styles.root}>
      <div
        className={styles.banners}
        data-testid="patient-path-banners"
        aria-label={t('start.patientPath.bannersAriaLabel')}
      >
        {showCrisisBanner && crisisTile ? (
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
            </span>
            <span className={styles.bannerEvidence}>{t('start.patientPath.crisis.evidence')}</span>
            <Badge appearance="tint" color="warning">
              {t('start.patientPath.advisoryBadge')}
            </Badge>
          </article>
        ) : null}

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
          <svg
            className={styles.wave}
            viewBox="0 0 1000 118"
            preserveAspectRatio="none"
            aria-hidden="true"
            focusable="false"
          >
            <defs>
              <linearGradient id="ppWaveGradient" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#33546B" />
                <stop offset="55%" stopColor="#24708F" />
                <stop offset="100%" stopColor="#218A5A" />
              </linearGradient>
            </defs>
            <path
              d="M0,78 C120,78 168,26 300,26 C432,26 512,92 660,92 C792,92 872,34 1000,42"
              fill="none"
              stroke="url(#ppWaveGradient)"
              strokeWidth="3"
              vectorEffect="non-scaling-stroke"
            />
          </svg>

          {operationalStops.map(({ bodyKey, tile, stepKey, evidenceKey }, index) => {
            const presentation = NODE_PRESENTATION[tile.boardKey];
            const nodeColor = presentation?.color ?? tokens.colorBrandBackground;
            const acronym = tile.agent.replace('-agent', '').toUpperCase();
            return (
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
                    style={{ backgroundColor: nodeColor }}
                    data-testid="patient-path-node"
                  >
                    <NodeGlyph id={presentation?.glyph ?? 'recovery'} />
                  </span>
                  <span className={styles.agentBadge} style={{ backgroundColor: nodeColor }}>
                    {acronym}
                  </span>
                  <span className={styles.stopTitle}>{t(stepKey)}</span>
                  <span
                    className={styles.evidenceChip}
                    style={{ borderColor: nodeColor }}
                    data-testid="patient-path-evidence"
                  >
                    {t(evidenceKey)}
                  </span>
                </Link>
              </li>
            );
          })}

          <li className={mergeClasses(styles.stop, styles.stopLow)} data-testid="patient-path-stop">
            <span
              className={styles.node}
              style={{ backgroundColor: RECOVERY_NODE_COLOR }}
              data-testid="patient-path-node"
            >
              <NodeGlyph id="recovery" />
            </span>
            <Badge appearance="tint" color="success">
              {t('start.patientPath.destinationBadge')}
            </Badge>
            <Title3 as="h3" className={styles.stopTitle}>
              {t('start.patientPath.recoveryTitle')}
            </Title3>
            <Caption1 className={styles.agentLine}>{t('start.patientPath.recoveryCaption')}</Caption1>
          </li>
        </ol>
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
