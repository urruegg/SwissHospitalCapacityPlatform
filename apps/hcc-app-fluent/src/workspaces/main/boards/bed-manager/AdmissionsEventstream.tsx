import { useTranslation } from 'react-i18next';
import { Badge, Body1, Caption1, makeStyles, tokens } from '@fluentui/react-components';

const useStyles = makeStyles({
  wrap: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXS },
  hint: { color: tokens.colorNeutralForeground3 },
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
    padding: 0,
    margin: 0,
    listStyle: 'none',
  },
  item: {
    display: 'flex',
    gap: tokens.spacingHorizontalS,
    alignItems: 'center',
    padding: `${tokens.spacingVerticalXXS} 0`,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  ts: { color: tokens.colorNeutralForeground3, flexShrink: 0 },
});

interface AdmissionsEventstreamProps {
  admissions: { id: string; ts: string; message: string; kind: 'admit' | 'discharge' }[];
}

export function AdmissionsEventstream({ admissions }: AdmissionsEventstreamProps) {
  const s = useStyles();
  const { t } = useTranslation();
  return (
    <div className={s.wrap}>
      <Caption1 className={s.hint}>{t('bmca.stream.hint')}</Caption1>
      <ul className={s.list} aria-label={t('bmca.stream.title')}>
        {admissions.map((ev) => (
          <li key={ev.id} className={s.item}>
            <Caption1 className={s.ts}>{ev.ts}</Caption1>
            <Badge
              appearance="tint"
              color={ev.kind === 'admit' ? 'informative' : 'success'}
            >
              {ev.kind}
            </Badge>
            <Body1>{ev.message}</Body1>
          </li>
        ))}
      </ul>
    </div>
  );
}
