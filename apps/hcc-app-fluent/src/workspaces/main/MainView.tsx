import type { JSX } from 'react';
import { useParams } from 'react-router-dom';
import { makeStyles, tokens } from '@fluentui/react-components';
import { BedManagerBoard } from './boards/bed-manager/BedManagerBoard';
import { DischargeBoard } from './boards/discharge/DischargeBoard';
import { OccupancyBoard } from './boards/occupancy/OccupancyBoard';
import { OrSteeringBoard } from './boards/or-steering/OrSteeringBoard';
import { StaffingBoard } from './boards/staffing/StaffingBoard';
import { CsaView } from './wizards/csa/CsaView';
import { MainSubNav } from './MainSubNav';
import { useRoleLens } from '../../context/role-context';
import { firstEligibleBoard } from '../../shell/planes/first-eligible-board';

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
  discharge: () => (
    <div data-testid="board-discharge-slot">
      <DischargeBoard />
    </div>
  ),
  'bed-manager': () => (
    <div data-testid="board-bed-manager-slot">
      <BedManagerBoard />
    </div>
  ),
  'or-steering': () => (
    <div data-testid="board-or-steering-slot">
      <OrSteeringBoard />
    </div>
  ),
  staffing: () => (
    <div data-testid="board-staffing-slot">
      <StaffingBoard />
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
  const { capabilities } = useRoleLens();
  const { board } = useParams();
  // Sprint 29 M2 — default to the first patient-journey board the role can see,
  // not a hard-coded bed-manager.
  const fallback = firstEligibleBoard(capabilities);
  const activeBoard = board ?? fallback;
  const Board = BOARDS[activeBoard] ?? BOARDS[fallback];
  return (
    <div className={s.root}>
      <MainSubNav />
      <Board />
    </div>
  );
}
