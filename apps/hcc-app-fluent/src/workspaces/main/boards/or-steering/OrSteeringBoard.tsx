import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Text, makeStyles, mergeClasses, tokens } from '@fluentui/react-components';
import { space, radii, elevation } from '../../../../theme/design-system';
import type { ContextInsight, ResidualPressure, RoleBoardData } from '../../../../journey/RoleBoard';
import type { OrCase, OrCaseEvent, OrSteeringPayload, ReslotLever } from '../../../../data/roleboard/or-steering-data';
import { orSteeringBoard } from './or-steering-board';
import { BoardHeader } from '../occupancy/BoardHeader';
import { OrCaseEventstream } from './OrCaseEventstream';
import { OrCaseScheduleTable } from './OrCaseScheduleTable';
import { OrReslotLeversBoard } from './OrReslotLeversBoard';
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
  // Source (live incoming OR cases) -> insights (elective OR schedule) on one level.
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

/** Sprint 20 (parity) / Sprint 27 — OR steering (orsa) surface: live incoming OR cases + elective OR schedule (upper lane) → reslot levers (lower lane). */
export function OrSteeringBoard() {
  const s = useStyles();
  const { t } = useTranslation();
  const { mode } = useMode();
  const { hospital } = useHospital();
  const { source } = useDataSource();
  const rail = useCopilotRail();
  const [data, setData] = useState<RoleBoardData<OrSteeringPayload> | null>(null);
  const [prev, setPrev] = useState<ResidualPressure | null>(null);

  useEffect(() => {
    const scope = mode === 'demo'
      ? GOLDEN_THREAD_SCOPE
      : { hospital, windowHours: 72, pinned: false };
    let active = true;
    void orSteeringBoard.load(scope, mode).then((loaded) => {
      if (active) {
        setData(loaded);
        rail.showDefault(orSteeringBoard.defaultReco(loaded));
      }
    });
    void residualFromPrev(orSteeringBoard.agent, scope, mode).then((residual) => {
      if (active) setPrev(residual);
    });
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, hospital, source]);

  if (!data) return <Text>{t('board.loading', 'Loading...')}</Text>;

  const banner = bannerFor(mode, orSteeringBoard.agent, prev);
  const payload = data.payload;

  const route = (insight: ContextInsight) => {
    const reco = orSteeringBoard.recoFor(insight, data);
    void routeInsight(insight, reco, { agent: orSteeringBoard.agent, openWithReco: rail.openWithReco });
  };

  const onSelectCase = (c: OrCase) => {
    route({
      id: c.recoId,
      label: t('insight.orDefer', { specialty: c.specialty }),
      context: { case: c.id, specialty: c.specialty, slot: c.slot, bedsImpact: c.bedsImpact },
    });
  };

  const onSelectLever = (lever: ReslotLever) => {
    route({
      id: lever.recoId,
      label: lever.label,
      context: { lever: lever.id, bedsProtected: lever.bedsProtected },
    });
  };

  const onSelectEvent = (ev: OrCaseEvent) => {
    route({
      id: `orcase-${ev.id}`,
      label: t('insight.orCaseEvent', { caseNo: ev.caseNo }),
      context: { orCase: ev.caseNo, ts: ev.ts, kind: ev.kind },
    });
  };

  // The "View reslot plan" CTA opens the site-gap reslot playbook (with the sba handoff).
  const onViewPlan = () => {
    route({ id: 'or-gap', label: t('orsa.gap.label'), context: { residualBeds: payload.residualBeds } });
  };

  return (
    <section className={s.root} data-testid="board-or-steering" aria-label={t('board.orSteering')}>
      <HandoffBanner banner={banner} provenance={data.provenance} />
      <GroundingNotice degraded={data.degraded} />
      <BoardHeader
        agent={orSteeringBoard.agent}
        title={t('board.orSteering')}
        provenance={data.provenance}
        lens="OR Steering"
      />

      {/* Source (live incoming OR cases) -> insights (elective OR schedule) on one level. */}
      <div className={s.sourceInsightRow}>
        <div className={mergeClasses(s.panel, s.sourcePane)}>
          <OrCaseEventstream events={payload.liveCases} onSelectEvent={onSelectEvent} />
        </div>
        <div className={mergeClasses(s.panel, s.insightPane)}>
          <OrCaseScheduleTable cases={payload.cases} onSelectCase={onSelectCase} />
        </div>
      </div>

      <div className={s.panel}>
        <OrReslotLeversBoard
          levers={payload.levers}
          onSelectLever={onSelectLever}
          onViewPlan={onViewPlan}
          summary={payload.leverSummary}
        />
      </div>
    </section>
  );
}
