import type { EvidenceStep, EvidenceTrace } from '../iq-client';

/**
 * Sprint 39 P2 (B3) — the bundled DC-EVIDENCE-TRACE-v1 demo fixture.
 *
 * Serves the Closed-Loop Evidence surface in Simulated mode (no agent-host
 * required), so the closed-loop proof is demoable offline. It mirrors the shape
 * of `closedloop.evidence.build_evidence_trace` exactly (the same contract the
 * Live endpoint returns), but authors the canonical demo WALK across the four
 * journey roles OOA -> DCA -> BMCA -> ORSA, all sharing ONE `golden_thread`, so
 * the reviewer sees one synthetic patient's flow close end-to-end. Provenance is
 * honestly `simulated` (ADR-0013 / ADR-0016 - PHI-free demo scope); the Live
 * trace carries the golden `simulated`/`live` badge the endpoint reports.
 *
 * `accept` = every step approved -> applied -> beds freed / case confirmed.
 * `deny`   = approval withheld -> nothing applied -> the breach persists.
 */

const GOLDEN_THREAD = 'gt-evd-demo-USZ';
const NOW = '1970-01-01T00:00:00Z';
const WARD = 'C3';

interface RoleWalk {
  role: string;
  agent: string;
  leverId: string;
  occupied: number;
  capacity: number;
  citations: string[];
  signal: string;
  insight: string;
  predicted: number;
  realised: number;
  metric: string;
  approver: string;
  bedsFreed: string[];
  discharged: string[];
  promoted: string[];
}

// The four canonical demo roles, in patient-journey order. Each carries a
// plausible, grounded read + a deterministic predicted impact; the DCA step is
// the one with a real bed-freeing effect (mirrors the backend's single lever).
const WALK: RoleWalk[] = [
  {
    role: 'ooa',
    agent: 'ooa-agent',
    leverId: 'OOA-FLAG-BREACH',
    occupied: 60,
    capacity: 58,
    citations: ['gold.fact_occupancy_forecast', 'gold.fact_capacity_baseline'],
    signal: '72h occupancy forecast breaches staffed capacity on C3 (60/58).',
    insight: 'Flag the C3 72h breach and hand off to discharge to free 3 beds.',
    predicted: 3,
    realised: 3,
    metric: 'beds',
    approver: 'ooa-lead',
    bedsFreed: [],
    discharged: [],
    promoted: [],
  },
  {
    role: 'dca',
    agent: 'dca-agent',
    leverId: 'DCA-UNBLOCK-BARRIER',
    occupied: 60,
    capacity: 58,
    citations: ['gold.fact_discharge_readiness', 'gold.bed_assignment'],
    signal: '3 discharge-ready patients on C3 blocked by transport barriers.',
    insight: 'Resolve 3 transport barriers to free 3 beds on C3.',
    predicted: 3,
    realised: 3,
    metric: 'beds',
    approver: 'alice',
    bedsFreed: ['C3-12', 'C3-14', 'C3-19'],
    discharged: ['PT-0001', 'PT-0007', 'PT-0011'],
    promoted: [],
  },
  {
    role: 'bmca',
    agent: 'bmca-agent',
    leverId: 'BMCA-PLACE-INBOUND',
    occupied: 57,
    capacity: 58,
    citations: ['gold.bed_assignment', 'gold.fact_capacity_baseline'],
    signal: '2 inbound placements waiting for the beds C3 just freed.',
    insight: 'Place 2 inbound patients into the freed C3 beds.',
    predicted: 2,
    realised: 2,
    metric: 'placements',
    approver: 'bmca-lead',
    bedsFreed: [],
    discharged: [],
    promoted: ['PT-2201', 'PT-2202'],
  },
  {
    role: 'orsa',
    agent: 'orsa-agent',
    leverId: 'ORSA-CONFIRM-CASE',
    occupied: 57,
    capacity: 58,
    citations: ['gold.fact_or_schedule', 'gold.bed_assignment'],
    signal: '1 elective OR case can proceed now C3 has a downstream bed.',
    insight: 'Confirm 1 elective case now the downstream bed exists.',
    predicted: 1,
    realised: 1,
    metric: 'cases',
    approver: 'orsa-lead',
    bedsFreed: [],
    discharged: [],
    promoted: ['OR-3390'],
  },
];

function stepFor(w: RoleWalk, branch: 'accept' | 'deny'): EvidenceStep {
  const accepted = branch === 'accept';
  return {
    role: w.role,
    agent: w.agent,
    journey_stage: 'DISCHARGE_READY',
    epic_input: {
      wardId: WARD,
      occupiedBeds: w.occupied,
      bedCapacity: w.capacity,
      citations: w.citations,
      provenance: 'simulated',
    },
    agent_read: { signal: w.signal },
    recommendation: {
      lever_id: w.leverId,
      params: { ward: WARD },
      predicted_impact: { metric: w.metric, value: w.predicted },
      insight_text: w.insight,
    },
    copilot: {
      requiresApproval: true,
      decision: branch,
      approver: accepted ? w.approver : '',
      decision_ts: NOW,
    },
    action: { status: accepted ? 'applied' : 'denied' },
    outcome: {
      contract: 'DC-SIM-OUTCOME-v1',
      golden_thread: GOLDEN_THREAD,
      lever_id: w.leverId,
      applied_ts: NOW,
      predicted_impact: { metric: w.metric, value: w.predicted },
      realised_impact: { metric: w.metric, value: accepted ? w.realised : 0 },
      state_delta: accepted
        ? { beds_freed: w.bedsFreed, patients_discharged: w.discharged, patients_promoted: w.promoted }
        : { beds_freed: [], patients_discharged: [], patients_promoted: [] },
      divergence: 0,
      provenance: 'simulated',
      applied: accepted,
    },
  };
}

/**
 * Build the bundled demo trace for `branch`. Deterministic + PHI-free; the same
 * `golden_thread` threads all four steps so the demo walk reads as one patient's
 * closed loop.
 */
export function evidenceTraceFixture(branch: 'accept' | 'deny'): EvidenceTrace {
  return {
    contract: 'DC-EVIDENCE-TRACE-v1',
    golden_thread: GOLDEN_THREAD,
    patient: { synthetic_id: 'PT-0001', specialty: 'General medicine', provenance: 'simulated' },
    branch,
    generated_ts: NOW,
    steps: WALK.map((w) => stepFor(w, branch)),
  };
}
