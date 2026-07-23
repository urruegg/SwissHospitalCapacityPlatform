import { useEffect, useState } from 'react';
import { makeStyles, tokens, Title2, Button, Text } from '@fluentui/react-components';
import { useTranslation } from 'react-i18next';
import type { RoleBoardData } from '../../../../journey/RoleBoard';
import type { BedManagerPayload } from '../../../../data/roleboard/bed-manager-data';
import { Canvas } from '../../../../whiteboard/Canvas';
import { useLayoutManager } from '../../../../whiteboard/LayoutManager';
import { bedManagerCards } from './mock-data';
import { CopilotDrawer } from '../../../../copilot-drawer/Drawer';
import { useMode } from '../../../../context/mode-context';
import { useHospital } from '../../../../context/hospital-context';
import { useCopilotRail } from '../../../../copilot-rail/rail-context';
import { HandoffBanner } from '../../../../shell/HandoffBanner';
import { bannerFor } from '../../../../journey/handoff-orchestrator';
import { GOLDEN_THREAD_SCOPE, SEED_SITUATION } from '../../../../journey/golden-thread';
import { routeInsight } from '../../../../copilot-rail/InsightRouter';
import { bedManagerBoard } from './bed-manager-board';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalM,
  },
  summary: {
    display: 'flex',
    gap: tokens.spacingHorizontalM,
    flexWrap: 'wrap',
  },
  insights: {
    display: 'flex',
    gap: tokens.spacingHorizontalS,
    flexWrap: 'wrap',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: tokens.spacingVerticalM,
  },
});

/** Sprint 13 T3/T6 — BedManager @ USZ reference operational whiteboard. */
export function BedManagerBoard() {
  const styles = useStyles();
  const { t } = useTranslation();
  const { mode } = useMode();
  const { hospital } = useHospital();
  const rail = useCopilotRail();
  const layout = useLayoutManager(bedManagerCards);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [data, setData] = useState<RoleBoardData<BedManagerPayload> | null>(null);

  useEffect(() => {
    const scope = mode === 'demo'
      ? GOLDEN_THREAD_SCOPE
      : { hospital, windowHours: 72, pinned: false };
    let active = true;
    void bedManagerBoard.load(scope, mode).then((loaded) => {
      if (active) setData(loaded);
    });
    return () => {
      active = false;
    };
  }, [mode, hospital]);

  const banner = data
    ? bannerFor(mode, bedManagerBoard.agent, mode === 'demo' ? SEED_SITUATION : null)
    : null;
  const insights = data ? bedManagerBoard.insights(data) : [];

  return (
    <section className={styles.root} aria-label={t('bedManager.title')}>
      {data && banner ? (
        <>
          <HandoffBanner banner={banner} provenance={data.provenance} />
          <Text className={styles.summary}>
            <span>{t('board.bedsShort')}: {data.payload.bedsShort}</span>
            <span>{t('board.bedsReallocated')}: {data.payload.bedsReallocated}</span>
            <span>{t('board.residual')}: {data.payload.residualBeds}</span>
          </Text>
          <div className={styles.insights}>
            {insights.map((insight) => (
              <Button
                key={insight.id}
                appearance="subtle"
                onClick={() =>
                  void routeInsight(insight, {
                    agent: bedManagerBoard.agent,
                    openWithContext: rail.openWithContext,
                  })
                }
              >
                {insight.label}
              </Button>
            ))}
          </div>
        </>
      ) : null}
      <div className={styles.header}>
        <Title2>{t('bedManager.title')}</Title2>
        <Button appearance="primary" onClick={() => setDrawerOpen(true)}>
          {t('bedManager.askBmca')}
        </Button>
      </div>
      <Canvas layout={layout} />
      <CopilotDrawer
        agent="bmca-agent"
        open={drawerOpen}
        onOpenChange={setDrawerOpen}
      />
    </section>
  );
}
