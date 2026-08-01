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
import type { DischargeCandidate, ReadinessStatus } from '../../../../data/roleboard/discharge-data';
import { ragColors } from '../../../../theme/curavias-theme';

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
  patient: { fontWeight: tokens.fontWeightSemibold },
  patientCell: { display: 'flex', alignItems: 'center', gap: tokens.spacingHorizontalXS, flexWrap: 'wrap' },
  patientTrigger: { borderBottom: `1px dotted ${tokens.colorNeutralStroke1}`, cursor: 'help' },
  patientCard: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXXS, maxWidth: '260px' },
  patientHead: { fontWeight: tokens.fontWeightSemibold },
  muted: { color: tokens.colorNeutralForeground3 },
});

/** readiness → Fluent badge colour: READY green, BLOCKED red, PENDING amber. */
const READINESS_COLOR: Record<ReadinessStatus, 'success' | 'danger' | 'warning'> = {
  READY: 'success',
  BLOCKED: 'danger',
  PENDING: 'warning',
};

interface DischargeWorklistTableProps {
  candidates: DischargeCandidate[];
  onSelectCandidate: (candidate: DischargeCandidate) => void;
}

/** Sprint 27 — Discharge worklist: PATIENT / WARD / READINESS / BARRIER / EST. FREE, anonymised. */
export function DischargeWorklistTable({ candidates, onSelectCandidate }: DischargeWorklistTableProps) {
  const s = useStyles();
  const { t } = useTranslation();
  return (
    <div className={s.wrap}>
      <div className={s.header}>
        <Text className={s.title}>{t('dca.table.title', { count: candidates.length })}</Text>
        <Caption1 className={s.hint}>{t('dca.table.hint')}</Caption1>
      </div>
      <table className={s.table}>
        <thead>
          <tr>
            <th className={s.th}>{t('dca.table.patient')}</th>
            <th className={s.th}>{t('dca.table.ward')}</th>
            <th className={s.th}>{t('dca.table.readiness')}</th>
            <th className={s.th}>{t('dca.table.barrier')}</th>
            <th className={mergeClasses(s.th, s.thNum)}>{t('dca.table.estFree')}</th>
          </tr>
        </thead>
        <tbody>
          {candidates.map((c) => {
            const rowLabel = t('insight.dischargeExpediteDetail', { ward: c.ward, blocker: c.blocker });
            const ready = c.readiness === 'READY';
            return (
              <tr
                key={c.id}
                role="button"
                tabIndex={0}
                aria-label={`${c.patientId} — ${rowLabel}`}
                onClick={() => onSelectCandidate(c)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') onSelectCandidate(c);
                  else if (e.key === ' ') { e.preventDefault(); onSelectCandidate(c); }
                }}
                style={{ cursor: 'pointer' }}
              >
                <td className={mergeClasses(s.td, s.patient)}>
                  <span className={s.patientCell}>
                    <Tooltip
                      withArrow
                      positioning="after"
                      relationship="description"
                      content={
                        <div className={s.patientCard}>
                          <Body2 className={s.patientHead}>{c.ward} · {c.readiness}</Body2>
                          <Caption1 className={s.muted}>
                            {c.blocker || t('dca.table.noBarrier')} · {t('dca.table.estFree')}: {c.estFreeLabel}
                          </Caption1>
                        </div>
                      }
                    >
                      <span className={s.patientTrigger}>{c.patientId}</span>
                    </Tooltip>
                    {c.provenance && (
                      <Badge
                        appearance="outline"
                        size="small"
                        color={c.provenance === 'live' ? 'success' : 'informative'}
                        aria-label={t('dca.table.provenance', { source: c.provenance })}
                      >
                        {t(`dca.table.source.${c.provenance}`)}
                      </Badge>
                    )}
                  </span>
                </td>
                <td className={s.td}>{c.ward}</td>
                <td className={s.td}>
                  <Badge appearance="tint" color={READINESS_COLOR[c.readiness]}>
                    {c.readiness}
                  </Badge>
                </td>
                <td className={s.td}>{c.blocker || t('dca.table.noBarrier')}</td>
                <td
                  className={mergeClasses(s.td, s.tdNum)}
                  style={ready ? { color: ragColors.good, fontWeight: tokens.fontWeightSemibold } : undefined}
                >
                  {c.estFreeLabel}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
