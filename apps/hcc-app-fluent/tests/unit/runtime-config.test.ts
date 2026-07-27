import { afterEach, describe, expect, it, vi } from 'vitest';
import { getAgentHostUrl } from '../../src/config/runtime-config';

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
