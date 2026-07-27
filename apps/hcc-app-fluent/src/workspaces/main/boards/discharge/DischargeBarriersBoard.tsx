import { useTranslation } from 'react-i18next';
import { Badge, Body1, Button, Caption1, Text, makeStyles, mergeClasses, tokens } from '@fluentui/react-components';
import {
  VehicleTruckProfileRegular,
  PillRegular,
  BedRegular,
  CheckmarkCircleRegular,
  HomeRegular,
  ArrowRightRegular,
  type FluentIcon,
} from '@fluentui/react-icons';
import type { BarrierIcon, BarrierSummary, CapacityBarrier } from '../../../../data/roleboard/discharge-data';
import { sortCapacityBarriers } from '../../../../data/roleboard/discharge-data';
import { space, radii } from '../../../../theme/design-system';
import { ragColors } from '../../../../theme/curavias-theme';

const ICONS: Record<BarrierIcon, FluentIcon> = {
  transport: VehicleTruckProfileRegular,
  meds: PillRegular,
  stepdown: BedRegular,
  signoff: CheckmarkCircleRegular,
  homecare: HomeRegular,
};

const useStyles = makeStyles({
  wrap: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalM },
  // Full-bleed grey header inside the padded card (negative margins match the panel padding).
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
  owner: { color: tokens.colorNeutralForeground2, flexShrink: 0, minWidth: '150px' },
  wait: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalXS, flexShrink: 0, minWidth: '92px' },
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
});

interface DischargeBarriersBoardProps {
  barriers: CapacityBarrier[];
  onSelectBarrier: (barrier: CapacityBarrier) => void;
  onViewPlan?: () => void;
  summary?: BarrierSummary;
}

/** Sprint 27 — capacity barriers (lower lane): ranked rows sorted by bed impact, mirrors the bmca PlacementBarriersBoard. */
export function DischargeBarriersBoard({ barriers, onSelectBarrier, onViewPlan, summary }: DischargeBarriersBoardProps) {
  const s = useStyles();
  const { t } = useTranslation();
  const sorted = sortCapacityBarriers(barriers);
  const maxImpact = Math.max(1, ...sorted.map((b) => b.bedImpact));

  return (
    <div className={s.wrap}>
      <div className={s.headerBar}>
        <Text className={s.title}>{t('dca.barriers.title')}</Text>
        <Caption1 className={s.hint}>{t('dca.barriers.hint')}</Caption1>
      </div>

      <div className={s.summaryRow}>
        {summary ? (
          <Caption1>
            {t('dca.barriers.summary', {
              ready: summary.readyNow,
              blocked: summary.blocked,
              barriers: summary.barriers,
              beds: summary.bedsRecoverable,
            })}
          </Caption1>
        ) : (
          <span />
        )}
        <Button appearance="primary" size="small" onClick={onViewPlan}>
          {t('dca.barriers.cta')}
        </Button>
      </div>

      <ul className={s.list} aria-label={t('dca.barriers.title')}>
        {sorted.map((b, idx) => {
          const Glyph = ICONS[b.icon];
          const dotColor =
            b.waitTone === 'over' ? ragColors.bad : b.waitTone === 'watch' ? ragColors.neutral : ragColors.good;
          const impact = b.impactLabel ?? t(b.bedImpact === 1 ? 'dca.barriers.bedOne' : 'dca.barriers.bedMany', {
            n: b.bedImpact,
          });
          return (
            <li
              key={b.id}
              className={idx === 0 ? mergeClasses(s.row, s.rowTop) : s.row}
              role="button"
              tabIndex={0}
              aria-label={b.name}
              onClick={() => onSelectBarrier(b)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  onSelectBarrier(b);
                }
              }}
            >
              <span className={idx === 0 ? mergeClasses(s.rank, s.rankTop) : s.rank}>{idx + 1}</span>
              <Glyph className={s.icon} aria-hidden />
              <div className={s.nameCol}>
                <div className={s.nameRow}>
                  <Body1 className={s.name}>{b.name}</Body1>
                  {b.agingRisk && (
                    <Badge appearance="tint" color="danger" size="small">
                      {t('dca.barriers.agingRisk')}
                    </Badge>
                  )}
                </div>
                <Caption1 className={s.desc}>{b.description}</Caption1>
              </div>
              <div className={s.impact}>
                <span className={s.bar} aria-hidden>
                  {Array.from({ length: maxImpact }, (_, i) => (
                    <span key={i} className={i < b.bedImpact ? mergeClasses(s.cell, s.cellOn) : s.cell} />
                  ))}
                </span>
                <Caption1>{impact}</Caption1>
              </div>
              <Caption1 className={s.owner}>{b.owner}</Caption1>
              <span className={s.wait}>
                <span className={s.dot} style={{ backgroundColor: dotColor }} aria-hidden />
                <Caption1>{b.wait}</Caption1>
              </span>
              <span className={s.action}>
                <Caption1>{b.action}</Caption1>
                <ArrowRightRegular aria-hidden />
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
