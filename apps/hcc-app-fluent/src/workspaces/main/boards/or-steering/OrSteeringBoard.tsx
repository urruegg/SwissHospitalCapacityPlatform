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
import type { RoleBoardData } from '../../../../journey/RoleBoard';
import type { OrSteeringPayload } from '../../../../data/roleboard/or-steering-data';
import { orSteeringBoard } from './or-steering-board';
import { HandoffBanner } from '../../../../shell/HandoffBanner';
import { bannerFor } from '../../../../journey/handoff-orchestrator';
import { GOLDEN_THREAD_SCOPE, SEED_SITUATION } from '../../../../journey/golden-thread';
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

/** Sprint 3 (parity) — OR steering (orsa) surface: deferrals + actionable insights. */
export function OrSteeringBoard() {
  const s = useStyles();
  const { t } = useTranslation();
  const { mode } = useMode();
  const { hospital } = useHospital();
  const rail = useCopilotRail();
  const [data, setData] = useState<RoleBoardData<OrSteeringPayload> | null>(null);

  useEffect(() => {
    const scope = mode === 'demo'
      ? GOLDEN_THREAD_SCOPE
      : { hospital, windowHours: 72, pinned: false };
    let active = true;
    void orSteeringBoard.load(scope, mode).then((loaded) => {
      if (active) setData(loaded);
    });
    return () => {
      active = false;
    };
  }, [mode, hospital]);

  if (!data) return <Text>{t('board.loading')}</Text>;

  const banner = bannerFor(mode, orSteeringBoard.agent, mode === 'demo' ? SEED_SITUATION : null);
  const insights = orSteeringBoard.insights(data);

  return (
    <section className={s.root} data-testid="board-or-steering" aria-label={t('board.orSteering')}>
      <HandoffBanner banner={banner} provenance={data.provenance} />
      <Title3>{t('board.orSteering')}</Title3>
      <Text className={s.summary}>
        <span>{t('board.bedsShort')}: {data.payload.bedsShort}</span>
        <span>{t('board.casesDeferred')}: {data.payload.casesDeferred}</span>
        <span>{t('board.bedsFreed')}: {data.payload.bedsFreed}</span>
        <span>{t('board.residual')}: {data.payload.residualBeds}</span>
      </Text>
      <div className={s.candidates}>
        {data.payload.cases.map((orCase) => (
          <Card key={orCase.id} className={s.candidate}>
            <Text weight="semibold">{orCase.specialty}</Text>
            <Text>{orCase.slot}</Text>
            <Text>
              {orCase.bedsImpact} {t('board.beds')}
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
              void routeInsight(insight, {
                agent: orSteeringBoard.agent,
                openWithContext: rail.openWithContext,
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
