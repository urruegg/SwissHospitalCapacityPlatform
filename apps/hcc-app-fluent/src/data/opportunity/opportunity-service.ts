import demo from './opportunity-demo.json';

export type OpportunityStatus =
  | 'new'
  | 'evaluating'
  | 'qualified'
  | 'onboarding'
  | 'won'
  | 'disqualified'
  | 'lost';

export interface OpportunityLatestEvent {
  at: string;
  by: string;
  event: string;
}

export interface OpportunityRow {
  id: string;
  hospitalName: string;
  archetype: string;
  status: OpportunityStatus;
  language: string;
  roiPct: number | null;
  poVerdict: string | null;
  latestEvent: OpportunityLatestEvent | null;
}

export type StatusCounts = Record<OpportunityStatus, number>;

export interface OpportunityPipeline {
  total: number;
  open: number;
  statusCounts: StatusCounts;
  weightedRoiPct: number | null;
  weightedRoiOpportunityCount: number;
  weightedRoiWeightSum: number;
  stageWeights: Record<OpportunityStatus, number>;
}

export interface OpportunityDataset {
  generatedAt: string;
  sourcePath: string;
  pipeline: OpportunityPipeline;
  opportunities: OpportunityRow[];
}

/** Sprint 33 WS-D D5 — committed app fixture for the Backstage opportunity pipeline. */
export function loadOpportunityDataset(): OpportunityDataset {
  return demo as OpportunityDataset;
}

export function getOpportunityPipeline(): OpportunityPipeline {
  return loadOpportunityDataset().pipeline;
}

export function listOpportunities(): OpportunityRow[] {
  return loadOpportunityDataset().opportunities;
}

export function getStatusCounts(): StatusCounts {
  return getOpportunityPipeline().statusCounts;
}

export function getWeightedRoi(): number | null {
  return getOpportunityPipeline().weightedRoiPct;
}
