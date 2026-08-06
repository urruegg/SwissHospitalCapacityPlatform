export type StartSectionId =
  | 'hero'
  | 'challenger'
  | 'vision'
  | 'work-chart'
  | 'cio-why-now'
  | 'hospitals'
  | 'patient-path'
  | 'ninety-day'
  | 'bva';

export type StartSectionKind = 'static' | 'data' | 'launcher';

export interface StartSection {
  id: StartSectionId;
  titleKey: string;
  kind: StartSectionKind;
}

export const START_SECTIONS = [
  { id: 'hero', titleKey: 'start.frontier.hero.title', kind: 'data' },
  { id: 'challenger', titleKey: 'start.frontier.challenger.title', kind: 'static' },
  { id: 'vision', titleKey: 'start.frontier.vision.title', kind: 'static' },
  { id: 'work-chart', titleKey: 'start.frontier.workChart.title', kind: 'static' },
  { id: 'cio-why-now', titleKey: 'start.frontier.cioWhyNow.title', kind: 'static' },
  { id: 'hospitals', titleKey: 'start.frontier.hospitals.title', kind: 'static' },
  { id: 'patient-path', titleKey: 'start.frontier.patientPath.title', kind: 'launcher' },
  { id: 'ninety-day', titleKey: 'start.frontier.ninetyDay.title', kind: 'static' },
  { id: 'bva', titleKey: 'start.frontier.bva.title', kind: 'data' },
] as const satisfies readonly StartSection[];

/**
 * Sprint 40 START polish — the mockup's "The room pushed back" challenger roster.
 * Six real, dated, attributed review-session challengers, each a tab in the section.
 * All copy is i18n-keyed under `start.frontier.challenger.personas.<id>.*`. The two
 * German-origin quotes (CIO Furler, CISO von Buren) carry an English gloss via
 * `hasGloss`; the authentic quotes are kept verbatim and are never machine-translated.
 * `accent` maps to the mockup tag colour (navy for most, green for hospital operations).
 */
export type ChallengerPersonaId = 'coo' | 'cio' | 'cto' | 'ciso' | 'ops' | 'it';

export interface ChallengerPersona {
  id: ChallengerPersonaId;
  accent: 'navy' | 'green';
  /** True when the quote is German-origin and carries a separate English gloss. */
  hasGloss: boolean;
}

export const CHALLENGER_PERSONAS = [
  { id: 'coo', accent: 'navy', hasGloss: false },
  { id: 'cio', accent: 'navy', hasGloss: true },
  { id: 'cto', accent: 'navy', hasGloss: false },
  { id: 'ciso', accent: 'navy', hasGloss: true },
  { id: 'ops', accent: 'green', hasGloss: false },
  { id: 'it', accent: 'navy', hasGloss: false },
] as const satisfies readonly ChallengerPersona[];

/**
 * Sprint 40 START polish — the mockup's "Why Curavias exists" (vision & mission)
 * section. Three data groups back it:
 *  - VISION_WORD_ROWS: the cura/via/curavias etymology table. The Latin term is the
 *    row `id` (a proper noun rendered verbatim, never translated); meaning + product
 *    columns are i18n chrome.
 *  - VISION_MARK_STEPS: the three-step logo journey (Start -> Care -> Success); the
 *    final Success step is `highlighted` (mockup `.mstep.on`).
 *  - VISION_PILLS: the closing advisory/human/swiss guarantees. Each pill is a fixed
 *    EN|DE bilingual brand statement (label + echo, identical across locales per the
 *    challenger's Approach B); the swiss pill carries the CH flag.
 * The vision + mission statements themselves are likewise bilingual brand copy carried
 * as `start.frontier.vision.{vision,mission}.{primary,echo}` (identical en/de).
 */
export type VisionWordId = 'cura' | 'via' | 'curavias';

export interface VisionWordRow {
  id: VisionWordId;
  meaningKey: `start.frontier.vision.word.rows.${VisionWordId}.meaning`;
  productKey: `start.frontier.vision.word.rows.${VisionWordId}.product`;
}

export const VISION_WORD_ROWS = [
  {
    id: 'cura',
    meaningKey: 'start.frontier.vision.word.rows.cura.meaning',
    productKey: 'start.frontier.vision.word.rows.cura.product',
  },
  {
    id: 'via',
    meaningKey: 'start.frontier.vision.word.rows.via.meaning',
    productKey: 'start.frontier.vision.word.rows.via.product',
  },
  {
    id: 'curavias',
    meaningKey: 'start.frontier.vision.word.rows.curavias.meaning',
    productKey: 'start.frontier.vision.word.rows.curavias.product',
  },
] as const satisfies readonly VisionWordRow[];

export type VisionMarkStepId = 'start' | 'care' | 'success';

export interface VisionMarkStep {
  id: VisionMarkStepId;
  labelKey: `start.frontier.vision.mark.steps.${VisionMarkStepId}.label`;
  captionKey: `start.frontier.vision.mark.steps.${VisionMarkStepId}.caption`;
  /** True for the final Success step (mockup `.mstep.on`). */
  highlighted: boolean;
}

export const VISION_MARK_STEPS = [
  {
    id: 'start',
    labelKey: 'start.frontier.vision.mark.steps.start.label',
    captionKey: 'start.frontier.vision.mark.steps.start.caption',
    highlighted: false,
  },
  {
    id: 'care',
    labelKey: 'start.frontier.vision.mark.steps.care.label',
    captionKey: 'start.frontier.vision.mark.steps.care.caption',
    highlighted: false,
  },
  {
    id: 'success',
    labelKey: 'start.frontier.vision.mark.steps.success.label',
    captionKey: 'start.frontier.vision.mark.steps.success.caption',
    highlighted: true,
  },
] as const satisfies readonly VisionMarkStep[];

export type VisionPillId = 'advisory' | 'human' | 'swiss';

export interface VisionPill {
  id: VisionPillId;
  labelKey: `start.frontier.vision.pills.${VisionPillId}.label`;
  echoKey: `start.frontier.vision.pills.${VisionPillId}.echo`;
  /** True for the Swiss-residency pill (mockup CH flag prefix). */
  flag: boolean;
}

export const VISION_PILLS = [
  {
    id: 'advisory',
    labelKey: 'start.frontier.vision.pills.advisory.label',
    echoKey: 'start.frontier.vision.pills.advisory.echo',
    flag: false,
  },
  {
    id: 'human',
    labelKey: 'start.frontier.vision.pills.human.label',
    echoKey: 'start.frontier.vision.pills.human.echo',
    flag: false,
  },
  {
    id: 'swiss',
    labelKey: 'start.frontier.vision.pills.swiss.label',
    echoKey: 'start.frontier.vision.pills.swiss.echo',
    flag: true,
  },
] as const satisfies readonly VisionPill[];

export interface PatientPathOperationalStop {
  boardKey: string;
  bodyKey: string;
  /** Operational step name shown under the circular node (mockup `.jtitle`). */
  stepKey: string;
  /** Evidence chip shown on the node (mockup `.jevi`). */
  evidenceKey: string;
}

export const PATIENT_PATH_OPERATIONAL_STOPS = [
  {
    boardKey: 'occupancy',
    bodyKey: 'start.patientPath.operational.occupancy',
    stepKey: 'start.patientPath.stops.occupancy.step',
    evidenceKey: 'start.patientPath.stops.occupancy.evidence',
  },
  {
    boardKey: 'bed-manager',
    bodyKey: 'start.patientPath.operational.bedManager',
    stepKey: 'start.patientPath.stops.bedManager.step',
    evidenceKey: 'start.patientPath.stops.bedManager.evidence',
  },
  {
    boardKey: 'or-steering',
    bodyKey: 'start.patientPath.operational.orSteering',
    stepKey: 'start.patientPath.stops.orSteering.step',
    evidenceKey: 'start.patientPath.stops.orSteering.evidence',
  },
  {
    boardKey: 'staffing',
    bodyKey: 'start.patientPath.operational.staffing',
    stepKey: 'start.patientPath.stops.staffing.step',
    evidenceKey: 'start.patientPath.stops.staffing.evidence',
  },
  {
    boardKey: 'discharge',
    bodyKey: 'start.patientPath.operational.discharge',
    stepKey: 'start.patientPath.stops.discharge.step',
    evidenceKey: 'start.patientPath.stops.discharge.evidence',
  },
] as const satisfies readonly PatientPathOperationalStop[];

export type DcInsightBeatId = 'signal' | 'understanding' | 'recommendation' | 'action' | 'coordination';

export interface DcInsightBeat {
  id: DcInsightBeatId;
  labelKey: `start.patientPath.dcInsight.beats.${DcInsightBeatId}.label`;
  bodyKey: `start.patientPath.dcInsight.beats.${DcInsightBeatId}.body`;
}

export const DC_INSIGHT_BEATS = [
  {
    id: 'signal',
    labelKey: 'start.patientPath.dcInsight.beats.signal.label',
    bodyKey: 'start.patientPath.dcInsight.beats.signal.body',
  },
  {
    id: 'understanding',
    labelKey: 'start.patientPath.dcInsight.beats.understanding.label',
    bodyKey: 'start.patientPath.dcInsight.beats.understanding.body',
  },
  {
    id: 'recommendation',
    labelKey: 'start.patientPath.dcInsight.beats.recommendation.label',
    bodyKey: 'start.patientPath.dcInsight.beats.recommendation.body',
  },
  {
    id: 'action',
    labelKey: 'start.patientPath.dcInsight.beats.action.label',
    bodyKey: 'start.patientPath.dcInsight.beats.action.body',
  },
  {
    id: 'coordination',
    labelKey: 'start.patientPath.dcInsight.beats.coordination.label',
    bodyKey: 'start.patientPath.dcInsight.beats.coordination.body',
  },
] as const satisfies readonly DcInsightBeat[];

export type WorkModeId = 'humans' | 'agents' | 'on-demand';

export interface WorkMode {
  id: WorkModeId;
  titleKey: `start.frontier.workChart.modes.${WorkModeId}.title`;
  bodyKey: `start.frontier.workChart.modes.${WorkModeId}.body`;
}

export const WORK_MODES = [
  {
    id: 'humans',
    titleKey: 'start.frontier.workChart.modes.humans.title',
    bodyKey: 'start.frontier.workChart.modes.humans.body',
  },
  {
    id: 'agents',
    titleKey: 'start.frontier.workChart.modes.agents.title',
    bodyKey: 'start.frontier.workChart.modes.agents.body',
  },
  {
    id: 'on-demand',
    titleKey: 'start.frontier.workChart.modes.on-demand.title',
    bodyKey: 'start.frontier.workChart.modes.on-demand.body',
  },
] as const satisfies readonly WorkMode[];

// Mockup "How Curavias fits the Microsoft Frontier Firm" fit table
// (Frontier Firm principle -> concrete Curavias realisation). Advisory framing;
// all four rows are qualitative, no live business metrics.
export type WorkChartFitRowId = 'teams' | 'bosses' | 'on-demand' | 'trust';

export interface WorkChartFitRow {
  id: WorkChartFitRowId;
  principleKey: `start.frontier.workChart.fit.rows.${WorkChartFitRowId}.principle`;
  curaviasKey: `start.frontier.workChart.fit.rows.${WorkChartFitRowId}.curavias`;
}

export const WORK_CHART_FIT_ROWS = [
  {
    id: 'teams',
    principleKey: 'start.frontier.workChart.fit.rows.teams.principle',
    curaviasKey: 'start.frontier.workChart.fit.rows.teams.curavias',
  },
  {
    id: 'bosses',
    principleKey: 'start.frontier.workChart.fit.rows.bosses.principle',
    curaviasKey: 'start.frontier.workChart.fit.rows.bosses.curavias',
  },
  {
    id: 'on-demand',
    principleKey: 'start.frontier.workChart.fit.rows.on-demand.principle',
    curaviasKey: 'start.frontier.workChart.fit.rows.on-demand.curavias',
  },
  {
    id: 'trust',
    principleKey: 'start.frontier.workChart.fit.rows.trust.principle',
    curaviasKey: 'start.frontier.workChart.fit.rows.trust.curavias',
  },
] as const satisfies readonly WorkChartFitRow[];

export type CioDecisionId =
  | 'bed-allocation'
  | 'or-slots'
  | 'staffing'
  | 'discharge'
  | 'transfers'
  | 'crisis'
  | 'data-quality';

export interface CioDecision {
  id: CioDecisionId;
  decisionKey: `start.frontier.cioWhyNow.decisions.${CioDecisionId}.decision`;
  todayKey: `start.frontier.cioWhyNow.decisions.${CioDecisionId}.today`;
  previewKey: `start.frontier.cioWhyNow.decisions.${CioDecisionId}.preview`;
}

export const CIO_DECISIONS = [
  {
    id: 'bed-allocation',
    decisionKey: 'start.frontier.cioWhyNow.decisions.bed-allocation.decision',
    todayKey: 'start.frontier.cioWhyNow.decisions.bed-allocation.today',
    previewKey: 'start.frontier.cioWhyNow.decisions.bed-allocation.preview',
  },
  {
    id: 'or-slots',
    decisionKey: 'start.frontier.cioWhyNow.decisions.or-slots.decision',
    todayKey: 'start.frontier.cioWhyNow.decisions.or-slots.today',
    previewKey: 'start.frontier.cioWhyNow.decisions.or-slots.preview',
  },
  {
    id: 'staffing',
    decisionKey: 'start.frontier.cioWhyNow.decisions.staffing.decision',
    todayKey: 'start.frontier.cioWhyNow.decisions.staffing.today',
    previewKey: 'start.frontier.cioWhyNow.decisions.staffing.preview',
  },
  {
    id: 'discharge',
    decisionKey: 'start.frontier.cioWhyNow.decisions.discharge.decision',
    todayKey: 'start.frontier.cioWhyNow.decisions.discharge.today',
    previewKey: 'start.frontier.cioWhyNow.decisions.discharge.preview',
  },
  {
    id: 'transfers',
    decisionKey: 'start.frontier.cioWhyNow.decisions.transfers.decision',
    todayKey: 'start.frontier.cioWhyNow.decisions.transfers.today',
    previewKey: 'start.frontier.cioWhyNow.decisions.transfers.preview',
  },
  {
    id: 'crisis',
    decisionKey: 'start.frontier.cioWhyNow.decisions.crisis.decision',
    todayKey: 'start.frontier.cioWhyNow.decisions.crisis.today',
    previewKey: 'start.frontier.cioWhyNow.decisions.crisis.preview',
  },
  {
    id: 'data-quality',
    decisionKey: 'start.frontier.cioWhyNow.decisions.data-quality.decision',
    todayKey: 'start.frontier.cioWhyNow.decisions.data-quality.today',
    previewKey: 'start.frontier.cioWhyNow.decisions.data-quality.preview',
  },
] as const satisfies readonly CioDecision[];

export type FrontierHospitalId = 'curanova' | 'curalp' | 'vialta';

export interface FrontierHospital {
  id: FrontierHospitalId;
  nameKey: `start.frontier.hospitals.sites.${FrontierHospitalId}.name`;
  profileKey: `start.frontier.hospitals.sites.${FrontierHospitalId}.profile`;
  /** Synthetic aggregate hard-facts row (mockup `.metarow`): beds / FTE / sites. */
  factsKey: `start.frontier.hospitals.sites.${FrontierHospitalId}.facts`;
  focusKey: `start.frontier.hospitals.sites.${FrontierHospitalId}.focus`;
}

export const FRONTIER_HOSPITALS = [
  {
    id: 'curanova',
    nameKey: 'start.frontier.hospitals.sites.curanova.name',
    profileKey: 'start.frontier.hospitals.sites.curanova.profile',
    factsKey: 'start.frontier.hospitals.sites.curanova.facts',
    focusKey: 'start.frontier.hospitals.sites.curanova.focus',
  },
  {
    id: 'curalp',
    nameKey: 'start.frontier.hospitals.sites.curalp.name',
    profileKey: 'start.frontier.hospitals.sites.curalp.profile',
    factsKey: 'start.frontier.hospitals.sites.curalp.facts',
    focusKey: 'start.frontier.hospitals.sites.curalp.focus',
  },
  {
    id: 'vialta',
    nameKey: 'start.frontier.hospitals.sites.vialta.name',
    profileKey: 'start.frontier.hospitals.sites.vialta.profile',
    factsKey: 'start.frontier.hospitals.sites.vialta.facts',
    focusKey: 'start.frontier.hospitals.sites.vialta.focus',
  },
] as const satisfies readonly FrontierHospital[];

/**
 * Per-hospital operating-role rows (mockup `.row-mini`): every synthetic
 * hospital runs the same four-role shape — two human roles (bed side / ops
 * side), the runtime agents, and the Product Owner Agent. The concrete labels
 * differ per hospital and resolve from
 * `start.frontier.hospitals.sites.<id>.roles.<roleId>`.
 */
export type FrontierHospitalRoleId = 'bedside' | 'opsside' | 'agents' | 'po';

/** Visual accent family for a role row (mockup: human=navy, agent=green, po=violet). */
export type FrontierHospitalRoleKind = 'human' | 'agent' | 'po';

export interface FrontierHospitalRole {
  roleId: FrontierHospitalRoleId;
  kind: FrontierHospitalRoleKind;
}

export const FRONTIER_HOSPITAL_ROLES = [
  { roleId: 'bedside', kind: 'human' },
  { roleId: 'opsside', kind: 'human' },
  { roleId: 'agents', kind: 'agent' },
  { roleId: 'po', kind: 'po' },
] as const satisfies readonly FrontierHospitalRole[];

export type FrontierAgentId =
  | 'ooa-agent'
  | 'bmca-agent'
  | 'dca-agent'
  | 'orsa-agent'
  | 'sba-agent'
  | 'csa-agent'
  | 'data-quality-agent';

export interface FrontierAgent {
  id: FrontierAgentId;
  nameKey: `start.frontier.hospitals.agents.${FrontierAgentId}.name`;
  roleKey: `start.frontier.hospitals.agents.${FrontierAgentId}.role`;
}

export const FRONTIER_AGENTS = [
  {
    id: 'ooa-agent',
    nameKey: 'start.frontier.hospitals.agents.ooa-agent.name',
    roleKey: 'start.frontier.hospitals.agents.ooa-agent.role',
  },
  {
    id: 'bmca-agent',
    nameKey: 'start.frontier.hospitals.agents.bmca-agent.name',
    roleKey: 'start.frontier.hospitals.agents.bmca-agent.role',
  },
  {
    id: 'dca-agent',
    nameKey: 'start.frontier.hospitals.agents.dca-agent.name',
    roleKey: 'start.frontier.hospitals.agents.dca-agent.role',
  },
  {
    id: 'orsa-agent',
    nameKey: 'start.frontier.hospitals.agents.orsa-agent.name',
    roleKey: 'start.frontier.hospitals.agents.orsa-agent.role',
  },
  {
    id: 'sba-agent',
    nameKey: 'start.frontier.hospitals.agents.sba-agent.name',
    roleKey: 'start.frontier.hospitals.agents.sba-agent.role',
  },
  {
    id: 'csa-agent',
    nameKey: 'start.frontier.hospitals.agents.csa-agent.name',
    roleKey: 'start.frontier.hospitals.agents.csa-agent.role',
  },
  {
    id: 'data-quality-agent',
    nameKey: 'start.frontier.hospitals.agents.data-quality-agent.name',
    roleKey: 'start.frontier.hospitals.agents.data-quality-agent.role',
  },
] as const satisfies readonly FrontierAgent[];

export type NinetyDayPhaseId = 'frame-ground' | 'build-prove' | 'operate-scale';
export type NinetyDayOutcomeId =
  | 'decision-map'
  | 'governance-baseline'
  | 'workflow-slices'
  | 'control-findings'
  | 'adoption-playbook'
  | 'scale-decision';

export interface NinetyDayPhase {
  id: NinetyDayPhaseId;
  titleKey: `start.frontier.ninetyDay.phases.${NinetyDayPhaseId}.title`;
  rangeKey: `start.frontier.ninetyDay.phases.${NinetyDayPhaseId}.range`;
  bodyKey: `start.frontier.ninetyDay.phases.${NinetyDayPhaseId}.body`;
  outcomeKeys: readonly [
    `start.frontier.ninetyDay.phases.${NinetyDayPhaseId}.outcomes.${NinetyDayOutcomeId}`,
    `start.frontier.ninetyDay.phases.${NinetyDayPhaseId}.outcomes.${NinetyDayOutcomeId}`,
  ];
}

export const NINETY_DAY_PHASES = [
  {
    id: 'frame-ground',
    titleKey: 'start.frontier.ninetyDay.phases.frame-ground.title',
    rangeKey: 'start.frontier.ninetyDay.phases.frame-ground.range',
    bodyKey: 'start.frontier.ninetyDay.phases.frame-ground.body',
    outcomeKeys: [
      'start.frontier.ninetyDay.phases.frame-ground.outcomes.decision-map',
      'start.frontier.ninetyDay.phases.frame-ground.outcomes.governance-baseline',
    ],
  },
  {
    id: 'build-prove',
    titleKey: 'start.frontier.ninetyDay.phases.build-prove.title',
    rangeKey: 'start.frontier.ninetyDay.phases.build-prove.range',
    bodyKey: 'start.frontier.ninetyDay.phases.build-prove.body',
    outcomeKeys: [
      'start.frontier.ninetyDay.phases.build-prove.outcomes.workflow-slices',
      'start.frontier.ninetyDay.phases.build-prove.outcomes.control-findings',
    ],
  },
  {
    id: 'operate-scale',
    titleKey: 'start.frontier.ninetyDay.phases.operate-scale.title',
    rangeKey: 'start.frontier.ninetyDay.phases.operate-scale.range',
    bodyKey: 'start.frontier.ninetyDay.phases.operate-scale.body',
    outcomeKeys: [
      'start.frontier.ninetyDay.phases.operate-scale.outcomes.adoption-playbook',
      'start.frontier.ninetyDay.phases.operate-scale.outcomes.scale-decision',
    ],
  },
] as const satisfies readonly NinetyDayPhase[];
