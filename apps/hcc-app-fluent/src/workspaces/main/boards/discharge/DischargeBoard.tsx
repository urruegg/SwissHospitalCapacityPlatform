import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Button,
  Card,
  Text,
  Title3,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import type { ResidualPressure, RoleBoardData } from '../../../../journey/RoleBoard';
import type { DischargePayload } from '../../../../data/roleboard/discharge-data';
import { dischargeBoard } from './discharge-board';
import { HandoffBanner } from '../../../../shell/HandoffBanner';
import { bannerFor, residualFromPrev } from '../../../../journey/handoff-orchestrator';
import { GOLDEN_THREAD_SCOPE } from '../../../../journey/golden-thread';
import { routeInsight } from '../../../../copilot-rail/InsightRouter';
import { useCopilotRail } from '../../../../copilot-rail/rail-context';
import { useMode } from '../../../../context/mode-context';
import { useHospital } from '../../../../context/hospital-context';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalM,
    padding: tokens.spacingHorizontalL,
  },
  summary: {
    display: 'flex',
    gap: tokens.spacingHorizontalM,
    flexWrap: 'wrap',
  },
  candidates: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, minmax(0, 1fr))',
    gap: tokens.spacingHorizontalM,
  },
  candidate: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
    padding: tokens.spacingHorizontalM,
  },
  insights: {
    display: 'flex',
    gap: tokens.spacingHorizontalS,
    flexWrap: 'wrap',
  },
});

/** Sprint 2 (parity) — Discharge (dca) surface: readiness + actionable insights. */
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
      if (active) setData(loaded);
    });
    void residualFromPrev(dischargeBoard.agent, scope, mode).then((residual) => {
      if (active) setPrev(residual);
    });
    return () => {
      active = false;
    };
  }, [mode, hospital]);

  if (!data) return <Text>{t('board.loading')}</Text>;

  const banner = bannerFor(mode, dischargeBoard.agent, prev);
  const insights = dischargeBoard.insights(data);

  return (
    <section className={s.root} data-testid="board-discharge" aria-label={t('board.discharge')}>
      <HandoffBanner banner={banner} provenance={data.provenance} />
      <Title3>{t('board.discharge')}</Title3>
      <Text className={s.summary}>
        <span>{t('board.bedsNeeded')}: {data.payload.bedsNeeded}</span>
        <span>{t('board.bedsFreeable')}: {data.payload.bedsFreeable}</span>
        <span>{t('board.residual')}: {data.payload.residualBeds}</span>
      </Text>
      <div className={s.candidates}>
        {data.payload.candidates.map((candidate) => (
          <Card key={candidate.id} className={s.candidate}>
            <Text weight="semibold">{candidate.ward}</Text>
            <Text>{candidate.blocker}</Text>
            <Text>
              {candidate.bedsFreeable} {t('board.beds')}
            </Text>
          </Card>
        ))}
      </div>
      <div className={s.insights}>
        {insights.map((insight) => (
          <Button
            key={insight.id}
            appearance="subtle"
            onClick={() =>
              void routeInsight(insight, dischargeBoard.recoFor(insight, data), {
                agent: dischargeBoard.agent,
                openWithReco: rail.openWithReco,
              })
            }
          >
            {insight.label}
          </Button>
        ))}
      </div>
    </section>
  );
}
