import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Text, makeStyles, tokens } from '@fluentui/react-components';
import { space, radii, elevation } from '../../../../theme/design-system';
import type { ContextInsight, ResidualPressure, RoleBoardData } from '../../../../journey/RoleBoard';
import type { OccupancyPayload } from '../../../../data/roleboard/occupancy-data';
import { occupancyBoard } from './occupancy-board';
import { BoardHeader } from './BoardHeader';
import { WardForecastTable } from './WardForecastTable';
import { CapacityFlowDiagram } from './CapacityFlowDiagram';
import { HandoffBanner } from '../../../../shell/HandoffBanner';
import { bannerFor, residualFromPrev } from '../../../../journey/handoff-orchestrator';
import { GOLDEN_THREAD_SCOPE } from '../../../../journey/golden-thread';
import { routeInsight } from '../../../../copilot-rail/InsightRouter';
import { useCopilotRail } from '../../../../copilot-rail/rail-context';
import { useMode } from '../../../../context/mode-context';
import { useHospital } from '../../../../context/hospital-context';

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: space.l, padding: space.l },
  panel: {
    backgroundColor: tokens.colorNeutralBackground1,
    borderRadius: radii.card,
    boxShadow: elevation.card,
    padding: space.l,
  },
});

/** Sprint 20 (parity) — Occupancy (ooa) surface: BoardHeader + WardForecastTable + CapacityFlowDiagram. */
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
      if (active) {
        setData(loaded);
        rail.showDefault(occupancyBoard.defaultReco(loaded));
      }
    });
    void residualFromPrev(occupancyBoard.agent, scope, mode).then((residual) => {
      if (active) setPrev(residual);
    });
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, hospital]);

  if (!data) return <Text>{t('board.loading', 'Loading...')}</Text>;

  const banner = bannerFor(mode, occupancyBoard.agent, prev);
  const payload = data.payload;

  const route = (insight: ContextInsight) => {
    const reco = occupancyBoard.recoFor(insight, data);
    void routeInsight(insight, reco, { agent: occupancyBoard.agent, openWithReco: rail.openWithReco });
  };

  return (
    <section className={s.root} data-testid="board-occupancy" aria-label={t('board.occupancy')}>
      <HandoffBanner banner={banner} provenance={data.provenance} />
      <BoardHeader agent={occupancyBoard.agent} title={t('board.occupancy')} provenance={data.provenance} lens="Bed Ops" />
      <div className={s.panel}>
        <WardForecastTable
          wards={payload.wards}
          onSelectWard={(w) => route({ id: w.recoId, label: w.label, context: { channel: w.id, occupancyPct: w.forecastPct } })}
        />
      </div>
      <div className={s.panel}>
        <CapacityFlowDiagram
          channels={payload.channels}
          streams={payload.streams}
          capacity={payload.capacity}
          onSelectStream={(st) => route({ id: st.recoId, label: st.label, context: { stream: st.id, level: st.levelLabel } })}
          onSelectGap={() => route({ id: 'site-gap', label: t('ooa.gap.label'), context: { gapBeds: payload.capacity.gapBeds } })}
        />
      </div>
    </section>
  );
}
