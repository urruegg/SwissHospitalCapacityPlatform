import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Text, makeStyles, tokens } from '@fluentui/react-components';
import { space, radii, elevation } from '../../../../theme/design-system';
import { EvidenceTracePanel } from './EvidenceTracePanel';
import type { EvidenceTrace } from '../../../../data/iq-client';
import { iqEvidence, isAgentHostConfigured } from '../../../../data/iq-client';
import { evidenceTraceFixture } from '../../../../data/roleboard/evidence-fixture';
import { getContextEnvelope } from '../../../../data/roleboard/golden-source-client';
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

/**
 * Sprint 39 P2 (B3/B4) — the Closed-Loop Evidence surface.
 *
 * Renders the DC-EVIDENCE-TRACE-v1 derived proof of the operational loop: the
 * five-part proof per journey step, the shared `golden_thread`, an accept<->deny
 * branch toggle, and a demo walk across the roles. Live (source==='live' && the
 * agent-host is configured && a per-user ContextEnvelope exists, ADR-0052) loads
 * the trace from `GET /agents/dca/evidence` through the single IQ gateway;
 * Simulated (or a live failure) renders the bundled fixture and fails loud
 * (`degraded`). The trace's `outcome` steps are the SAME DC-SIM-OUTCOME-v1 the
 * copilot accept surface (B2) shows - the validation==UX unification (FR-UXL-004).
 */
export function ClosedLoopEvidenceBoard() {
  const s = useStyles();
  const { t } = useTranslation();
  const { mode } = useMode();
  const { hospital } = useHospital();
  const { source } = useDataSource();
  const [branch, setBranch] = useState<'accept' | 'deny'>('accept');
  const [trace, setTrace] = useState<EvidenceTrace | null>(null);
  const [degraded, setDegraded] = useState(false);

  useEffect(() => {
    let active = true;
    const env = getContextEnvelope();
    const live = source === 'live' && isAgentHostConfigured() && env !== null;
    void (async () => {
      if (live && env) {
        try {
          const result = await iqEvidence('dca', branch, env);
          if (!active) return;
          setTrace(result.data);
          setDegraded(false);
          return;
        } catch {
          // Fail loud: keep the bundled demo trace, flag degraded. Never silently
          // pretend live.
          if (!active) return;
          setTrace(evidenceTraceFixture(branch));
          setDegraded(true);
          return;
        }
      }
      // Simulated (or host unconfigured): the bundled demo trace.
      setTrace(evidenceTraceFixture(branch));
      setDegraded(false);
    })();
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, hospital, source, branch]);

  if (!trace) return <Text>{t('board.loading', 'Loading...')}</Text>;

  return (
    <section className={s.root} data-testid="board-evidence" aria-label={t('board.evidence', 'Closed-Loop Evidence')}>
      <div className={s.panel}>
        <EvidenceTracePanel trace={trace} branch={branch} onBranchChange={setBranch} degraded={degraded} />
      </div>
    </section>
  );
}
