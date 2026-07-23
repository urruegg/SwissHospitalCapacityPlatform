import type { RoleBoard } from '../../journey/RoleBoard';
import { occupancyBoard } from '../../workspaces/main/boards/occupancy/occupancy-board';
import { dischargeBoard } from '../../workspaces/main/boards/discharge/discharge-board';
import { bedManagerBoard } from '../../workspaces/main/boards/bed-manager/bed-manager-board';
import { orSteeringBoard } from '../../workspaces/main/boards/or-steering/or-steering-board';
import { staffingBoard } from '../../workspaces/main/boards/staffing/staffing-board';
import { crisisBoard } from '../../workspaces/main/boards/crisis/crisis-board';

const BOARDS: Record<string, RoleBoard<unknown>> = {
  occupancy: occupancyBoard as RoleBoard<unknown>,
  discharge: dischargeBoard as RoleBoard<unknown>,
  'bed-manager': bedManagerBoard as RoleBoard<unknown>,
  'or-steering': orSteeringBoard as RoleBoard<unknown>,
  staffing: staffingBoard as RoleBoard<unknown>,
  crisis: crisisBoard as RoleBoard<unknown>,
};

export function boardForRoute(pathname: string): RoleBoard<unknown> | null {
  const board = pathname.match(/^\/main\/([^/]+)/)?.[1];
  return (board && BOARDS[board]) || null;
}
