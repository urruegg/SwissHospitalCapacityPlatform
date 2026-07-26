import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Text,
  makeStyles,
  mergeClasses,
  tokens,
} from '@fluentui/react-components';
import { space, radii, elevation } from '../../../../theme/design-system';
import type { ContextInsight, ResidualPressure, RoleBoardData } from '../../../../journey/RoleBoard';
import type {
  BedManagerPayload,
  PlacementRequest,
  PlacementBarrier,
  AdmissionEvent,
} from '../../../../data/roleboard/bed-manager-data';
import { sortBarriers } from '../../../../data/roleboard/bed-manager-data';
import { bedManagerBoard } from './bed-manager-board';
import { BoardHeader } from '../occupancy/BoardHeader';
import { PlacementRequestsTable } from './PlacementRequestsTable';
import { PlacementBarriersBoard } from './PlacementBarriersBoard';
import { BedStateKpis } from './BedStateKpis';
import { AdmissionsEventstream } from './AdmissionsEventstream';
import { GroundingNotice } from '../GroundingNotice';
import { HandoffBanner } from '../../../../shell/HandoffBanner';
import { bannerFor, residualFromPrev } from '../../../../journey/handoff-orchestrator';
import { GOLDEN_THREAD_SCOPE } from '../../../../journey/golden-thread';
import { routeInsight } from '../../../../copilot-rail/InsightRouter';
import { useCopilotRail } from '../../../../copilot-rail/rail-context';
import { useMode } from '../../../../context/mode-context';
import { useHospital } from '../../../../context/hospital-context';
import { useDataSource } from '../../../../context/data-source-context';

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: space.l, padding: space.l },
  panel: {
    backgroundColor: tokens.colorNeutralBackground1,
    borderRadius: radii.card,
    boxShadow: elevation.card,
    padding: space.l,
  },
  // Source (live admissions) -> insights (placement worklist) on one level.
  sourceInsightRow: {
    display: 'flex',
    gap: space.l,
    alignItems: 'stretch',
    flexWrap: 'wrap',
  },
  sourcePane: {
    flexGrow: 0,
    flexShrink: 0,
    flexBasis: '300px',
    minWidth: '260px',
    overflowY: 'auto',
  },
  insightPane: {
    flexGrow: 1,
    flexShrink: 1,
    flexBasis: '420px',
    minWidth: 0,
  },
});

/** Sprint 20 (parity) — BedManager (bmca) surface: BoardHeader + placement worklist + barriers + KPIs + eventstream + Power BI embed. */
export function BedManagerBoard() {
  const s = useStyles();
  const { t } = useTranslation();
  const { mode } = useMode();
  const { hospital } = useHospital();
  const { source } = useDataSource();
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
  }, [mode, hospital, source]);

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
        requestNo: r.id,
        source: r.source,
        target: r.target,
      }),
      context: {
        placement: r.id,
        source: r.source,
        target: r.target,
        status: r.status,
        barrier: r.barrier,
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

  const onSelectAdmission = (ev: AdmissionEvent) => {
    route({
      id: `admission-${ev.id}`,
      label: t('insight.admissionEvent', { patient: ev.patient, ward: ev.ward }),
      context: { admission: ev.id, ts: ev.ts, ward: ev.ward, patient: ev.patient, kind: ev.kind },
    });
  };

  return (
    <section
      className={s.root}
      data-testid="board-bed-manager"
      aria-label={t('bedManager.title')}
    >
      <HandoffBanner banner={banner} provenance={data.provenance} />
      <GroundingNotice degraded={data.degraded} />
      <BoardHeader
        agent={bedManagerBoard.agent}
        title={t('board.bedManager')}
        provenance={data.provenance}
        lens="Bed Management"
      />

      {/* Source (live admissions) -> insights (placement worklist) on one level. */}
      <div className={s.sourceInsightRow}>
        <div className={mergeClasses(s.panel, s.sourcePane)}>
          <AdmissionsEventstream admissions={payload.admissions} onSelectAdmission={onSelectAdmission} />
        </div>
        <div className={mergeClasses(s.panel, s.insightPane)}>
          <PlacementRequestsTable
            placements={payload.placements}
            onSelectRequest={onSelectRequest}
          />
        </div>
      </div>

      <div className={s.panel}>
        <PlacementBarriersBoard
          barriers={payload.barriers}
          onSelectBarrier={onSelectBarrier}
          onAutoSequence={onAutoSequence}
        />
      </div>

      <BedStateKpis payload={payload} />
    </section>
  );
}
