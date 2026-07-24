import { useTranslation } from 'react-i18next';
import {
  Badge,
  Body1,
  Caption1,
  Card,
  CardHeader,
  ProgressBar,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import type { BedManagerPayload, SlaRisk } from '../../../../data/roleboard/bed-manager-data';

const useStyles = makeStyles({
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
    gap: tokens.spacingHorizontalM,
  },
  card: { padding: tokens.spacingHorizontalM },
  progressWrap: { marginTop: tokens.spacingVerticalXS },
  label: { color: tokens.colorNeutralForeground3 },
});

function slaRiskColor(risk: SlaRisk) {
  if (risk === 'HIGH') return 'danger' as const;
  if (risk === 'MED') return 'warning' as const;
  if (risk === 'LOW') return 'informative' as const;
  return 'success' as const;
}

interface BedStateKpisProps {
  payload: Pick<BedManagerPayload, 'utilPct' | 'freeBeds' | 'targetFree' | 'slaRisk'>;
}

export function BedStateKpis({ payload }: BedStateKpisProps) {
  const s = useStyles();
  const { t } = useTranslation();
  return (
    <div className={s.grid}>
      {/* Utilisation tile with progress bar */}
      <Card className={s.card} appearance="filled-alternative">
        <CardHeader
          header={<Body1><b>{payload.utilPct}%</b></Body1>}
          description={<Caption1 className={s.label}>{t('bmca.kpis.utilPct')}</Caption1>}
        />
        <div className={s.progressWrap}>
          <ProgressBar value={payload.utilPct / 100} />
        </div>
      </Card>

      {/* Free beds tile */}
      <Card className={s.card} appearance="filled-alternative">
        <CardHeader
          header={<Body1><b>{payload.freeBeds}</b></Body1>}
          description={<Caption1 className={s.label}>{t('bmca.kpis.freeBeds')}</Caption1>}
        />
      </Card>

      {/* Target free tile */}
      <Card className={s.card} appearance="filled-alternative">
        <CardHeader
          header={<Body1><b>{payload.targetFree}</b></Body1>}
          description={<Caption1 className={s.label}>{t('bmca.kpis.targetFree')}</Caption1>}
        />
      </Card>

      {/* SLA risk tile */}
      <Card className={s.card} appearance="filled-alternative">
        <CardHeader
          header={
            <Badge appearance="tint" color={slaRiskColor(payload.slaRisk)}>
              {payload.slaRisk}
            </Badge>
          }
          description={<Caption1 className={s.label}>{t('bmca.kpis.slaRisk')}</Caption1>}
        />
      </Card>
    </div>
  );
}
