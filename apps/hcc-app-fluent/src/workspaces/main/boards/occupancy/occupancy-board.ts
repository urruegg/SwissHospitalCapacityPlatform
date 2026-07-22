import i18n from '../../../../i18n';
import type { RoleBoard, RoleBoardData } from '../../../../journey/RoleBoard';
import type { OccupancyPayload } from '../../../../data/roleboard/occupancy-data';
import { loadOccupancy } from '../../../../data/roleboard/golden-source-client';

/** Sprint 1 (parity) — the ooa RoleBoard implementation (occupancy foresight). */
export const occupancyBoard: RoleBoard<OccupancyPayload> = {
  agent: 'ooa-agent',
  ceiling: 'read',
  load: (scope, mode) => loadOccupancy(scope, mode),
  insights: (data: RoleBoardData<OccupancyPayload>) =>
    data.payload.channels
      .filter((c) => c.occupancyPct >= 100)
      .map((c) => ({
        id: c.id,
        label: i18n.t('insight.occupancyRising', { channel: c.label }),
        context: { channel: c.id, occupancyPct: c.occupancyPct, deltaBeds: c.deltaBeds },
      })),
  toHandoff: (data: RoleBoardData<OccupancyPayload>) => {
    const lead = data.payload.channels[0];
    return {
      fromAgent: 'ooa-agent',
      headline: `${lead.label} -> ${lead.occupancyPct}% in ${data.scope.windowHours}h, site ${data.payload.siteDeltaBeds} beds`,
      metrics: { occupancyPct: lead.occupancyPct, deltaBeds: data.payload.siteDeltaBeds },
    };
  },
  fromHandoff: () => ({ situation: '72h occupancy forecast', loopBackToOoa: false }),
};
