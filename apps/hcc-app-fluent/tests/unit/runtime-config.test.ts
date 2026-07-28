import { afterEach, describe, expect, it, vi } from 'vitest';
import { getAgentHostUrl, getGoldenSourceUrl, getFoundryThreadsEnabled } from '../../src/config/runtime-config';

/**
 * #447 — runtime config injection. The app must read the agent-host URL from a
 * runtime-injected `window.__ENV__` (written by the container entrypoint from the
 * per-env `AGENT_HOST_URL`) BEFORE the build-time `import.meta.env` fallback, so a
 * single env-agnostic image serves both SIT and PROD.
 */
describe('runtime-config getAgentHostUrl', () => {
  afterEach(() => {
    delete (window as { __ENV__?: unknown }).__ENV__;
    vi.unstubAllEnvs();
  });

  it('prefers window.__ENV__.AGENT_HOST_URL over the build-time fallback', () => {
    vi.stubEnv('VITE_AGENT_HOST_URL', 'https://sit.example');
    (window as { __ENV__?: { AGENT_HOST_URL?: string } }).__ENV__ = {
      AGENT_HOST_URL: 'https://prod.example',
    };
    expect(getAgentHostUrl()).toBe('https://prod.example');
  });

  it('falls back to import.meta.env.VITE_AGENT_HOST_URL when the runtime value is absent', () => {
    vi.stubEnv('VITE_AGENT_HOST_URL', 'https://fallback.example');
    expect(getAgentHostUrl()).toBe('https://fallback.example');
  });

  it('falls back to the build-time value when the runtime value is empty', () => {
    vi.stubEnv('VITE_AGENT_HOST_URL', 'https://fallback.example');
    (window as { __ENV__?: { AGENT_HOST_URL?: string } }).__ENV__ = { AGENT_HOST_URL: '' };
    expect(getAgentHostUrl()).toBe('https://fallback.example');
  });

  it('returns an empty string when neither runtime nor build-time value is set', () => {
    vi.stubEnv('VITE_AGENT_HOST_URL', '');
    expect(getAgentHostUrl()).toBe('');
  });
});

/**
 * #424 M2 — the golden-source (IQ structured-read) base URL follows the same
 * runtime-injection contract as the agent-host URL, so one env-agnostic image
 * points at each environment's live golden surface without a rebuild.
 */
describe('runtime-config getGoldenSourceUrl', () => {
  afterEach(() => {
    delete (window as { __ENV__?: unknown }).__ENV__;
    vi.unstubAllEnvs();
  });

  it('prefers window.__ENV__.GOLDEN_SOURCE_URL over the build-time fallback', () => {
    vi.stubEnv('VITE_GOLDEN_SOURCE_URL', 'https://sit.example/golden');
    (window as { __ENV__?: { GOLDEN_SOURCE_URL?: string } }).__ENV__ = {
      GOLDEN_SOURCE_URL: 'https://prod.example/golden',
    };
    expect(getGoldenSourceUrl()).toBe('https://prod.example/golden');
  });

  it('falls back to import.meta.env.VITE_GOLDEN_SOURCE_URL when the runtime value is absent', () => {
    vi.stubEnv('VITE_GOLDEN_SOURCE_URL', 'https://fallback.example/golden');
    expect(getGoldenSourceUrl()).toBe('https://fallback.example/golden');
  });

  it('returns an empty string when neither runtime nor build-time value is set', () => {
    vi.stubEnv('VITE_GOLDEN_SOURCE_URL', '');
    expect(getGoldenSourceUrl()).toBe('');
  });
});

/**
 * #424 M3 — the Foundry-threads feature gate follows the same runtime-injection
 * contract as the agent-host / golden-source URLs, so one env-agnostic image
 * flips live threads per environment without a rebuild.
 */
describe('runtime-config getFoundryThreadsEnabled', () => {
  afterEach(() => {
    delete (window as { __ENV__?: unknown }).__ENV__;
    vi.unstubAllEnvs();
  });

  it('prefers window.__ENV__.FOUNDRY_THREADS_ENABLED over the build-time fallback', () => {
    vi.stubEnv('VITE_FOUNDRY_THREADS_ENABLED', '');
    (window as { __ENV__?: { FOUNDRY_THREADS_ENABLED?: string } }).__ENV__ = {
      FOUNDRY_THREADS_ENABLED: 'true',
    };
    expect(getFoundryThreadsEnabled()).toBe(true);
  });

  it('falls back to import.meta.env.VITE_FOUNDRY_THREADS_ENABLED when the runtime value is absent', () => {
    vi.stubEnv('VITE_FOUNDRY_THREADS_ENABLED', 'true');
    expect(getFoundryThreadsEnabled()).toBe(true);
  });

  it('returns false when neither runtime nor build-time value is set', () => {
    vi.stubEnv('VITE_FOUNDRY_THREADS_ENABLED', '');
    expect(getFoundryThreadsEnabled()).toBe(false);
  });
});
