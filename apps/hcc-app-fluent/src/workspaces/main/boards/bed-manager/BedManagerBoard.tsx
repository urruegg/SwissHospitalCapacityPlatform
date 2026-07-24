import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Body1,
  Card,
  CardHeader,
  Caption1,
  Text,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import type { ContextInsight, ResidualPressure, RoleBoardData } from '../../../../journey/RoleBoard';
import type {
  BedManagerPayload,
  PlacementRequest,
  PlacementBarrier,
} from '../../../../data/roleboard/bed-manager-data';
import { sortBarriers } from '../../../../data/roleboard/bed-manager-data';
import { bedManagerBoard } from './bed-manager-board';
import { BoardHeader } from '../occupancy/BoardHeader';
import { PlacementRequestsTable } from './PlacementRequestsTable';
import { PlacementBarriersBoard } from './PlacementBarriersBoard';
import { BedStateKpis } from './BedStateKpis';
import { AdmissionsEventstream } from './AdmissionsEventstream';
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
    gap: tokens.spacingVerticalL,
    padding: tokens.spacingHorizontalL,
  },
  pbiCard: { padding: tokens.spacingHorizontalM },
});

/** Sprint 20 (parity) — BedManager (bmca) surface: BoardHeader + placement worklist + barriers + KPIs + eventstream + Power BI embed. */
export function BedManagerBoard() {
  const s = useStyles();
  const { t } = useTranslation();
  const { mode } = useMode();
  const { hospital } = useHospital();
  const rail = useCopilotRail();
  const [data, setData] = useState<RoleBoardData<BedManagerPayload> | null>(null);
  const [prev, setPrev] = useState<ResidualPressure | null>(null);

  useEffect(() => {
    const scope =
      mode === 'demo'
        ? GOLDEN_THREAD_SCOPE
        : { hospital, windowHours: 72, pinned: false };
    let active = true;
    void bedManagerBoard.load(scope, mode).then((loaded) => {
      if (active) {
        setData(loaded);
        rail.showDefault(bedManagerBoard.defaultReco(loaded));
      }
    });
    void residualFromPrev(bedManagerBoard.agent, scope, mode).then((residual) => {
      if (active) setPrev(residual);
    });
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, hospital]);

  if (!data) return <Text>{t('board.loading', 'Loading...')}</Text>;

  const banner = bannerFor(mode, bedManagerBoard.agent, prev);
  const payload = data.payload;

  const route = (insight: ContextInsight) => {
    const reco = bedManagerBoard.recoFor(insight, data);
    void routeInsight(insight, reco, {
      agent: bedManagerBoard.agent,
      openWithReco: rail.openWithReco,
    });
  };

  const onSelectRequest = (r: PlacementRequest) => {
    route({
      id: r.recoId,
      label: t('insight.placementMove', {
        patientId: r.patientId,
        fromWard: r.fromWard,
        toWard: r.toWard,
      }),
      context: {
        placement: r.id,
        patientId: r.patientId,
        fromWard: r.fromWard,
        toWard: r.toWard,
      },
    });
  };

  const onSelectBarrier = (b: PlacementBarrier) => {
    route({ id: b.recoId, label: b.label, context: { barrier: b.id, bedImpact: b.bedImpact } });
  };

  const onAutoSequence = () => {
    const top = sortBarriers(payload.barriers)[0];
    if (top) onSelectBarrier(top);
  };

  return (
    <section
      className={s.root}
      data-testid="board-bed-manager"
      aria-label={t('bedManager.title')}
    >
      <HandoffBanner banner={banner} provenance={data.provenance} />
      <BoardHeader
        agent={bedManagerBoard.agent}
        title={t('board.bedManager')}
        provenance={data.provenance}
        lens="Bed Management"
      />

      <PlacementRequestsTable
        placements={payload.placements}
        onSelectRequest={onSelectRequest}
      />

      <PlacementBarriersBoard
        barriers={payload.barriers}
        onSelectBarrier={onSelectBarrier}
        onAutoSequence={onAutoSequence}
      />

      <BedStateKpis payload={payload} />

      <AdmissionsEventstream admissions={payload.admissions} />

      {/* Power BI embed — preserved from Sprint 13 (capacity-dashboard, Direct Lake, RLS by hospital) */}
      <Card className={s.pbiCard} data-testid="pbi-embed">
        <CardHeader
          header={<Body1><b>{t('bmca.pbi.title')}</b></Body1>}
          description={<Caption1>{payload.powerBiEmbed.reportName}</Caption1>}
        />
        <Body1>{payload.powerBiEmbed.embedPlaceholder}</Body1>
      </Card>
    </section>
  );
}
