import { useTranslation } from 'react-i18next';
import {
  Body2,
  Caption1,
  Text,
  Tooltip,
  makeStyles,
  mergeClasses,
  tokens,
} from '@fluentui/react-components';
import type { PlacementRequest, PlacementStatus } from '../../../../data/roleboard/bed-manager-data';
import { RagBadge } from '../occupancy/RagBadge';
import type { ChipTone } from '../../../../copilot-rail/reco';

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
  td: { padding: tokens.spacingVerticalXS, borderBottom: `1px solid ${tokens.colorNeutralStroke2}` },
  req: { fontWeight: tokens.fontWeightSemibold },
  reqTrigger: { borderBottom: `1px dotted ${tokens.colorNeutralStroke1}`, cursor: 'help' },
  reqCard: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXXS, maxWidth: '260px' },
  reqHead: { fontWeight: tokens.fontWeightSemibold },
  muted: { color: tokens.colorNeutralForeground3 },
});

/** STATUS → brand RAG tone: PLACED green (ok), WAITING amber (watch), BLOCKED red (over). */
const STATUS_TONE: Record<PlacementStatus, ChipTone> = {
  PLACED: 'ok',
  WAITING: 'watch',
  BLOCKED: 'over',
};

interface PlacementRequestsTableProps {
  placements: PlacementRequest[];
  onSelectRequest: (request: PlacementRequest) => void;
}

export function PlacementRequestsTable({ placements, onSelectRequest }: PlacementRequestsTableProps) {
  const s = useStyles();
  const { t } = useTranslation();
  return (
    <div className={s.wrap}>
      <div className={s.header}>
        <Text className={s.title}>{t('bmca.table.title', { count: placements.length })}</Text>
        <Caption1 className={s.hint}>{t('bmca.table.hint')}</Caption1>
      </div>
      <table className={s.table}>
        <thead>
          <tr>
            <th className={s.th}>{t('bmca.table.request')}</th>
            <th className={s.th}>{t('bmca.table.source')}</th>
            <th className={s.th}>{t('bmca.table.target')}</th>
            <th className={s.th}>{t('bmca.table.status')}</th>
            <th className={s.th}>{t('bmca.table.barrier')}</th>
          </tr>
        </thead>
        <tbody>
          {placements.map((r) => {
            const rowLabel = t('insight.placementMove', {
              requestNo: r.id,
              source: r.source,
              target: r.target,
            });
            return (
              <tr
                key={r.id}
                role="button"
                tabIndex={0}
                aria-label={rowLabel}
                onClick={() => onSelectRequest(r)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') onSelectRequest(r);
                  else if (e.key === ' ') { e.preventDefault(); onSelectRequest(r); }
                }}
                style={{ cursor: 'pointer' }}
              >
                <td className={mergeClasses(s.td, s.req)}>
                  <Tooltip
                    withArrow
                    positioning="after"
                    relationship="description"
                    content={
                      <div className={s.reqCard}>
                        <Body2 className={s.reqHead}>{r.source} → {r.target}</Body2>
                        <Caption1 className={s.muted}>{r.status}{r.barrier ? ` · ${r.barrier}` : ''}</Caption1>
                      </div>
                    }
                  >
                    <span className={s.reqTrigger}>{r.id}</span>
                  </Tooltip>
                </td>
                <td className={s.td}>{r.source}</td>
                <td className={s.td}>{r.target}</td>
                <td className={s.td}>
                  <RagBadge tone={STATUS_TONE[r.status]}>{r.status}</RagBadge>
                </td>
                <td className={s.td}>{r.barrier ?? '—'}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
