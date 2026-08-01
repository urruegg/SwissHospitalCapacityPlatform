import { afterEach, describe, expect, it, vi } from 'vitest';
import { iqEvidence } from '../../src/data/iq-client';
import type { ContextEnvelope } from '../../src/context/context-envelope';

/**
 * Sprint 39 P2 (B3) — the closed-loop evidence read wire contract. The IQ gateway
 * is the only permitted fetch site (ingress guard), so the evidence GET lives in
 * iq-client. Asserts the exact URL (`/agents/{role}/evidence?branch=...&hospital=...`),
 * the scoped identity headers, and the fail-loud behaviour on an HTTP error.
 */
const env: ContextEnvelope = {
  userOid: 'oid-123',
  heldRoles: ['HCC.DischargeCoordinator'],
  activeRole: 'HCC.DischargeCoordinator',
  hospitalScope: 'usz',
  dataSource: 'live',
  agent: 'dca-agent',
  windowHours: 72,
};

const identity = {
  'X-User-Oid': 'oid-123',
  'X-Hospital-Scope': 'usz',
  'X-Active-Role': 'HCC.DischargeCoordinator',
};

const TRACE = {
  contract: 'DC-EVIDENCE-TRACE-v1',
  golden_thread: 'gt-plan-ev',
  patient: { synthetic_id: 'PT-0001', specialty: 'General medicine', provenance: 'live' },
  branch: 'accept',
  generated_ts: '1970-01-01T00:00:00Z',
  steps: [
    {
      role: 'dca',
      agent: 'dca-agent',
      journey_stage: 'DISCHARGE_READY',
      epic_input: { wardId: 'C3', occupiedBeds: 60, bedCapacity: 58, citations: ['gold.fact_occupancy_forecast'], provenance: 'live' },
      agent_read: { signal: '3 blocked by transport' },
      recommendation: { lever_id: 'DCA-UNBLOCK-BARRIER', predicted_impact: { metric: 'beds', value: 3 }, insight_text: 'Resolve 3 barriers' },
      copilot: { requiresApproval: true, decision: 'accept', approver: 'alice', decision_ts: '1970-01-01T00:00:00Z' },
      action: { cosmos_id: 'a1', status: 'applied' },
      outcome: {
        contract: 'DC-SIM-OUTCOME-v1', golden_thread: 'gt-plan-ev', lever_id: 'DCA-UNBLOCK-BARRIER',
        predicted_impact: { metric: 'beds', value: 3 }, realised_impact: { metric: 'beds', value: 3 },
        divergence: 0, provenance: 'live', applied: true,
      },
    },
  ],
};

describe('iqEvidence', () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
  });

  it('GETs /agents/{role}/evidence with the branch + hospital + scoped identity headers', async () => {
    vi.stubEnv('VITE_AGENT_HOST_URL', 'https://host.example');
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => TRACE });
    vi.stubGlobal('fetch', fetchMock);

    const result = await iqEvidence('dca', 'accept', env);

    expect(result.data.contract).toBe('DC-EVIDENCE-TRACE-v1');
    expect(result.data.golden_thread).toBe('gt-plan-ev');
    expect(result.provenance).toBe('live');
    expect(result.degraded).toBe(false);
    expect(result.citations).toContain('gold.fact_occupancy_forecast');
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe('https://host.example/agents/dca/evidence?branch=accept&hospital=USZ');
    expect(init.headers).toEqual(expect.objectContaining(identity));
  });

  it('passes the deny branch through to the query string', async () => {
    vi.stubEnv('VITE_AGENT_HOST_URL', 'https://host.example');
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ ...TRACE, branch: 'deny' }) });
    vi.stubGlobal('fetch', fetchMock);

    await iqEvidence('dca', 'deny', env);

    const [url] = fetchMock.mock.calls[0];
    expect(url).toBe('https://host.example/agents/dca/evidence?branch=deny&hospital=USZ');
  });

  it('throws loud on a non-ok evidence response (caller degrades to fixture)', async () => {
    vi.stubEnv('VITE_AGENT_HOST_URL', 'https://host.example');
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 400 }));
    await expect(iqEvidence('dca', 'accept', env)).rejects.toThrow(/evidence load failed: 400/);
  });
});
