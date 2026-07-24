import { useTranslation } from 'react-i18next';
import { Caption1, makeStyles, tokens } from '@fluentui/react-components';
import type { StaffMove } from '../../../../data/roleboard/staffing-data';

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

interface CoverageWorklistTableProps {
  moves: StaffMove[];
  onSelectMove: (move: StaffMove) => void;
}

export function CoverageWorklistTable({ moves, onSelectMove }: CoverageWorklistTableProps) {
  const s = useStyles();
  const { t } = useTranslation();
  return (
    <div className={s.wrap}>
      <Caption1 className={s.hint}>{t('sba.table.hint')}</Caption1>
      <table className={s.table}>
        <thead>
          <tr>
            <th className={s.th}>{t('sba.table.role')}</th>
            <th className={s.th}>{t('sba.table.fromUnit')}</th>
            <th className={s.th}>{t('sba.table.toUnit')}</th>
            <th className={s.th}>{t('sba.table.fte')}</th>
            <th className={s.th}>{t('sba.table.shiftGap')}</th>
          </tr>
        </thead>
        <tbody>
          {moves.map((m) => {
            const rowLabel = t('insight.staffShift', { role: m.role, fromUnit: m.fromUnit, toUnit: m.toUnit });
            return (
              <tr
                key={m.id}
                role="button"
                tabIndex={0}
                aria-label={rowLabel}
                onClick={() => onSelectMove(m)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') onSelectMove(m);
                  else if (e.key === ' ') { e.preventDefault(); onSelectMove(m); }
                }}
                style={{ cursor: 'pointer' }}
              >
                <td className={s.td}>{m.role}</td>
                <td className={s.td}>{m.fromUnit}</td>
                <td className={s.td}>{m.toUnit}</td>
                <td className={s.td}>{m.fte}</td>
                <td className={s.td}>{m.shiftGap}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
