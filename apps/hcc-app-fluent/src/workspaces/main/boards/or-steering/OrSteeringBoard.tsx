import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Badge, Button, Text, makeStyles, tokens } from '@fluentui/react-components';
import type { ContextInsight, ResidualPressure, RoleBoardData } from '../../../../journey/RoleBoard';
import type { OrCase, OrSteeringPayload, ReslotLever } from '../../../../data/roleboard/or-steering-data';
import { sortReslotLevers } from '../../../../data/roleboard/or-steering-data';
import { orSteeringBoard } from './or-steering-board';
import { BoardHeader } from '../occupancy/BoardHeader';
import { OrCaseScheduleTable } from './OrCaseScheduleTable';
import { OrReslotLeversBoard } from './OrReslotLeversBoard';
import { HandoffBanner } from '../../../../shell/HandoffBanner';
import { bannerFor, residualFromPrev } from '../../../../journey/handoff-orchestrator';
import { GOLDEN_THREAD_SCOPE } from '../../../../journey/golden-thread';
import { routeInsight } from '../../../../copilot-rail/InsightRouter';
import { useCopilotRail } from '../../../../copilot-rail/rail-context';
import { useMode } from '../../../../context/mode-context';
import { useHospital } from '../../../../context/hospital-context';

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalL, padding: tokens.spacingHorizontalL },
  gapStrip: {
    display: 'flex',
    gap: tokens.spacingHorizontalM,
    alignItems: 'center',
    flexWrap: 'wrap',
    padding: `${tokens.spacingVerticalS} ${tokens.spacingHorizontalM}`,
    background: tokens.colorNeutralBackground2,
    borderRadius: tokens.borderRadiusMedium,
  },
});

/** Sprint 20 (parity) — OR steering (orsa) surface: HandoffBanner → BoardHeader → OrCaseScheduleTable → OrReslotLeversBoard. */
export function OrSteeringBoard() {
  const s = useStyles();
  const { t } = useTranslation();
  const { mode } = useMode();
  const { hospital } = useHospital();
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
    // rail.showDefault calls a stable useState setter; intentionally excluded so the effect runs only when mode/hospital changes
  }, [mode, hospital]);

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

  const onSelectGap = () => {
    route({ id: 'or-gap', label: t('orsa.gap.label'), context: { residualBeds: payload.residualBeds } });
  };

  const onAutoSequence = () => {
    // levers are pre-sorted by design; sortReslotLevers is the canonical comparator
    const top = sortReslotLevers(payload.levers)[0];
    if (top) onSelectLever(top);
  };

  return (
    <section className={s.root} data-testid="board-or-steering" aria-label={t('board.orSteering')}>
      <HandoffBanner banner={banner} provenance={data.provenance} />
      <BoardHeader
        agent={orSteeringBoard.agent}
        title={t('board.orSteering')}
        provenance={data.provenance}
        lens="OR Steering"
      />
      {/* Gap summary strip — mirrors OOA/DCA gap cards; click opens the or-gap reco */}
      <div className={s.gapStrip}>
        <Text>{t('board.bedsShort')}: <strong>{payload.bedsShort}</strong></Text>
        <Text>{t('board.casesDeferred')}: <strong>{payload.casesDeferred}</strong></Text>
        <Text>{t('board.bedsFreed')}: <strong>{payload.bedsFreed}</strong></Text>
        <Badge appearance="tint" color="warning">{payload.residualBeds} {t('board.beds')}</Badge>
        <Button appearance="outline" size="small" onClick={onSelectGap}>
          {t('orsa.gap.cta')}
        </Button>
      </div>
      <OrCaseScheduleTable cases={payload.cases} onSelectCase={onSelectCase} />
      <OrReslotLeversBoard levers={payload.levers} onSelectLever={onSelectLever} onAutoSequence={onAutoSequence} />
    </section>
  );
}
