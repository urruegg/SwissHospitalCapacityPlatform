import type { Provenance } from '../journey/RoleBoard';
import type { ContextEnvelope } from '../context/context-envelope';
import { getAgentHostUrl, getGoldenSourceUrl } from '../config/runtime-config';

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
// without code edits. #424 M2 — resolved at call time (runtime-injected
// window.__ENV__ first, build-time VITE_* fallback) so one env-agnostic image
// serves every environment, matching the agent-host URL contract (#447). (MSAL
// config lives in auth/msal-provider.ts and is not a golden-data ingress, so it
// is out of this gateway's scope.)
function goldenSourceUrl(): string {
  return getGoldenSourceUrl();
}
// #447 — runtime-injected first (window.__ENV__), build-time VITE_* as fallback,
// so one env-agnostic image serves every environment (no per-env bake).
function agentHostBaseUrl(): string {
  return getAgentHostUrl();
}

/** True when the golden structured-data surface (Fabric Data Agent / Gold REST) is configured. */
export function isGoldenSourceConfigured(): boolean {
  return goldenSourceUrl().length > 0;
}

/** True when the Foundry agent host is configured. */
export function isAgentHostConfigured(): boolean {
  return agentHostBaseUrl().length > 0;
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
  const res = await fetch(`${goldenSourceUrl()}${path}`);
  if (!res.ok) throw new Error(`IQ structured read failed: ${res.status}`);
  const body = (await res.json()) as StructuredEnvelope<T>;
  const payload = body.payload ?? (body as unknown as T);
  return { payload, citations: body.citations ?? [] };
}

/**
 * Per-user OBO/RLS scope headers (ADR-0052). Attached to identity-aware IQ calls
 * (thread mint + chat) so the agent-host can scope the thread and its turns to
 * the signed-in user, exactly as the golden read path does.
 */
function identityHeaders(env: ContextEnvelope): Record<string, string> {
  return {
    'X-User-Oid': env.userOid ?? '',
    'X-Hospital-Scope': env.hospitalScope,
    'X-Active-Role': env.activeRole,
  };
}

/** A minted `(userOid x agent)` thread + where it is persisted (#424 M3). */
export interface ThreadMint {
  threadId: string;
  provenance: string;
}

/**
 * Mint (or reuse) the live `(userOid x agent)` Foundry thread on the agent-host
 * (`POST /agents/{name}/threads`, #424 M3). Carries the ContextEnvelope as scoped
 * identity headers; the server refuses deny-by-default without `X-User-Oid`.
 * Throws loud on transport / HTTP error so the caller can fall back to a
 * simulated thread. Only call when `isAgentHostConfigured()`.
 */
export async function iqMintThread(agent: string, env: ContextEnvelope): Promise<ThreadMint> {
  const res = await fetch(`${agentHostBaseUrl()}/agents/${encodeURIComponent(agent)}/threads`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', ...identityHeaders(env) },
  });
  if (!res.ok) throw new Error(`thread mint failed: ${res.status}`);
  return (await res.json()) as ThreadMint;
}

/** Options for a thread-scoped, identity-aware chat call (#424 M3). */
export interface AgentChatOptions {
  /** The `(userOid x agent)` thread to thread this turn onto (server conversation id). */
  threadId?: string;
  /** ContextEnvelope for OBO/RLS identity headers; omitted → no identity headers. */
  env?: ContextEnvelope | null;
}

/** Conversational read / answer through the Foundry agent host. Only call when `isAgentHostConfigured()`. */
export async function iqAgentChat<T>(
  agent: string,
  prompt: string,
  opts?: AgentChatOptions,
): Promise<T> {
  const headers: Record<string, string> = { 'content-type': 'application/json' };
  if (opts?.env) Object.assign(headers, identityHeaders(opts.env));
  const body: Record<string, unknown> = { prompt };
  if (opts?.threadId) body.threadId = opts.threadId;
  const res = await fetch(`${agentHostBaseUrl()}/agents/${encodeURIComponent(agent)}/chat`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`agent chat failed: ${res.status}`);
  return (await res.json()) as T;
}

/** Fetch the deployed agent list from the Foundry agent host. Only call when `isAgentHostConfigured()`. */
export async function iqAgentList<T>(): Promise<T> {
  const res = await fetch(`${agentHostBaseUrl()}/agents`);
  if (!res.ok) throw new Error(`agent list failed: ${res.status}`);
  return (await res.json()) as T;
}

/** A user-interaction event on a captured agent turn (Sprint 30 M2; DC-AGENT-INTERACTION-v1.userEvents). */
export interface InteractionEvent {
  /** Event kind, e.g. `thumbs`. */
  type: string;
  /** Optional value, e.g. `up` / `down`. */
  value?: string;
  /** Optional client timestamp (ISO 8601); the server also stamps its own. */
  ts?: string;
}

/**
 * Append a user-interaction event to a captured agent turn via the agent-host
 * (`POST /agents/{name}/interactions/{id}/events`, merged in Sprint 30 Plan 1).
 * The IQ gateway is the only permitted `fetch` site (ingress guard), so the
 * event POST lives here. Resolves the base URL at call-time so a runtime-injected
 * host (window.__ENV__) is honoured. Throws loud on transport / HTTP error so the
 * caller can surface a failure rather than silently drop feedback. Only call when
 * `isAgentHostConfigured()`.
 */
export async function postInteractionEvent(
  agent: string,
  interactionId: string,
  event: InteractionEvent,
): Promise<void> {
  const base = getAgentHostUrl();
  const res = await fetch(
    `${base}/agents/${encodeURIComponent(agent)}/interactions/${encodeURIComponent(interactionId)}/events`,
    {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(event),
    },
  );
  if (!res.ok) throw new Error(`interaction event failed: ${res.status}`);
}
