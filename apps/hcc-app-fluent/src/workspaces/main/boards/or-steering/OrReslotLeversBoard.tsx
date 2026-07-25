import { useTranslation } from 'react-i18next';
import { Badge, Button, Caption1, makeStyles, tokens } from '@fluentui/react-components';
import { sortReslotLevers } from '../../../../data/roleboard/or-steering-data';
import type { ReslotLever } from '../../../../data/roleboard/or-steering-data';

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
  bedsCell: { width: '4rem', textAlign: 'right' },
});

interface OrReslotLeversBoardProps {
  levers: ReslotLever[];
  onSelectLever: (lever: ReslotLever) => void;
  onAutoSequence?: () => void;
}

export function OrReslotLeversBoard({ levers, onSelectLever, onAutoSequence }: OrReslotLeversBoardProps) {
  const s = useStyles();
  const { t } = useTranslation();

  const sorted = sortReslotLevers(levers);

  return (
    <div className={s.wrap}>
      <div className={s.header}>
        <Caption1 className={s.hint}>{t('orsa.levers.hint')}</Caption1>
        <Button appearance="primary" size="small" onClick={onAutoSequence}>
          {t('orsa.levers.cta')}
        </Button>
      </div>
      <table className={s.table}>
        <thead>
          <tr>
            <th className={`${s.th} ${s.rankCell}`}>{t('orsa.levers.rank')}</th>
            <th className={s.th}>{t('orsa.levers.label')}</th>
            <th className={`${s.th} ${s.bedsCell}`}>{t('orsa.levers.bedsProtected')}</th>
            <th className={s.th}>{t('orsa.levers.detail')}</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((lever, idx) => (
            <tr
              key={lever.id}
              role="button"
              tabIndex={0}
              aria-label={lever.label}
              onClick={() => onSelectLever(lever)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') onSelectLever(lever);
              }}
              style={{ cursor: 'pointer' }}
            >
              <td className={`${s.td} ${s.rankCell}`}>
                <Badge appearance="tint" color="brand" shape="circular">
                  {idx + 1}
                </Badge>
              </td>
              <td className={s.td}>{lever.label}</td>
              <td className={`${s.td} ${s.bedsCell}`}>{lever.bedsProtected}</td>
              <td className={s.td}>{lever.detail}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
