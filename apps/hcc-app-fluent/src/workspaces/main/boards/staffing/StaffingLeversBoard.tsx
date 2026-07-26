import { useTranslation } from 'react-i18next';
import { Badge, Body1, Button, Caption1, Text, makeStyles, mergeClasses, tokens } from '@fluentui/react-components';
import {
  PersonRegular,
  ArrowSyncRegular,
  ClockRegular,
  PeopleRegular,
  ShieldRegular,
  ArrowRightRegular,
  type FluentIcon,
} from '@fluentui/react-icons';
import type { StaffLeverIcon, StaffLeverSummary, StaffingLever } from '../../../../data/roleboard/staffing-data';
import { sortStaffingLevers } from '../../../../data/roleboard/staffing-data';
import { space, radii } from '../../../../theme/design-system';
import { ragColors } from '../../../../theme/curavias-theme';

const ICONS: Record<StaffLeverIcon, FluentIcon> = {
  skillmatch: PersonRegular,
  float: ArrowSyncRegular,
  overtime: ClockRegular,
  buddy: PeopleRegular,
  agency: ShieldRegular,
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
  covered: { color: ragColors.good, fontWeight: tokens.fontWeightSemibold },
  reserve: { color: tokens.colorNeutralForeground3 },
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
});

interface StaffingLeversBoardProps {
  levers: StaffingLever[];
  onSelectLever: (lever: StaffingLever) => void;
  onViewPlan?: () => void;
  summary?: StaffLeverSummary;
}

/** Sprint 27 — staffing levers (lower lane): ranked rows sorted by beds covered, mirrors the bmca/orsa levers board. */
export function StaffingLeversBoard({ levers, onSelectLever, onViewPlan, summary }: StaffingLeversBoardProps) {
  const s = useStyles();
  const { t } = useTranslation();
  const sorted = sortStaffingLevers(levers);
  const maxImpact = Math.max(1, ...sorted.map((l) => l.bedsEnabled));

  return (
    <div className={s.wrap}>
      <div className={s.headerBar}>
        <Text className={s.title}>{t('sba.levers.title')}</Text>
        <Caption1 className={s.hint}>{t('sba.levers.hint')}</Caption1>
      </div>

      <div className={s.summaryRow}>
        {summary ? (
          <Caption1>
            {t('sba.levers.summary', {
              oncology: summary.oncologyToSecure,
              general: summary.generalCovered,
              beds: summary.bedsStaffed,
            })}
          </Caption1>
        ) : (
          <span />
        )}
        <Button appearance="primary" size="small" onClick={onViewPlan}>
          {t('sba.levers.cta')}
        </Button>
      </div>

      <ul className={s.list} aria-label={t('sba.levers.title')}>
        {sorted.map((l, idx) => {
          const Glyph = ICONS[l.icon];
          const dotColor =
            l.timingTone === 'over' ? ragColors.bad : l.timingTone === 'watch' ? ragColors.neutral : ragColors.good;
          const bedLabel = t(l.bedsEnabled === 1 ? 'sba.levers.bedOne' : 'sba.levers.bedMany', {
            n: l.bedsEnabled,
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
                  {l.critical && (
                    <Badge appearance="tint" color="danger" size="small">
                      {t('sba.levers.critical')}
                    </Badge>
                  )}
                  {l.lastResort && (
                    <Badge appearance="tint" color="danger" size="small">
                      {t('sba.levers.lastResort')}
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
                    <span key={i} className={i < l.bedsEnabled ? mergeClasses(s.cell, s.cellOn) : s.cell} />
                  ))}
                </span>
                {l.impactLabel ? (
                  <Caption1 className={l.bedsEnabled > 0 ? s.covered : s.reserve}>{l.impactLabel}</Caption1>
                ) : (
                  <Caption1>{bedLabel}</Caption1>
                )}
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
    </div>
  );
}
