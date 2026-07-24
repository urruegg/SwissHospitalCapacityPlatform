import { useTranslation } from 'react-i18next';
import { Badge, Caption1, makeStyles, tokens } from '@fluentui/react-components';
import { chipBadgeColor, impactBadgeColor } from '../../../../copilot-rail/reco';
import type { ExternalSignal } from '../../../../data/roleboard/crisis-data';

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

interface CrisisSignalsTableProps {
  signals: ExternalSignal[];
  onSelectSignal: (signal: ExternalSignal) => void;
}

/** Sprint 20 M5 (parity) — DC-EXT-SIGNAL-v1 Trust-A signals table. */
export function CrisisSignalsTable({ signals, onSelectSignal }: CrisisSignalsTableProps) {
  const s = useStyles();
  const { t } = useTranslation();

  return (
    <div className={s.wrap}>
      <Caption1 className={s.hint}>{t('csa.signals.hint')}</Caption1>
      <table className={s.table}>
        <thead>
          <tr>
            <th className={s.th}>{t('csa.signals.source')}</th>
            <th className={s.th}>{t('csa.signals.feed')}</th>
            <th className={s.th}>{t('csa.signals.status')}</th>
            <th className={s.th}>{t('csa.signals.trustClass')}</th>
            <th className={s.th}>{t('csa.signals.certainty')}</th>
            <th className={s.th}>{t('csa.signals.probability')}</th>
          </tr>
        </thead>
        <tbody>
          {signals.map((signal) => {
            const rowLabel = `${signal.source}: ${signal.feed}`;
            const isFiltered = signal.filtered === true;
            return (
              <tr
                key={signal.id}
                role="button"
                tabIndex={0}
                aria-label={rowLabel}
                onClick={() => onSelectSignal(signal)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') onSelectSignal(signal);
                  if (e.key === ' ') { e.preventDefault(); onSelectSignal(signal); }
                }}
                style={{ cursor: 'pointer' }}
              >
                <td className={s.td}>{signal.source}</td>
                <td className={s.td}>{signal.feed}</td>
                <td className={s.td}>
                  <Badge
                    appearance="tint"
                    color={isFiltered ? chipBadgeColor('signal') : impactBadgeColor('status')}
                  >
                    {isFiltered ? t('csa.status.filtered') : t('csa.status.nominal')}
                  </Badge>
                </td>
                <td className={s.td}>
                  <Badge appearance="tint" color={impactBadgeColor('trust')}>
                    {signal.trustClass}
                  </Badge>
                </td>
                <td className={s.td}>{signal.certainty}</td>
                <td className={s.td}>{signal.probability}%</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
