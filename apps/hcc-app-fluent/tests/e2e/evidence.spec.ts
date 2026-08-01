import { expect, test } from '@playwright/test';

/**
 * Sprint 39 P2 (B3/B4) — the Closed-Loop Evidence surface end-to-end.
 *
 * Forces Live (runtime agent-host URL via `window.__ENV__` + the header
 * Data-source toggle) and stubs `GET /agents/{role}/evidence`, returning an
 * accept trace or a deny trace based on the `branch` query param. Asserts the
 * five-part proof + the shared golden_thread render, and that the branch toggle
 * switches the trace (accept applied -> deny breach persists). Deterministic and
 * offline: no agent-host required.
 */

const STEP = (branch: 'accept' | 'deny') => ({
  role: 'dca',
  agent: 'dca-agent',
  journey_stage: 'DISCHARGE_READY',
  epic_input: {
    wardId: 'C3',
    occupiedBeds: 60,
    bedCapacity: 58,
    citations: ['gold.fact_occupancy_forecast', 'gold.bed_assignment'],
    provenance: 'live',
  },
  agent_read: { signal: '3 discharge-ready blocked by transport barriers on C3' },
  recommendation: {
    lever_id: 'DCA-UNBLOCK-BARRIER',
    predicted_impact: { metric: 'beds', value: 3 },
    insight_text: 'Resolve 3 transport barriers to free 3 beds on C3',
  },
  copilot: {
    requiresApproval: true,
    decision: branch,
    approver: branch === 'accept' ? 'alice' : '',
    decision_ts: '1970-01-01T00:00:00Z',
  },
  action: { cosmos_id: 'a1', status: branch === 'accept' ? 'applied' : 'denied' },
  outcome: {
    contract: 'DC-SIM-OUTCOME-v1',
    golden_thread: 'gt-e2e',
    lever_id: 'DCA-UNBLOCK-BARRIER',
    predicted_impact: { metric: 'beds', value: 3 },
    realised_impact: { metric: 'beds', value: branch === 'accept' ? 3 : 0 },
    divergence: 0,
    provenance: 'live',
    applied: branch === 'accept',
  },
});

const TRACE = (branch: 'accept' | 'deny') => ({
  contract: 'DC-EVIDENCE-TRACE-v1',
  golden_thread: 'gt-e2e',
  patient: { synthetic_id: 'PT-0001', specialty: 'General medicine', provenance: 'live' },
  branch,
  generated_ts: '1970-01-01T00:00:00Z',
  steps: [STEP(branch)],
});

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.setItem('curavias.lang', 'en');
    (window as unknown as { __ENV__: Record<string, string> }).__ENV__ = {
      AGENT_HOST_URL: 'https://host.test',
    };
  });
  // Stub the evidence read: return the accept or deny trace per the branch query.
  await page.route('**/agents/*/evidence*', async (route) => {
    const branch = new URL(route.request().url()).searchParams.get('branch') === 'deny' ? 'deny' : 'accept';
    await route.fulfill({ json: TRACE(branch) });
  });
});

async function goLiveOnEvidence(page: import('@playwright/test').Page) {
  await page.goto('/main/evidence');
  await expect(page.getByTestId('board-evidence')).toBeVisible();
  // Flip Data source -> Live; the board loads the (stubbed) evidence trace.
  await page.getByRole('switch', { name: 'Data source' }).click();
}

test('renders the five-part proof + golden_thread from the accept trace', async ({ page }) => {
  await goLiveOnEvidence(page);

  // The shared golden_thread is visible (from the stubbed Live trace).
  await expect(page.getByTestId('evidence-golden-thread')).toContainText('gt-e2e');

  // All five parts of the proof render.
  await expect(page.getByTestId('evidence-part-epic')).toBeVisible();
  await expect(page.getByTestId('evidence-part-read')).toBeVisible();
  await expect(page.getByTestId('evidence-part-reco')).toBeVisible();
  await expect(page.getByTestId('evidence-part-copilot')).toBeVisible();
  await expect(page.getByTestId('evidence-part-outcome')).toBeVisible();

  // Accept branch: the outcome is applied + 3 beds realised.
  const outcome = page.getByTestId('evidence-part-outcome');
  await expect(outcome).toContainText(/Realised impact: 3 beds/);
  await expect(outcome).toContainText('Applied');
  // B4 — the outcome cites the same DC-SIM-OUTCOME-v1 contract + golden_thread.
  await expect(page.getByTestId('evidence-outcome-thread')).toContainText('DC-SIM-OUTCOME-v1');
});

test('the branch toggle switches the trace to the deny branch (breach persists)', async ({ page }) => {
  await goLiveOnEvidence(page);
  await expect(page.getByTestId('evidence-part-outcome')).toContainText('Applied');

  // Toggle to the deny branch; the board re-fetches the deny trace.
  await page.getByRole('tab', { name: /Deny branch/ }).click();

  const outcome = page.getByTestId('evidence-part-outcome');
  await expect(outcome).toContainText(/Realised impact: 0 beds/);
  await expect(outcome).toContainText('Not applied');
  await expect(page.getByTestId('evidence-part-copilot')).toContainText('Denied');
});
