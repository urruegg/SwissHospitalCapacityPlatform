import { expect, test } from '@playwright/test';

/**
 * Sprint 39 P2 (B1 + B2) — the operational closed loop end-to-end.
 *
 * Forces Live by injecting a runtime agent-host URL (`window.__ENV__`) and
 * flipping the header Data-source toggle, then stubs the two agent-host
 * endpoints so the walk is deterministic and offline:
 *   - GET  /agents/dca/worklist  -> 3 live observations + a grounded reco
 *   - POST /agents/dca/decisions -> a DC-SIM-OUTCOME-v1 (accept frees 3 beds)
 *
 * Asserts (a) a worklist row renders from the stub, (b) Accept -> the outcome is
 * shown side-by-side AND the worklist shrinks on re-fetch, (c) Deny leaves the
 * worklist unchanged. NFR-UXL-001: the app only submits the human decision; the
 * agent-host owns the HITL apply.
 */

const obs = (patient: string, aged: number) => ({
  patient,
  ward: 'C3',
  readiness: 'BLOCKED',
  barrier: 'transport',
  aged_h: aged,
  provenance: 'live',
});

const WORKLIST = {
  role: 'dca',
  ward: 'C3',
  observations: [obs('PT-901', 4), obs('PT-902', 6), obs('PT-903', 2)],
  recommendation: {
    lever_id: 'DCA-UNBLOCK-BARRIER',
    params: { barrier_type: 'transport', n: 3, ward: 'C3' },
    predicted_impact: { metric: 'beds', value: 3 },
    insight_text: 'Resolve 3 transport barriers to free 3 beds on C3',
    citations: ['gold.discharge_candidates', 'gold.fact_capacity_baseline'],
  },
  provenance: 'live',
};

const WORKLIST_SHRUNK = { ...WORKLIST, observations: [obs('PT-901', 4)] };

const ACCEPT_OUTCOME = {
  contract: 'DC-SIM-OUTCOME-v1',
  plan_id: 'plan-e2e',
  golden_thread: 'gt-plan-e2e',
  lever_id: 'DCA-UNBLOCK-BARRIER',
  applied_ts: '1970-01-01T00:00:00Z',
  predicted_impact: { metric: 'beds', value: 3 },
  realised_impact: { metric: 'beds', value: 3 },
  state_delta: { beds_freed: ['C3'], patients_discharged: ['PT-901'], patients_promoted: [] },
  divergence: 0,
  provenance: 'live',
  applied: true,
  branch: 'accept',
  decision: 'accept',
  approver: 'oid-e2e',
};

const DENY_OUTCOME = {
  ...ACCEPT_OUTCOME,
  realised_impact: { metric: 'beds', value: 0 },
  state_delta: { beds_freed: [], patients_discharged: [], patients_promoted: [] },
  applied: false,
  branch: 'deny',
  decision: 'deny',
};

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.setItem('curavias.lang', 'en');
    // Force the app to treat the agent-host as configured (runtime-config reads
    // window.__ENV__ before the build-time VITE_* fallback). No golden source is
    // configured, so the base board load stays on fixtures and only the worklist
    // overlay hits the (stubbed) host.
    (window as unknown as { __ENV__: Record<string, string> }).__ENV__ = {
      AGENT_HOST_URL: 'https://host.test',
    };
  });
});

async function goLiveOnDischarge(page: import('@playwright/test').Page) {
  await page.goto('/main/discharge');
  await expect(page.getByTestId('board-discharge')).toBeVisible();
  // Flip Data source -> Live; the board re-loads and overlays the live worklist.
  await page.getByRole('switch', { name: 'Data source' }).click();
}

test('live worklist renders and Accept closes the loop (outcome + worklist shrinks)', async ({ page }) => {
  let worklistCalls = 0;
  await page.route('**/agents/dca/worklist*', async (route) => {
    worklistCalls += 1;
    await route.fulfill({ json: worklistCalls === 1 ? WORKLIST : WORKLIST_SHRUNK });
  });
  await page.route('**/agents/dca/decisions', async (route) => {
    await route.fulfill({ json: ACCEPT_OUTCOME });
  });

  await goLiveOnDischarge(page);

  // (a) A worklist row renders from the stub (all three live observations).
  await expect(page.getByText('PT-901')).toBeVisible();
  await expect(page.getByText('PT-902')).toBeVisible();
  await expect(page.getByText('PT-903')).toBeVisible();

  // Open the copilot rail; it shows the live reco with the accept/deny gate.
  await page.getByRole('button', { name: 'Open agent' }).click();
  const rail = page.getByRole('complementary', { name: /agent/i });
  await expect(rail.getByRole('button', { name: 'Accept' })).toBeVisible();
  await expect(rail.getByRole('button', { name: 'Deny' })).toBeVisible();

  // (b) Accept -> outcome rendered side-by-side, accept branch highlighted...
  await rail.getByRole('button', { name: 'Accept' }).click();
  const outcome = rail.getByTestId('decision-outcome');
  await expect(outcome).toBeVisible();
  await expect(outcome.getByTestId('outcome-accept')).toHaveAttribute('aria-current', 'true');
  await expect(outcome.getByTestId('outcome-deny')).toBeVisible();
  await expect(outcome).toContainText(/3 beds freed/i);
  await expect(outcome).toContainText(/breach persists/i);

  // ...and the worklist shrinks on the accept re-fetch (only PT-901 remains).
  await expect(page.getByText('PT-902')).toHaveCount(0);
  await expect(page.getByText('PT-903')).toHaveCount(0);
  await expect(page.getByText('PT-901')).toBeVisible();
});

test('Deny leaves the worklist unchanged and shows the deny branch', async ({ page }) => {
  let worklistCalls = 0;
  await page.route('**/agents/dca/worklist*', async (route) => {
    worklistCalls += 1;
    await route.fulfill({ json: WORKLIST });
  });
  await page.route('**/agents/dca/decisions', async (route) => {
    await route.fulfill({ json: DENY_OUTCOME });
  });

  await goLiveOnDischarge(page);
  await expect(page.getByText('PT-902')).toBeVisible();

  await page.getByRole('button', { name: 'Open agent' }).click();
  const rail = page.getByRole('complementary', { name: /agent/i });
  await rail.getByRole('button', { name: 'Deny' }).click();

  const outcome = rail.getByTestId('decision-outcome');
  await expect(outcome.getByTestId('outcome-deny')).toHaveAttribute('aria-current', 'true');
  await expect(outcome).toContainText(/breach persists/i);

  // Deny is a no-op: the worklist is unchanged (no re-fetch) and all rows remain.
  await expect(page.getByText('PT-901')).toBeVisible();
  await expect(page.getByText('PT-902')).toBeVisible();
  await expect(page.getByText('PT-903')).toBeVisible();
  expect(worklistCalls).toBe(1);
});
