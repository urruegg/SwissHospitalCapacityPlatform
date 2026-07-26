import { describe, it, expect } from 'vitest';

/**
 * Sprint 27 — IQ single-ingress guard (docs/architecture/app-iq-data-access-pattern.md).
 *
 * The IQ gateway (`src/data/iq-client.ts`) is the ONLY place allowed to call
 * `fetch` for golden data. This test eager-imports every `src` module as raw
 * text (via Vite `import.meta.glob`, no Node builtins) and fails if any other
 * module reads data ad hoc, so no surface bypasses the IQ layer / evidence
 * envelope. (MSAL / Graph identity calls are not `fetch` and are out of scope.)
 */
const modules = import.meta.glob('../../src/**/*.{ts,tsx}', {
  query: '?raw',
  eager: true,
  import: 'default',
}) as Record<string, string>;

/** The IQ layer: the raw gateway + the evidence-envelope structured-read adapter (OBO/RLS, ADR-0052). */
const IQ_LAYER = ['src/data/iq-client.ts', 'src/data/roleboard/golden-source-client.ts'];

describe('IQ single-ingress guard', () => {
  it('only the IQ layer (iq-client + golden-source-client) calls fetch()', () => {
    const offenders = Object.entries(modules)
      .filter(([, source]) => /\bfetch\s*\(/.test(source))
      .map(([path]) => path)
      .filter((path) => !IQ_LAYER.some((allowed) => path.endsWith(allowed)));
    expect(offenders).toEqual([]);
  });
});
