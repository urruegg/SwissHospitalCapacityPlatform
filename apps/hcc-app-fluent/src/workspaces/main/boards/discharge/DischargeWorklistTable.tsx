import { useTranslation } from 'react-i18next';
import { Badge, Caption1, makeStyles, tokens } from '@fluentui/react-components';
import { chipBadgeColor } from '../../../../copilot-rail/reco';
import type { DischargeCandidate, ReadinessStatus } from '../../../../data/roleboard/discharge-data';

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

function readinessBadgeColor(r: ReadinessStatus) {
  if (r === 'READY') return chipBadgeColor('ok');
  if (r === 'BLOCKED') return chipBadgeColor('blocked');
  return chipBadgeColor('pending');
}

interface DischargeWorklistTableProps {
  candidates: DischargeCandidate[];
  onSelectCandidate: (candidate: DischargeCandidate) => void;
}

export function DischargeWorklistTable({ candidates, onSelectCandidate }: DischargeWorklistTableProps) {
  const s = useStyles();
  const { t } = useTranslation();
  return (
    <div className={s.wrap}>
      <Caption1 className={s.hint}>{t('dca.table.hint')}</Caption1>
      <table className={s.table}>
        <thead>
          <tr>
            <th className={s.th}>{t('dca.table.patient')}</th>
            <th className={s.th}>{t('dca.table.ward')}</th>
            <th className={s.th}>{t('dca.table.readiness')}</th>
            <th className={s.th}>{t('dca.table.blocker')}</th>
            <th className={s.th}>{t('dca.table.estFree')}</th>
          </tr>
        </thead>
        <tbody>
          {candidates.map((c) => {
            const rowLabel = t('insight.dischargeExpediteDetail', { ward: c.ward, blocker: c.blocker });
            return (
              <tr
                key={c.id}
                role="button"
                tabIndex={0}
                aria-label={rowLabel}
                onClick={() => onSelectCandidate(c)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') onSelectCandidate(c);
                }}
                style={{ cursor: 'pointer' }}
              >
                <td className={s.td}>{c.patientId}</td>
                <td className={s.td}>{c.ward}</td>
                <td className={s.td}>
                  <Badge appearance="tint" color={readinessBadgeColor(c.readiness)}>
                    {c.readiness}
                  </Badge>
                </td>
                <td className={s.td}>{c.blocker}</td>
                <td className={s.td}>{c.estFreeHours}h</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
