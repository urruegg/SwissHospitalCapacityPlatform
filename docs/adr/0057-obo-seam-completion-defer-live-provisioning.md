# ADR-0057: OBO seam completion, defer live provisioning (#424 M5)

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg |
| **Decision-makers** | @urruegg |
| **Related** | [Sprint 29 design](../superpowers/specs/2026-07-26-sprint-29-foundry-iq-context-architecture-design.md), [M4 RLS design](../superpowers/specs/2026-07-28-sprint-29-m4-rls-provider-design.md), [M5 OBO seam design](../superpowers/specs/2026-07-28-sprint-29-m5-obo-seam-design.md), [ADR-0013](0013-temporary-us-region-demo-scope.md), [ADR-0016](0016-no-phi-in-mvp-demo-scope.md), [ADR-0033](0033-fabric-data-agent-as-foundry-grounding-tool.md), [ADR-0052](0052-app-context-envelope-per-agent-threads.md), [issue #424](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/424), [issue #510](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/510) |

## Context

Issue #424 milestone M5 is "Live OBO (Entra to Fabric/Foundry)". Its intent is to
let the agent-host act **on-behalf-of** the signed-in user so that Fabric and
Foundry enforce per-user, per-hospital row-level security instead of the
uniform managed-identity (model/MI) scope in place after M1–M4.

An evidence check (2026-07-28) against the running SIT stack and the deployed
Fabric artefacts established that real per-user OBO requires **four** independent
pieces, all currently absent:

1. **App token forwarding** — `apps/hcc-app-fluent` attaches only the
   `x-user-oid` / `x-hospital-scope` / `x-active-role` scope headers; it does not
   forward a bearer access token. MSAL is real (`ihzhhpf-app` SPA registration)
   but no agent-host API scope is requested.
2. **Agent-host Entra app registration** — a confidential-client registration
   with **delegated Fabric permissions** and an OBO trust to the SPA app. This
   does not exist and is **explicitly outside** the westus2 synthetic-demo scope
   fixed by ADR-0013 and ADR-0016.
3. **OBO exchange code** — `apps/hcc-agent-host/src/auth/token_validator.py`
   ships `acquire_obo_token()` as a `NotImplementedError` placeholder; the golden
   and thread endpoints do not yet extract or validate a bearer token.
4. **Dynamic-RLS TMDL + deployable persona source (#510)** — the deployed
   `capacity-dashboard` roles have **no dynamic `USERPRINCIPALNAME()` row
   predicate** and the persona table is a non-deployable local CSV. Even with a
   valid OBO token, Fabric would not scope per-hospital-by-user until #510 lands.

Pieces 2 and 4 are governance- and data-lane changes that expand the current
demo scope (new Entra consent surface; a change to the deployed semantic model).
Pieces 1 and 3 are code + config that can be completed and fully tested **without**
expanding scope, keeping SIT on its honest simulated/native defaults — mirroring
the evidence-grounded capability ladder adopted for M4 (ADR-0052, M4 design).

## Decision

Adopt **Path B: complete the OBO seam in code and configuration now; defer live
provisioning to a future, separately-gated scope expansion.**

1. **Implement the OBO exchange** (`acquire_obo_token`) as real, dependency-
   injectable `azure-identity` `OnBehalfOfCredential` logic, guarded by explicit
   configuration (`OBO_ENABLED` + `OBO_*` env). Unconfigured (the SIT default) it
   raises clearly rather than fabricating a token.
2. **Complete the ingress seam** — a `build_obo_context()` helper extracts and
   validates the `Authorization: Bearer` user assertion, and, only when OBO is
   configured, exchanges it and injects the resulting token into the existing
   `FabricDataAgentRlsProvider` and `FoundryThreadProvider`. Deny-by-default and
   honest provenance are preserved end to end.
3. **Forward the token from the app** only when an agent-host API scope
   (`VITE_AGENT_HOST_SCOPE`) is configured; otherwise the app sends no bearer and
   the server stays simulated/native. Config, not code.
4. **Thread `OBO_ENABLED` (default `false`)** through the three agent-host Bicep
   layers. SIT and PROD keep it off in this slice.
5. **Do not provision** the agent-host Entra app registration, do not request
   delegated Fabric consent, and do not change the deployed RLS model in this
   milestone. Those, together with #510, become the content of a future
   **scope-expansion ADR** and a go-live change gated by `approved-to-apply`.

## Consequences

### Positive

- M5 lands a fully-tested, config-selectable OBO path that flips to live per-user
  RLS/threads by configuration alone, with no further code change (same pattern
  as `RLS_PROVIDER` and `THREAD_PROVIDER`).
- The demo stays inside ADR-0013 / ADR-0016 (westus2, synthetic, no PHI): no new
  Entra consent surface, no change to the deployed semantic model.
- Provenance stays honest — the running SIT surface continues to report
  `simulated` / `native`, never claiming per-user enforcement it cannot make.

### Negative / deferred

- Real per-user structured Fabric RLS is **not** demonstrated live by this
  milestone; it remains gated on the future scope-expansion ADR **and** #510.
- The OBO exchange code path cannot be exercised end-to-end against live Entra in
  CI; it is verified by dependency-injected unit tests plus a configured-vs-
  unconfigured integration test, not a live token round-trip.

### Follow-up (the deferred Path A, when scope expands)

1. Register the agent-host confidential client; expose an `access_as_user` scope
   on `ihzhhpf-app`; grant + consent delegated Fabric permissions.
2. Set `OBO_ENABLED=true` + `OBO_*` and `VITE_AGENT_HOST_SCOPE`; flip
   `RLS_PROVIDER=fabric-data-agent` and `THREAD_PROVIDER=foundry`.
3. Land #510 (dynamic-RLS TMDL predicate + deployable persona source).
4. Verify per-user structured RLS under a real signed-in user; record the scope
   expansion in a new ADR superseding the demo-scope boundary for this path.

## Alternatives considered

- **Path A — full live OBO now.** Rejected for this milestone: it expands the
  ADR-0013 demo scope (new Entra consent + deployed-model change) and depends on
  #510, none of which is required to land a verifiable, honest seam.
- **Skip the seam, leave placeholders.** Rejected: it would leave M5 with no
  testable deliverable and no config path to go-live, and would repeat the
  ADR-0052 "not consumed yet" gap the ladder is designed to close.
