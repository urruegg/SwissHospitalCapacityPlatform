import { useTranslation } from 'react-i18next';
import { Badge, Button, Caption1, makeStyles, tokens } from '@fluentui/react-components';
import type { PlacementBarrier } from '../../../../data/roleboard/bed-manager-data';
import { sortBarriers } from '../../../../data/roleboard/bed-manager-data';

const useStyles = makeStyles({
  wrap: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXS },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    gap: tokens.spacingHorizontalS,
  },
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

interface PlacementBarriersBoardProps {
  barriers: PlacementBarrier[];
  onSelectBarrier: (barrier: PlacementBarrier) => void;
  onAutoSequence?: () => void;
}

export function PlacementBarriersBoard({ barriers, onSelectBarrier, onAutoSequence }: PlacementBarriersBoardProps) {
  const s = useStyles();
  const { t } = useTranslation();

  const sorted = sortBarriers(barriers);

  return (
    <div className={s.wrap}>
      <div className={s.header}>
        <Caption1 className={s.hint}>{t('bmca.barriers.hint')}</Caption1>
        <Button appearance="primary" size="small" onClick={onAutoSequence}>
          {t('bmca.barriers.cta')}
        </Button>
      </div>
      <table className={s.table}>
        <thead>
          <tr>
            <th className={`${s.th} ${s.rankCell}`}>{t('bmca.barriers.rank')}</th>
            <th className={s.th}>{t('bmca.barriers.label')}</th>
            <th className={`${s.th} ${s.impactCell}`}>{t('bmca.barriers.bedImpact')}</th>
            <th className={s.th}>{t('bmca.barriers.detail')}</th>
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
