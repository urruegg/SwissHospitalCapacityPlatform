import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Badge, Button, Text, makeStyles, tokens } from '@fluentui/react-components';
import type { ContextInsight, ResidualPressure, RoleBoardData } from '../../../../journey/RoleBoard';
import type { StaffMove, StaffingLever, StaffingPayload } from '../../../../data/roleboard/staffing-data';
import { sortStaffingLevers } from '../../../../data/roleboard/staffing-data';
import { staffingBoard } from './staffing-board';
import { BoardHeader } from '../occupancy/BoardHeader';
import { CoverageWorklistTable } from './CoverageWorklistTable';
import { StaffingLeversBoard } from './StaffingLeversBoard';
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

/** Sprint 20 (parity) — Staffing (sba) surface: HandoffBanner → BoardHeader → gap strip → CoverageWorklistTable → StaffingLeversBoard. */
export function StaffingBoard() {
  const s = useStyles();
  const { t } = useTranslation();
  const { mode } = useMode();
  const { hospital } = useHospital();
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
    // rail.showDefault calls a stable useState setter; intentionally excluded so the effect runs only when mode/hospital changes
  }, [mode, hospital]);

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

  const onSelectGap = () => {
    route({ id: 'staffing-gap', label: t('sba.gap.label'), context: { residualBeds: payload.residualBeds } });
  };

  const onAutoSequence = () => {
    // levers are pre-sorted by design; sortStaffingLevers is the canonical comparator
    const top = sortStaffingLevers(payload.levers)[0];
    if (top) onSelectLever(top);
  };

  return (
    <section className={s.root} data-testid="board-staffing" aria-label={t('board.staffing')}>
      <HandoffBanner banner={banner} provenance={data.provenance} />
      <BoardHeader
        agent={staffingBoard.agent}
        title={t('board.staffing')}
        provenance={data.provenance}
        lens="Staffing Balance"
      />
      {/* Gap summary strip — mirrors ORSA/DCA gap strip; click opens the staffing-gap reco */}
      <div className={s.gapStrip}>
        <Text>{t('board.bedsShort')}: <strong>{payload.bedsShort}</strong></Text>
        <Text>{t('board.surgeBeds')}: <strong>{payload.surgeBedsEnabled}</strong></Text>
        <Badge appearance="tint" color="success">
          {payload.residualBeds === 0 ? t('sba.kpi.balanced') : `${payload.residualBeds} ${t('board.beds')}`}
        </Badge>
        <Button appearance="outline" size="small" onClick={onSelectGap}>
          {t('sba.gap.cta')}
        </Button>
      </div>
      <CoverageWorklistTable moves={payload.moves} onSelectMove={onSelectMove} />
      <StaffingLeversBoard levers={payload.levers} onSelectLever={onSelectLever} onAutoSequence={onAutoSequence} />
    </section>
  );
}
