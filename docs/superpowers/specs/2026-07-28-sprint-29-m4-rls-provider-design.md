# Sprint 29 #424 M4 — Live Fabric RLS via staged `RlsProvider` seam

| Field | Value |
|-------|-------|
| **Version** | 1.1.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg |
| **Status** | Draft |
| **Previous Version** | 1.0.0 (staged seam framing, pre evidence-check) |

> **Related**: [Sprint 29 design](2026-07-26-sprint-29-foundry-iq-context-architecture-design.md) ·
> [M3 thread-provider design](2026-07-28-sprint-29-m3-live-thread-provider-design.md) ·
> [ADR-0052](../../adr/0052-app-context-envelope-per-agent-threads.md) ·
> [ADR-0013](../../adr/0013-temporary-us-region-demo-scope.md) ·
> [ADR-0016](../../adr/0016-no-phi-in-mvp-demo-scope.md) ·
> [ADR-0033](../../adr/0033-fabric-data-agent-as-foundry-grounding-tool.md) ·
> [Fabric IQ ready evidence](../../architecture/fabric-iq-ready-evidence.md) ·
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

## 1.1 What is provably deployed (evidence check, 2026-07-28)

Before choosing a pattern we verified the **actual** deployed Fabric capability
(not assumptions). Sources: [`fabric-iq-ready-evidence.md`](../../architecture/fabric-iq-ready-evidence.md),
the semantic-model TMDL under `data-platform/reports/capacity-dashboard.SemanticModel/`,
and `apps/hcc-agent-host/src/tools/fabric_data_agent_client.py`.

| Capability | Proven state | Evidence |
|-----------|--------------|----------|
| Direct-Lake semantic model `capacity-dashboard` (`08245059-…`) | **Live**, gate-verified (16 rel / 27 measures / 8 RLS roles) | `verify-semantic-model.yml`; evidence §3 |
| RLS roles | **Live**, but grammar is PHI gate (`_data_quality="phi"→FALSE`), **static membership** (`member 'admin@…'`), and one **aggregated predicate** (`GuestAggregated → dim_hospital="Aggregated"`) | `definition/roles/*.tmdl` |
| Fabric Data Agent `da_hospital_capacity` (`b2e53c23-…`) | **Live**, read-only, enforces RLS + PHI, cited `hcp:*` in live probes | evidence §4/§5 |
| agent-host → Fabric auth | **User-assigned managed identity, Fabric Viewer** via `DefaultAzureCredential` — **not OBO** | `fabric_data_agent_client.py` `_default_token_provider` |

**Two independent blockers to true per-user RLS** (both must clear before the
structured read can be per-user):

1. **No OBO.** The agent-host queries under its managed identity, so Fabric sees
   one principal for every end user (already the M5 dependency).
2. **No dynamic row predicate.** Even with OBO, the deployed roles would not scope
   per-hospital-by-user: the only per-hospital filter is the *static*
   `GuestAggregated` ("Aggregated" only). The `USERPRINCIPALNAME()` persona logic
   exists **only as display measures** on `dim_persona`, sourced from a local CSV
   that "will not resolve in a Fabric deployment context" (comment in
   `dim_persona.tmdl`). A **dynamic-RLS TMDL predicate + a deployable persona
   source** are a **data-lane follow-up** ([#510](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/510), sequenced with M5).

**Consequence:** an in-process synthetic filter is honest **only** if labelled
`simulated`; a from-scratch "live per-user Fabric RLS" arm cannot work at M4
regardless of effort. The live RLS-enforcing surface that *does* exist today is
the **Fabric Data Agent** on the `/chat` grounding path (model/MI scope).

## 2. Goals / non-goals

#### Goals

- Refactor the golden service's RLS enforcement into an **`RlsProvider` seam** so
  the enforcement point is a named, swappable unit — mirroring M3's approved
  `ThreadProvider`. The seam is an **evidence-grounded capability ladder** whose
  rungs are bounded by what is provably deployable (§1.1).
- **Rung 0** — ship a `SimulatedRlsProvider` (default) that filters synthetic rows
  by `hospitalScope`, provenance `simulated`, within ADR-0013/0016 scope (no OBO,
  no new cloud infra). Honest demonstration of the RLS *shape*, never `live`.
- **Rung 1** — ship a `FabricDataAgentRlsProvider` that **reuses the proven, live**
  Fabric Data Agent client (`da_hospital_capacity`) rather than a from-scratch
  stub. It carries provenance `live`, but because the agent-host queries under its
  managed identity (§1.1) it **refuses the structured read without an OBO token**
  — so no code path can claim per-user "live" RLS before M5.
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
- No dynamic-RLS TMDL predicate or deployable persona source — that is the
  **data-lane follow-up** ([#510](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/510)) sequenced with M5.
- No change to the six pinned board fixtures or the app RoleBoard rendering.
- No PHI, ever — all rows synthetic (ADR-0016).

## 3. Decision (approved 2026-07-28, evidence-refined)

Adopt the **evidence-grounded capability ladder** on the `RlsProvider` seam,
directly analogous to the M3 `ThreadProvider` decision the user approved:

| Rung | Provider | Provenance | Scope enforced | Buildable at M4 |
|------|----------|------------|----------------|-----------------|
| 0 (now) | `SimulatedRlsProvider` | `simulated` | shape only (aggregated⇒all, site⇒one) | ✅ default |
| 1 (now) | `FabricDataAgentRlsProvider` → proven client | `live` | real PHI + model RLS, **MI/uniform** — refuses structured read without OBO | ✅ reuses proven infra |
| 2 (M5) | same path + OBO token | `live` | **per-user** — *also* needs dynamic-RLS TMDL + persona source | ⛔ data-lane work |

The simulated provider is the SIT default now; the Data-Agent provider reuses the
**already-proven** live client and is selected via **config, not code**
(`RLS_PROVIDER=fabric-data-agent`). This avoids throwaway work, keeps provenance
honest (never labels synthetic filtering `live`), and makes deny-by-default parity
verifiable today.

Rejected alternatives:

- **Synthetic-only, no live arm** — smaller, but ignores the proven Data-Agent
  capability and leaves the seam disconnected from the real RLS surface.
- **From-scratch dormant `FabricRlsProvider` stub** — reinvents a live path that
  already exists as the proven `FabricDataAgentClient`; less honest about where
  live RLS actually is.
- **Pull real per-user Fabric RLS forward now** — impossible at M4: blocked on
  both OBO **and** a dynamic-RLS TMDL change (§1.1); would merge M4+M5 and still
  require data-lane work.

## 4. Design

### 4.1 `RlsProvider` seam (`src/golden/rls.py`)

A small unit with one purpose: decide which rows a caller may see and stamp the
provenance of that decision.

```text
ScopeDecision(dataclass): rows: list[dict]; scope: str; provider: str; provenance: str

class RlsProvider(Protocol):
    provider: str            # "simulated" | "fabric-data-agent"
    provenance: str          # "simulated" | "live"
    def scope(self, rows, *, hospital_scope, user_oid) -> ScopeDecision: ...

class SimulatedRlsProvider:   # Rung 0, default
    # provider="simulated", provenance="simulated"
    # deny-by-default: empty scope or empty oid -> RlsProviderError
    # aggregated -> all rows; else rows whose "hospital" in (None, scope)

class FabricDataAgentRlsProvider:   # Rung 1, reuses the proven live client
    # provider="fabric-data-agent", provenance="live"
    # __init__(client, obo_token=None): holds the proven FabricDataAgentClient
    # scope() deny-by-default on empty scope/oid; without obo_token -> RlsProviderError
    #   (message points to the live /chat grounding path; per-user structured
    #    scope lands at M5 = OBO + dynamic-RLS TMDL). Live query is a TODO(M5).

def build_rls_provider(*, data_agent_client=None, obo_token=None) -> RlsProvider:
    # selects via RLS_PROVIDER env (default "simulated");
    # "fabric-data-agent" requires data_agent_client to be injected
```

`RlsProviderError` maps to HTTP 401 (deny-by-default) at the endpoint, preserving
the existing `GoldenScopeError` semantics (now an alias of `RlsProviderError`).
`apply_row_scope` is retained as a thin back-compat helper for existing
callers/tests.

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
(`build_rls_provider(data_agent_client=live)` → simulated in SIT), routes the
scope decision through it, and adds an `_rls` block to the JSON response:

```json
{ "...payload...": "...", "_rls": { "scope": "hospital-usz", "provider": "simulated", "provenance": "simulated" } }
```

The endpoint also stamps `X-Data-Provenance: live` (M2 semantic: the HTTP read is
live, distinct from the RLS mode) plus `X-Rls-Provider` / `X-Rls-Provenance` /
`X-Applied-Scope` headers. The existing six board payloads keep serving through
the same provider (their single-site rows are unaffected: every scope still sees
them, now with honest `_rls` provenance). Deny-by-default and unknown-resource
behaviour is unchanged.

### 4.4 Config / infra

- Agent-host env `RLS_PROVIDER` (default `simulated`) added to the agent-host
  Container App module + `infra/main.bicep`; `infra/main.json` regenerated. SIT
  leaves the default (`simulated`); M5 will set `fabric-data-agent` + supply the
  OBO wiring and the dynamic-RLS TMDL predicate.

## 5. Data flow

```text
app RoleBoard loader (M2)  --GET /golden/{resource} + X-User-Oid/X-Hospital-Scope-->
  agent-host golden endpoint
    -> build_rls_provider(data_agent_client=live) [simulated default]
    -> provider.scope(rows, hospital_scope, user_oid)
       - no oid/scope -> RlsProviderError -> 401
       - aggregated   -> all rows
       - site         -> rows tagged that site + untagged
    -> payload + _rls{scope,provider="simulated",provenance="simulated"}
```

At M5: `RLS_PROVIDER=fabric-data-agent` + OBO token ⇒ `FabricDataAgentRlsProvider`
issues the Direct-Lake read on-behalf-of the user (once the dynamic-RLS TMDL
predicate lands); Fabric enforces per-user RLS; provenance `live`. No app change,
no endpoint change.

## 6. Error handling

- **Deny-by-default**: empty `hospital_scope` or empty `user_oid` ⇒
  `RlsProviderError` ⇒ HTTP 401 (parity with today's `GoldenScopeError`).
- **Unknown resource**: `UnknownResourceError` ⇒ HTTP 404 (unchanged).
- **Data-Agent provider without OBO**: `RlsProviderError` ⇒ HTTP 401 — never a
  silent fall-through to unscoped rows; the message points to the live `/chat`
  grounding path and names M5 (OBO + dynamic-RLS TMDL).
- **Misconfig** (`RLS_PROVIDER=fabric-data-agent` with no injected client) ⇒
  `build_rls_provider` raises at startup (`HostState` construction), so the app
  fails fast rather than ever serving unscoped data.

## 7. Testing

- **Unit** (`tests/unit/test_rls_provider.py`, TDD red→green):
  - simulated: aggregated ⇒ all; site ⇒ only that site + untagged; deny-by-
    default on empty oid/scope; provenance `simulated`.
  - factory: default ⇒ `SimulatedRlsProvider`; `RLS_PROVIDER=fabric-data-agent`
    without client ⇒ raises; with client ⇒ `FabricDataAgentRlsProvider`.
  - data-agent provider: holds the injected client; `scope()` without OBO ⇒
    `RlsProviderError`; provenance `live`.
- **Integration** (`tests/integration/test_golden_rls.py`):
  - `GET /golden/network` `aggregated` ⇒ all sites; `hospital-usz` ⇒ USZ +
    untagged; missing scope ⇒ 401; `_rls` block present with `provider=simulated`.
  - existing six boards still 200 with `_rls` metadata; unknown resource ⇒ 404.
- **Regression**: existing `golden` + threads + chat suites stay green; app
  `golden-export-parity` untouched (new resource not pinned). Full agent-host
  pytest: **129 passed**.

## 8. Verification in SIT (after deploy)

Against the running SIT agent-host (`salmonsand` FQDN), synthetic/no-PHI:

- `GET /golden/network` with `X-User-Oid` + `X-Hospital-Scope: aggregated` ⇒ rows
  from all three sites; `_rls.provider=simulated`, `provenance=simulated`.
- Same with `X-Hospital-Scope: hospital-usz` ⇒ only USZ + untagged rows.
- Without `X-Hospital-Scope` (or `X-User-Oid`) ⇒ **401**.
- The six board resources still return 200 with an honest `_rls` block.

## 9. Governance

- **Scope**: ADR-0013 westus2 synthetic/no-PHI demo. The simulated provider adds
  no cloud infra, no identity, no OBO — no scope-expansion ADR needed for M4. The
  Data-Agent provider reuses the *already-approved* live Data Agent (ADR-0033/0034)
  but stays refused for the structured path until M5; enabling per-user structured
  RLS at M5 is the step that requires the demo-scope-expansion decision **and** the
  data-lane dynamic-RLS TMDL follow-up ([#510](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/510)).
- **Deploy**: plan-first; agent-host image rebuild + `sit.bicepparam` bump are
  approval-gated (`approved-to-apply`, AGENTS.md §4).
- **Doc versioning**: this spec v1.1.0 (§9 of copilot-instructions).

## 10. Milestone fit

M4 of the #424 chain (M1 app wiring ✅ · M2 live golden read ✅ · M3 live threads
✅ · **M4 RLS seam + observable data + proven-client live arm** · M5 OBO →
`RLS_PROVIDER=fabric-data-agent` + `THREAD_PROVIDER=foundry` + dynamic-RLS TMDL ·
M6 provenance/docs/ADR-0052 closeout). M4 makes the RLS enforcement point real,
observable, and honest about provenance; M5 makes it enforced per-user by Fabric
under the signed-in user. The dynamic-RLS TMDL predicate + deployable persona
source is a **data-lane follow-up** ([#510](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/510)) that must land with M5 or per-user
scope will not materialise.
