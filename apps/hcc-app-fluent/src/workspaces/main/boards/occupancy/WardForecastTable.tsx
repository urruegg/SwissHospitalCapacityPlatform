import { useTranslation } from 'react-i18next';
import { Badge, Caption1, makeStyles, tokens } from '@fluentui/react-components';
import { ArrowUpRegular, ArrowRightRegular, ArrowDownRegular } from '@fluentui/react-icons';
import { chipBadgeColor } from '../../../../copilot-rail/reco';
import type { WardRow, WardTrend } from '../../../../data/roleboard/occupancy-data';

const useStyles = makeStyles({
  wrap: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXS },
  hint: { color: tokens.colorNeutralForeground3 },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: {
    textAlign: 'left',
    padding: tokens.spacingVerticalXS,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    color: tokens.colorNeutralForeground3,
    fontWeight: tokens.fontWeightSemibold,
  },
  td: { padding: tokens.spacingVerticalXS, borderBottom: `1px solid ${tokens.colorNeutralStroke2}` },
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
              role="button"
              tabIndex={0}
              aria-label={`${w.label} ${w.forecastPct}%`}
              onClick={() => onSelectWard(w)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') onSelectWard(w);
              }}
              style={{ cursor: 'pointer' }}
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
