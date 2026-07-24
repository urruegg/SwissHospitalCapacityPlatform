import { useTranslation } from 'react-i18next';
import { Badge, Button, Caption1, makeStyles, tokens } from '@fluentui/react-components';
import type { CapacityBarrier } from '../../../../data/roleboard/discharge-data';

const useStyles = makeStyles({
  wrap: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXS },
  header: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: tokens.spacingHorizontalS },
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
  rankCell: { width: '2.5rem', textAlign: 'center' },
  impactCell: { width: '4rem', textAlign: 'right' },
});

interface DischargeBarriersBoardProps {
  barriers: CapacityBarrier[];
  onSelectBarrier: (barrier: CapacityBarrier) => void;
  onAutoSequence?: () => void;
}

export function DischargeBarriersBoard({ barriers, onSelectBarrier, onAutoSequence }: DischargeBarriersBoardProps) {
  const s = useStyles();
  const { t } = useTranslation();

  const sorted = [...barriers].sort((a, b) => b.bedImpact - a.bedImpact || a.id.localeCompare(b.id));

  return (
    <div className={s.wrap}>
      <div className={s.header}>
        <Caption1 className={s.hint}>{t('dca.barriers.hint')}</Caption1>
        <Button appearance="primary" size="small" onClick={onAutoSequence}>
          {t('dca.barriers.cta')}
        </Button>
      </div>
      <table className={s.table}>
        <thead>
          <tr>
            <th className={`${s.th} ${s.rankCell}`}>{t('dca.barriers.rank')}</th>
            <th className={s.th}>{t('dca.barriers.label')}</th>
            <th className={`${s.th} ${s.impactCell}`}>{t('dca.barriers.bedImpact')}</th>
            <th className={s.th}>{t('dca.barriers.detail')}</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((b, idx) => (
            <tr
              key={b.id}
              role="button"
              tabIndex={0}
              aria-label={b.label}
              onClick={() => onSelectBarrier(b)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') onSelectBarrier(b);
              }}
              style={{ cursor: 'pointer' }}
            >
              <td className={`${s.td} ${s.rankCell}`}>
                <Badge appearance="tint" color="brand" shape="circular">
                  {idx + 1}
                </Badge>
              </td>
              <td className={s.td}>{b.label}</td>
              <td className={`${s.td} ${s.impactCell}`}>{b.bedImpact}</td>
              <td className={s.td}>{b.detail}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
