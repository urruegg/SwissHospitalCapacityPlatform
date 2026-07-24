import type { GroundedReco } from '../copilot-rail/reco';

/**
 * Sprint 1 (parity) — the FROZEN per-surface contract. Every MAIN role board
 * implements this identical shape so later role sprints are parallelizable.
 */
export type AgentId =
  | 'ooa-agent' | 'dca-agent' | 'bmca-agent'
  | 'orsa-agent' | 'sba-agent' | 'csa-agent';

export type Ceiling = 'read' | 'write' | 'deploy';
export type Provenance = 'live' | 'simulated';
export type Mode = 'demo' | 'user';

export interface ScenarioScope {
  hospital: string;      // hospital scope id (from hospital-context)
  windowHours: number;   // forecast/observation window (Demo pins this)
  pinned: boolean;       // true when Demo pins the golden-thread slice
}

export interface RoleBoardData<P = unknown> {
  provenance: Provenance;   // set by the data layer, never by a component
  scope: ScenarioScope;
  payload: P;               // board-specific, contract-typed per role
}

export interface ContextInsight {
  id: string;
  label: string;                       // e.g. "Medicine A rising"
  context: Record<string, unknown>;    // sent to the agent on click
}

export interface ResidualPressure {
  fromAgent: AgentId;
  headline: string;                    // e.g. "site -16 beds"
  metrics: Record<string, number>;
}

export interface BannerContext {
  situation: string;
  loopBackToOoa: boolean;
}

export interface RoleBoard<P = unknown> {
  agent: AgentId;
  ceiling: Ceiling;
  /** Prompts shown as ask-about chips in the docked rail. */
  askAbout: string[];
  load(scope: ScenarioScope, mode: Mode): Promise<RoleBoardData<P>>;
  insights(data: RoleBoardData<P>): ContextInsight[];
  /** Proactive reco shown when the rail first opens (no insight clicked). */
  defaultReco(data: RoleBoardData<P>): GroundedReco;
  /** Grounded reco for a clicked insight; deterministic, from trusted data. */
  recoFor(insight: ContextInsight, data: RoleBoardData<P>): GroundedReco;
  toHandoff(data: RoleBoardData<P>): ResidualPressure;
  fromHandoff(prev: ResidualPressure | null): BannerContext;
}