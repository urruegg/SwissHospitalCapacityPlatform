import { occupancyBoard } from '../main/boards/occupancy/occupancy-board';
import { dischargeBoard } from '../main/boards/discharge/discharge-board';
import { bedManagerBoard } from '../main/boards/bed-manager/bed-manager-board';
import { orSteeringBoard } from '../main/boards/or-steering/or-steering-board';
import { staffingBoard } from '../main/boards/staffing/staffing-board';
import { crisisBoard } from '../main/boards/crisis/crisis-board';
import type { AgentId, Ceiling } from '../../journey/RoleBoard';

export interface LauncherTile {
  route: string;
  boardKey: string;
  agent: AgentId;
  ceiling: Ceiling;
  labelKey: string;
  requiresCsaNav: boolean;
}

export const LAUNCHER_TILES: LauncherTile[] = [
  {
    route: '/main/occupancy',
    boardKey: 'occupancy',
    agent: occupancyBoard.agent,
    ceiling: occupancyBoard.ceiling,
    labelKey: 'start.launcher.occupancy',
    requiresCsaNav: false,
  },
  {
    route: '/main/discharge',
    boardKey: 'discharge',
    agent: dischargeBoard.agent,
    ceiling: dischargeBoard.ceiling,
    labelKey: 'start.launcher.discharge',
    requiresCsaNav: false,
  },
  {
    route: '/main/bed-manager',
    boardKey: 'bed-manager',
    agent: bedManagerBoard.agent,
    ceiling: bedManagerBoard.ceiling,
    labelKey: 'start.launcher.bedManager',
    requiresCsaNav: false,
  },
  {
    route: '/main/or-steering',
    boardKey: 'or-steering',
    agent: orSteeringBoard.agent,
    ceiling: orSteeringBoard.ceiling,
    labelKey: 'start.launcher.orSteering',
    requiresCsaNav: false,
  },
  {
    route: '/main/staffing',
    boardKey: 'staffing',
    agent: staffingBoard.agent,
    ceiling: staffingBoard.ceiling,
    labelKey: 'start.launcher.staffing',
    requiresCsaNav: false,
  },
  {
    route: '/main/crisis',
    boardKey: 'crisis',
    agent: crisisBoard.agent,
    ceiling: crisisBoard.ceiling,
    labelKey: 'start.launcher.crisis',
    requiresCsaNav: true,
  },
];
