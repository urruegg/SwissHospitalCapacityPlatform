import { useTranslation } from 'react-i18next';
import { Badge, Caption1, makeStyles, tokens } from '@fluentui/react-components';
import { chipBadgeColor } from '../../../../copilot-rail/reco';
import type { OrCase } from '../../../../data/roleboard/or-steering-data';

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

interface OrCaseScheduleTableProps {
  cases: OrCase[];
  onSelectCase: (orCase: OrCase) => void;
}

export function OrCaseScheduleTable({ cases, onSelectCase }: OrCaseScheduleTableProps) {
  const s = useStyles();
  const { t } = useTranslation();
  return (
    <div className={s.wrap}>
      <Caption1 className={s.hint}>{t('orsa.table.hint')}</Caption1>
      <table className={s.table}>
        <thead>
          <tr>
            <th className={s.th}>{t('orsa.table.specialty')}</th>
            <th className={s.th}>{t('orsa.table.slot')}</th>
            <th className={s.th}>{t('orsa.table.bedsImpact')}</th>
            <th className={s.th}>{t('orsa.table.bedsProtected')}</th>
            <th className={s.th}>{t('orsa.table.deferable')}</th>
          </tr>
        </thead>
        <tbody>
          {cases.map((c) => {
            const rowLabel = t('insight.orDefer', { specialty: c.specialty });
            return (
              <tr
                key={c.id}
                role="button"
                tabIndex={0}
                aria-label={rowLabel}
                onClick={() => onSelectCase(c)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') onSelectCase(c);
                }}
                style={{ cursor: 'pointer' }}
              >
                <td className={s.td}>{c.specialty}</td>
                <td className={s.td}>{c.slot}</td>
                <td className={s.td}>{c.bedsImpact}</td>
                <td className={s.td}>{c.bedsProtected}</td>
                <td className={s.td}>
                  <Badge
                    appearance="tint"
                    color={chipBadgeColor(c.deferable ? 'ok' : 'pending')}
                  >
                    {c.deferable ? t('orsa.table.yes') : t('orsa.table.no')}
                  </Badge>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
