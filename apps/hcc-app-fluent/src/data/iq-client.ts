import type { Provenance } from '../journey/RoleBoard';
import { getAgentHostUrl } from '../config/runtime-config';

/**
 * Sprint 27 — IQ-layer data-access gateway (the single data ingress).
 *
 * Per [docs/architecture/app-iq-data-access-pattern.md]. This module is the ONLY
 * place in the app allowed to hold a golden-data endpoint or call `fetch`; board
 * loaders and the agent manifest are thin callers. A guard test
 * (`tests/unit/iq-ingress-guard.test.ts`) enforces the single ingress.
 *
 * Precedence mirrors the Fabric -> Foundry grounding contract
 * ([docs/architecture/fabric-foundry-grounding-contract.md], ADR-0033):
 *   - structured facts  -> Fabric Data Agent / semantic model over Gold (here)
 *   - knowledge/answers -> Foundry agent host (here)
 *   - fabric-mcp        -> actions only (never a read path; not here)
 *
 * Provenance reuses the frozen RoleBoard contract: `live` == golden evidence
 * served from the IQ layer, `simulated` == demo fixtures (ADR-0013 / ADR-0016).
 */

/** Where a read was ultimately served from. */
export type IqSource = 'fabric-data-agent' | 'golden-source' | 'foundry-agent' | 'simulated';

/**
 * Evidence envelope for an IQ read. `citations` should carry >= 1 `hcp:*` /
 * `gold.*` id for structured reads; `degraded` is true when the IQ surface was
 * configured but unavailable and the layer fell back to a fixture (fail loud,
 * never silent).
 */
export interface IqResult<T> {
  data: T;
  provenance: Provenance;
  citations: string[];
  degraded: boolean;
  source: IqSource;
}

// The only golden-data endpoint config in the app. Region-agnostic (ADR-0035):
// values come from env so westus2 (demo) lifts to eastus2 / switzerlandnorth
// without code edits. (MSAL config lives in auth/msal-provider.ts and is not a
// golden-data ingress, so it is out of this gateway's scope.)
const goldenSourceUrl: string = import.meta.env.VITE_GOLDEN_SOURCE_URL ?? '';
// #447 — runtime-injected first (window.__ENV__), build-time VITE_* as fallback,
// so one env-agnostic image serves every environment (no per-env bake).
const agentHostBaseUrl: string = getAgentHostUrl();

/** True when the golden structured-data surface (Fabric Data Agent / Gold REST) is configured. */
export function isGoldenSourceConfigured(): boolean {
  return goldenSourceUrl.length > 0;
}

/** True when the Foundry agent host is configured. */
export function isAgentHostConfigured(): boolean {
  return agentHostBaseUrl.length > 0;
}

/** The golden source may wrap its payload with citations, or return the bare payload. */
interface StructuredEnvelope<T> {
  payload?: T;
  citations?: string[];
}

/**
 * Structured read through the IQ layer. Fetches `${VITE_GOLDEN_SOURCE_URL}${path}`
 * and returns the payload plus any citations. Throws on transport / HTTP error so
 * the caller degrades loudly to its fixture. Only call when `isGoldenSourceConfigured()`.
 */
export async function iqStructuredRead<T>(path: string): Promise<{ payload: T; citations: string[] }> {
  const res = await fetch(`${goldenSourceUrl}${path}`);
  if (!res.ok) throw new Error(`IQ structured read failed: ${res.status}`);
  const body = (await res.json()) as StructuredEnvelope<T>;
  const payload = body.payload ?? (body as unknown as T);
  return { payload, citations: body.citations ?? [] };
}

/** Conversational read / answer through the Foundry agent host. Only call when `isAgentHostConfigured()`. */
export async function iqAgentChat<T>(agent: string, prompt: string): Promise<T> {
  const res = await fetch(`${agentHostBaseUrl}/agents/${encodeURIComponent(agent)}/chat`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) throw new Error(`agent chat failed: ${res.status}`);
  return (await res.json()) as T;
}

/** Fetch the deployed agent list from the Foundry agent host. Only call when `isAgentHostConfigured()`. */
export async function iqAgentList<T>(): Promise<T> {
  const res = await fetch(`${agentHostBaseUrl}/agents`);
  if (!res.ok) throw new Error(`agent list failed: ${res.status}`);
  return (await res.json()) as T;
}
