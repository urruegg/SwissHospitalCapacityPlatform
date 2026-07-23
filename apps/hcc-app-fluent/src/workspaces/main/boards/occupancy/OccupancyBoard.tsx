import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Button,
  Card,
  Text,
  Title3,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import type { ResidualPressure, RoleBoardData } from '../../../../journey/RoleBoard';
import type { OccupancyPayload } from '../../../../data/roleboard/occupancy-data';
import { occupancyBoard } from './occupancy-board';
import { HandoffBanner } from '../../../../shell/HandoffBanner';
import { bannerFor, residualFromPrev } from '../../../../journey/handoff-orchestrator';
import { GOLDEN_THREAD_SCOPE } from '../../../../journey/golden-thread';
import { routeInsight } from '../../../../copilot-rail/InsightRouter';
import { useCopilotRail } from '../../../../copilot-rail/rail-context';
import { useMode } from '../../../../context/mode-context';
import { useHospital } from '../../../../context/hospital-context';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalM,
    padding: tokens.spacingHorizontalL,
  },
  channels: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, minmax(0, 1fr))',
    gap: tokens.spacingHorizontalM,
  },
  channel: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
    padding: tokens.spacingHorizontalM,
  },
  insights: {
    display: 'flex',
    gap: tokens.spacingHorizontalS,
    flexWrap: 'wrap',
  },
});

/** Sprint 1 (parity) — Occupancy (ooa) surface: foresight + actionable insights. */
export function OccupancyBoard() {
  const s = useStyles();
  const { t } = useTranslation();
  const { mode } = useMode();
  const { hospital } = useHospital();
  const rail = useCopilotRail();
  const [data, setData] = useState<RoleBoardData<OccupancyPayload> | null>(null);
  const [prev, setPrev] = useState<ResidualPressure | null>(null);

  useEffect(() => {
    const scope = mode === 'demo'
      ? GOLDEN_THREAD_SCOPE
      : { hospital, windowHours: 72, pinned: false };
    let active = true;
    void occupancyBoard.load(scope, mode).then((loaded) => {
      if (active) setData(loaded);
    });
    void residualFromPrev(occupancyBoard.agent, scope, mode).then((residual) => {
      if (active) setPrev(residual);
    });
    return () => {
      active = false;
    };
  }, [mode, hospital]);

  if (!data) return <Text>{t('board.loading')}</Text>;

  const banner = bannerFor(mode, occupancyBoard.agent, prev);
  const insights = occupancyBoard.insights(data);

  return (
    <section className={s.root} data-testid="board-occupancy" aria-label={t('board.occupancy')}>
      <HandoffBanner banner={banner} provenance={data.provenance} />
      <Title3>{t('board.occupancy')}</Title3>
      <div className={s.channels}>
        {data.payload.channels.map((channel) => (
          <Card key={channel.id} className={s.channel}>
            <Text weight="semibold">{channel.label}</Text>
            <Text size={600}>{channel.occupancyPct}%</Text>
            <Text>
              {channel.deltaBeds} {t('board.beds')}
            </Text>
          </Card>
        ))}
      </div>
      <div className={s.insights}>
        {insights.map((insight) => (
          <Button
            key={insight.id}
            appearance="subtle"
            onClick={() =>
              void routeInsight(insight, {
                agent: occupancyBoard.agent,
                openWithContext: rail.openWithContext,
              })
            }
          >
            {insight.label}
          </Button>
        ))}
      </div>
    </section>
  );
}
