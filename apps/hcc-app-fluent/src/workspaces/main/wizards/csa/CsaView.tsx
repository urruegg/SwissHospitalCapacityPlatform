import { useEffect, useState } from 'react';
import { Text, makeStyles, tokens } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import type { ContextInsight, ResidualPressure, RoleBoardData } from '../../../../journey/RoleBoard';
import type { CrisisPayload, ExternalSignal, Scenario } from '../../../../data/roleboard/crisis-data';
import { sortScenarios } from '../../../../data/roleboard/crisis-data';
import { useMode } from '../../../../context/mode-context';
import { useHospital } from '../../../../context/hospital-context';
import { useCopilotRail } from '../../../../copilot-rail/rail-context';
import { HandoffBanner } from '../../../../shell/HandoffBanner';
import { BoardHeader } from '../../boards/occupancy/BoardHeader';
import { bannerFor, residualFromPrev } from '../../../../journey/handoff-orchestrator';
import { GOLDEN_THREAD_SCOPE } from '../../../../journey/golden-thread';
import { routeInsight } from '../../../../copilot-rail/InsightRouter';
import { CsaRoleGuard } from './CsaRoleGuard';
import { CsaWizard } from './CsaWizard';
import { crisisBoard } from '../../boards/crisis/crisis-board';
import { CrisisSignalsTable } from '../../boards/crisis/CrisisSignalsTable';
import { CrisisScenariosBoard } from '../../boards/crisis/CrisisScenariosBoard';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalM,
  },
  panel: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalL,
    padding: tokens.spacingHorizontalL,
  },
});

/**
 * Sprint 20 M5 — CSA surface.
 *
 * Wraps the existing Sprint 16 CSA wizard with its role guard behind `/main/crisis`.
 * The guard (design spec §8) renders a friendly deny message for callers
 * without a CSA-authorised role; the outer section is always present so the
 * surface has a stable test/anchor id.
 */
export function CsaView() {
  const styles = useStyles();
  const location = useLocation();
  const showRoleBoard = location.pathname.includes('/main/crisis');

  return (
    <section className={styles.root} data-testid="csa-view">
      {showRoleBoard ? <CrisisRoleBoardBlock /> : null}
      <CsaRoleGuard>
        <CsaWizard />
      </CsaRoleGuard>
    </section>
  );
}

function CrisisRoleBoardBlock() {
  const styles = useStyles();
  const { t } = useTranslation();
  const { mode } = useMode();
  const { hospital } = useHospital();
  const rail = useCopilotRail();
  const [data, setData] = useState<RoleBoardData<CrisisPayload> | null>(null);
  const [prev, setPrev] = useState<ResidualPressure | null>(null);

  useEffect(() => {
    const scope = mode === 'demo'
      ? GOLDEN_THREAD_SCOPE
      : { hospital, windowHours: 72, pinned: false };
    let active = true;
    void crisisBoard.load(scope, mode).then((loaded) => {
      if (active) {
        setData(loaded);
        rail.showDefault(crisisBoard.defaultReco(loaded));
      }
    });
    void residualFromPrev(crisisBoard.agent, scope, mode).then((residual) => {
      if (active) setPrev(residual);
    });
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
    // rail.showDefault calls a stable useState setter; intentionally excluded so the effect runs only when mode/hospital changes
  }, [mode, hospital]);

  if (!data) return <Text>{t('board.loading', 'Loading...')}</Text>;

  const banner = bannerFor(mode, crisisBoard.agent, prev);
  const payload = data.payload;

  const route = (insight: ContextInsight) => {
    const reco = crisisBoard.recoFor(insight, data);
    void routeInsight(insight, reco, { agent: crisisBoard.agent, openWithReco: rail.openWithReco });
  };

  const onSelectSignal = (signal: ExternalSignal) => {
    route({
      id: signal.id,
      label: `${signal.source}: ${signal.feed}`,
      context: { signal: signal.id, source: signal.source, filtered: signal.filtered ?? false },
    });
  };

  const onSelectScenario = (scenario: Scenario) => {
    route({
      id: scenario.id,
      label: t('insight.stressTest', { scenario: scenario.name }),
      context: { scenario: scenario.id, probability: scenario.probability, bedImpact: scenario.bedImpact },
    });
  };

  const onSimulateTop = () => {
    const top = sortScenarios(payload.scenarios)[0];
    if (top) onSelectScenario(top);
  };

  return (
    <div className={styles.panel} data-testid="board-crisis-panel">
      <HandoffBanner banner={banner} provenance={data.provenance} />
      <BoardHeader
        agent={crisisBoard.agent}
        title={t('board.crisis')}
        provenance={data.provenance}
        lens="Crisis"
      />
      <CrisisSignalsTable signals={payload.signals} onSelectSignal={onSelectSignal} />
      <CrisisScenariosBoard
        scenarios={payload.scenarios}
        onSelectScenario={onSelectScenario}
        onSimulateTop={onSimulateTop}
      />
    </div>
  );
}
