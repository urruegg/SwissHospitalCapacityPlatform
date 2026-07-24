import i18n from '../../../../i18n';
import type { GroundedReco } from '../../../../copilot-rail/reco';
import type { RoleBoard, RoleBoardData, ContextInsight } from '../../../../journey/RoleBoard';
import type { BedManagerPayload, PlacementRequest, PlacementBarrier } from '../../../../data/roleboard/bed-manager-data';
import { loadBedManager } from '../../../../data/roleboard/golden-source-client';

/** Sprint 20 (parity) — the bmca RoleBoard implementation (placement + bed-state). */
export const bedManagerBoard: RoleBoard<BedManagerPayload> = {
  agent: 'bmca-agent',
  ceiling: 'write',
  load: (scope, mode) => loadBedManager(scope, mode),

  insights: (data: RoleBoardData<BedManagerPayload>): ContextInsight[] => {
    const seen = new Set<string>();

    const placementInsights: ContextInsight[] = data.payload.placements.map(
      (r: PlacementRequest) => ({
        id: r.recoId,
        label: i18n.t('insight.placementMove', {
          patientId: r.patientId,
          fromWard: r.fromWard,
          toWard: r.toWard,
        }),
        context: {
          placement: r.id,
          patientId: r.patientId,
          fromWard: r.fromWard,
          toWard: r.toWard,
        },
      }),
    );

    const barrierInsights: ContextInsight[] = data.payload.barriers.map(
      (b: PlacementBarrier) => ({
        id: b.recoId,
        label: b.label,
        context: { barrier: b.id, bedImpact: b.bedImpact },
      }),
    );

    const gapInsight: ContextInsight = {
      id: 'placement-gap',
      label: i18n.t('bmca.gap.label'),
      context: { residualBeds: data.payload.residualBeds },
    };

    return [...placementInsights, ...barrierInsights, gapInsight].filter((ins) => {
      if (seen.has(ins.id)) return false;
      seen.add(ins.id);
      return true;
    });
  },

  askAbout: [
    i18n.t('bmca.askAbout.topPressure'),
    i18n.t('bmca.askAbout.placementQueue'),
    i18n.t('bmca.askAbout.slaRisk'),
  ],

  defaultReco: (data: RoleBoardData<BedManagerPayload>): GroundedReco =>
    data.payload.defaultReco,

  recoFor: (insight: ContextInsight, data: RoleBoardData<BedManagerPayload>): GroundedReco =>
    data.payload.recoById[insight.id] ?? data.payload.defaultReco,

  toHandoff: (data: RoleBoardData<BedManagerPayload>) => ({
    fromAgent: 'bmca-agent',
    headline: `${data.payload.bedsReallocated} beds reallocated, site still ${data.payload.residualBeds} beds`,
    metrics: { bedsReallocated: data.payload.bedsReallocated, deltaBeds: data.payload.residualBeds },
  }),

  fromHandoff: (prev) => ({
    situation: prev ? prev.headline : 'Bed reallocation',
    loopBackToOoa: false,
  }),
};
