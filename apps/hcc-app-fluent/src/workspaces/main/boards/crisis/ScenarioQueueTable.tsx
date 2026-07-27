import { useTranslation } from 'react-i18next';
import { Badge, Caption1, Text, makeStyles, mergeClasses, tokens } from '@fluentui/react-components';
import type { QueueResult, QueuedScenario } from '../../../../data/roleboard/crisis-data';
import { ragColors } from '../../../../theme/curavias-theme';

/** result → Fluent badge colour. STRESS-MAX renders subtle/neutral. */
const RESULT_COLOR: Record<QueueResult, 'danger' | 'warning' | 'success' | 'subtle'> = {
  SIMULATE: 'danger',
  MODELLED: 'warning',
  WATCH: 'warning',
  HOLDS: 'success',
  'STRESS-MAX': 'subtle',
};

function impactColor(tone: QueuedScenario['impactTone']): string | undefined {
  return tone === 'over' ? ragColors.bad : tone === 'watch' ? ragColors.neutral : tone === 'ok' ? ragColors.good : tokens.colorNeutralForeground4;
}

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
  scenario: { fontWeight: tokens.fontWeightSemibold },
  trigger: { color: tokens.colorNeutralForeground2 },
  impact: { fontWeight: tokens.fontWeightSemibold },
});

interface ScenarioQueueTableProps {
  queue: QueuedScenario[];
  onSelectQueued: (row: QueuedScenario) => void;
}

/** Sprint 27 — Scenario queue (middle lane): shocks pressure-tested with trigger, impact, likelihood, result. */
export function ScenarioQueueTable({ queue, onSelectQueued }: ScenarioQueueTableProps) {
  const s = useStyles();
  const { t } = useTranslation();
  return (
    <div className={s.wrap}>
      <div className={s.header}>
        <Text className={s.title}>{t('csa.queue.title', { count: queue.length })}</Text>
        <Caption1 className={s.hint}>{t('csa.queue.hint')}</Caption1>
      </div>
      <table className={s.table}>
        <thead>
          <tr>
            <th className={s.th}>{t('csa.queue.scenario')}</th>
            <th className={s.th}>{t('csa.queue.trigger')}</th>
            <th className={s.th}>{t('csa.queue.impact')}</th>
            <th className={s.th}>{t('csa.queue.likelihood')}</th>
            <th className={s.th}>{t('csa.queue.result')}</th>
          </tr>
        </thead>
        <tbody>
          {queue.map((row) => (
            <tr
              key={row.id}
              role="button"
              tabIndex={0}
              aria-label={`${row.id} — ${row.name}`}
              onClick={() => onSelectQueued(row)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') onSelectQueued(row);
                else if (e.key === ' ') { e.preventDefault(); onSelectQueued(row); }
              }}
              style={{ cursor: 'pointer' }}
            >
              <td className={mergeClasses(s.td, s.scenario)}>{row.id} · {row.name}</td>
              <td className={mergeClasses(s.td, s.trigger)}>{row.trigger}</td>
              <td className={mergeClasses(s.td, s.impact)} style={{ color: impactColor(row.impactTone) }}>{row.impact}</td>
              <td className={s.td}>{row.likelihood}</td>
              <td className={s.td}>
                <Badge appearance="tint" color={RESULT_COLOR[row.result]}>
                  {row.result}
                </Badge>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
