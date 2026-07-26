import { useTranslation } from 'react-i18next';
import {
  Badge,
  Body2,
  Caption1,
  Text,
  Tooltip,
  makeStyles,
  mergeClasses,
  tokens,
} from '@fluentui/react-components';
import type { ShiftStatus, StaffMove } from '../../../../data/roleboard/staffing-data';

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
  table: { width: '100%', borderCollapse: 'collapse' },
  th: {
    textAlign: 'left',
    padding: tokens.spacingVerticalXS,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    color: tokens.colorNeutralForeground3,
    fontWeight: tokens.fontWeightSemibold,
  },
  thNum: { textAlign: 'right' },
  td: { padding: tokens.spacingVerticalXS, borderBottom: `1px solid ${tokens.colorNeutralStroke2}` },
  tdNum: { textAlign: 'right' },
  shiftNo: { fontWeight: tokens.fontWeightSemibold },
  shiftTrigger: { borderBottom: `1px dotted ${tokens.colorNeutralStroke1}`, cursor: 'help' },
  shiftCard: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXXS, maxWidth: '260px' },
  shiftHead: { fontWeight: tokens.fontWeightSemibold },
  muted: { color: tokens.colorNeutralForeground3 },
  covers: { color: tokens.colorNeutralForeground2 },
});

/** status → Fluent badge colour: GAP red, FILLED green, PENDING amber, WATCH amber. */
const STATUS_COLOR: Record<ShiftStatus, 'danger' | 'success' | 'warning'> = {
  GAP: 'danger',
  FILLED: 'success',
  PENDING: 'warning',
  WATCH: 'warning',
};

interface CoverageWorklistTableProps {
  moves: StaffMove[];
  onSelectMove: (move: StaffMove) => void;
}

/** Sprint 27 — Coverage worklist: 9-column shift-gap worklist with per-shift coverage status. */
export function CoverageWorklistTable({ moves, onSelectMove }: CoverageWorklistTableProps) {
  const s = useStyles();
  const { t } = useTranslation();
  return (
    <div className={s.wrap}>
      <div className={s.header}>
        <Text className={s.title}>{t('sba.table.title', { count: moves.length })}</Text>
        <Caption1 className={s.hint}>{t('sba.table.hint')}</Caption1>
      </div>
      <table className={s.table}>
        <thead>
          <tr>
            <th className={s.th}>{t('sba.table.shift')}</th>
            <th className={s.th}>{t('sba.table.time')}</th>
            <th className={s.th}>{t('sba.table.fromUnit')}</th>
            <th className={s.th}>{t('sba.table.toUnit')}</th>
            <th className={mergeClasses(s.th, s.thNum)}>{t('sba.table.fte')}</th>
            <th className={s.th}>{t('sba.table.window')}</th>
            <th className={s.th}>{t('sba.table.skill')}</th>
            <th className={s.th}>{t('sba.table.covers')}</th>
            <th className={s.th}>{t('sba.table.status')}</th>
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
                aria-label={`${m.shiftNo} — ${rowLabel}`}
                onClick={() => onSelectMove(m)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') onSelectMove(m);
                  else if (e.key === ' ') { e.preventDefault(); onSelectMove(m); }
                }}
                style={{ cursor: 'pointer' }}
              >
                <td className={mergeClasses(s.td, s.shiftNo)}>
                  <Tooltip
                    withArrow
                    positioning="after"
                    relationship="description"
                    content={
                      <div className={s.shiftCard}>
                        <Body2 className={s.shiftHead}>{m.skill} · {m.window} {m.time}</Body2>
                        <Caption1 className={s.muted}>
                          {m.fromUnit} → {m.toUnit} · {m.fte} FTE · {m.covers}
                        </Caption1>
                      </div>
                    }
                  >
                    <span className={s.shiftTrigger}>{m.shiftNo}</span>
                  </Tooltip>
                </td>
                <td className={s.td}>{m.time}</td>
                <td className={s.td}>{m.fromUnit}</td>
                <td className={s.td}>{m.toUnit}</td>
                <td className={mergeClasses(s.td, s.tdNum)}>{m.fte}</td>
                <td className={s.td}>{m.window}</td>
                <td className={s.td}>{m.skill}</td>
                <td className={mergeClasses(s.td, s.covers)}>{m.covers}</td>
                <td className={s.td}>
                  <Badge appearance="tint" color={STATUS_COLOR[m.status]}>
                    {m.status}
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
