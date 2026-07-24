import i18n from '../../../../i18n';
import type { GroundedReco } from '../../../../copilot-rail/reco';
import type { RoleBoard, RoleBoardData, ContextInsight } from '../../../../journey/RoleBoard';
import type { CrisisPayload } from '../../../../data/roleboard/crisis-data';
import { sortScenarios } from '../../../../data/roleboard/crisis-data';
import { loadCrisis } from '../../../../data/roleboard/golden-source-client';

/** Sprint 20 M5 (parity) — the csa RoleBoard implementation (crisis readiness). */
export const crisisBoard: RoleBoard<CrisisPayload> = {
  agent: 'csa-agent',
  ceiling: 'deploy',
  load: (scope, mode) => loadCrisis(scope, mode),
  insights: (data: RoleBoardData<CrisisPayload>): ContextInsight[] => {
    const filteredSignalIds = new Set(
      data.payload.signals.filter((s) => s.filtered).map((s) => s.id),
    );
    // Scenarios whose triggerSignal is a filtered/quarantined signal do NOT produce an armed insight
    return data.payload.scenarios
      .filter((s) => !s.triggerSignal || !filteredSignalIds.has(s.triggerSignal))
      .map((s) => ({
        id: s.id,
        label: i18n.t('insight.stressTest', { scenario: s.name }),
        context: {
          scenario: s.id,
          probability: s.probability,
          bedImpact: s.bedImpact,
        },
      }));
  },
  askAbout: [
    i18n.t('csa.askAbout.heatwaveImpact'),
    i18n.t('csa.askAbout.signalReadiness'),
    i18n.t('csa.askAbout.scenarioSimulation'),
  ],
  defaultReco: (data: RoleBoardData<CrisisPayload>): GroundedReco => data.payload.defaultReco,
  recoFor: (insight: ContextInsight, data: RoleBoardData<CrisisPayload>): GroundedReco =>
    data.payload.recoById[insight.id] ?? data.payload.defaultReco,
  toHandoff: (data: RoleBoardData<CrisisPayload>) => {
    const top = sortScenarios(data.payload.scenarios)[0];
    return {
      fromAgent: 'csa-agent',
      headline: `${top.name} p=${top.probability}% would add ${top.bedImpact} bed-days - loop back to occupancy`,
      metrics: { probability: top.probability, bedImpact: top.bedImpact },
    };
  },
  fromHandoff: (prev) => ({
    situation: prev ? prev.headline : 'Crisis readiness',
    loopBackToOoa: true,
  }),
};
