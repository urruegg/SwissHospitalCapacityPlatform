import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Text, makeStyles, tokens } from '@fluentui/react-components';
import { space, radii, elevation } from '../../../../theme/design-system';
import type { ContextInsight, ResidualPressure, RoleBoardData } from '../../../../journey/RoleBoard';
import type { StaffMove, StaffingLever, StaffingPayload } from '../../../../data/roleboard/staffing-data';
import { staffingBoard } from './staffing-board';
import { BoardHeader } from '../occupancy/BoardHeader';
import { CoverageWorklistTable } from './CoverageWorklistTable';
import { StaffingLeversBoard } from './StaffingLeversBoard';
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

/** Sprint 20 (parity) / Sprint 27 — Staffing (sba) surface: coverage worklist (upper lane) → staffing levers (lower lane). */
export function StaffingBoard() {
  const s = useStyles();
  const { t } = useTranslation();
  const { mode } = useMode();
  const { hospital } = useHospital();
  const { source } = useDataSource();
  const rail = useCopilotRail();
  const [data, setData] = useState<RoleBoardData<StaffingPayload> | null>(null);
  const [prev, setPrev] = useState<ResidualPressure | null>(null);

  useEffect(() => {
    const scope = mode === 'demo'
      ? GOLDEN_THREAD_SCOPE
      : { hospital, windowHours: 72, pinned: false };
    let active = true;
    void staffingBoard.load(scope, mode).then((loaded) => {
      if (active) {
        setData(loaded);
        rail.showDefault(staffingBoard.defaultReco(loaded));
      }
    });
    void residualFromPrev(staffingBoard.agent, scope, mode).then((residual) => {
      if (active) setPrev(residual);
    });
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, hospital, source]);

  if (!data) return <Text>{t('board.loading', 'Loading...')}</Text>;

  const banner = bannerFor(mode, staffingBoard.agent, prev);
  const payload = data.payload;

  const route = (insight: ContextInsight) => {
    const reco = staffingBoard.recoFor(insight, data);
    void routeInsight(insight, reco, { agent: staffingBoard.agent, openWithReco: rail.openWithReco });
  };

  const onSelectMove = (m: StaffMove) => {
    route({
      id: m.recoId,
      label: t('insight.staffShift', { role: m.role, fromUnit: m.fromUnit, toUnit: m.toUnit }),
      context: { move: m.id, fromUnit: m.fromUnit, toUnit: m.toUnit, role: m.role, fte: m.fte },
    });
  };

  const onSelectLever = (lever: StaffingLever) => {
    route({
      id: lever.recoId,
      label: lever.label,
      context: { lever: lever.id, bedsEnabled: lever.bedsEnabled },
    });
  };

  // The "View staffing plan" CTA opens the site-balance playbook (with the csa handoff).
  const onViewPlan = () => {
    route({ id: 'staffing-gap', label: t('sba.gap.label'), context: { residualBeds: payload.residualBeds } });
  };

  return (
    <section className={s.root} data-testid="board-staffing" aria-label={t('board.staffing')}>
      <HandoffBanner banner={banner} provenance={data.provenance} />
      <GroundingNotice degraded={data.degraded} />
      <BoardHeader
        agent={staffingBoard.agent}
        title={t('board.staffing')}
        provenance={data.provenance}
        lens="Staffing Balance"
      />

      <div className={s.panel}>
        <CoverageWorklistTable moves={payload.moves} onSelectMove={onSelectMove} />
      </div>

      <div className={s.panel}>
        <StaffingLeversBoard
          levers={payload.levers}
          onSelectLever={onSelectLever}
          onViewPlan={onViewPlan}
          summary={payload.leverSummary}
        />
      </div>
    </section>
  );
}
