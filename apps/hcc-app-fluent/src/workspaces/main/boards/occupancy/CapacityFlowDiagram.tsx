import { useTranslation } from 'react-i18next';
import { Badge, Body1, Caption1, Card, Text, makeStyles, tokens } from '@fluentui/react-components';
import { ArrowRightRegular } from '@fluentui/react-icons';
import { chipBadgeColor } from '../../../../copilot-rail/reco';
import { SignalsPanel } from './SignalsPanel';
import type {
  BoardSignal,
  CapacitySummary,
  SignalChannel,
  SpecStream,
} from '../../../../data/roleboard/occupancy-data';

const useStyles = makeStyles({
  hint: { color: tokens.colorNeutralForeground3, marginBottom: tokens.spacingVerticalXS },
  flow: {
    display: 'grid',
    gridTemplateColumns: '1fr auto 1fr auto 1fr',
    alignItems: 'stretch',
    gap: tokens.spacingHorizontalS,
  },
  col: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXS },
  colHead: { color: tokens.colorNeutralForeground3, fontWeight: tokens.fontWeightSemibold },
  arrow: { display: 'flex', alignItems: 'center', color: tokens.colorNeutralForeground3 },
  channel: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalXS,
    padding: tokens.spacingVerticalXS,
    borderRadius: tokens.borderRadiusMedium,
    backgroundColor: tokens.colorNeutralBackground2,
  },
  streamBtn: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXXS,
    padding: tokens.spacingHorizontalS,
    textAlign: 'left',
    cursor: 'pointer',
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    borderRadius: tokens.borderRadiusMedium,
    background: tokens.colorNeutralBackground1,
    font: 'inherit',
  },
  streamHead: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: tokens.spacingHorizontalXS },
  fedBy: { color: tokens.colorNeutralForeground3 },
  output: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalXXS, padding: tokens.spacingHorizontalS },
  gapBtn: {
    padding: tokens.spacingHorizontalS,
    textAlign: 'left',
    cursor: 'pointer',
    border: `1px solid ${tokens.colorPaletteRedBorder2}`,
    borderRadius: tokens.borderRadiusMedium,
    background: tokens.colorNeutralBackground1,
    font: 'inherit',
  },
});

interface CapacityFlowDiagramProps {
  signals: BoardSignal[];
  channels: SignalChannel[];
  streams: SpecStream[];
  capacity: CapacitySummary;
  onSelectStream: (stream: SpecStream) => void;
  onSelectGap: () => void;
}

export function CapacityFlowDiagram({
  signals,
  channels,
  streams,
  capacity,
  onSelectStream,
  onSelectGap,
}: CapacityFlowDiagramProps) {
  const s = useStyles();
  const { t } = useTranslation();
  const channelLabel = (id: string) => channels.find((c) => c.id === id)?.label ?? id;
  return (
    <div>
      <Caption1 className={s.hint}>{t('ooa.flow.hint')}</Caption1>
      <div className={s.flow}>
        <div className={s.col}>
          <SignalsPanel signals={signals} />
        </div>
        <div className={s.arrow}><ArrowRightRegular /></div>
        <div className={s.col}>
          <Caption1 className={s.colHead}>{t('ooa.flow.streams')}</Caption1>
          {streams.map((st) => (
            <button
              key={st.id}
              type="button"
              className={s.streamBtn}
              aria-label={st.label}
              onClick={() => onSelectStream(st)}
            >
              <span className={s.streamHead}>
                <Body1>{st.label}</Body1>
                <Badge appearance="filled" color={chipBadgeColor(st.level)}>{st.levelLabel}</Badge>
              </span>
              <Caption1 className={s.fedBy}>
                {t('ooa.flow.fedBy', { channels: st.fedBy.map(channelLabel).join(' \u00b7 ') })}
              </Caption1>
            </button>
          ))}
        </div>
        <div className={s.arrow}><ArrowRightRegular /></div>
        <div className={s.col}>
          <Caption1 className={s.colHead}>{t('ooa.flow.recommendation', 'Recommendation')}</Caption1>
          <Card className={s.output}>
            <Caption1>{t('ooa.flow.current')}</Caption1>
            <Text weight="semibold">
              {`${capacity.currentBeds} / ${capacity.currentTotal} \u00b7 ${capacity.currentPct}%`}
            </Text>
          </Card>
          <Card className={s.output}>
            <Caption1>{t('ooa.flow.forecast72')}</Caption1>
            <Text weight="semibold">
              {`${capacity.forecastBeds} / ${capacity.forecastTotal} \u00b7 ${capacity.forecastPct}%`}
            </Text>
          </Card>
          <button
            type="button"
            className={s.gapBtn}
            aria-label={t('ooa.gap.aria')}
            onClick={onSelectGap}
          >
            <Body1>{t('ooa.gap.card', { beds: Math.abs(capacity.gapBeds) })}</Body1>
          </button>
        </div>
      </div>
    </div>
  );
}
