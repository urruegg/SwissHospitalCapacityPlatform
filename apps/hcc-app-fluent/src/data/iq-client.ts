import type { Provenance } from '../journey/RoleBoard';
import type { ContextEnvelope } from '../context/context-envelope';
import { getAgentHostUrl, getGoldenSourceUrl, getAgentHostScope } from '../config/runtime-config';

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
  const res = await fetch(`${goldenSourceUrl()}${path}`, { headers: { ...(await bearerHeader()) } });
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

/**
 * A bearer-token acquirer for a given scope. Returns the raw access token, or
 * `null` when none can be obtained (no signed-in account / silent renewal fails).
 */
export type BearerAcquirer = (scope: string) => Promise<string | null>;

/**
 * Default acquirer: silently acquire an MSAL access token for `scope`. Lazily
 * imports the MSAL provider so module load never constructs a browser client in
 * tests / SSR — only reached when an agent-host scope is actually configured.
 */
const defaultBearerAcquirer: BearerAcquirer = async (scope) => {
  try {
    const { msalInstance } = await import('../auth/msal-provider');
    const account = msalInstance.getActiveAccount() ?? msalInstance.getAllAccounts()[0];
    if (!account) return null;
    const result = await msalInstance.acquireTokenSilent({ scopes: [scope], account });
    return result.accessToken ?? null;
  } catch {
    return null;
  }
};

/**
 * Per-user OBO bearer header (#424 M5, ADR-0057). Deny-by-default posture: when
 * no agent-host scope is configured (SIT default) this is a no-op — byte-parity
 * with M4 (no bearer, simulated/native path). When a scope is configured, attach
 * `Authorization: Bearer <token>` so the agent-host can perform the on-behalf-of
 * exchange; if the token cannot be acquired, attach nothing (the server denies
 * loudly when OBO is on rather than serving a wide read). `acquire` is injectable
 * for tests.
 */
export async function bearerHeader(
  acquire: BearerAcquirer = defaultBearerAcquirer,
): Promise<Record<string, string>> {
  const scope = getAgentHostScope();
  if (!scope) return {};
  const token = await acquire(scope);
  return token ? { Authorization: `Bearer ${token}` } : {};
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
    headers: { 'content-type': 'application/json', ...identityHeaders(env), ...(await bearerHeader()) },
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
  Object.assign(headers, await bearerHeader());
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

/**
 * Sprint 39 P2 — the operational closed loop (worklist + decisions).
 *
 * Two agent-host endpoints wired through the single IQ ingress. The role is the
 * SHORT role id the host keys on (e.g. `dca`, not `dca-agent`). Both carry the
 * caller's `ContextEnvelope` as scoped OBO/RLS identity headers so the agent-host
 * can attribute the human approver — `X-User-Oid` is the HITL approver seam
 * (NFR-UXL-001): the app never applies directly, it only submits the decision.
 */

/** One barrier/readiness observation on a role's worklist (agent-host shape). */
export interface WorklistObservation {
  patient: string;
  ward: string;
  readiness: string;
  barrier?: string;
  aged_h?: number;
  provenance: Provenance;
}

/** The single grounded recommendation attached to a worklist (agent-host shape). */
export interface WorklistRecommendation {
  lever_id: string | null;
  params?: Record<string, unknown>;
  predicted_impact?: { metric: string; value: number };
  insight_text: string;
  citations: string[];
}

/** A role's live worklist: observations + one grounded recommendation. */
export interface Worklist {
  role: string;
  ward: string;
  observations: WorklistObservation[];
  recommendation: WorklistRecommendation;
  provenance: Provenance;
}

/** The `DC-SIM-OUTCOME-v1` a single human accept/deny produces (agent-host shape). */
export interface DecisionOutcome {
  contract: string;
  plan_id: string;
  golden_thread: string;
  lever_id: string | null;
  applied_ts: string;
  predicted_impact: { metric: string; value: number };
  realised_impact: { metric: string; value: number };
  state_delta: { beds_freed: string[]; patients_discharged: string[]; patients_promoted: string[] };
  divergence: number;
  provenance: Provenance;
  applied: boolean;
  branch: string;
  decision: string;
  approver: string;
}

/** Resolve the target hospital for an operational-loop call from the envelope. */
function hospitalOf(env: ContextEnvelope): string {
  const scope = env.hospitalScope;
  return scope && scope !== 'aggregated' ? scope.toUpperCase() : 'USZ';
}

/**
 * Read a role's live worklist from the agent-host
 * (`GET /agents/{role}/worklist`, Sprint 39 P2). Carries the ContextEnvelope as
 * scoped identity headers. Throws loud on transport / HTTP error so the caller
 * degrades to its fixture and surfaces the degradation (never silently). Only
 * call when `isAgentHostConfigured()`. Returns an evidence envelope whose
 * `citations` carry the recommendation's grounding ids.
 */
export async function iqWorklist(role: string, env: ContextEnvelope): Promise<IqResult<Worklist>> {
  const res = await fetch(
    `${agentHostBaseUrl()}/agents/${encodeURIComponent(role)}/worklist?hospital=${encodeURIComponent(hospitalOf(env))}`,
    { headers: { ...identityHeaders(env), ...(await bearerHeader()) } },
  );
  if (!res.ok) throw new Error(`worklist load failed: ${res.status}`);
  const data = (await res.json()) as Worklist;
  return {
    data,
    provenance: data.provenance,
    citations: data.recommendation?.citations ?? [],
    degraded: false,
    source: 'foundry-agent',
  };
}

/**
 * Submit a single human accept/deny on a role's recommendation to the agent-host
 * (`POST /agents/{role}/decisions`, Sprint 39 P2). The `X-User-Oid` header is the
 * HITL approver: the agent-host enforces the gate (a bot/self approver → 403, a
 * missing oid → 401). The app NEVER applies directly (NFR-UXL-001); it only
 * submits the decision and renders the returned outcome. Throws loud on HTTP
 * error (the status is in the message so the caller can surface a refusal without
 * retrying). Only call when `isAgentHostConfigured()`.
 */
export async function iqDecision(
  role: string,
  decision: 'accept' | 'deny',
  params: Record<string, unknown>,
  env: ContextEnvelope,
): Promise<DecisionOutcome> {
  const res = await fetch(`${agentHostBaseUrl()}/agents/${encodeURIComponent(role)}/decisions`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', ...identityHeaders(env), ...(await bearerHeader()) },
    body: JSON.stringify({ decision, hospital: hospitalOf(env), params }),
  });
  if (!res.ok) throw new Error(`decision failed: ${res.status}`);
  return (await res.json()) as DecisionOutcome;
}
