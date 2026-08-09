---
Version: 1.0.0
Date: 2026-08-09
Author: Copilot coding agent (autopilot, delegated)
Status: Draft
Previous Version: n/a (initial brainstormed design)
---

# OBO as the Preferred End-to-End Pattern: Context-Sensitive Boards + Role-Agent Decisions with a Tracked Audit Trail — Design

> Produced via the Superpowers `brainstorming` skill. User asked directly:
> "brainstorm if we use OBO as our preferred design pattern, what needs to be
> changed in the underlying platform configuration, that it works end to end
> knowing about the tenant limitation... achieve a demoable showcase end to
> end using the admin account with all assigned roles to get context
> sensitive (board recommendations at the context) and asking the role agent
> to get the actionable recommendation from golden sources back to either
> accept or deny with a tracked audit trail." User was unavailable for the
> normal one-question-at-a-time dialogue and explicitly said: *"work
> autonomously and make good decisions."* This design is therefore built from
> direct, empirical investigation of this tenant's and this codebase's actual
> state (documented below), following the same evidence-first discipline as
> [the same-day OBO grounding design](2026-08-09-obo-self-service-fabric-grounding-design.md).
> **Not yet implemented — Entra mutations require `approved-to-apply` per
> AGENTS.md §4; this doc is the brainstorm + design artefact.**

## 1. Context

### 1.1 What already exists (found by direct inspection, not assumed)

This is not a green-field ask. Investigating the live tenant and the codebase
turned up substantially more already-built plumbing than expected:

| Piece | State |
| ----- | ----- |
| **Frontend RBAC model** (`apps/hcc-app-fluent/src/auth/rbac-model.ts`) | 17 `HCC.*` roles fully defined (`HCC.SuperAdmin` ... `HCC.Auditor`), each with a hospital scope, agent ceiling, and nav capability — mirrors `data/entra/app-roles.csv` master data. |
| **`ihzhhpf-app` Entra App Roles** | **Already live** — confirmed via Graph: all 17 roles are defined on the SPA registration today. |
| **`admin@`'s role assignments on `ihzhhpf-app`** | **Already live** — confirmed via Graph: `admin@` holds 16 of the 17 roles (`HCC.SuperAdmin`, `HCC.PlatformAdmin`, `HCC.BedManager`, `HCC.DischargeCoordinator`, ... all but `HCC.GuestReadOnly`'s peers are present; the full list was pulled live). |
| **Frontend role-lens** (`context/role-context.tsx`, `context/context-envelope.ts`) | Already derives `heldRoles`/`activeRole`/`hospitalScope` from the ID token's `roles` claim, defaults to least-privilege (`HCC.Viewer`) when absent, and **narrows-only** (never elevates) when a user switches roles in-session. This is genuinely real identity-driven UX already, not simulated — the "System Administrator / HCC.SuperAdmin" badge seen live in this session's browser testing was this real mechanism at work. |
| **`hcc-agent-host` Entra App Roles** | **Empty** (`appRoles: []`) — the backend resource app has no role model at all. |
| **`ValidatedCaller` claim extraction** (`auth/token_validator.py`) | Already parses `roles`, `hospital`, `env` out of any validated JWT — but... |
| **`OboContext`** (`auth/obo_context.py`) | ...only carries `user_oid` + `obo_token` forward. `roles`/`hospital` are extracted then thrown away before reaching any endpoint. |
| **`X-Active-Role` / `X-Hospital-Scope` headers** (`api/app.py`) | Currently the **only** source of role/hospital context the backend sees — client-supplied, unverified against the caller's real assigned roles even when a valid OBO bearer is presented. |
| **Role-agent recommendation → accept/deny loop** (`loop/worklist.py`, `loop/decisions.py`, `/agents/{name}/worklist`, `/agents/{name}/decisions`) | **Already built** (Sprint 39 P2). Produces a real, well-shaped outcome (`DC-SIM-OUTCOME-v1`: `golden_thread`, `citations`, `predicted_impact`, `approver`, `applied`, `provenance`). Only `dca-agent` has a real lever; the other 4 roles return an honest "role effect pending" placeholder. Runs on a bundled static JSON snapshot (`gold-snapshot-usz.json`), not the live/OBO Fabric adapter chat already uses. |
| **`x_user_oid` on `/decisions`** | The **only** identity behind "approver" — a plain client header, not cross-checked against any verified token. `plan_runtime.approve_action` refuses a bot/self-named approver, but does not verify the oid is real. |
| **Durable audit storage** (`persistence/cosmos_client.py`) | `CosmosPersistence` is **always** the in-memory stand-in — no live Cosmos wiring exists anywhere in `hcc-agent-host` (unlike the `csa-agent`, which has a real Cosmos account). `loop/decisions.py`'s `decide()` even builds a throwaway `InMemoryStore()` per call. "Tracked audit trail" today means "shaped like one," not "persisted." |

### 1.2 The actual root cause of today's SIT incident (re-diagnosed)

Issue #569 (filed earlier this session) proposed splitting `OBO_ENABLED` into
two flags because enabling it broke `/golden`. Re-reading `build_obo_context`
closely during this brainstorm found a **more precise** root cause: the
function does not distinguish *"no bearer was presented at all"* (a Demo-mode
or legacy caller) from *"a bearer was presented but is invalid"* — both raise
`TokenValidationError` → 401 whenever `OBO_ENABLED=true`. Demo mode never
sends a bearer, so turning OBO on globally hard-blocks every Demo-mode read,
regardless of which endpoint. **This is a bearer-presence bug, not a
cross-endpoint-flag-scoping problem.** §4 Approach A fixes this directly and
**supersedes** #569's proposed flag split with a smaller, more correct fix
(the design notes this explicitly; #569 should be closed in favour of this
design once approved).

### 1.3 The tenant limitation, reconfirmed for this new surface

The same finding validated for Fabric OneLake access (2026-08-09, see the
sibling design doc) applies here too: **owner-only, self-service operations
need no Fabric/Power BI/Global Administrator.** Confirmed live for the new
surface this design needs:

- `admin@` is the sole **owner** of both `hcc-agent-host` and (implicitly,
  having registered it) `ihzhhpf-app`.
- Defining App Roles on an app registration and assigning them to users via
  the corresponding Enterprise Application's "Users and groups" pane is an
  **owner-level** capability — no directory role (Application Administrator,
  Cloud Application Administrator, Global Administrator) is required. This is
  not a guess: it is the exact mechanism that put `ihzhhpf-app`'s 17 roles and
  `admin@`'s 16 assignments in place already, live, in this tenant.
- `hcc-agent-host`'s service principal has `appRoleAssignmentRequired: false`
  (any org member can sign in) — orthogonal to explicit role assignment,
  which is what actually populates the `roles` claim.
- No new consent screen is triggered by adding/assigning app roles — this is
  an application-configuration action by the owner, not a permission grant
  requiring user or admin consent.

## 2. Goals

- Make the **admin account's real, already-assigned Entra roles** (not a
  client-side simulated switcher) drive which board and which role-agent
  recommendation the demo shows — "context sensitive" end to end, including
  on the **backend**, not just the frontend badge.
- Let a demo user ask a role agent (starting with `dca-agent`, which already
  has a real lever) for its actionable recommendation, see the golden-sourced
  citations behind it, and **Accept** or **Deny** it.
- Make that Accept/Deny decision produce a **durably persisted**, identity-
  verified audit record — not just a well-shaped in-memory response.
- Do all of this using **OBO as the standard, always-preferred auth pattern**
  for any authenticated ("User mode") request, while **Demo mode** (no
  sign-in) continues to work unchanged — fixing the actual bug that broke it
  earlier today, not working around it with a second flag.
- Continue requiring **zero Fabric/Power BI/Global Administrator** action —
  everything here is owner-level, self-service, exactly like the sibling OBO
  grounding design.

## 3. Non-goals (explicitly deferred, already tracked elsewhere)

- **True per-hospital dynamic Fabric RLS** (`RLS_PROVIDER=fabric-data-agent`
  Rung 2) — needs issue #510 (dynamic-RLS TMDL predicate) and is already
  tracked by issue #560. Out of scope here; `/golden` keeps its existing
  simulated-vs-live-managed-identity behavior, now just reachable under OBO
  without the incident bug.
- **Replacing the deterministic `SimState`/`compute_expected_impact` engine**
  with live Fabric aggregates — a real engineering effort (translating Gold
  rows into the fixture shape the sim expects) that is not required to make
  the showcase honest: the existing `provenance` labeling already
  distinguishes simulated math from live reads, and this design adds a
  **real, live-grounded citation** alongside the (still honestly-labeled
  simulated) recommendation math, rather than rewriting the engine. Flagged
  as a Phase 2 stretch, not core.
- **The other 4 role agents' real levers** (`bmca`, `ooa`, `orsa`, `sba`) —
  each returns an honest placeholder today; giving them real levers is
  separate, larger, per-role work.
- **B2B guest onboarding** — already captured as its own deferred track in
  `docs/superpowers/ideas/2026-08-02-signin-followups-b2b-guest-and-obo-rls.md`.
- **Custom `hospital` claim per user** — no per-user hospital custom claim is
  configured on `ihzhhpf-app` today (single-site USZ demo default). Adding one
  needs a claims-mapping-policy feasibility check (uncertain whether that's
  owner-level or admin-gated) and is not required for the core ask (role
  context is the primary "context sensitive" driver; hospital stays the
  existing `aggregated`/`APP_HOME_HOSPITAL` override).

## 4. Approaches considered

### Approach A (recommended) — Fix bearer-presence semantics + mirror roles onto the backend + durable audit trail

Three small, independent, testable changes, sequenced to be safe at every
step:

1. **Fix `build_obo_context`'s deny-by-default semantics.** Distinguish "no
   `Authorization` header at all" (→ `None`, unchanged simulated/native path,
   exactly like OBO being off) from "a header was presented but decode/
   validate/exchange failed" (→ still raises, still a 401 — deny-by-default
   preserved for anyone who actually attempted auth). This one change makes
   `OBO_ENABLED=true` safe to leave on globally: Demo mode (no bearer, ever)
   is unaffected; User mode (always sends a bearer once `VITE_AGENT_HOST_SCOPE`
   is configured) gets real enforcement. Supersedes #569.
2. **Mirror the 17 `HCC.*` App Roles + `admin@`'s assignments from
   `ihzhhpf-app` onto `hcc-agent-host`** (owner-level, self-service, gated by
   `approved-to-apply` per AGENTS.md §4 — a new IAM surface even though no
   admin is needed). This makes the **access token** used for the OBO bearer
   (audience = `hcc-agent-host`) carry the same `roles` claim the **ID
   token** already carries, so server-side code can see it.
3. **Propagate `roles`/`hospital` through `OboContext`** (add the two fields;
   `build_obo_context` already has `ValidatedCaller.roles`/`.hospital` in
   hand, just needs to forward them) and **validate, don't just trust,**
   `X-Active-Role`/`X-Hospital-Scope` against them: when an OBO context is
   present, the requested active role must be a member of `obo.roles`
   (mirrors the frontend's existing narrow-only rule, now enforced
   server-side too); a mismatch is a 403, not a silent widen. When OBO is
   absent (Demo mode), behavior is unchanged (today's trust-the-header
   posture, which is an accepted, already-existing, ADR-0016-scoped risk on
   synthetic no-PHI data).
4. **Extend `/agents/{name}/worklist` and `/agents/{name}/decisions`** to
   also read the `authorization` header and build an OBO context, deriving
   `caller_oid`/`approver` from the **verified token oid** when present
   (falling back to the existing `x_user_oid` header when OBO is absent —
   unchanged Demo-mode behavior). This closes the "approver identity is an
   unverified header" gap for the authenticated path, which matters
   precisely because this is the identity that lands in the audit trail.
5. **Wire the same per-request OBO `FabricAdapter`** (`state.fabric_for`,
   already built for chat) into `build_worklist` as a **corroborating
   citation lookup**: when OBO is present, attempt a live `/golden`-equivalent
   read for the role's relevant table and attach it as an additional,
   honestly-labeled `liveGroundingCitations` alongside the existing
   simulated-engine `citations` — not a replacement for the deterministic
   math (see §3 non-goals), just real evidence sitting next to it.
6. **Implement a live `CosmosPersistence`** and wire `/agents/{name}/decisions`
   to write its outcome into the `approval-events` container. **Re-verified
   live during this brainstorm: the infra for this already exists and is
   already deployed** — `infra/modules/agent-host/cosmos.bicep` provisions a
   **dedicated** `cosmos-ihzhhpf-sit` account (confirmed live via `az
   cosmosdb list`), its `agenthost` database already has the
   `approval-events` container (confirmed live via `az cosmosdb sql container
   list`), `COSMOS_ENDPOINT` is already injected into the running container
   (`container-app.bicep`), and `Cosmos DB Built-in Data Contributor` is
   already granted to the agent-host's managed identity
   (`main.bicep`'s `agentHostCosmosDataContributor`). **This is a pure
   application-code gap, not an infra gap** — `persistence/cosmos_client.py`'s
   `CosmosPersistence` simply never got a live-`azure-cosmos` implementation.
   Config-gated exactly like `_build_chat_model`/`_build_live_data_agent`:
   absent `COSMOS_ENDPOINT` → today's in-memory behavior, unchanged; no new
   Bicep required.
7. **Re-enable `agentHostOboEnabled=true`** in `sit.bicepparam` once (1)-(6)
   are live-verified — this time safe, because Demo mode's no-bearer traffic
   is no longer refused by construction.

**Trade-offs:** more moving pieces than a pure config flip, but every piece is
small, independently unit-testable (mirrors this repo's existing
dependency-injection test discipline — no live Entra/Cosmos needed for CI),
and reversible. The Entra role-mirroring step is a new IAM surface requiring
its own `approved-to-apply` comment, same governance gate as the sibling OBO
design's app registration.

### Approach B — Keep client-trusted role headers; only add live Fabric grounding + Cosmos persistence

Skip mirroring App Roles onto `hcc-agent-host` and the server-side role
validation (items 2-3 above); keep trusting `X-Active-Role` as-is; only fix
the bearer-presence bug, extend worklist/decisions with OBO-derived oid, and
add Cosmos persistence.

**Rejected as primary, but the fallback if role-mirroring hits an
unexpected blocker:** smaller and faster, but leaves the exact spoofing gap
this brainstorm surfaced ("any caller can claim any active role via a plain
header") open on the one surface (accept/deny + audit trail) where an
unverified identity matters most — a human's recorded decision. Given the
role-mirroring is proven mechanically to work (it already worked once, live,
for `ihzhhpf-app`), there is no real reason to accept this residual risk.

### Approach C — Full live-Fabric-fed decision engine (replace `SimState`'s gold source entirely)

Rewire `build_worklist`/`decide()` to compute impact from live OBO'd Fabric
Gold rows instead of the bundled JSON snapshot.

**Rejected for this design** (kept as the named Phase 2 in §3): materially
larger (needs a Gold-rows-to-`SimState`-fixture translation layer per role),
not required to make the showcase honest (provenance labeling already
distinguishes real from simulated), and would delay the achievable Phase 1
that directly answers the four things asked for (OBO end to end, context
sensitivity, a role-agent decision, a tracked audit trail).

## 5. Architecture (Approach A)

```mermaid
sequenceDiagram
    participant User as admin@ (User mode, real sign-in)
    participant SPA as hcc-app-fluent
    participant Host as hcc-agent-host
    participant Entra as Microsoft Entra ID
    participant Cosmos as Cosmos (approval-events)

    User->>SPA: Sign in; role lens shows all 16 held HCC.* roles
    User->>SPA: Narrow to HCC.DischargeCoordinator
    SPA->>Host: GET /agents/dca-agent/worklist  Bearer <token, roles=[...]>
    Host->>Host: build_obo_context -> OboContext(oid, roles, hospital, obo_token)
    Host->>Host: validate X-Active-Role in obo.roles (403 if not)
    Host->>Host: build_worklist(dca, SimState) + live citation lookup via fabric_for(obo_token)
    Host-->>SPA: observations + recommendation (simulated math) + liveGroundingCitations (real, if reachable)
    User->>SPA: Accept
    SPA->>Host: POST /agents/dca-agent/decisions  Bearer <token>  {decision:"accept"}
    Host->>Host: decide(..., approver=obo.user_oid)  [verified oid, not a header]
    Host->>Cosmos: write("approval-events", DC-SIM-OUTCOME-v1 + approver + golden_thread)
    Host-->>SPA: outcome (applied, predicted/realised impact, provenance)
```

### 5.1 New / changed pieces

| Piece | File(s) | Change |
| ----- | ------- | ------ |
| Bearer-presence-aware deny-by-default | `apps/hcc-agent-host/src/auth/obo_context.py` | `build_obo_context`: empty/absent `Authorization` header → `None` even when `OBO_ENABLED=true` (today it raises); a **present-but-invalid** bearer still raises. New unit tests for both branches. |
| `OboContext` carries roles/hospital | `apps/hcc-agent-host/src/auth/obo_context.py` | Add `roles: tuple[str, ...]` and `hospital: str` fields, populated from the already-computed `ValidatedCaller`. |
| Server-side role/hospital validation | `apps/hcc-agent-host/src/api/app.py` | `golden()` and `chat()`: when `obo` is present, reject (`403`) an `X-Active-Role` not in `obo.roles`; when absent, unchanged. |
| Worklist/decisions accept a bearer | `apps/hcc-agent-host/src/api/app.py` | `/agents/{name}/worklist` and `/agents/{name}/decisions` gain an `authorization` header param; `caller_oid`/`approver` prefer `obo.user_oid` over `x_user_oid` when present. **No frontend change needed** — `iqWorklist`/`iqDecision` in `apps/hcc-app-fluent/src/data/iq-client.ts` already attach `bearerHeader()` (confirmed by inspection); the backend just isn't reading it on these two routes yet. |
| Live grounding citation in worklist | `apps/hcc-agent-host/src/loop/worklist.py`, `api/app.py` | `build_worklist` gains an optional `fabric` param (type `FabricAdapter \| None`); when present, attempts a real read for the role's table and attaches `liveGroundingCitations` (empty/absent on any failure — honest graceful-miss, mirrors `FabricDeltaClient.query()`'s existing behavior). |
| Real, config-gated Cosmos persistence | `apps/hcc-agent-host/src/persistence/cosmos_client.py`, `api/app.py` | New `LiveCosmosPersistence` built only when `COSMOS_ENDPOINT` env is non-empty (already injected live, see §1.1/§4), using `azure-cosmos` + `DefaultAzureCredential` (mirrors `_build_chat_model`/`_build_live_data_agent`'s guarded-optional pattern; RBAC already granted, no new IAM). The `/decisions` endpoint writes `decide()`'s outcome to `approval-events` keyed by `correlationId`. **No Bicep change needed** — infra is already deployed. |
| Entra: mirror App Roles + assignments | (Entra config, no code) | 17 `HCC.*` App Roles added to `hcc-agent-host`; `admin@` assigned the same set already held on `ihzhhpf-app`. `approved-to-apply` gated. |

## 6. Risks / open items

- **Role-mirroring is a new IAM surface** — even though owner-level and
  self-service, AGENTS.md §4 requires its own `approved-to-apply` comment
  before any Entra write. Not yet executed; this doc is the plan for it.
- **`liveGroundingCitations` on `worklist` could 401/403** if the caller's
  active role doesn't intersect with a table the role needs — must fail
  gracefully to "no live citation" (matching `FabricDeltaClient`'s existing
  graceful-miss contract), never surface as a hard error on what is otherwise
  a successful worklist read.
- **Server-side role validation could regress an existing legitimate flow**
  if any current caller relies on requesting a role wider than what's on the
  `hcc-agent-host` token (e.g., before the mirrored assignments are fully in
  place) — sequence the Entra mirroring **before** flipping on the server-
  side validation check, and keep the check OBO-gated (absent OBO = unchanged
  today's behavior) so Demo mode never regresses.
- **This supersedes issue #569** — once this design's item (1) ships and is
  verified, #569 (the flag-split idea) should be closed with a comment
  pointing here, not implemented separately.
- **Consistent with, not a replacement for, ADR-0057** — ADR-0057 explicitly
  deferred the *board-data* Fabric Data Agent Rung 1/2 RLS depth (needs
  #510). This design does not touch that; it operates entirely on top of the
  already-decided OBO seam, extending its *reach* (which endpoints use it,
  whose identity claims propagate) rather than its *depth* (how Fabric itself
  enforces row scope).

## 7. Sequencing

1. `obo_context.py` bearer-presence fix + `OboContext.roles`/`.hospital` +
   unit tests (no live Entra needed — same dependency-injection discipline
   as existing OBO tests). Safe to ship alone; makes `OBO_ENABLED=true` safe
   for `/golden` and `/chat` regardless of the rest of this plan.
2. Entra: mirror App Roles + `admin@`'s assignments onto `hcc-agent-host`
   (`approved-to-apply` gate).
3. Server-side role/hospital validation in `golden()`/`chat()`, gated on OBO
   presence; unit tests for both the matching and mismatched cases.
4. Extend `/worklist` and `/decisions` to accept a bearer; derive
   `caller_oid`/`approver` from `obo.user_oid` when present; unit tests.
5. Live grounding citation in `build_worklist` (optional `fabric` param);
   unit tests with a fake `FabricAdapter`.
6. Implement `LiveCosmosPersistence` (config-gated on `COSMOS_ENDPOINT`,
   already deployed and injected — no new Bicep) and wire `/decisions` to
   write outcomes to `approval-events`; unit tests with the existing
   in-memory fake plus a new "live-when-configured" test mirroring
   `_build_chat_model`'s pattern.
7. Flip `agentHostOboEnabled=true` in `sit.bicepparam` (the only remaining
   Bicep change).
8. Live verification: sign in as `admin@`, narrow to `HCC.DischargeCoordinator`,
   confirm the worklist shows a real corroborating citation, Accept a
   recommendation, confirm the outcome is queryable from Cosmos with the
   verified oid as approver. Confirm Demo mode (no sign-in) is unaffected
   throughout.
9. Update issue #567 with the live evidence; close #569 in favour of this
   design's item (1).

## 8. Traceability

Extends [ADR-0057](../../adr/0057-obo-seam-completion-defer-live-provisioning.md)'s
OBO seam to two endpoints it doesn't yet cover (`/worklist`, `/decisions`) and
to backend-side role/hospital enforcement, without touching the Fabric-RLS
depth ADR-0057 and issue #560/#510 already own. Related: issue #567 (Sprint 43
epic), issue #569 (superseded by §4 Approach A item 1), issue #560 (Fabric RLS
depth, untouched), `#424` M4/M5, ADR-0007 (Cosmos persistence contract),
`docs/superpowers/ideas/2026-08-02-signin-followups-b2b-guest-and-obo-rls.md`
(Track 2, partially advanced by this design).
