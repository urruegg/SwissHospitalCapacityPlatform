import { useTranslation } from 'react-i18next';
import { Badge, Caption1, makeStyles, tokens } from '@fluentui/react-components';
import { ArrowUpRegular, ArrowRightRegular, ArrowDownRegular } from '@fluentui/react-icons';
import { chipBadgeColor } from '../../../../copilot-rail/reco';
import type { WardRow, WardTrend } from '../../../../data/roleboard/occupancy-data';
import { space, motion, focus } from '../../../../theme/design-system';

const useStyles = makeStyles({
  wrap: { display: 'flex', flexDirection: 'column', gap: space.s },
  hint: { color: tokens.colorNeutralForeground3 },
  table: { width: '100%', maxWidth: '820px', borderCollapse: 'collapse' },
  th: {
    textAlign: 'left',
    paddingTop: space.s,
    paddingBottom: space.s,
    paddingLeft: space.m,
    paddingRight: space.m,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    color: tokens.colorNeutralForeground3,
    fontWeight: tokens.fontWeightSemibold,
  },
  td: {
    paddingTop: space.s,
    paddingBottom: space.s,
    paddingLeft: space.m,
    paddingRight: space.m,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  row: {
    cursor: 'pointer',
    transitionProperty: 'background-color',
    transitionDuration: motion.durationFast,
    transitionTimingFunction: motion.easyEase,
    ':hover': { backgroundColor: tokens.colorNeutralBackground1Hover },
    ':focus-visible': {
      outlineWidth: focus.ringWidth,
      outlineStyle: 'solid',
      outlineColor: tokens.colorStrokeFocus2,
      outlineOffset: `-${focus.ringOffset}`,
    },
  },
});

function TrendIcon({ trend }: { trend: WardTrend }) {
  if (trend === 'rising') return <ArrowUpRegular aria-label="rising" />;
  if (trend === 'falling') return <ArrowDownRegular aria-label="falling" />;
  return <ArrowRightRegular aria-label="flat" />;
}

interface WardForecastTableProps {
  wards: WardRow[];
  onSelectWard: (ward: WardRow) => void;
}

export function WardForecastTable({ wards, onSelectWard }: WardForecastTableProps) {
  const s = useStyles();
  const { t } = useTranslation();
  return (
    <div className={s.wrap}>
      <Caption1 className={s.hint}>{t('ooa.table.hint')}</Caption1>
      <table className={s.table}>
        <thead>
          <tr>
            <th className={s.th}>{t('ooa.table.ward')}</th>
            <th className={s.th}>{t('ooa.table.now')}</th>
            <th className={s.th}>{t('ooa.table.trend')}</th>
            <th className={s.th}>{t('ooa.table.forecast')}</th>
            <th className={s.th}>{t('ooa.table.flag')}</th>
          </tr>
        </thead>
        <tbody>
          {wards.map((w) => (
            <tr
              key={w.id}
              className={s.row}
              role="button"
              tabIndex={0}
              aria-label={`${w.label} ${w.forecastPct}%`}
              onClick={() => onSelectWard(w)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') onSelectWard(w);
                else if (e.key === ' ') { e.preventDefault(); onSelectWard(w); }
              }}
            >
              <td className={s.td}>{w.label}</td>
              <td className={s.td}>{`${w.nowPct}%`}</td>
              <td className={s.td}><TrendIcon trend={w.trend} /></td>
              <td className={s.td}>{`${w.forecastPct}%`}</td>
              <td className={s.td}>
                <Badge appearance="tint" color={chipBadgeColor(w.flag)}>
                  {w.flag.toUpperCase()}
                </Badge>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
