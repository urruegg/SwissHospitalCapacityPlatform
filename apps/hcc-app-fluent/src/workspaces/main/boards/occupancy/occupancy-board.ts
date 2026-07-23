import i18n from '../../../../i18n';
import type { ContextInsight, RoleBoard, RoleBoardData } from '../../../../journey/RoleBoard';
import type { OccupancyPayload } from '../../../../data/roleboard/occupancy-data';
import { loadOccupancy } from '../../../../data/roleboard/golden-source-client';

/** Sprint 20 (parity) — the ooa RoleBoard implementation (occupancy foresight). */
export const occupancyBoard: RoleBoard<OccupancyPayload> = {
  agent: 'ooa-agent',
  ceiling: 'read',
  askAbout: [
    i18n.t('ooa.askAbout.wardTips'),
    i18n.t('ooa.askAbout.fluPeak'),
    i18n.t('ooa.askAbout.icuStaffing'),
  ],
  load: (scope, mode) => loadOccupancy(scope, mode),
  insights: (data: RoleBoardData<OccupancyPayload>) => {
    const wardInsights: ContextInsight[] = data.payload.wards.map((w) => ({
      id: w.recoId,
      label: i18n.t('insight.occupancyRising', { channel: w.label }),
      context: { channel: w.id, occupancyPct: w.forecastPct },
    }));
    const streamInsights: ContextInsight[] = data.payload.streams.map((st) => ({
      id: st.recoId,
      label: st.label,
      context: { stream: st.id, level: st.levelLabel },
    }));
    const gap: ContextInsight = {
      id: 'site-gap',
      label: i18n.t('ooa.gap.label'),
      context: { gapBeds: data.payload.capacity.gapBeds },
    };
    const seen = new Set<string>();
    return [...wardInsights, ...streamInsights, gap].filter((i) => {
      if (seen.has(i.id)) return false;
      seen.add(i.id);
      return true;
    });
  },
  defaultReco: (data: RoleBoardData<OccupancyPayload>) => data.payload.defaultReco,
  recoFor: (insight, data: RoleBoardData<OccupancyPayload>) =>
    data.payload.recoById[insight.id] ?? data.payload.recoById['site-gap'],
  toHandoff: (data: RoleBoardData<OccupancyPayload>) => {
    const lead = data.payload.wards[0];
    return {
      fromAgent: 'ooa-agent',
      headline: `${lead.label} -> ${lead.forecastPct}% in ${data.scope.windowHours}h, site ${data.payload.siteDeltaBeds} beds`,
      metrics: { occupancyPct: lead.forecastPct, deltaBeds: data.payload.siteDeltaBeds },
    };
  },
  fromHandoff: () => ({ situation: '72h occupancy forecast', loopBackToOoa: false }),
};
