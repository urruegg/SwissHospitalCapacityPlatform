import type { JSX } from 'react';
import { useParams } from 'react-router-dom';
import { BedManagerBoard } from './boards/bed-manager/BedManagerBoard';

/**
 * Sprint 20 M5 — Main surface.
 *
 * Routes the existing whiteboard boards behind `/main/:board?`, defaulting to
 * the BedManager reference board. Each board owns its own whiteboard `Canvas`
 * (see BedManagerBoard), so MainView only selects and mounts the board.
 */
const BOARDS: Record<string, () => JSX.Element> = {
  'bed-manager': () => (
    <div data-testid="board-bed-manager">
      <BedManagerBoard />
    </div>
  ),
};

export function MainView() {
  const { board = 'bed-manager' } = useParams();
  const Board = BOARDS[board] ?? BOARDS['bed-manager'];
  return <Board />;
}
