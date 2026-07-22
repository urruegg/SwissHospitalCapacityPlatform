import type { JSX } from 'react';
import { useParams } from 'react-router-dom';
import { makeStyles, tokens } from '@fluentui/react-components';
import { BedManagerBoard } from './boards/bed-manager/BedManagerBoard';
import { OccupancyBoard } from './boards/occupancy/OccupancyBoard';
import { CsaView } from './wizards/csa/CsaView';
import { MainSubNav } from './MainSubNav';

/**
 * Sprint 1 (parity) — MAIN surface: sub-nav + the selected role board.
 */
const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: tokens.spacingVerticalS },
});

const BOARDS: Record<string, () => JSX.Element> = {
  occupancy: () => (
    <div data-testid="board-occupancy-slot">
      <OccupancyBoard />
    </div>
  ),
  'bed-manager': () => (
    <div data-testid="board-bed-manager">
      <BedManagerBoard />
    </div>
  ),
  crisis: () => (
    <div data-testid="board-crisis">
      <CsaView />
    </div>
  ),
};

export function MainView() {
  const s = useStyles();
  const { board = 'bed-manager' } = useParams();
  const Board = BOARDS[board] ?? BOARDS['bed-manager'];
  return (
    <div className={s.root}>
      <MainSubNav />
      <Board />
    </div>
  );
}
