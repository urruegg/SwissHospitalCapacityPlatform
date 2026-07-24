import i18n from '../../../../i18n';
import type { RoleBoard, RoleBoardData, ContextInsight } from '../../../../journey/RoleBoard';
import type { StaffingPayload } from '../../../../data/roleboard/staffing-data';
import { loadStaffing } from '../../../../data/roleboard/golden-source-client';

/** Sprint 20 (parity) — the sba RoleBoard implementation (staffing balance, ring-closer). */
export const staffingBoard: RoleBoard<StaffingPayload> = {
  agent: 'sba-agent',
  ceiling: 'write',
  load: (scope, mode) => loadStaffing(scope, mode),
  insights: (data: RoleBoardData<StaffingPayload>): ContextInsight[] => {
    const seen = new Set<string>();
    return data.payload.moves
      .map((m) => ({
        id: m.recoId,
        label: i18n.t('insight.staffShift', { role: m.role, fromUnit: m.fromUnit, toUnit: m.toUnit }),
        context: {
          move: m.id,
          fromUnit: m.fromUnit,
          toUnit: m.toUnit,
          role: m.role,
          fte: m.fte,
        },
      }))
      .filter((ins) => {
        if (seen.has(ins.id)) return false;
        seen.add(ins.id);
        return true;
      });
  },
  askAbout: [
    i18n.t('sba.askAbout.surgeGap'),
    i18n.t('sba.askAbout.orsaCoverage'),
    i18n.t('sba.askAbout.csaEscalation'),
  ],
  defaultReco: (data: RoleBoardData<StaffingPayload>) => data.payload.defaultReco,
  recoFor: (insight: ContextInsight, data: RoleBoardData<StaffingPayload>) =>
    data.payload.recoById[insight.id] ?? data.payload.defaultReco,
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
    loopBackToOoa: true, // SBA closes the ring; loops back to OOA (residual 0)
  }),
};
