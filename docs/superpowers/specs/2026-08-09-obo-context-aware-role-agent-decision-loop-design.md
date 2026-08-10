---
Version: 1.3.0
Date: 2026-08-10
Author: Copilot coding agent (autopilot, delegated)
Status: Draft
Previous Version: 1.2.0 (wired ooa+bmca via Sprint 26 WS-B catalog, deferred PO agent to issue #570; this bump corrects §1.3 -- role-assignment, not role-definition, genuinely requires a directory role admin@ does not hold, found live during Task 8 execution and blocking Task 9)
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

### 1.3 The tenant limitation, reconfirmed for this new surface — CORRECTED 2026-08-10

The same finding validated for Fabric OneLake access (2026-08-09, see the
sibling design doc) applies to **defining** App Roles: **owner-only,
self-service, no Fabric/Power BI/Global Administrator needed.** Confirmed
live: `az ad app update --app-roles ...` succeeded against `hcc-agent-host`
using only `admin@`'s Global Reader access — all 17 roles landed.

**Correction, found live during Task 8 execution (2026-08-10): assigning a
role to a principal is a *different* operation with a *different*
requirement.** `POST /servicePrincipals/{id}/appRoleAssignedTo` — confirmed
via [Microsoft's own docs](https://learn.microsoft.com/en-us/graph/api/serviceprincipal-post-approleassignedto)
and a real, reproducible `403 Authorization_RequestDenied` — requires the
signed-in user to hold one of: Directory Synchronization Accounts, Directory
Writer, Hybrid Identity Administrator, Identity Governance Administrator,
Privileged Role Administrator (least-privileged supported), User
Administrator, Application Administrator, or Cloud Application Administrator.
**There is no "owner of the resource" exception for this specific write** —
unlike defining the app's own `appRoles` property. This holds regardless of
whether the assigned principal is a user or a security group (same
API, same required-roles list).

`admin@`'s actual directory role membership (`GET /me/memberOf`) is
confirmed to be **Global Reader only** — no qualifying role. Also discovered:
`ihzhhpf-app`'s existing 17 "role assignments" are mostly **security-group**
assignments (one `HCC.*` group per role; `admin@` is a *member*, inheriting
the role via group membership) — meaning that original bootstrap was done by
some identity that *did* hold a qualifying directory role at the time (most
likely the sealed break-glass Global Administrator, used once), not
routine self-service by the current `admin@` identity as this design
originally assumed.

- `admin@` is the sole **owner** of both `hcc-agent-host` and (implicitly,
  having registered it) `ihzhhpf-app` — sufficient for defining App Roles,
  **not** sufficient for assigning them to a principal.
- `hcc-agent-host`'s service principal has `appRoleAssignmentRequired: false`
  (any org member can sign in) — orthogonal to explicit role assignment,
  which is what actually populates the `roles` claim.
- No new consent screen is triggered by adding app roles — that part of the
  claim holds. Assigning a principal to a role is a directory-role-gated
  write, not a consent-gated one, so this point doesn't change the outcome
  either way.

**Practical consequence:** Task 8 Step 5 (assign `admin@` to `hcc-agent-host`'s
new roles) is **blocked** pending one of: (a) temporary elevation of `admin@`
(or another available identity) to a qualifying directory role for one write,
then revert; (b) the sealed break-glass Global Administrator, used once; (c)
finding another already-privileged identity in the tenant. Task 9 (flipping
`agentHostOboEnabled=true`) must **not** proceed until this is resolved —
without any role assignment, every signed-in user's OBO token would carry an
empty `roles` claim, and Task 2's `_require_active_role_held` check would
403 every non-empty `X-Active-Role` request, breaking the live demo the
moment OBO is enabled (a foreseeable, avoidable repeat of the earlier
shared-flag incident, this time caught before deployment).

## 2. Goals

- Make the **admin account's real, already-assigned Entra roles** (not a
  client-side simulated switcher) drive which board and which role-agent
  recommendation the demo shows — "context sensitive" end to end, including
  on the **backend**, not just the frontend badge.
- Let a demo user ask **`dca`, `ooa`, and `bmca`** for their actionable
  recommendation (three roles, not one), see the golden-sourced citations
  behind it, and **Accept** or **Deny** it:
  - `dca` (existing) and the two newly-wired roles reuse the **already-built**
    Sprint 26 WS-B formula registry (`compute_expected_impact`) — real,
    deterministic, gold-grounded predicted-impact math, not invented numbers.
  - `ooa`'s lever (`OOA-EXPEDITE-DISCHARGE`) grounds on the existing
    `patients_in_stage(DISCHARGE_READY)` observation — zero new `SimState`
    logic.
  - `bmca`'s lever (`BMCA-REBALANCE-CENSUS`) grounds on the ward's own
    occupancy-vs-90%-target gap (mirrors the existing `target_pct=90`
    convention already used by `plan_runtime.open_plan`); its `to_ward` param
    is a fixed, documented single-ward-MVP assumption (mirrors `dca`'s own
    fixed `_BARRIER_TYPE = "transport"` constant).
  - Only `dca` has a real `effect:` mapping (actual `SimState` mutation on
    Accept). `ooa`/`bmca` Accept/Deny is still a **real, tracked** decision on
    a **real, grounded** number — honestly recorded as `applied: false`
    ("actuation not yet modeled for this lever"), never a fabricated mutation.
  - `orsa`/`sba` stay on today's honest "role effect pending" placeholder —
    deferred pending real domain modeling (see §3 Non-goals).
- Make that Accept/Deny decision produce a **durably persisted**, identity-
  verified audit record — not just a well-shaped in-memory response. This
  reuses the same live Cosmos wiring (Task 5) that also durably persists
  **every other agent-memory write** this app already makes (`conversations`,
  `agent_interactions`, `audit`) — see §4 item 6's expanded framing.
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
- **`ooa`/`orsa`/`sba`'s real actuation** — **correction found on further investigation:** the PREDICTED-IMPACT math for all 5 roles already exists (Sprint 26 WS-B) — `data-platform/decision/levers/{ooa,bmca,orsa,sba,csa}.yaml` each declare a real `impact_formula_ref` resolved by `data-platform/decision/impact/compute_expected_impact.py`'s formula registry (`expedite_discharge_beds`, `rebalance_census_beds`, `defer_elective_slots`, `flex_staff_beds`, `activate_surge_beds`). The gap is narrower than first thought: `loop/worklist.py`/`loop/decisions.py` never wire into this registry for anything but `dca`, and **only `dca.yaml` declares an `effect:` block** (the SimState actuation mapping) — the other four have no state-mutation defined at all. `ooa` and `bmca` are groundable now using only existing `SimState` fields (see §2 Goals); `orsa` (`ORSA-DEFER-ELECTIVE`, needs an OR-case concept) and `sba` (`SBA-FLEX-STAFF-BEDS`, needs a shift/staffing concept) have no matching `SimState` domain object at all and remain deferred pending real domain modeling — not a wiring gap, a genuine data-model gap.
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
   `ihzhhpf-app` onto `hcc-agent-host`.** Defining the roles is owner-level,
   self-service (confirmed live). **Assigning `admin@` to them is not** — see
   §1.3's correction; this step needs a qualifying directory role, gated by
   `approved-to-apply` per AGENTS.md §4 regardless. This makes the **access
   token** used for the OBO bearer (audience = `hcc-agent-host`) carry the
   same `roles` claim the **ID token** already carries, so server-side code
   can see it.
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
6. **Implement a live `CosmosPersistence`** — this is deliberately framed as
   **Cosmos DB as Agent Memory**, not narrowly as "decisions audit trail":
   `Orchestrator` uses **one** `persistence` instance for every write it
   makes (`conversations`, `agent_interactions` — i.e. real chat/turn history
   already flows through it today, just to the in-memory stand-in), so wiring
   a single live client makes **all four containers** durable at once,
   matching this repo's own Cosmos DB guidance (chat history, user context,
   multi-user isolation — see the always-applied `azurecosmosdb.instructions.md`).
   `/agents/{name}/decisions` additionally writes its outcome into
   `approval-events` (the tracked audit trail specifically). **Re-verified
   live during this brainstorm: the infra for this already exists and is
   already deployed** — `infra/modules/agent-host/cosmos.bicep` provisions a
   **dedicated** `cosmos-ihzhhpf-sit` account (confirmed live via `az
   cosmosdb list`), its `agenthost` database already has all four containers
   including `approval-events` (confirmed live via `az cosmosdb sql container
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

- **BLOCKED (found live, 2026-08-10): role assignment needs a directory role
  `admin@` doesn't have.** Defining `hcc-agent-host`'s 17 App Roles
  succeeded (owner-level, self-service, confirmed live). Assigning `admin@`
  to any of them (`POST .../appRoleAssignedTo`) returns a real, reproducible
  `403 Authorization_RequestDenied` — this Graph API requires the caller to
  hold Application Administrator, Cloud Application Administrator, User
  Administrator, Privileged Role Administrator, Identity Governance
  Administrator, Hybrid Identity Administrator, Directory Writer, or
  Directory Synchronization Accounts (per
  [Microsoft's docs](https://learn.microsoft.com/en-us/graph/api/serviceprincipal-post-approleassignedto)),
  none of which `admin@` holds (`GET /me/memberOf` confirms Global Reader
  only). See §1.3's correction. **Task 9 (`agentHostOboEnabled=true`) must
  not proceed until this is resolved** — flipping it with zero role
  assignments in place would make every signed-in user's OBO token carry an
  empty `roles` claim, and the Task 2 `_require_active_role_held` check
  would then 403 any non-empty `X-Active-Role` request, breaking the demo
  the moment OBO is enabled.
- **Role-mirroring is a new IAM surface** — even though role *definition* is
  owner-level and self-service, AGENTS.md §4 requires its own
  `approved-to-apply` comment before any Entra write, and role *assignment*
  additionally needs the elevated-access resolution above.
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
2. Server-side role/hospital validation in `golden()`/`chat()`, gated on OBO
   presence; unit tests for both the matching and mismatched cases.
3. Extend `/worklist` and `/decisions` to accept a bearer; derive
   `caller_oid`/`approver` from `obo.user_oid` when present; unit tests.
4. Extend `/agents/{name}/tools/{tool}` (CSA's HITL gate endpoint) with the
   same OBO-derived approver identity as item 3 — closes the "no identity at
   all" gap on CSA's `enforce_gates()` path (see §8.1).
5. Live grounding citation in `build_worklist` (optional `fabric` param);
   unit tests with a fake `FabricAdapter`.
6. Wire `ooa` (`OOA-EXPEDITE-DISCHARGE`) and `bmca` (`BMCA-REBALANCE-CENSUS`)
   into the **already-built** Sprint 26 WS-B formula registry
   (`compute_expected_impact`) via a small shared role -> lever registry;
   `decide()`'s Accept path for these two roles is a real, tracked decision on
   a real number, honestly recorded as `applied: false` (no `effect:` mapping
   exists yet for either lever). `orsa`/`sba` remain on today's placeholder —
   genuine domain-model gaps (no OR-case/staffing concept in `SimState`), not
   a wiring gap.
7. Implement `LiveCosmosPersistence` (config-gated on `COSMOS_ENDPOINT`,
   already deployed and injected — no new Bicep) and wire `/decisions` to
   write outcomes to `approval-events`; unit tests with the existing
   in-memory fake plus a new "live-when-configured" test mirroring
   `_build_chat_model`'s pattern. This one client now durably persists **all**
   agent memory (`conversations`, `agent_interactions`, `audit`,
   `approval-events`), not just decisions.
8. Entra: mirror App Roles + `admin@`'s assignments onto `hcc-agent-host`
   (`approved-to-apply` gate).
9. Flip `agentHostOboEnabled=true` in `sit.bicepparam` (the only remaining
   Bicep change).
10. Live verification: sign in as `admin@`, narrow to `HCC.DischargeCoordinator`,
    `HCC.BedManager`, and a role that maps to `ooa`, confirm each worklist
    shows a real corroborating citation, Accept a recommendation on all three,
    confirm every outcome is queryable from Cosmos with the verified oid as
    approver. Confirm Demo mode (no sign-in) is unaffected throughout.
11. Update issue #567 with the live evidence; close #569 in favour of this
    design's item (1).

## 8. Aligning `csa-agent` and `product-owner-agent` into this pattern

Both agents were reviewed for whether they can join the same OBO + real-role +
golden-sources pattern. They are in very different positions:

### 8.1 `csa-agent` — architecturally close, one gap

`agents/csa-agent/manifest.yaml` declares `runtime: agent-host` — **the same
`hcc-agent-host` FastAPI app** the 5 role agents run on. Concretely:

- Its `/agents/csa-agent/chat` calls go through the **same** `chat()` handler
  Task 1-3 fix — the bearer-presence fix and server-side role validation
  apply to it automatically, no extra work.
- Its `fabric:gold-capacity` grounding source can use the **same**
  `state.fabric_for(obo_token)` per-request adapter Task 4 builds, if CSA's
  own tool-invocation code path calls into the same `HostState.fabric`/
  `fabric_for` seam (not yet verified in this brainstorm — a quick follow-up
  check, not a redesign).
- The one real gap: CSA's HITL model is **different** from the role-agents'
  `/decisions` accept/deny — it uses `hitl/gate_enforcer.py`'s
  `enforce_gates()` via `/agents/{name}/tools/{tool}` (HITL-01 gates the
  Fabric simulation-run trigger, HITL-04 gates the recommendation draft PR).
  That endpoint's `ToolRequest` carries only `params`/`hitlEvidence` today —
  **no identity at all**, verified or otherwise. Aligning CSA into "a tracked,
  identity-verified audit trail" needs the same treatment Task 3 gives
  `/worklist`/`/decisions`: read the `authorization` header, build an OBO
  context, and record the verified `obo.user_oid` as the gate-approval
  identity (currently `enforce_gates` has no approver field to attach it to
  — a small, additive schema change, same shape as `loop/decisions.py`'s
  `approver` field).
- Its own dedicated `cosmos-csa-ihzhhpf-sit` account is unaffected by this
  design's Task 5 (which targets the separate `cosmos-ihzhhpf-sit` account) —
  no conflict, just a note that CSA's audit records would land in a
  *different* account than the role-agents' `approval-events`, which may or
  may not be the intended long-term shape (worth a follow-up decision, not
  blocking).

**Recommendation:** a small additional task — extend `/agents/{name}/tools/{tool}`
with the same OBO-derived approver pattern as Task 3 — is in reach of this
same plan. Verifying CSA's Fabric-grounding call path is a quick follow-up
check.

### 8.2 `product-owner-agent` — deferred to its own follow-up sprint (user decision, 2026-08-09)

`agents/product-owner-agent/manifest.yaml` declares
`runtime: copilot-coding-agent` for its control-plane identity (the
`@product-owner-agent`-mentioned GitHub issue responder) — **not**
`hcc-agent-host`. Its "in-app Copilot rail" (the actual user-facing surface
this design would otherwise care about) is a **wholly separate, dedicated
Container App**: `infra/modules/experience-hosting/po-agent-runtime/main.bicep`
provisions its own Container App (`ca-po-*`), its own Cosmos account
(`cosmos-po-*`, confirmed live via `az cosmosdb list`), its own Azure OpenAI
deployment, and its own Key Vault — a completely different codebase from
`hcc-agent-host` (the real image is built by a separate
`po-agent-runtime-build.yml`, not located or inspected in this brainstorm).

**Decision:** the user explicitly asked to leave this aside and track it as
its own follow-up sprint rather than fold it into this plan or investigate
its source now — a different codebase/hosting model than everything else in
this design, so it deserves its own scoped brainstorm rather than a rushed
assessment here. Tracked as issue #570 (filed alongside this revision); no
further PO-agent work is in scope for this plan.

## 9. Traceability

Extends [ADR-0057](../../adr/0057-obo-seam-completion-defer-live-provisioning.md)'s
OBO seam to two endpoints it doesn't yet cover (`/worklist`, `/decisions`) and
to backend-side role/hospital enforcement, without touching the Fabric-RLS
depth ADR-0057 and issue #560/#510 already own. Related: issue #567 (Sprint 43
epic), issue #569 (superseded by §4 Approach A item 1), issue #560 (Fabric RLS
depth, untouched), issue #570 (product-owner-agent runtime alignment,
deferred follow-up sprint per §8.2), `#424` M4/M5, ADR-0007 (Cosmos
persistence contract),
`docs/superpowers/ideas/2026-08-02-signin-followups-b2b-guest-and-obo-rls.md`
(Track 2, partially advanced by this design).
