/**
 * Sprint 14.1 · T5 — Showcase Evidence card payload contracts.
 *
 * Mirrors the shape emitted by `scripts/evidence/build_app_fixture.py` into
 * `evidence-demo.json`. Every card payload carries {@link EvidenceProvenance}
 * so the whiteboard's provenance contract (design spec §5, §10) can render
 * `sourceUrl` + `asOf` on every card and fail visibly when either is missing.
 */

export interface EvidenceProvenance {
  /** Clickable source-of-truth URL (repo blob or GA-evidence source). */
  sourceUrl: string;
  /** Repo-relative path the fact was parsed from. */
  sourcePath?: string;
  /** ISO date the evidence was curated / snapshotted. */
  asOf: string;
}

export type ReadinessStatus = 'Ready' | 'Blocked';
export type Maturity = 'GA' | 'Preview' | 'NotAvailable';

export interface ReadinessResult {
  status: ReadinessStatus;
  region: string;
  showcaseOnly: boolean;
  blockingReason: string | null;
}

export interface RegionChip {
  region: string;
  maturity: Maturity;
}

export interface BomCardPayload {
  id: string;
  name: string;
  type: string;
  category: string;
  sku?: string | null;
  regionChip: RegionChip | null;
  dependencyCount: number;
  realisesRequirements: string[];
  governedByAdrs: string[];
  readiness: { tShow?: ReadinessResult; tProd?: ReadinessResult };
  provenance: EvidenceProvenance;
}

export interface AdrCardPayload {
  id: string;
  title: string;
  status: string;
  decisionSummary: string;
  provenance: EvidenceProvenance;
}

export interface PrdRequirementCardPayload {
  id: string;
  kind: string;
  family: string;
  title: string;
  mvp: boolean;
  provenance: EvidenceProvenance;
}

export interface GaEvidenceCardPayload {
  bomId: string;
  region: string;
  maturity: Maturity;
  verifiedBy: string;
  provenance: EvidenceProvenance;
}

export interface DependencyEdgePayload {
  fromId: string;
  toId: string;
  type: string;
  provenance: EvidenceProvenance;
}

export interface ReadinessSummaryRow {
  track: string;
  readyCount: number;
  total: number;
  readyPct: number;
}

export interface EvidenceDataset {
  generatedAt: string;
  summary: ReadinessSummaryRow[];
  boms: BomCardPayload[];
  adrs: AdrCardPayload[];
  requirements: PrdRequirementCardPayload[];
  gaEvidence: GaEvidenceCardPayload[];
  dependencies: DependencyEdgePayload[];
}
