import type { AppEnv } from './claim-parser';

/**
 * Sprint 13 T2 — resolve the deployment environment.
 *
 * The `env` claim from the token is authoritative when present. As a fallback
 * (e.g. an anonymous shell before sign-in) we derive it from the slot host name
 * so SIT vs PROD routing works before claims are available (design spec §8
 * env-scoping test, ADR-0013 westus2 demo scope).
 */
export function envFromHost(hostname: string): AppEnv {
  const h = hostname.toLowerCase();
  if (h.includes('-sit') || h.includes('sit.')) return 'sit';
  if (h.includes('-prod') || h.includes('prod.')) return 'prod';
  return 'dev';
}

export function detectEnv(claimEnv: AppEnv | undefined, hostname: string): AppEnv {
  return claimEnv ?? envFromHost(hostname);
}
