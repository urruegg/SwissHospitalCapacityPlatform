import { useTranslation } from 'react-i18next';
import { Badge, Caption1, Title3, makeStyles, tokens } from '@fluentui/react-components';
import type { AgentId, Provenance } from '../../../../journey/RoleBoard';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: tokens.spacingHorizontalM,
    flexWrap: 'wrap',
  },
  titles: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXXS },
  agentLabel: { color: tokens.colorBrandForeground1, textTransform: 'uppercase', letterSpacing: '0.04em' },
  badges: { display: 'flex', gap: tokens.spacingHorizontalXS, flexWrap: 'wrap' },
});

interface BoardHeaderProps {
  agent: AgentId;
  title: string;
  provenance: Provenance;
  lens: string;
}

export function BoardHeader({ agent, title, provenance, lens }: BoardHeaderProps) {
  const s = useStyles();
  const { t } = useTranslation();
  return (
    <header className={s.root}>
      <div className={s.titles}>
        <Caption1 className={s.agentLabel}>{`MAIN \u00b7 ${agent}`}</Caption1>
        <Title3>{title}</Title3>
      </div>
      <div className={s.badges}>
        <Badge appearance="tint" color={provenance === 'simulated' ? 'warning' : 'success'}>
          {provenance === 'simulated' ? t('badge.simulatedData') : t('badge.liveData')}
        </Badge>
        <Badge appearance="tint" color="brand">
          {t('badge.accessLens', { lens })}
        </Badge>
      </div>
    </header>
  );
}
