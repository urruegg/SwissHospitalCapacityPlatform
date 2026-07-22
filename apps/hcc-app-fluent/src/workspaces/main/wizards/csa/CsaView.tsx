import { useEffect, useState } from 'react';
import { Button, makeStyles, Text, Title3, tokens } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import type { RoleBoardData } from '../../../../journey/RoleBoard';
import { CRISIS_PINNED, type CrisisPayload } from '../../../../data/roleboard/crisis-data';
import { useMode } from '../../../../context/mode-context';
import { useHospital } from '../../../../context/hospital-context';
import { useCopilotRail } from '../../../../copilot-rail/rail-context';
import { HandoffBanner } from '../../../../shell/HandoffBanner';
import { bannerFor } from '../../../../journey/handoff-orchestrator';
import { GOLDEN_THREAD_SCOPE, SEED_SITUATION } from '../../../../journey/golden-thread';
import { routeInsight } from '../../../../copilot-rail/InsightRouter';
import { CsaRoleGuard } from './CsaRoleGuard';
import { CsaWizard } from './CsaWizard';
import { crisisBoard } from '../../boards/crisis/crisis-board';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalM,
  },
  panel: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalS,
  },
  columns: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
    gap: tokens.spacingHorizontalL,
  },
  list: {
    marginTop: 0,
    marginBottom: 0,
    paddingLeft: tokens.spacingHorizontalXL,
  },
  insights: {
    display: 'flex',
    gap: tokens.spacingHorizontalS,
    flexWrap: 'wrap',
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
  const demoData: RoleBoardData<CrisisPayload> = {
    provenance: 'simulated',
    scope: GOLDEN_THREAD_SCOPE,
    payload: CRISIS_PINNED,
  };
  const [userData, setUserData] = useState<RoleBoardData<CrisisPayload> | null>(null);

  useEffect(() => {
    const scope = mode === 'demo'
      ? GOLDEN_THREAD_SCOPE
      : { hospital, windowHours: 72, pinned: false };
    if (mode === 'demo') {
      return undefined;
    }
    let active = true;
    void crisisBoard.load(scope, mode).then((loaded) => {
      if (active) setUserData(loaded);
    });
    return () => {
      active = false;
    };
  }, [mode, hospital]);

  const data = mode === 'demo' ? demoData : userData;
  const banner = data
    ? bannerFor(mode, crisisBoard.agent, mode === 'demo' ? SEED_SITUATION : null)
    : null;
  const insights = data ? crisisBoard.insights(data) : [];

  if (!data || !banner) return null;

  return (
    <div className={styles.panel}>
      <HandoffBanner banner={banner} provenance={data.provenance} />
      <Title3>{t('board.crisis')}</Title3>
      <div className={styles.columns}>
        <div>
          <Text weight="semibold" as="h3">{t('board.signals')}</Text>
          <ul className={styles.list}>
            {data.payload.signals.map((signal) => (
              <li key={signal.id}>
                {signal.source}: {signal.label} ({signal.certainty})
              </li>
            ))}
          </ul>
        </div>
        <div>
          <Text weight="semibold" as="h3">{t('board.scenarios')}</Text>
          <ul className={styles.list}>
            {data.payload.scenarios.map((scenario) => (
              <li key={scenario.id}>
                <span>{scenario.label}</span> — p={scenario.probability}, {scenario.bedDayImpact} {t('board.bedDays')}
              </li>
            ))}
          </ul>
        </div>
      </div>
      <div className={styles.insights}>
        {insights.map((insight) => (
          <Button
            key={insight.id}
            appearance="subtle"
            onClick={() =>
              void routeInsight(insight, {
                agent: crisisBoard.agent,
                openWithContext: rail.openWithContext,
              })
            }
          >
            {insight.label}
          </Button>
        ))}
      </div>
    </div>
  );
}
