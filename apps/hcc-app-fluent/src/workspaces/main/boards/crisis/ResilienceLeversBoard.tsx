import { useTranslation } from 'react-i18next';
import { Badge, Body1, Button, Caption1, Text, makeStyles, mergeClasses, tokens } from '@fluentui/react-components';
import {
  ShieldRegular,
  BatteryChargeRegular,
  ArrowExportRegular,
  GridRegular,
  WarningRegular,
  ArrowRightRegular,
  type FluentIcon,
} from '@fluentui/react-icons';
import type { AbsorbedSummary, ResilienceLever, ResilienceLeverIcon, ResilienceSummary } from '../../../../data/roleboard/crisis-data';
import { space, radii } from '../../../../theme/design-system';
import { ragColors } from '../../../../theme/curavias-theme';

const ICONS: Record<ResilienceLeverIcon, FluentIcon> = {
  spof: ShieldRegular,
  buffer: BatteryChargeRegular,
  discharge: ArrowExportRegular,
  gate: GridRegular,
  escalation: WarningRegular,
};

type Tone = 'over' | 'watch' | 'ok' | 'muted';
function toneColor(tone: Tone): string {
  return tone === 'over' ? ragColors.bad : tone === 'watch' ? ragColors.neutral : tone === 'ok' ? ragColors.good : tokens.colorNeutralForeground4;
}

const useStyles = makeStyles({
  wrap: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalM },
  headerBar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalS,
    marginTop: `calc(-1 * ${space.l})`,
    marginLeft: `calc(-1 * ${space.l})`,
    marginRight: `calc(-1 * ${space.l})`,
    paddingTop: tokens.spacingVerticalS,
    paddingBottom: tokens.spacingVerticalS,
    paddingLeft: space.l,
    paddingRight: space.l,
    backgroundColor: tokens.colorNeutralBackground3,
    borderTopLeftRadius: radii.card,
    borderTopRightRadius: radii.card,
  },
  title: { fontWeight: tokens.fontWeightSemibold },
  hint: { color: tokens.colorNeutralForeground3 },
  summaryRow: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalS,
  },
  list: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalS, padding: 0, margin: 0, listStyle: 'none' },
  row: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalM,
    padding: tokens.spacingVerticalS,
    borderRadius: tokens.borderRadiusMedium,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    cursor: 'pointer',
    ':hover': { backgroundColor: tokens.colorNeutralBackground1Hover },
    ':focus-visible': { boxShadow: `0 0 0 2px ${tokens.colorStrokeFocus2}` },
  },
  rowTop: { border: `1px solid ${ragColors.good}` },
  rank: {
    width: '24px',
    height: '24px',
    borderRadius: '50%',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
    fontSize: tokens.fontSizeBase200,
    fontWeight: tokens.fontWeightSemibold,
    backgroundColor: tokens.colorNeutralBackground4,
    color: tokens.colorNeutralForeground2,
  },
  rankTop: { backgroundColor: ragColors.good, color: '#0E0F11' },
  icon: { fontSize: '20px', color: tokens.colorNeutralForeground2, flexShrink: 0 },
  nameCol: { display: 'flex', flexDirection: 'column', gap: '2px', flexGrow: 1, minWidth: 0 },
  nameRow: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalXS, flexWrap: 'wrap' },
  name: { fontWeight: tokens.fontWeightSemibold },
  desc: { color: tokens.colorNeutralForeground3 },
  impact: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalXS, flexShrink: 0, minWidth: '92px' },
  bar: { display: 'inline-flex', gap: '2px' },
  cell: { width: '12px', height: '8px', borderRadius: '2px', backgroundColor: tokens.colorNeutralBackground4 },
  cellOn: { backgroundColor: ragColors.good },
  last: { color: tokens.colorNeutralForeground3 },
  owner: { color: tokens.colorNeutralForeground2, flexShrink: 0, minWidth: '150px' },
  timing: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalXS, flexShrink: 0, minWidth: '92px' },
  dot: { width: '8px', height: '8px', borderRadius: '50%', flexShrink: 0 },
  action: {
    display: 'flex',
    alignItems: 'center',
    gap: '2px',
    justifyContent: 'flex-end',
    color: tokens.colorNeutralForeground3,
    flexShrink: 0,
    minWidth: '104px',
  },
  // Absorbed footer
  absorbRow: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: tokens.spacingHorizontalS, paddingTop: tokens.spacingVerticalXS },
  absorbLabel: { color: tokens.colorNeutralForeground3 },
  absorbCount: { fontWeight: tokens.fontWeightSemibold },
  absorbBar: { display: 'flex', height: '8px', borderRadius: '4px', overflow: 'hidden', width: '100%' },
  liveSync: { color: ragColors.good, paddingTop: '2px' },
});

interface ResilienceLeversBoardProps {
  levers: ResilienceLever[];
  onSelectLever: (lever: ResilienceLever) => void;
  onViewPlan?: () => void;
  summary?: ResilienceSummary;
  absorbed?: AbsorbedSummary;
}

/** Sprint 27 — Resilience levers (lower lane): curated priority order (SPOF first), mirrors the bmca/orsa/sba levers board. */
export function ResilienceLeversBoard({ levers, onSelectLever, onViewPlan, summary, absorbed }: ResilienceLeversBoardProps) {
  const s = useStyles();
  const { t } = useTranslation();
  const maxImpact = Math.max(1, ...levers.map((l) => l.bedsProtected));

  return (
    <div className={s.wrap}>
      <div className={s.headerBar}>
        <Text className={s.title}>{t('csa.levers.title')}</Text>
        <Caption1 className={s.hint}>{t('csa.levers.hint')}</Caption1>
      </div>

      <div className={s.summaryRow}>
        {summary ? (
          <Caption1>
            {t('csa.levers.summary', {
              tested: summary.stressTested,
              holds: summary.holdsUnder,
              reserve: summary.needsReserve,
            })}
          </Caption1>
        ) : (
          <span />
        )}
        <Button appearance="primary" size="small" onClick={onViewPlan}>
          {t('csa.levers.cta')}
        </Button>
      </div>

      <ul className={s.list} aria-label={t('csa.levers.title')}>
        {levers.map((l, idx) => {
          const Glyph = ICONS[l.icon];
          const dotColor = toneColor(l.timingTone);
          const impact = l.impactLabel ?? t(l.bedsProtected === 1 ? 'csa.levers.bedOne' : 'csa.levers.bedMany', {
            n: l.bedsProtected,
          });
          return (
            <li
              key={l.id}
              className={idx === 0 ? mergeClasses(s.row, s.rowTop) : s.row}
              role="button"
              tabIndex={0}
              aria-label={l.label}
              onClick={() => onSelectLever(l)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  onSelectLever(l);
                }
              }}
            >
              <span className={idx === 0 ? mergeClasses(s.rank, s.rankTop) : s.rank}>{idx + 1}</span>
              <Glyph className={s.icon} aria-hidden />
              <div className={s.nameCol}>
                <div className={s.nameRow}>
                  <Body1 className={s.name}>{l.label}</Body1>
                  {l.spof && (
                    <Badge appearance="tint" color="danger" size="small">
                      {t('csa.levers.spof')}
                    </Badge>
                  )}
                  {l.handoffTo && (
                    <Badge appearance="tint" color="brand" size="small">
                      → {l.handoffTo}
                    </Badge>
                  )}
                </div>
                <Caption1 className={s.desc}>{l.description}</Caption1>
              </div>
              <div className={s.impact}>
                <span className={s.bar} aria-hidden>
                  {Array.from({ length: maxImpact }, (_, i) => (
                    <span key={i} className={i < l.bedsProtected ? mergeClasses(s.cell, s.cellOn) : s.cell} />
                  ))}
                </span>
                <Caption1 className={l.impactLabel && l.bedsProtected === 0 ? s.last : undefined}>{impact}</Caption1>
              </div>
              <Caption1 className={s.owner}>{l.owner}</Caption1>
              <span className={s.timing}>
                <span className={s.dot} style={{ backgroundColor: dotColor }} aria-hidden />
                <Caption1>{l.timing}</Caption1>
              </span>
              <span className={s.action}>
                <Caption1>{l.window}</Caption1>
                <ArrowRightRegular aria-hidden />
              </span>
            </li>
          );
        })}
      </ul>

      {absorbed && (
        <>
          <div className={s.absorbRow}>
            <Caption1 className={s.absorbLabel}>{t('csa.levers.absorbedLabel')}</Caption1>
            <Caption1 className={s.absorbCount}>{t('csa.levers.absorbed', { absorbed: absorbed.absorbed, total: absorbed.total })}</Caption1>
          </div>
          <div className={s.absorbBar} aria-hidden>
            <span style={{ width: '55%', backgroundColor: ragColors.good }} />
            <span style={{ width: '30%', backgroundColor: ragColors.neutral }} />
            <span style={{ width: '15%', backgroundColor: '#8B5CF6' }} />
          </div>
          <Caption1 className={s.liveSync}>{t('csa.levers.liveSync')}</Caption1>
        </>
      )}
    </div>
  );
}
