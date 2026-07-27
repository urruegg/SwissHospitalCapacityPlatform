import { useTranslation } from 'react-i18next';
import { Badge, Body1, Body2, Caption1, Text, makeStyles, mergeClasses, tokens } from '@fluentui/react-components';
import type { ExternalSignal, InternalSignal, Scenario } from '../../../../data/roleboard/crisis-data';
import { sortScenarios } from '../../../../data/roleboard/crisis-data';
import { ragColors } from '../../../../theme/curavias-theme';

/** Per-signal short display (Trust-A externals). Falls back to the raw status. */
const SIGNAL_DISPLAY: Record<string, { label: string; badge: string; tone: Tone }> = {
  'meteoswiss-heat': { label: 'heat L3/5', badge: 'ACTUAL', tone: 'over' },
  'bag-resp': { label: 'RSV rising ▲', badge: 'ACTUAL', tone: 'over' },
  'sed-seismic': { label: 'seismic nominal', badge: 'OK', tone: 'ok' },
  'alertswiss-heat-test': { label: 'quiet', badge: '1 Test quar.', tone: 'muted' },
};

type Tone = 'over' | 'watch' | 'ok' | 'muted';

function toneColor(tone: Tone): string {
  return tone === 'over' ? ragColors.bad : tone === 'watch' ? ragColors.neutral : tone === 'ok' ? ragColors.good : tokens.colorNeutralForeground4;
}

/** probability → scenario band. */
function band(probability: number): { label: string; tone: Tone } {
  if (probability >= 50) return { label: 'HIGH', tone: 'over' };
  if (probability >= 20) return { label: 'WATCH', tone: 'watch' };
  return { label: 'LOW', tone: 'muted' };
}

const useStyles = makeStyles({
  wrap: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalS },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalS,
  },
  title: { fontWeight: tokens.fontWeightSemibold },
  hint: { color: tokens.colorNeutralForeground3 },
  cols: { display: 'flex', gap: tokens.spacingHorizontalL, alignItems: 'stretch', flexWrap: 'wrap' },
  col: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXS, flexGrow: 1, flexBasis: '260px', minWidth: 0 },
  colHead: { color: tokens.colorNeutralForeground3, fontWeight: tokens.fontWeightSemibold, textTransform: 'uppercase', fontSize: tokens.fontSizeBase200, letterSpacing: '0.04em' },
  // Signal row (left column)
  sigRow: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalS,
    padding: `${tokens.spacingVerticalXS} ${tokens.spacingHorizontalS}`,
    borderRadius: tokens.borderRadiusMedium,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    cursor: 'pointer',
    ':hover': { backgroundColor: tokens.colorNeutralBackground1Hover },
    ':focus-visible': { boxShadow: `0 0 0 2px ${tokens.colorStrokeFocus2}` },
  },
  sigDot: { width: '8px', height: '8px', borderRadius: '50%', flexShrink: 0 },
  sigBody: { display: 'flex', flexDirection: 'column', gap: '1px', flexGrow: 1, minWidth: 0 },
  sigName: { fontWeight: tokens.fontWeightSemibold },
  sigDetail: { color: tokens.colorNeutralForeground3 },
  sigBadge: { flexShrink: 0, color: tokens.colorNeutralForeground3, fontWeight: tokens.fontWeightSemibold, fontSize: tokens.fontSizeBase200 },
  subHead: { color: tokens.colorNeutralForeground3, fontWeight: tokens.fontWeightSemibold, fontSize: tokens.fontSizeBase200, marginTop: tokens.spacingVerticalXS },
  // Scenario card (middle)
  scRow: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
    padding: tokens.spacingVerticalS,
    borderRadius: tokens.borderRadiusMedium,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    cursor: 'pointer',
    ':hover': { backgroundColor: tokens.colorNeutralBackground1Hover },
    ':focus-visible': { boxShadow: `0 0 0 2px ${tokens.colorStrokeFocus2}` },
  },
  scHead: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: tokens.spacingHorizontalXS },
  scName: { fontWeight: tokens.fontWeightSemibold },
  scFed: { color: tokens.colorNeutralForeground3 },
  // Probability card (right)
  probCard: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
    padding: tokens.spacingVerticalS,
    borderRadius: tokens.borderRadiusMedium,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  probHead: { display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: tokens.spacingHorizontalXS },
  probPct: { fontWeight: tokens.fontWeightBold, fontSize: tokens.fontSizeBase500 },
  probSub: { color: tokens.colorNeutralForeground3 },
  bar: { height: '6px', borderRadius: '3px', backgroundColor: tokens.colorNeutralBackground4, overflow: 'hidden', marginTop: '4px' },
  barFill: { height: '100%', borderRadius: '3px' },
  footNote: {
    padding: tokens.spacingVerticalS,
    borderRadius: tokens.borderRadiusMedium,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    color: tokens.colorNeutralForeground3,
  },
  footHead: { fontWeight: tokens.fontWeightSemibold, color: tokens.colorNeutralForeground2 },
  trustLine: { color: tokens.colorNeutralForeground4, fontSize: tokens.fontSizeBase200 },
});

interface TrustedSignalsPanelProps {
  signals: ExternalSignal[];
  internalSignals: InternalSignal[];
  scenarios: Scenario[];
  onSelectSignal: (signal: ExternalSignal) => void;
  onSelectScenario: (scenario: Scenario) => void;
}

/** Sprint 27 — Trusted signals (upper lane): external + internal signals → potential scenarios → probability. */
export function TrustedSignalsPanel({
  signals,
  internalSignals,
  scenarios,
  onSelectSignal,
  onSelectScenario,
}: TrustedSignalsPanelProps) {
  const s = useStyles();
  const { t } = useTranslation();
  const sorted = sortScenarios(scenarios);

  return (
    <div className={s.wrap}>
      <div className={s.header}>
        <Text className={s.title}>{t('csa.signals.title')}</Text>
        <Caption1 className={s.hint}>{t('csa.signals.hint')}</Caption1>
      </div>

      <div className={s.cols}>
        {/* Left — external + internal signals */}
        <div className={s.col}>
          <Caption1 className={s.colHead}>{t('csa.signals.external')}</Caption1>
          {signals.map((sig) => {
            const d = SIGNAL_DISPLAY[sig.id] ?? { label: sig.status, badge: sig.status, tone: 'muted' as Tone };
            return (
              <div
                key={sig.id}
                className={s.sigRow}
                role="button"
                tabIndex={0}
                aria-label={`${sig.source}: ${d.label}`}
                onClick={() => onSelectSignal(sig)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSelectSignal(sig); }
                }}
              >
                <span className={s.sigDot} style={{ backgroundColor: toneColor(d.tone) }} aria-hidden />
                <span className={s.sigBody}>
                  <Body2 className={s.sigName}>{sig.source}</Body2>
                  <Caption1 className={s.sigDetail}>{d.label}</Caption1>
                </span>
                <span className={s.sigBadge}>{d.badge}</span>
              </div>
            );
          })}
          <Caption1 className={mergeClasses(s.colHead, s.subHead)}>{t('csa.signals.internal')}</Caption1>
          {internalSignals.map((sig) => (
            <div key={sig.id} className={s.sigRow} style={{ cursor: 'default' }}>
              <span className={s.sigDot} style={{ backgroundColor: toneColor(sig.badgeTone) }} aria-hidden />
              <span className={s.sigBody}>
                <Body2 className={s.sigName}>{sig.label}</Body2>
                <Caption1 className={s.sigDetail}>{sig.detail}</Caption1>
              </span>
              <span className={s.sigBadge} style={{ color: toneColor(sig.badgeTone) }}>{sig.badge}</span>
            </div>
          ))}
        </div>

        {/* Middle — potential scenarios */}
        <div className={s.col}>
          <Caption1 className={s.colHead}>{t('csa.signals.scenarios')}</Caption1>
          {sorted.map((sc) => {
            const b = band(sc.probability);
            return (
              <div
                key={sc.id}
                className={s.scRow}
                role="button"
                tabIndex={0}
                aria-label={sc.name}
                onClick={() => onSelectScenario(sc)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSelectScenario(sc); }
                }}
              >
                <div className={s.scHead}>
                  <Body1 className={s.scName}>{sc.name}</Body1>
                  <Badge appearance="tint" color="informative" size="small" style={{ backgroundColor: 'transparent', color: toneColor(b.tone) }}>
                    {sc.isSpof ? 'SPOF' : b.label}
                  </Badge>
                </div>
                <Caption1 className={s.scFed}>{t('csa.signals.fedBy', { p: sc.probability })}</Caption1>
              </div>
            );
          })}
        </div>

        {/* Right — probability */}
        <div className={s.col}>
          <Caption1 className={s.colHead}>{t('csa.signals.probability')}</Caption1>
          {sorted.map((sc) => {
            const b = band(sc.probability);
            return (
              <div key={sc.id} className={s.probCard}>
                <div className={s.probHead}>
                  <Body2 className={s.sigName}>{sc.name}</Body2>
                  <span className={s.probPct} style={{ color: toneColor(b.tone) }}>{sc.probability}%</span>
                </div>
                <Caption1 className={s.probSub}>{t('csa.signals.certainty', { c: sc.probability })}</Caption1>
                <div className={s.bar}>
                  <div className={s.barFill} style={{ width: `${sc.probability}%`, backgroundColor: toneColor(b.tone) }} />
                </div>
              </div>
            );
          })}
          <div className={s.footNote}>
            <Caption1 className={s.footHead}>{t('csa.signals.scaleTitle')}</Caption1>
            <Caption1>{t('csa.signals.scale')}</Caption1>
          </div>
          <Caption1 className={s.trustLine}>{t('csa.signals.trustLine')}</Caption1>
        </div>
      </div>
    </div>
  );
}
