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
import type { StaffingPayload } from '../../../../data/roleboard/staffing-data';
import { staffingBoard } from './staffing-board';
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

/** Sprint 3 (parity) — Staffing (sba) surface: FTE shifts + actionable insights. */
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
      if (active) setData(loaded);
    });
    void residualFromPrev(staffingBoard.agent, scope, mode).then((residual) => {
      if (active) setPrev(residual);
    });
    return () => {
      active = false;
    };
  }, [mode, hospital]);

  if (!data) return <Text>{t('board.loading')}</Text>;

  const banner = bannerFor(mode, staffingBoard.agent, prev);
  const insights = staffingBoard.insights(data);

  return (
    <section className={s.root} data-testid="board-staffing" aria-label={t('board.staffing')}>
      <HandoffBanner banner={banner} provenance={data.provenance} />
      <Title3>{t('board.staffing')}</Title3>
      <Text className={s.summary}>
        <span>{t('board.bedsShort')}: {data.payload.bedsShort}</span>
        <span>{t('board.surgeBeds')}: {data.payload.surgeBedsEnabled}</span>
        <span>{t('board.residual')}: {data.payload.residualBeds}</span>
      </Text>
      <div className={s.candidates}>
        {data.payload.moves.map((move) => (
          <Card key={move.id} className={s.candidate}>
            <Text weight="semibold">{move.role}</Text>
            <Text>{move.fromUnit} -&gt; {move.toUnit}</Text>
            <Text>
              {move.fte} {t('board.fte')}
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
                agent: staffingBoard.agent,
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
