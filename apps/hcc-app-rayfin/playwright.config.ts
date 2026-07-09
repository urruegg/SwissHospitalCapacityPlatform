import { defineConfig, devices } from '@playwright/test';

/** Sprint 13 T7 — Playwright config for the Rayfin PoC placeholder smoke test. */
export default defineConfig({
  testDir: './tests',
  testMatch: ['e2e/**/*.spec.ts'],
  timeout: 30_000,
  reporter: [['list']],
  use: {
    baseURL: 'http://localhost:4273',
    trace: 'on-first-retry',
  },
  webServer: {
    command: 'npm run build && npm run preview -- --port 4273',
    url: 'http://localhost:4273',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});
