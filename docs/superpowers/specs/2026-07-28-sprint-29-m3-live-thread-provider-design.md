# Sprint 29 #424 M3 — Live thread map via staged `ThreadProvider` seam

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg |
| **Status** | Draft |
| **Previous Version** | — (new) |

> **Related**: [Sprint 29 design](2026-07-26-sprint-29-foundry-iq-context-architecture-design.md) ·
> [ADR-0052](../../adr/0052-app-context-envelope-per-agent-threads.md) ·
> [ADR-0013](../../adr/0013-temporary-us-region-demo-scope.md) ·
> [ADR-0016](../../adr/0016-no-phi-in-mvp-demo-scope.md) ·
> [ADR-0032](../../adr/0032-foundry-control-plane-eastus2.md) ·
> [ADR-0033](../../adr/0033-fabric-data-agent-as-foundry-grounding-tool.md) ·
> [issue #424](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/424)

## 1. Problem

Sprint 29 shipped the app-side context architecture (Approach A) with a
**config-gated, simulated** `(userOid × agent) → threadId` map. Issue #424 is the
Approach B SIT follow-up. M2 delivered the live golden-source read path. **M3 must
replace the simulated thread minter with a live one** so each board-agent's chat
threads its turns server-side, with honest live-vs-simulated provenance.

Today:

- The app (`copilot-drawer/useConversation.ts`) calls `foundryThreadMap.getOrCreate(env)`
  with a **simulated** minter (`sim-thread-…`) and then **discards** the threadId
  (comment: "handed to the agent-host in #424 M3"). Chat POSTs `{prompt}` only.
- The agent-host `POST /agents/{name}/chat` already accepts a `conversationId` and
  threads it through `orchestrator.dispatch(conversation_id=…)`, but there is **no
  mint endpoint** and no identity-header contract on chat.
- `persistence/cosmos_client.py` already exposes a Cosmos-swappable `conversations`
  container partitioned by `conversationId` (in-memory stand-in today).
- `tools/fabric_data_agent_client.py` already implements the **real** Foundry
  Assistants `POST /threads` → messages → runs pattern (proof the Foundry thread
  machinery exists in-repo).

## 2. The decision: staged / mixed, not either-or

### What the target design mandates

The Sprint 29 design §4.1 north-star is **real Foundry-managed threads**
(`chat + envelope → Foundry thread per user × agent → Foundry IQ`) minted under
the user's **OBO** token (§4.2, ADR-0052 Decision items 5–6). So the sustainable
end-state is **Option 2** (real Foundry threads + OBO). But Option 2 is only
meaningful **with OBO**, which is milestone **M5** — minting a "real" Foundry
thread now under *app* identity would violate the OBO-per-user rule and be a
throwaway.

### Chosen approach

Implement M3 as **Option 1's backend behind the interface Option 2 needs**, then
flip at M5 — the design's own *"config, not code"* seam philosophy.

Introduce a server-side **`ThreadProvider`** abstraction with two implementations:

| Provider | Backend | Provenance | Status |
|----------|---------|------------|--------|
| `NativeThreadProvider` | existing `CosmosPersistence.conversations` seam (in-memory now, Cosmos later) | `native` | **default in SIT (M3, now)** |
| `FoundryThreadProvider` | eastus2 Foundry Assistants threads API (pattern already in `fabric_data_agent_client.py`) | `foundry` | config-selected, dormant until **M5 (OBO)** |

The app gets a **real live minter round-trip** either way; the mint endpoint and
identity headers are built once and reused verbatim by Option 2. At M5, lighting
up the Foundry provider is a **config flip + OBO token source**, not an app or
interface change.

### Why this is sustainable

1. **No throwaway** — the M3 endpoint, app minter, identity headers, and tests are
   reused verbatim by Option 2.
2. **Honest provenance at every stage** — `native` now, `foundry` at M5; never a
   silent "live".
3. **Governance-clean** — the native path stays inside ADR-0013 synthetic scope
   (no new infra, no OBO), so M3 ships without a scope-expansion ADR. That ADR is
   added exactly when it is needed (M5), covering real Foundry-thread persistence
   plus OBO app-registration.
4. **Respects the M-chain** — threads (M3) before OBO (M5), matching the design's
   dependency order.

## 3. Design

### 3.1 Agent-host (server)

- **`ThreadProvider` interface** (`orchestrator/` or new `threads/` module):
  `mint(user_oid, agent) -> ThreadRef{ thread_id, provenance }` (idempotent per
  `(user_oid × agent)`); `provenance ∈ {native, foundry}`.
  - `NativeThreadProvider`: derives a stable id from `(user_oid × agent)`,
    persists `(oid×agent) → thread_id` + seeds a `conversations` record via
    `CosmosPersistence`. Returns the existing id on repeat.
  - `FoundryThreadProvider`: config-selected; calls the eastus2 Foundry Assistants
    threads API (reusing the `fabric_data_agent_client.py` pattern). **Not wired in
    M3** — interface + a stub/guard that refuses without OBO context; fully lit at
    M5. Selected by an env flag (e.g. `THREAD_PROVIDER=native|foundry`).
- **`POST /agents/{name}/threads`** — identity headers `X-User-Oid` (required,
  **deny-by-default** 401 without it, mirroring `/golden`), `X-Active-Role`.
  Returns `{ threadId, provenance }`. Idempotent per `(userOid × agent)`.
- **`POST /agents/{name}/chat`** — extended to accept `threadId` (falls back to the
  legacy `conversationId` default for back-compat) + the same identity headers;
  dispatch keeps `conversation_id = threadId` so turns thread server-side.
- Persistence stays in-memory `CosmosPersistence` in M3 (Cosmos swap is a later
  toggle, out of scope here).
- CORS already allows `x-user-oid` / `x-active-role`; add the new verb if needed.

### 3.2 App (`apps/hcc-app-fluent`)

- **`data/iq-client.ts`** (single ingress — only permitted `fetch` site):
  - add `iqMintThread(agent, env) -> { threadId, provenance }` → `POST /threads`
    with identity headers.
  - extend `iqAgentChat(agent, prompt, threadId)` to send `threadId` + identity
    headers.
- **`copilot-drawer/foundry-thread-map.ts`** — inject a **live minter** that calls
  `iqMintThread` when threads are enabled + host configured; keep the simulated
  minter as the offline/CI fallback (honest `simulated` provenance when no host).
- **`copilot-drawer/useConversation.ts`** — pass the resolved `threadId` into
  `invokeAgent` → `iqAgentChat` (stop discarding it).
- **`copilot-drawer/agent-manifest.ts`** — thread `threadId` through `invokeAgent`.
- **Runtime-injectable `FOUNDRY_THREADS_ENABLED`** — mirror M2's `GOLDEN_SOURCE_URL`
  (`runtime-config.ts` + `docker-entrypoint.d/30-env-config.sh` + `vite-env.d.ts`)
  so one image flips the flag per-env without a rebuild.
- `context/session-reset.ts` already resets `foundryThreadMap` on sign-out —
  unchanged.

### 3.3 Infra / deploy (governed, gated)

- Bicep: add a runtime-injected `FOUNDRY_THREADS_ENABLED` env to the app-fluent
  module (mirror the M2 `GOLDEN_SOURCE_URL` pattern); set
  `appFluentFoundryThreadsEnabled=true` in `sit.bicepparam`. Optional
  `THREAD_PROVIDER=native` env on the agent-host module (defaults to native).
- Governed two-step rollout: build both images (mergeSHA) → SIT ACR (approve `sit`
  gate) → bump `agentHostImage` + `appFluentImage` in `sit.bicepparam` → merge →
  `cd-infra-deploy-sit.yml` (approve `sit` gate). **`approved-to-apply` required.**

### 3.4 Error handling

- Mint without `X-User-Oid` → 401 deny-by-default (no silent guest thread).
- `FoundryThreadProvider` selected without OBO context (pre-M5) → refuse + honest
  error; never fall back to app-identity mint.
- Thread-mint failure in the app → fall back to a fresh local thread + `simulated`
  provenance; never cross-contaminate another agent's context.

## 4. Testing (TDD, red → green)

Agent-host (pytest):

- mint is idempotent per `(oid × agent)`; different agent/user ⇒ new threadId.
- mint deny-by-default without `X-User-Oid` (401).
- `NativeThreadProvider` persists + reuses via `CosmosPersistence`.
- chat with `threadId` threads history; legacy `conversationId` still works.
- `FoundryThreadProvider` refuses without OBO context (pre-M5 guard).

App (vitest):

- live minter calls the host once per `(user × agent)` and reuses.
- `threadId` flows to `iqAgentChat`; identity headers attached.
- offline / no-host path stays `simulated`.
- reset on sign-out clears the map.

Gates: `npm --prefix apps/hcc-app-fluent run lint && run build && test` +
agent-host pytest + Playwright smoke/a11y on any UI change.

## 5. Live verification (SIT, after deploy)

- mint returns a stable id per `(user × agent)` across turns; a different agent ⇒
  new id; sign-out clears; chat history threads.
- deny-by-default without identity; provenance honest (`native`).
- app front-end 200; `env-config.js` injects `FOUNDRY_THREADS_ENABLED`.

## 6. Governance

- Native path (M3): no new Azure resource, no PHI, no OBO → **within ADR-0013 /
  ADR-0016**. No scope-expansion ADR required for M3.
- Foundry path (M5): real Foundry-thread persistence + OBO app-registration →
  **needs a demo-scope-expansion ADR** (added at M5), plus M6 records the
  provider decision in an ADR referencing this spec.
- Synthetic data only; no PHI ever. Every deploy step plan-first + fresh
  `what-if` + `approved-to-apply`.

## 7. Out of scope (M3)

- OBO / real Foundry-thread persistence (M5).
- Fabric semantic-model RLS (M4).
- Cosmos live persistence swap (later toggle).
- PROD lift (separate gate).
