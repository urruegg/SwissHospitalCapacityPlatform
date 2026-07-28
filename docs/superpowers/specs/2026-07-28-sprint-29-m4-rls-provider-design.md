# Sprint 29 #424 M4 — Live Fabric RLS via staged `RlsProvider` seam

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg |
| **Status** | Draft |
| **Previous Version** | — (new) |

> **Related**: [Sprint 29 design](2026-07-26-sprint-29-foundry-iq-context-architecture-design.md) ·
> [M3 thread-provider design](2026-07-28-sprint-29-m3-live-thread-provider-design.md) ·
> [ADR-0052](../../adr/0052-app-context-envelope-per-agent-threads.md) ·
> [ADR-0013](../../adr/0013-temporary-us-region-demo-scope.md) ·
> [ADR-0016](../../adr/0016-no-phi-in-mvp-demo-scope.md) ·
> [ADR-0033](../../adr/0033-fabric-data-agent-as-foundry-grounding-tool.md) ·
> [issue #424](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/424)

## 1. Problem

Issue #424 is the Approach B (live SIT) follow-up to Sprint 29. M2 delivered the
live golden-source read path; M3 delivered the live per-agent thread minter. **M4
must make row-level security (RLS) by `hospitalScope` real and verifiable** —
"aggregated ⇒ all sites, a single site ⇒ only that site, no proven scope ⇒
nothing" — instead of the current in-process no-op.

Today the agent-host golden service (`src/golden/service.py`) enforces RLS
**in-process** via `apply_row_scope(rows, hospital_scope)` over the six committed
board fixtures. Its own docstring names this "the seam that lifts to live Fabric
RLS in #424 M4 without an app change." But:

- **RLS is currently a no-op.** All six board fixtures are **single-site** (no
  `hospital` tag), so `apply_row_scope` returns every row for every scope. The
  deny-by-default *scope/oid* gate works (`GoldenScopeError` → 401), but the
  **row filtering** cannot be observed or verified end-to-end.
- **The six fixtures are frozen.** `tests/unit/golden-export-parity.test.ts` pins
  each board JSON byte-equal to the app's `*_PINNED` constants, so RLS cannot be
  demonstrated by tagging existing board rows without rippling into app board
  rendering — out of scope for a server-side RLS milestone.
- **Real Fabric RLS needs the user's identity.** Per the Sprint 29 design (§4.1,
  "user-triggered calls use **OBO**; the Fabric semantic model enforces **RLS** by
  `hospitalScope`/`role`") and ADR-0052 (OBO + Fabric RLS are *simulated*
  together), a Fabric Direct-Lake semantic model applies per-user RLS only when
  the query runs **on-behalf-of the signed-in user**. Without OBO the agent-host
  queries under its own managed identity and Fabric returns unscoped rows. **OBO
  is #424 M5.** Therefore M4 (Fabric RLS) is coupled to M5 (OBO) exactly as M3's
  live threads were coupled to OBO.

## 2. Goals / non-goals

#### Goals

- Refactor the golden service's RLS enforcement into an **`RlsProvider` seam** so
  the enforcement point is a named, swappable unit — mirroring M3's approved
  `ThreadProvider`.
- Ship an `InProcessRlsProvider` (default) that filters synthetic rows by
  `hospitalScope`, provenance `simulated`, within ADR-0013/0016 scope (no OBO, no
  new cloud infra).
- Ship a **dormant** `FabricRlsProvider` that will query the live Fabric
  semantic model and **refuses without an OBO token** — so no code path can
  silently claim "live" RLS before M5.
- Make RLS **observable and live-verifiable in SIT now** by adding one
  server-only multi-site `network` golden resource whose rows carry `hospital`
  tags, so `aggregated ⇒ all sites`, `hospital-usz ⇒ USZ only`, `no scope ⇒ 401`
  are demonstrable against the running SIT agent-host.
- Report the enforced scope + provider provenance honestly in the golden
  response (`_rls` metadata) so the app and a human can see which path served the
  rows.

#### Non-goals

- No Entra OBO app-registration or token exchange (that is **M5**).
- No live Fabric semantic model / RLS-role provisioning (M5, gated by a
  demo-scope-expansion decision on ADR-0013).
- No change to the six pinned board fixtures or the app RoleBoard rendering.
- No PHI, ever — all rows synthetic (ADR-0016).

## 3. Decision (approved 2026-07-28)

Adopt the **staged `RlsProvider` seam** (option 1 of three), directly analogous
to the M3 `ThreadProvider` decision the user approved. The in-process provider is
the SIT default now; the Fabric provider is dormant until M5 flips it on via
**config, not code** (`RLS_PROVIDER=fabric` + an OBO token). This avoids throwaway
work, keeps provenance honest, and makes deny-by-default parity verifiable today.

Rejected alternatives:

- **Seam only, no data** — smaller, but leaves RLS un-observable live until M5;
  fails the #424 M4 acceptance ("confirm aggregated ⇒ all; site ⇒ only that
  site").
- **Pull real Fabric RLS forward now** — merges M4+M5, requires provisioning a
  Fabric Direct-Lake model + RLS roles + OBO and a demo-scope-expansion ADR;
  largest scope, defeats the milestone split.

## 4. Design

### 4.1 `RlsProvider` seam (`src/golden/rls.py`)

A small unit with one purpose: decide which rows a caller may see and stamp the
provenance of that decision.

```text
ScopeDecision(dataclass): rows: list[dict]; scope: str; provider: str; provenance: str

class RlsProvider(Protocol):
    provider: str            # "inprocess" | "fabric"
    provenance: str          # "simulated" | "live"
    def scope(self, rows, *, hospital_scope, user_oid) -> ScopeDecision: ...

class InProcessRlsProvider:   # default
    # provider="inprocess", provenance="simulated"
    # deny-by-default: empty scope or empty oid -> RlsProviderError
    # aggregated -> all rows; else rows whose "hospital" in (None, scope)

class FabricRlsProvider:      # dormant until M5
    # provider="fabric", provenance="live"
    # __init__ requires an obo_token; scope() with no token -> RlsProviderError
    # (query wiring is a TODO(M5): the live Fabric Direct-Lake call under OBO)

def build_rls_provider(*, obo_token=None) -> RlsProvider:
    # selects via RLS_PROVIDER env (default "inprocess"); "fabric" requires obo_token
```

`RlsProviderError` maps to HTTP 401 (deny-by-default) at the endpoint, preserving
the existing `GoldenScopeError` semantics. `apply_row_scope` is retained as the
in-process provider's internal helper (keeps its existing callers/tests green).

### 4.2 Multi-site `network` golden resource

Add `network` to `GOLDEN_RESOURCES` and a new `src/golden/data/network.json`
carrying synthetic **multi-site** capacity rows tagged by `hospital`
(`hospital-usz`, `hospital-ksa`, `hospital-bern`) plus site-agnostic rows (no
tag). This resource is **server-only** — no RoleBoard consumes it, so the
`golden-export-parity` guard (which pins the six boards) is untouched and the app
build is unaffected. It exists to make RLS observable:

| `X-Hospital-Scope` | rows returned |
|--------------------|---------------|
| `aggregated`       | all sites + untagged |
| `hospital-usz`     | USZ rows + untagged only |
| (absent)           | 401 (deny-by-default) |

### 4.3 Endpoint wiring (`src/api/app.py`)

`GET /golden/{resource}` (M2) builds the provider once on `HostState`
(`build_rls_provider()` → in-process in SIT), routes the scope decision through
it, and adds an `_rls` block to the JSON response:

```json
{ "...payload...": "...", "_rls": { "scope": "hospital-usz", "provider": "inprocess", "provenance": "simulated" } }
```

The existing six board payloads keep serving through the same provider (their
single-site rows are unaffected: every scope still sees them, now with honest
`_rls` provenance). Deny-by-default and unknown-resource behaviour is unchanged.

### 4.4 Config / infra

- Agent-host env `RLS_PROVIDER` (default `inprocess`) added to the agent-host
  Container App module + `infra/main.bicep`; `infra/main.json` regenerated. SIT
  leaves the default (`inprocess`); M5 will set `fabric` + supply OBO wiring.

## 5. Data flow

```text
app RoleBoard loader (M2)  --GET /golden/{resource} + X-User-Oid/X-Hospital-Scope-->
  agent-host golden endpoint
    -> build_rls_provider() [inprocess default]
    -> provider.scope(rows, hospital_scope, user_oid)
       - no oid/scope -> RlsProviderError -> 401
       - aggregated   -> all rows
       - site         -> rows tagged that site + untagged
    -> payload + _rls{scope,provider,provenance="simulated"}
```

At M5: `RLS_PROVIDER=fabric` + OBO token ⇒ `FabricRlsProvider.scope()` issues the
Direct-Lake query on-behalf-of the user; Fabric enforces RLS; provenance `live`.
No app change, no endpoint change.

## 6. Error handling

- **Deny-by-default**: empty `hospital_scope` or empty `user_oid` ⇒
  `RlsProviderError` ⇒ HTTP 401 (parity with today's `GoldenScopeError`).
- **Unknown resource**: `UnknownResourceError` ⇒ HTTP 404 (unchanged).
- **Fabric provider without OBO**: `RlsProviderError` ⇒ HTTP 401 — never a silent
  fall-through to unscoped rows.
- **Misconfig** (`RLS_PROVIDER=fabric` with no token) ⇒ `build_rls_provider`
  raises at request time; endpoint returns 503 (provider unavailable), never
  unscoped data.

## 7. Testing

- **Unit** (`tests/unit/test_rls_provider.py`, TDD red→green):
  - in-process: aggregated ⇒ all; site ⇒ only that site + untagged; deny-by-
    default on empty oid/scope; provenance `simulated`.
  - factory: default ⇒ in-process; `RLS_PROVIDER=fabric` without token ⇒ raises.
  - fabric provider: `scope()` without OBO ⇒ `RlsProviderError`.
- **Integration** (`tests/integration/test_golden_rls.py`):
  - `GET /golden/network` `aggregated` ⇒ all sites; `hospital-usz` ⇒ USZ +
    untagged; missing scope ⇒ 401; `_rls` block present with `provider=inprocess`.
  - existing six boards still 200 with `_rls` metadata; unknown resource ⇒ 404.
- **Regression**: existing `golden` + threads + chat suites stay green; app
  `golden-export-parity` untouched (new resource not pinned).

## 8. Verification in SIT (after deploy)

Against the running SIT agent-host (`salmonsand` FQDN), synthetic/no-PHI:

- `GET /golden/network` with `X-User-Oid` + `X-Hospital-Scope: aggregated` ⇒ rows
  from all three sites; `_rls.provider=inprocess`, `provenance=simulated`.
- Same with `X-Hospital-Scope: hospital-usz` ⇒ only USZ + untagged rows.
- Without `X-Hospital-Scope` (or `X-User-Oid`) ⇒ **401**.
- The six board resources still return 200 with an honest `_rls` block.

## 9. Governance

- **Scope**: ADR-0013 westus2 synthetic/no-PHI demo. In-process provider adds no
  cloud infra, no identity, no OBO — no scope-expansion ADR needed for M4. The
  Fabric provider stays dormant; enabling it at M5 is the step that requires the
  demo-scope-expansion decision.
- **Deploy**: plan-first; agent-host image rebuild + `sit.bicepparam` bump are
  approval-gated (`approved-to-apply`, AGENTS.md §4).
- **Doc versioning**: this spec v1.0.0 (§9 of copilot-instructions).

## 10. Milestone fit

M4 of the #424 chain (M1 app wiring ✅ · M2 live golden read ✅ · M3 live threads
✅ · **M4 RLS seam + observable data** · M5 OBO → `RLS_PROVIDER=fabric` +
`THREAD_PROVIDER=foundry` · M6 provenance/docs/ADR-0052 closeout). M4 makes the
RLS enforcement point real and verifiable; M5 makes it enforced by Fabric under
the signed-in user.
