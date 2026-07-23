import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Badge, Button, Text, makeStyles, tokens } from '@fluentui/react-components';
import type { ContextInsight, ResidualPressure, RoleBoardData } from '../../../../journey/RoleBoard';
import type { DischargePayload, DischargeCandidate, CapacityBarrier } from '../../../../data/roleboard/discharge-data';
import { dischargeBoard } from './discharge-board';
import { BoardHeader } from '../occupancy/BoardHeader';
import { DischargeWorklistTable } from './DischargeWorklistTable';
import { DischargeBarriersBoard } from './DischargeBarriersBoard';
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

/** Sprint 20 (parity) — Discharge (dca) surface: BoardHeader + gap-strip + DischargeWorklistTable + DischargeBarriersBoard. */
export function DischargeBoard() {
  const s = useStyles();
  const { t } = useTranslation();
  const { mode } = useMode();
  const { hospital } = useHospital();
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
  }, [mode, hospital]);

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
    route({ id: b.recoId, label: b.label, context: { barrier: b.id, bedImpact: b.bedImpact } });
  };

  // Routes the site-level discharge-gap reco (mirrors OOA onSelectGap)
  const onSelectGap = () => {
    route({ id: 'discharge-gap', label: t('dca.gap.label'), context: { gapBeds: payload.residualBeds } });
  };

  // Auto-sequence CTA routes the top-impact barrier's systemic reco
  const onAutoSequence = () => {
    const top = [...payload.barriers].sort((a, b) => b.bedImpact - a.bedImpact || a.id.localeCompare(b.id))[0];
    if (top) onSelectBarrier(top);
  };

  return (
    <section className={s.root} data-testid="board-discharge" aria-label={t('board.discharge')}>
      <HandoffBanner banner={banner} provenance={data.provenance} />
      <BoardHeader agent={dischargeBoard.agent} title={t('board.discharge')} provenance={data.provenance} lens="Discharge Ops" />
      {/* Gap summary strip — mirrors OOA site-gap card; click opens the discharge-gap reco */}
      <div className={s.gapStrip}>
        <Text>{t('board.bedsNeeded')}: <strong>{payload.bedsNeeded}</strong></Text>
        <Text>{t('board.bedsFreeable')}: <strong>{payload.bedsFreeable}</strong></Text>
        <Badge appearance="tint" color="warning">{payload.residualBeds} {t('board.beds')}</Badge>
        <Button appearance="outline" size="small" onClick={onSelectGap}>
          {t('dca.gap.cta')}
        </Button>
      </div>
      <DischargeWorklistTable candidates={payload.candidates} onSelectCandidate={onSelectCandidate} />
      <DischargeBarriersBoard barriers={payload.barriers} onSelectBarrier={onSelectBarrier} onAutoSequence={onAutoSequence} />
    </section>
  );
}
