/**
 * #447 — runtime configuration reader.
 *
 * A single, env-agnostic container image serves every environment. Per-env
 * values (e.g. the Foundry agent-host URL) are injected at container start into
 * `window.__ENV__` by `docker-entrypoint.d/30-env-config.sh`, which writes
 * `public/env-config.js` from the container's `AGENT_HOST_URL` env var. The
 * bundle loads `/env-config.js` (classic script) before the deferred module, so
 * `window.__ENV__` is populated by the time app code reads it.
 *
 * Precedence: runtime `window.__ENV__` first, then the build-time
 * `import.meta.env.VITE_*` fallback (so local `npm run dev` / tests still work
 * without a running container), then empty string.
 */

/** Runtime environment shape injected by the container entrypoint. */
export interface RuntimeEnv {
  /** Foundry agent-host base URL for this environment. */
  AGENT_HOST_URL?: string;
  /** Golden-source (IQ structured-read) base URL for this environment (#424 M2). */
  GOLDEN_SOURCE_URL?: string;
}

declare global {
  interface Window {
    __ENV__?: RuntimeEnv;
  }
}

function runtimeEnv(): RuntimeEnv {
  if (typeof window !== 'undefined' && window.__ENV__) {
    return window.__ENV__;
  }
  return {};
}

/**
 * Resolve the Foundry agent-host base URL: runtime-injected value first, then the
 * build-time `VITE_AGENT_HOST_URL` fallback, then empty (=> built-in mock).
 */
export function getAgentHostUrl(): string {
  const runtime = runtimeEnv().AGENT_HOST_URL;
  if (runtime && runtime.length > 0) {
    return runtime;
  }
  return import.meta.env.VITE_AGENT_HOST_URL ?? '';
}

/**
 * Resolve the golden-source (IQ structured-read) base URL: runtime-injected
 * value first, then the build-time `VITE_GOLDEN_SOURCE_URL` fallback, then empty
 * (=> the read path stays simulated / degrades loud). #424 M2.
 */
export function getGoldenSourceUrl(): string {
  const runtime = runtimeEnv().GOLDEN_SOURCE_URL;
  if (runtime && runtime.length > 0) {
    return runtime;
  }
  return import.meta.env.VITE_GOLDEN_SOURCE_URL ?? '';
}
