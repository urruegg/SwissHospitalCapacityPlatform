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
import type { OrAction, OrCase } from '../../../../data/roleboard/or-steering-data';

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
  caseNo: { fontWeight: tokens.fontWeightSemibold },
  caseTrigger: { borderBottom: `1px dotted ${tokens.colorNeutralStroke1}`, cursor: 'help' },
  caseCard: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXXS, maxWidth: '260px' },
  caseHead: { fontWeight: tokens.fontWeightSemibold },
  muted: { color: tokens.colorNeutralForeground3 },
  window: { color: tokens.colorNeutralForeground3 },
});

/** action → Fluent badge colour: DEFER amber, RESLOT blue, REDIRECT green, PROCEED red. */
const ACTION_COLOR: Record<OrAction, 'warning' | 'informative' | 'success' | 'danger'> = {
  DEFER: 'warning',
  RESLOT: 'informative',
  REDIRECT: 'success',
  PROCEED: 'danger',
};

interface OrCaseScheduleTableProps {
  cases: OrCase[];
  onSelectCase: (orCase: OrCase) => void;
}

/** Sprint 27 — Elective OR schedule (right pane): 8-column worklist with per-case steering action. */
export function OrCaseScheduleTable({ cases, onSelectCase }: OrCaseScheduleTableProps) {
  const s = useStyles();
  const { t } = useTranslation();
  return (
    <div className={s.wrap}>
      <div className={s.header}>
        <Text className={s.title}>{t('orsa.table.title', { count: cases.length })}</Text>
        <Caption1 className={s.hint}>{t('orsa.table.hint')}</Caption1>
      </div>
      <table className={s.table}>
        <thead>
          <tr>
            <th className={s.th}>{t('orsa.table.case')}</th>
            <th className={s.th}>{t('orsa.table.specialty')}</th>
            <th className={s.th}>{t('orsa.table.slot')}</th>
            <th className={s.th}>{t('orsa.table.postOp')}</th>
            <th className={mergeClasses(s.th, s.thNum)}>{t('orsa.table.bedsImpact')}</th>
            <th className={mergeClasses(s.th, s.thNum)}>{t('orsa.table.bedsProtected')}</th>
            <th className={s.th}>{t('orsa.table.action')}</th>
            <th className={s.th}>{t('orsa.table.window')}</th>
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
                aria-label={`${c.caseNo} — ${rowLabel}`}
                onClick={() => onSelectCase(c)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') onSelectCase(c);
                  else if (e.key === ' ') { e.preventDefault(); onSelectCase(c); }
                }}
                style={{ cursor: 'pointer' }}
              >
                <td className={mergeClasses(s.td, s.caseNo)}>
                  <Tooltip
                    withArrow
                    positioning="after"
                    relationship="description"
                    content={
                      <div className={s.caseCard}>
                        <Body2 className={s.caseHead}>{c.specialty} · {c.slot}</Body2>
                        <Caption1 className={s.muted}>
                          {c.action} · {c.window} · {t('orsa.table.postOp')}: {c.postOp}
                        </Caption1>
                      </div>
                    }
                  >
                    <span className={s.caseTrigger}>{c.caseNo}</span>
                  </Tooltip>
                </td>
                <td className={s.td}>{c.specialty}</td>
                <td className={s.td}>{c.slot}</td>
                <td className={s.td}>{c.postOp}</td>
                <td className={mergeClasses(s.td, s.tdNum)}>{c.bedsImpact}</td>
                <td className={mergeClasses(s.td, s.tdNum)}>{c.bedsProtected}</td>
                <td className={s.td}>
                  <Badge appearance="tint" color={ACTION_COLOR[c.action]}>
                    {c.action}
                  </Badge>
                </td>
                <td className={mergeClasses(s.td, s.window)}>{c.window}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
