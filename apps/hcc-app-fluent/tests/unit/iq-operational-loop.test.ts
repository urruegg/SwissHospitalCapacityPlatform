import { afterEach, describe, expect, it, vi } from 'vitest';
import { iqWorklist, iqDecision } from '../../src/data/iq-client';
import type { ContextEnvelope } from '../../src/context/context-envelope';

/**
 * Sprint 39 P2 — the operational closed loop wire contract. The IQ gateway is
 * the only permitted fetch site (ingress guard), so the worklist read and the
 * accept/deny decision POST live here. These assert the exact URL, verb, and the
 * scoped identity headers (incl. the `X-User-Oid` HITL approver seam) the
 * agent-host expects, plus the fail-loud behaviour on an HTTP error.
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

const WORKLIST = {
  role: 'dca',
  ward: 'C3',
  observations: [
    { patient: 'PT-1', ward: 'C3', readiness: 'BLOCKED', barrier: 'transport', aged_h: 4, provenance: 'live' },
    { patient: 'PT-2', ward: 'C3', readiness: 'BLOCKED', barrier: 'transport', aged_h: 6, provenance: 'live' },
    { patient: 'PT-3', ward: 'C3', readiness: 'BLOCKED', barrier: 'transport', aged_h: 2, provenance: 'live' },
  ],
  recommendation: {
    lever_id: 'DCA-UNBLOCK-BARRIER',
    params: { barrier_type: 'transport', n: 3, ward: 'C3' },
    predicted_impact: { metric: 'beds', value: 3 },
    insight_text: 'Resolve 3 transport barriers to free 3 beds on C3',
    citations: ['gold.discharge_candidates', 'gold.fact_capacity_baseline'],
  },
  provenance: 'live',
};

describe('iqWorklist', () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
  });

  it('GETs /agents/{role}/worklist with the hospital + scoped identity headers', async () => {
    vi.stubEnv('VITE_AGENT_HOST_URL', 'https://host.example');
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => WORKLIST });
    vi.stubGlobal('fetch', fetchMock);

    const result = await iqWorklist('dca', env);

    expect(result.data.observations).toHaveLength(3);
    expect(result.provenance).toBe('live');
    expect(result.degraded).toBe(false);
    expect(result.citations).toContain('gold.discharge_candidates');
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe('https://host.example/agents/dca/worklist?hospital=USZ');
    expect(init.headers).toEqual(expect.objectContaining(identity));
  });

  it('throws loud on a non-ok worklist response (caller degrades to fixture)', async () => {
    vi.stubEnv('VITE_AGENT_HOST_URL', 'https://host.example');
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 400 }));
    await expect(iqWorklist('dca', env)).rejects.toThrow(/worklist load failed: 400/);
  });
});

describe('iqDecision', () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
  });

  it('POSTs /agents/{role}/decisions with the X-User-Oid approver + decision body', async () => {
    vi.stubEnv('VITE_AGENT_HOST_URL', 'https://host.example');
    const outcome = {
      contract: 'DC-SIM-OUTCOME-v1', plan_id: 'plan-1', golden_thread: 'gt-plan-1',
      lever_id: 'DCA-UNBLOCK-BARRIER', applied_ts: '1970-01-01T00:00:00Z',
      predicted_impact: { metric: 'beds_freed', value: 3 },
      realised_impact: { metric: 'beds_freed', value: 3 },
      state_delta: { beds_freed: ['C3'], patients_discharged: ['PT-1'], patients_promoted: [] },
      divergence: 0, provenance: 'live', applied: true, branch: 'accept', decision: 'accept', approver: 'oid-123',
    };
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => outcome });
    vi.stubGlobal('fetch', fetchMock);

    const result = await iqDecision('dca', 'accept', { barrier_type: 'transport' }, env);

    expect(result.realised_impact.value).toBe(3);
    expect(result.applied).toBe(true);
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe('https://host.example/agents/dca/decisions');
    expect(init.method).toBe('POST');
    expect(init.headers).toEqual(expect.objectContaining({ 'content-type': 'application/json', ...identity }));
    expect(JSON.parse(init.body)).toEqual({ decision: 'accept', hospital: 'USZ', params: { barrier_type: 'transport' } });
  });

  it('throws loud with the status on a refusal (403 bot/self approver)', async () => {
    vi.stubEnv('VITE_AGENT_HOST_URL', 'https://host.example');
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 403 }));
    await expect(iqDecision('dca', 'accept', {}, env)).rejects.toThrow(/decision failed: 403/);
  });
});
