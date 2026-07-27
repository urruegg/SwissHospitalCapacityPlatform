import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Text, makeStyles, tokens } from '@fluentui/react-components';
import { space, radii, elevation } from '../../../../theme/design-system';
import type { ContextInsight, ResidualPressure, RoleBoardData } from '../../../../journey/RoleBoard';
import type { DischargePayload, DischargeCandidate, CapacityBarrier } from '../../../../data/roleboard/discharge-data';
import { dischargeBoard } from './discharge-board';
import { BoardHeader } from '../occupancy/BoardHeader';
import { DischargeWorklistTable } from './DischargeWorklistTable';
import { DischargeBarriersBoard } from './DischargeBarriersBoard';
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
});

/** Sprint 20 (parity) / Sprint 27 — Discharge (dca) surface: discharge worklist (upper lane) → capacity barriers (lower lane). */
export function DischargeBoard() {
  const s = useStyles();
  const { t } = useTranslation();
  const { mode } = useMode();
  const { hospital } = useHospital();
  const { source } = useDataSource();
  const rail = useCopilotRail();
  const [data, setData] = useState<RoleBoardData<DischargePayload> | null>(null);
  const [prev, setPrev] = useState<ResidualPressure | null>(null);

  useEffect(() => {
    const scope = mode === 'demo'
      ? GOLDEN_THREAD_SCOPE
      : { hospital, windowHours: 72, pinned: false };
    let active = true;
    void dischargeBoard.load(scope, mode).then((loaded) => {
      if (active) {
        setData(loaded);
        rail.showDefault(dischargeBoard.defaultReco(loaded));
      }
    });
    void residualFromPrev(dischargeBoard.agent, scope, mode).then((residual) => {
      if (active) setPrev(residual);
    });
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, hospital, source]);

  if (!data) return <Text>{t('board.loading', 'Loading...')}</Text>;

  const banner = bannerFor(mode, dischargeBoard.agent, prev);
  const payload = data.payload;

  const route = (insight: ContextInsight) => {
    const reco = dischargeBoard.recoFor(insight, data);
    void routeInsight(insight, reco, { agent: dischargeBoard.agent, openWithReco: rail.openWithReco });
  };

  const onSelectCandidate = (c: DischargeCandidate) => {
    route({
      id: c.recoId,
      label: t('insight.dischargeExpediteDetail', { ward: c.ward, blocker: c.blocker }),
      context: { candidate: c.id, ward: c.ward, blocker: c.blocker, bedsFreeable: c.bedsFreeable },
    });
  };

  const onSelectBarrier = (b: CapacityBarrier) => {
    route({ id: b.recoId, label: b.name, context: { barrier: b.id, bedImpact: b.bedImpact } });
  };

  // The "View coordinated plan" CTA opens the site discharge-gap playbook (with the bmca handoff).
  const onViewPlan = () => {
    route({ id: 'discharge-gap', label: t('dca.gap.label'), context: { gapBeds: payload.residualBeds } });
  };

  return (
    <section className={s.root} data-testid="board-discharge" aria-label={t('board.discharge')}>
      <HandoffBanner banner={banner} provenance={data.provenance} />
      <GroundingNotice degraded={data.degraded} />
      <BoardHeader agent={dischargeBoard.agent} title={t('board.discharge')} provenance={data.provenance} lens="Discharge Ops" />

      <div className={s.panel}>
        <DischargeWorklistTable candidates={payload.candidates} onSelectCandidate={onSelectCandidate} />
      </div>

      <div className={s.panel}>
        <DischargeBarriersBoard
          barriers={payload.barriers}
          onSelectBarrier={onSelectBarrier}
          onViewPlan={onViewPlan}
          summary={payload.barrierSummary}
        />
      </div>
    </section>
  );
}
