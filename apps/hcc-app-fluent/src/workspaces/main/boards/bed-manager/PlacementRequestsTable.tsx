import { useTranslation } from 'react-i18next';
import { Badge, Caption1, makeStyles, tokens } from '@fluentui/react-components';
import type { PlacementRequest, PlacementPriority } from '../../../../data/roleboard/bed-manager-data';

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

function priorityBadgeColor(p: PlacementPriority) {
  if (p === 'HIGH') return 'danger' as const;
  if (p === 'MED') return 'warning' as const;
  return 'informative' as const;
}

interface PlacementRequestsTableProps {
  placements: PlacementRequest[];
  onSelectRequest: (request: PlacementRequest) => void;
}

export function PlacementRequestsTable({ placements, onSelectRequest }: PlacementRequestsTableProps) {
  const s = useStyles();
  const { t } = useTranslation();
  return (
    <div className={s.wrap}>
      <Caption1 className={s.hint}>{t('bmca.table.hint')}</Caption1>
      <table className={s.table}>
        <thead>
          <tr>
            <th className={s.th}>{t('bmca.table.patient')}</th>
            <th className={s.th}>{t('bmca.table.priority')}</th>
            <th className={s.th}>{t('bmca.table.from')}</th>
            <th className={s.th}>{t('bmca.table.to')}</th>
            <th className={s.th}>{t('bmca.table.wait')}</th>
          </tr>
        </thead>
        <tbody>
          {placements.map((r) => {
            const rowLabel = t('insight.placementMove', {
              patientId: r.patientId,
              fromWard: r.fromWard,
              toWard: r.toWard,
            });
            return (
              <tr
                key={r.id}
                role="button"
                tabIndex={0}
                aria-label={rowLabel}
                onClick={() => onSelectRequest(r)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') onSelectRequest(r);
                }}
                style={{ cursor: 'pointer' }}
              >
                <td className={s.td}>{r.patientId}</td>
                <td className={s.td}>
                  <Badge appearance="tint" color={priorityBadgeColor(r.priority)}>
                    {r.priority}
                  </Badge>
                </td>
                <td className={s.td}>{r.fromWard}</td>
                <td className={s.td}>{r.toWard}</td>
                <td className={s.td}>{r.waitMin} min</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
