/**
 * Sprint 13 T7 — Rayfin PoC placeholder shell.
 *
 * Rayfin is a proprietary app generator whose CLI could not be run in this
 * environment (no network-reachable Rayfin toolchain / license). Per the T7
 * time-box rule (design spec §2.2, plan T7), the PoC is recorded as
 * "not evaluable in scope" — see README.md and the exit ADR
 * (docs/adr/0023-app-stack-fluent-vs-rayfin-decision.md).
 *
 * This file is a minimal, buildable stand-in that reuses the Curavias brand
 * tokens (data-platform/reports/capacity-dashboard.Report/themes/curavias-token-mapping.md)
 * so the app compiles in CI and the shared smoke test has a target. It is NOT a
 * Rayfin-generated artefact and must not be treated as PoC evidence.
 */

// Curavias brand tokens (subset) — kept in sync with the Power BI theme mapping.
const curavias = {
  brandBlue: '#365B7D',
  ink: '#2E4C68',
  background: '#FFFFFF',
  surface: '#F3F5F7',
};

export function App() {
  return (
    <div
      style={{
        fontFamily: 'Segoe UI, system-ui, sans-serif',
        color: curavias.ink,
        background: curavias.surface,
        minHeight: '100vh',
      }}
    >
      <header
        role="banner"
        style={{
          background: curavias.brandBlue,
          color: curavias.background,
          padding: '12px 24px',
          fontWeight: 600,
        }}
      >
        Curavias — Rayfin PoC (placeholder)
      </header>
      <main role="main" style={{ padding: 24 }}>
        <h1>Rayfin PoC — not evaluable in scope</h1>
        <p>
          The Rayfin generator was not runnable in this environment. This
          placeholder shell exists only to keep the track buildable in CI. See{' '}
          <code>README.md</code> and ADR-0023 for the decision rationale.
        </p>
      </main>
    </div>
  );
}
