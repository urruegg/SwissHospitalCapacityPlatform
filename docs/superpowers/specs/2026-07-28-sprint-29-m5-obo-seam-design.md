# Sprint 29 #424 M5 — OBO seam completion via config-gated on-behalf-of

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg |
| **Status** | Draft |
| **Previous Version** | — (new) |

> **Related**: [Sprint 29 design](2026-07-26-sprint-29-foundry-iq-context-architecture-design.md) ·
> [M3 thread-provider design](2026-07-28-sprint-29-m3-live-thread-provider-design.md) ·
> [M4 RLS design](2026-07-28-sprint-29-m4-rls-provider-design.md) ·
> [ADR-0057](../../adr/0057-obo-seam-completion-defer-live-provisioning.md) ·
> [ADR-0052](../../adr/0052-app-context-envelope-per-agent-threads.md) ·
> [ADR-0013](../../adr/0013-temporary-us-region-demo-scope.md) ·
> [ADR-0016](../../adr/0016-no-phi-in-mvp-demo-scope.md) ·
> [issue #424](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/424) ·
> [issue #510](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/510)

## 1. Problem

After M1–M4, the agent-host scopes structured golden reads and mints threads
under its own **managed identity**: every caller is one principal to Fabric and
Foundry. The `FabricDataAgentRlsProvider` (M4) and `FoundryThreadProvider` (M3)
both **refuse** rather than serve MI-scoped rows/threads as if they were
per-user — they wait for an on-behalf-of (OBO) token. M5 must supply that token
without dishonestly claiming per-user enforcement the deployed stack cannot make.

## 1.1 What is provably in place (evidence check, 2026-07-28)

| Piece | State | Consequence |
|-------|-------|-------------|
| App MSAL (`ihzhhpf-app` SPA) | **Real** (`@azure/msal-browser`) | Can acquire tokens, but requests only `openid/profile/User.Read` |
| App → agent-host bearer | **Absent** | App sends scope headers only; no `Authorization: Bearer` |
| `acquire_obo_token()` | **Placeholder** (`NotImplementedError`) | No OBO exchange wired |
| Endpoint bearer extraction/validation | **Absent** | Golden/thread paths never read a token |
| Agent-host Entra app-reg + delegated Fabric consent | **Absent** | Outside ADR-0013/0016 demo scope |
| Dynamic-RLS TMDL + deployable persona source (#510) | **Absent** | Even with OBO, Fabric won't scope per-hospital-by-user |

Two of these (Entra app-reg, #510 TMDL) expand demo scope; two (bearer forward,
OBO exchange) are code+config completable without expansion.

## 2. Goals / non-goals

#### Goals

- Implement the OBO exchange as **real, dependency-injectable** `azure-identity`
  code, guarded by `OBO_ENABLED` + `OBO_*` config; unconfigured raises clearly.
- Add a single `build_obo_context()` ingress seam: parse + validate the bearer
  user assertion, exchange it (when configured), inject the OBO token into the
  M3/M4 providers. Preserve deny-by-default and honest provenance.
- Forward the bearer from the app **only** when `VITE_AGENT_HOST_SCOPE` is set.
- Thread `OBO_ENABLED` (default `false`) through the three agent-host Bicep layers.
- Flip to live per-user RLS/threads by **configuration alone** (no code change).

#### Non-goals

- No agent-host Entra app registration, no delegated Fabric consent, no change to
  the deployed `capacity-dashboard` RLS model (deferred per ADR-0057).
- No live token round-trip in CI — verified by DI unit tests + configured-vs-
  unconfigured integration tests.
- No SIT/PROD behavior change: both stay `OBO_ENABLED=false` → simulated/native.
- #510 (dynamic-RLS TMDL) remains a separate data-lane deliverable.

## 3. Decision (Path B, approved 2026-07-28)

Complete the OBO seam in code + config; defer live provisioning to a future
scope-expansion ADR (ADR-0057). This mirrors the M4 capability ladder: what is
provably deployable bounds each rung, and go-live is a config flip.

## 4. Design

### 4.1 OBO exchange (`src/auth/token_validator.py`)

`acquire_obo_token(user_assertion, scope, *, credential_factory=None)` becomes
real: it builds an `OnBehalfOfCredential` from `OBO_TENANT_ID` / `OBO_CLIENT_ID`
/ `OBO_CLIENT_SECRET` (or a federated assertion) and returns the exchanged token
for `scope`. The `credential_factory` parameter is injected in tests so the flow
is verified without live Entra. The `azure-identity` import is guarded so CI
without the runtime extra still imports the module. Unconfigured → raises
`TokenValidationError` (never a fabricated token).

### 4.2 Ingress seam (`src/auth/obo_context.py`)

`build_obo_context(authorization_header, *, exchange=None) -> OboContext | None`:

- No header, or `OBO_ENABLED` unset/false → returns `None` (server stays
  simulated/native; deny-by-default unchanged).
- Header present + `OBO_ENABLED=true` → strips the `Bearer` prefix, validates claims via
  `validate_claims`, exchanges via `acquire_obo_token` (or the injected
  `exchange`), and returns `OboContext(user_oid, obo_token)`.
- Any validation/exchange failure → raises (maps to 401), never a silent downgrade.

### 4.3 Endpoint wiring (`src/api/app.py`)

`HostState` reads `Authorization` on the golden + thread routes and calls
`build_obo_context`. When it returns a context, the route builds the provider
with the OBO token (`build_rls_provider(..., obo_token=ctx.obo_token)`) and, for
threads, selects the OBO-carrying `FoundryThreadProvider`. When it returns
`None`, behavior is identical to today (simulated/native). The `_rls` block and
`X-Rls-*` headers already surface provenance honestly.

### 4.4 Config / infra

`OBO_ENABLED` (default `'false'`) plus `OBO_TENANT_ID` / `OBO_CLIENT_ID` /
`OBO_CLIENT_SECRET` (Key Vault reference placeholders, empty in SIT) are threaded
through `container-app.bicep` → `agent-host/main.bicep` → `infra/main.bicep`
(`agentHostOboEnabled`, default `false`). SIT/PROD keep OBO off in this slice.

### 4.5 App token forwarding (`src/data/iq-client.ts`)

A `bearerHeader()` helper calls MSAL `acquireTokenSilent({ scopes:
[VITE_AGENT_HOST_SCOPE] })` and returns `{ Authorization: 'Bearer <token>' }`
only when the scope env is set and a token is obtainable; otherwise `{}`. It is
merged into the identity-aware calls (thread mint, chat, golden). SIT default
(no scope env) sends no bearer.

## 5. Data flow

1. App: `acquireTokenSilent(agent-host scope)` → `Authorization: Bearer` +
   scope headers (only if `VITE_AGENT_HOST_SCOPE` set).
2. Agent-host route: `build_obo_context(Authorization)` →
   `None` (simulated/native) **or** `OboContext(user_oid, obo_token)`.
3. With a context: `build_rls_provider(client, obo_token)` /
   `FoundryThreadProvider` run on-behalf-of; provenance `live`.
4. Without: unchanged M4/M3 behavior; provenance `simulated`/`native`.

## 6. Error handling

- Missing/invalid bearer while `OBO_ENABLED=true` → 401 (deny-by-default).
- `OBO_ENABLED=true` but `OBO_*` unset → startup misconfiguration raises (fail
  fast, never serve unscoped as scoped).
- Exchange failure → 401, honest error, no downgrade to simulated under the guise
  of live.

## 7. Testing

- **Unit** (`tests/unit/test_obo_context.py`, `test_token_validator_obo.py`):
  no header → `None`; header + disabled → `None`; header + enabled → exchanges
  via injected fake and returns context; invalid token → raises; exchange error
  → raises; `acquire_obo_token` builds the credential from config and calls the
  injected factory; unconfigured raises.
- **Integration** (`tests/integration/test_golden_obo.py`): `OBO_ENABLED=false`
  → golden read unchanged (simulated, 401 without scope); `OBO_ENABLED=true` with
  an injected exchange → provider receives the OBO token (asserted via the M4
  provider refusal message flipping to the M5 "pending TMDL" refusal, proving the
  token reached the provider). No live Entra.
- Full agent-host `pytest` stays green.

## 8. Verification in SIT (after deploy)

SIT keeps `OBO_ENABLED=false`, so live verification is parity: `/golden/*` and
thread mint behave exactly as after M4/M3 (simulated/native, deny-by-default,
`_rls.provider=simulated`). The OBO path is proven by tests, not a live flip —
the live flip is the deferred Path A (ADR-0057).

## 9. Governance

- ADR-0057 records the Path B decision and the deferred Path A follow-up.
- Stays inside ADR-0013 (westus2) / ADR-0016 (no PHI): no new Entra consent, no
  deployed-model change.
- Secrets: `OBO_CLIENT_SECRET` is a Key Vault reference placeholder, never a
  literal (copilot-instructions §4). Empty in SIT.
- Go-live (Path A) is a separate, `approved-to-apply`-gated change plus #510.

## 10. Milestone fit

M5 of six (M1–M4 live in SIT). Completes the OBO seam so M6 can close #424 with a
config-flip-ready per-user path. #510 (data-lane dynamic-RLS TMDL) is sequenced
with the deferred go-live, not this milestone.
