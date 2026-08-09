import { defineConfig, devices } from '@playwright/test';

/** Sprint 13 T1 — Playwright config for the Fluent app smoke + a11y suites. */
export default defineConfig({
  testDir: './tests',
  testMatch: ['e2e/**/*.spec.ts', 'integration/**/*.spec.ts'],
  timeout: 30_000,
  fullyParallel: true,
  reporter: [['list']],
  use: {
    baseURL: 'http://localhost:4173',
    trace: 'on-first-retry',
  },
  webServer: {
    command: 'npm run build && npm run preview -- --port 4173',
    url: 'http://localhost:4173',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    {
      // Sprint 43 WS-4 -- runs against the real deployed SIT environment,
      // no webServer, no response stubbing. Opt-in via `npm run test:live`
      // (never part of the default `npm test`/CI run, since it depends on
      // live infrastructure being up and reachable).
      name: 'live',
      testDir: './tests/e2e-live',
      testMatch: ['**/*.spec.ts'],
      // Sprint 43 WS-5 -- a live GPT-5 reply can take up to ~30s (measured:
      // ooa-agent 22.8s via raw HTTP); 90s gives headroom over the 60s
      // conversation-growth poll in helpers/live-agent.ts.
      timeout: 90_000,
      use: {
        ...devices['Desktop Chrome'],
        baseURL: 'https://appsit.curavias.ch',
        trace: 'on-first-retry',
      },
    },
  ],
});
