import i18n from '../../../../i18n';
import type { GroundedReco } from '../../../../copilot-rail/reco';
import type { RoleBoard, RoleBoardData, ContextInsight } from '../../../../journey/RoleBoard';
import type { StaffingPayload } from '../../../../data/roleboard/staffing-data';
import { loadStaffing } from '../../../../data/roleboard/golden-source-client';

/** Sprint 3 (parity) — the sba RoleBoard implementation (staffing balance). */
export const staffingBoard: RoleBoard<StaffingPayload> = {
  agent: 'sba-agent',
  ceiling: 'write',
  load: (scope, mode) => loadStaffing(scope, mode),
  insights: (data: RoleBoardData<StaffingPayload>) =>
    data.payload.moves.map((m) => ({
      id: m.id,
      label: i18n.t('insight.staffShift', { role: m.role, fromUnit: m.fromUnit, toUnit: m.toUnit }),
      context: {
        move: m.id,
        fromUnit: m.fromUnit,
        toUnit: m.toUnit,
        role: m.role,
        fte: m.fte,
      },
    })),
  askAbout: [
    'What changed since last shift?',
    'Where is the biggest pressure?',
  ],
  defaultReco(): GroundedReco {
    return {
      agentLabel: 'Staffing Copilot',
      contextChip: { subject: 'Shift summary', tone: 'ok' },
      read: 'No proactive recommendation wired for this board yet (parity build focuses on occupancy).',
      levers: [],
      citations: [],
      provenance: 'simulated',
    };
  },
  recoFor(insight: ContextInsight): GroundedReco {
    return {
      agentLabel: 'Staffing Copilot',
      contextChip: { subject: insight.label, tone: 'watch' },
      read: `Context picked up for ${insight.label}. Detailed recommendation lands in a later sprint.`,
      levers: [],
      citations: [],
      provenance: 'simulated',
    };
  },
  toHandoff: (data: RoleBoardData<StaffingPayload>) => {
    const p = data.payload;
    return {
      fromAgent: 'sba-agent',
      headline: `${p.moves.length} staff moves enable ${p.surgeBedsEnabled} surge beds, site ${p.residualBeds === 0 ? 'balanced' : `still ${p.residualBeds} beds`}`,
      metrics: { surgeBedsEnabled: p.surgeBedsEnabled, deltaBeds: p.residualBeds },
    };
  },
  fromHandoff: (prev) => ({
    situation: prev ? prev.headline : 'Staffing balance',
    loopBackToOoa: false,
  }),
};
