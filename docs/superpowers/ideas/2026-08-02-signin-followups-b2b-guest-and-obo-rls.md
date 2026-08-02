# Sign-in follow-ups: B2B guest onboarding + per-user OBO/RLS

| Field | Value |
| ------- | ------- |
| **Version** | 1.0.1 |
| **Date** | 2026-08-02 |
| **Author** | Urs Rueegg |
| **Status** | Idea (deferred) |
| **Previous Version** | 1.0.0 (initial deferred-ideas capture) |

> Captured while brainstorming **Sprint A** (member sign-in + role-lens E2E, see
> the Sprint A design spec). These two tracks are explicitly **out of Sprint A**
> and each gets its own spec -> plan -> implementation cycle in a later sprint.

## Context

Sprint A wires real MSAL sign-in for **tenant member** accounts (e.g.
`admin@mngenvmcap164444.onmicrosoft.com`) so the Curavias app adapts to the
signed-in user's `HCC.*` role assignment and runs the operational loop under
their identity, against the agent-host's current (simulated-provenance) golden
data. Two capabilities were deliberately deferred:

## Track 1 - Sprint B: B2B guest onboarding (from another Entra tenant)

**Goal:** onboard an **external guest** (Entra B2B collaboration) from a different
tenant into `MngEnvMCAP164444`, assign them `HCC.*` app roles, and demo the
Curavias app end-to-end as that guest.

**Feasibility (checked 2026-08-02):** the tenant allows it -
`authorizationPolicy.allowInvitesFrom = adminsAndGuestInviters` (admins/guest
inviters may invite) and `crossTenantAccessPolicy/default` inbound B2B is
`allowed` (service default). Invited guests receive the **Restricted Guest**
role (`guestUserRoleId = 2af84b1e-...`) - limited directory access, but they can
authenticate and receive app roles.

**Sketch:**

1. Invite an external guest (Graph `POST /invitations`, or portal) - needs an
   admin / Guest Inviter.
2. Assign the guest an `HCC.*` app role on the `ihzhhpf-app` enterprise app
   (`appRoleAssignment`).
3. Confirm the single-tenant `ihzhhpf-app` registration issues the `roles` (and
   optional `hospital`/`env`) claims to guests.
4. Verify Conditional Access does not block/over-gate the guest sign-in (MFA is
   fine; a block policy is not).
5. Demo: guest signs in -> role lens adapts -> operational loop under the guest
   identity.

**Open questions:** which external tenant/email to invite; whether guests should
get `hospital`/`env` scoping claims; CA policy review for guests.

## Track 2 - Full per-user OBO/RLS on real golden rows (depth "Option B")

**Goal:** move beyond Sprint A's simulated-provenance golden data to **real
per-user row-level security**: the app acquires an agent-host API token, and the
agent-host performs the **on-behalf-of** exchange to Fabric so each user only
sees the golden rows their role + hospital scope permit.

**Why deferred:** this is the `#424 M5 OBO` work - it needs the agent-host OBO
seam turned on (`AGENT_HOST_SCOPE`), a dynamic-RLS TMDL predicate on the semantic
model, and the Fabric Data Agent RLS provider (Rung 1) wired for per-user scope.
Materially larger than Sprint A and independent of sign-in itself.

**What it unlocks:** true data isolation per user/hospital (not just a UI role
lens), honest `live` provenance on scoped reads, and the production-grade
Zero-Trust data path.

**Sketch:**

1. Expose an agent-host API scope on `ihzhhpf-app`; app acquires it via MSAL.
2. Turn on the agent-host OBO seam; validate the bearer + exchange on-behalf-of.
3. Author the dynamic-RLS TMDL predicate (userprincipalname / role -> hospital).
4. Switch the golden read to the Fabric Data Agent RLS provider (Rung 1).
5. Verify per-user scoping end-to-end; provenance flips to `live`.

### Known limitation carried from Sprint A

The Sprint A role-lens runtime `APP_HOME_HOSPITAL` / `APP_ENV` is an **override**,
not a claim-presence-aware fallback: `apps/hcc-app-fluent/src/auth/claim-parser.ts`
coerces a **missing** claim to a default sentinel (`env -> 'dev'`,
`hospital -> 'aggregated'`), so "omitted" is indistinguishable from "explicitly
default" downstream. For single-site SIT (USZ emits no custom `env`/`hospital`
claim) this is correct. For multi-hospital **per-user** scoping the OBO/RLS work
must:

1. make `claim-parser` distinguish "claim present" from "defaulted" (e.g. an
   optional `hospital?: Hospital`), and
2. let a **present** token claim win over the slot default, so a slot-injected
   `APP_HOME_HOSPITAL=usz` no longer silently mis-scopes e.g. a LUKS member to
   USZ.

Refs: `apps/hcc-app-fluent/src/context/role-context.tsx`,
`apps/hcc-app-fluent/src/auth/claim-parser.ts`.

## Relationship

Track 1 (who can sign in) and Track 2 (what data they see) are **independent**.
Sprint A delivers sign-in + role-lens + identity on current data; Track 1 adds
external guests; Track 2 adds real per-user data isolation. They can be
sequenced in either order after Sprint A.
