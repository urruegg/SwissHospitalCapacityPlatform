import i18n from '../../../../i18n';
import type { GroundedReco } from '../../../../copilot-rail/reco';
import type { RoleBoard, RoleBoardData, ContextInsight } from '../../../../journey/RoleBoard';
import type { BedManagerPayload } from '../../../../data/roleboard/bed-manager-data';
import { loadBedManager } from '../../../../data/roleboard/golden-source-client';

/** Sprint 2 (parity) — the bmca RoleBoard implementation (bed reallocation). */
export const bedManagerBoard: RoleBoard<BedManagerPayload> = {
  agent: 'bmca-agent',
  ceiling: 'write',
  load: (scope, mode) => loadBedManager(scope, mode),
  insights: (data: RoleBoardData<BedManagerPayload>) =>
    data.payload.reallocations.map((r) => ({
      id: r.id,
      label: i18n.t('insight.bedShift', { beds: r.beds, fromWard: r.fromWard, toWard: r.toWard }),
      context: {
        reallocation: r.id,
        fromWard: r.fromWard,
        toWard: r.toWard,
        beds: r.beds,
      },
    })),
  askAbout: [
    'What changed since last shift?',
    'Where is the biggest pressure?',
  ],
  defaultReco(): GroundedReco {
    return {
      agentLabel: 'Bed Management Copilot',
      contextChip: { subject: 'Shift summary', tone: 'ok' },
      read: 'No proactive recommendation wired for this board yet (parity build focuses on occupancy).',
      levers: [],
      citations: [],
      provenance: 'simulated',
    };
  },
  recoFor(insight: ContextInsight): GroundedReco {
    return {
      agentLabel: 'Bed Management Copilot',
      contextChip: { subject: insight.label, tone: 'watch' },
      read: `Context picked up for ${insight.label}. Detailed recommendation lands in a later sprint.`,
      levers: [],
      citations: [],
      provenance: 'simulated',
    };
  },
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
