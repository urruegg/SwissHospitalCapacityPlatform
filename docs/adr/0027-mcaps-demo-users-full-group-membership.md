# ADR-0027 — MCAPS demo-user model: `admin@` + `urruegg@` hold all 17 HCC.\* group memberships

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-07-13 |
| **Deciders** | @urruegg |
| **Superseded by** | — |

> Sprint 12 close-out ADR. Records why the platform ships to SIT with **two demo
> accounts** covering all 17 app roles instead of the 23 persona users originally
> called out in the Sprint 12 T4 plan. Referenced by
> [`infra/modules/entra/main.bicep`](../../infra/modules/entra/main.bicep),
> [`infra/modules/entra/users.bicep`](../../infra/modules/entra/users.bicep),
> [`infra/modules/entra/parameters/sit.bicepparam`](../../infra/modules/entra/parameters/sit.bicepparam),
> [`infra/modules/entra/parameters/sit-groups-only.bicepparam`](../../infra/modules/entra/parameters/sit-groups-only.bicepparam)
> (new), the Sprint 12 design spec, and the
> [Sprints 11-16 review checklist](../sprints/2026-07-10-sprints-11-16-review-checklist.md).

## Context

Sprint 12 T4 was authored assuming the [Microsoft Graph Bicep extension](https://learn.microsoft.com/graph/templates/bicep/overview-bicep-templates-for-graph)
would let us provision 23 persona users declaratively via
`Microsoft.Graph/users@v1.0`. On 2026-07-13, the Sprint 12 apply against tenant
`1337187a-4c41-4da9-8fca-731bba7a4329` failed for exactly those 23 users with
`BadRequest: Resource 'users' is readonly`.

Root cause (confirmed by
[Microsoft Learn](https://learn.microsoft.com/graph/templates/bicep/reference/users?view=graph-bicep-1.0#property-values)
and the
[January 2025 what's-new note](https://learn.microsoft.com/graph/templates/bicep/whats-new)):
the `users` Bicep type is intentionally **read-only** at both `v1.0` and `beta`.
It exists only to reference users via the `existing` keyword — never to create
them. Upgrading the extension from `0.2.0-preview` to the `1.0.0` GA release
does **not** change this. User creation is only possible via the Microsoft
Graph REST API (`POST /v1.0/users`) or `az ad user create`.

Two options were considered for closing Sprint 12:

- **Option A** — provision the 23 persona users out-of-band via Microsoft Graph
  REST, then refactor `users.bicep` to `existing` and re-run for
  groups + assignments.
- **Option B** — treat the 23 persona users as symbolic (they exist as a
  catalog in `sit.bicepparam` and `data/entra/users.csv` for future
  provisioning), skip user creation entirely, and give the two accounts we
  actually can use in the MCAPS tenant (`admin@` and `urruegg@`) membership in
  **all 17** `HCC.*` groups so every persona-role is demoable.

## Decision

**Adopt Option B.**

1. `Microsoft.Graph/users` is read-only in the Graph Bicep extension. This is by
   design and will not change.
2. The MCAPS-provided tenant `MngEnvMCAP164444` restricts how many real user
   objects we can/should mint for a demo-scope environment
   ([ADR-0012](0012-tenant-migration-to-mcap164444.md),
   [ADR-0013](0013-temporary-us-region-demo-scope.md)). Creating 23 real users
   through a side-channel just to satisfy a Bicep authoring artefact is not
   worth the tenant footprint or the ongoing password-reset overhead.
3. Both `admin@mngenvmcap164444.onmicrosoft.com` and
   `urruegg@MngEnvMCAP164444.onmicrosoft.com` are added as members of **all 17**
   `HCC.*` security groups. Because assignments are group-based
   (see `infra/modules/entra/assignments.bicep`), each account then carries all
   17 app roles in its JWT `roles` claim and can exercise every persona-role
   during the demo.
4. `infra/modules/entra/parameters/sit-groups-only.bicepparam` is added as the
   apply variant used for SIT: it inherits everything from the main module
   except `personas`, which is set to `[]`. This makes the "no user creation"
   decision an **explicit, version-controlled parameter choice**, not a silent
   deviation.
5. The 23 persona rows in `infra/modules/entra/parameters/sit.bicepparam` and
   `data/entra/users.csv` are **retained** as the catalog of intended personas
   for a future sprint that either refactors `users.bicep` to `existing` and
   pairs it with a Graph-REST provisioning script, or moves to a tenant where
   real users are appropriate.

## Rationale

| # | Criterion | Option A (Graph REST + Bicep refactor) | Option B (two demo accounts, all groups) — **chosen** |
| --- | --- | --- | --- |
| 1 | Effort to close Sprint 12 | Non-trivial: Graph REST provisioning script, `users.bicep` refactor, retest, ADR anyway. | Two commands per user × 17 groups (34 `az ad group member add` calls) already executed 2026-07-13. |
| 2 | Alignment with MCAPS tenant scope | Creates 23 real user objects in a demo tenant that only ever needs two operators. | Uses only the identities that already exist and are legitimately provisioned for platform use. |
| 3 | Alignment with ADR-0012 / ADR-0013 (demo scope) | Diverges — treats the tenant as if it were long-lived. | Reinforces — treats the tenant as demo-only. |
| 4 | Demo capability | Full — 23 personas can each be signed in as. | Full — both demo accounts carry every persona-role in `roles` claim; the app's role-gating logic is fully exercised. |
| 5 | Reversibility | Refactor is a source-of-truth change that would be hard to revert without breaking downstream sprints. | Reversible: delete the two members, restore original `sit.bicepparam` apply once a valid `users` provisioning path exists. |
| 6 | Traceability | Would require the same ADR anyway. | This ADR + `sit-groups-only.bicepparam` + membership evidence in the checklist. |

## Consequences

**Positive:**

- Sprint 12 closes with a **working** identity model — 17 app roles, 17 groups,
  and 17 group-based assignments live in SIT, plus two accounts covering every
  role for demo purposes.
- No dependency on the Graph Bicep extension's user-write capability, which is
  a permanent extension limitation.
- No creation of 23 real user objects in a tenant that does not need them.
- Removes the need to store or rotate a `temporaryPassword` for personas we do
  not intend to sign in as.
- All decisions are captured in version-controlled artefacts
  (`sit-groups-only.bicepparam`, this ADR, the audit checklist), not in tribal
  knowledge.

**Negative:**

- `admin@` and `urruegg@` become "god accounts" during the demo. Every role
  they hold is because they carry every group. This is acceptable **only** for
  the demo scope covered by ADR-0013; it would be inappropriate in PROD or in
  any tenant handling real workloads.
- Persona-level RBAC boundary testing is no longer possible with real
  identities — the app must still ship its role-gating logic, but end-to-end
  verification against 23 distinct users is deferred.
- The `sit.bicepparam` persona catalog is now a **spec artefact**, not a
  deployment target. A reader who trusts `az deployment sub create ...
  sit.bicepparam` end-to-end would still hit the read-only error until the
  `users.bicep` refactor happens.

## Follow-ups

1. **Refactor `users.bicep` in a future sprint** — switch to `existing` +
   accept pre-computed user IDs as inputs. Pair with a Graph-REST provisioning
   script under `scripts/entra/`. Track as a Sprint 12.2 or Sprint 18 backlog
   item.
2. **Document the two-account posture in the Sprint 13 app README** — the app
   shell must not assume that "user has role" implies "role is scoped to
   persona". For demo purposes, every logged-in account has every role.
3. **PROD promotion** ([issue #179](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/179))
   is decoupled from this decision: PROD will always require real per-persona
   users, so option A's refactor is a **prerequisite** for PROD, not for SIT.
4. **`entra-whatif.yml` behaviour** — the workflow already tolerates the
   `ExtensibleResourceNotSupported` diagnostics and does not attempt to apply.
   Update its README/comment header to note that a full apply of `sit.bicepparam`
   will fail for the `users` sub-deployment until Follow-up 1 is done, and that
   `sit-groups-only.bicepparam` is the SIT apply artefact.

## Evidence

- **Failed users deploy (v1)**: `entra-sit-20260713103046`
  (subscription `66a9953a-df37-4c51-856c-9971b9bf3e03`) — `appRoles-sit` ✅,
  `appReg-sit` ✅, `users-sit` ❌ (23× `Resource 'users' is readonly`).
- **Successful groups+assignments deploy**: `entra-sit-groups-20260713104552`
  — `Succeeded`. Idempotent no-ops on `app` and `servicePrincipal`; new
  resources: 17 `groups`, 17 `groupAppRoleAssignments`.
- **Group membership** verified via
  `az ad group member list --group HCC.<role>` for all 17 groups: each has
  exactly `admin@mngenvmcap164444.onmicrosoft.com` and
  `urruegg@MngEnvMCAP164444.onmicrosoft.com`.
- **Reproducer script**:
  [`scripts/entra/assign-demo-users-all-groups.ps1`](../../scripts/entra/assign-demo-users-all-groups.ps1)
  — idempotent; safe to re-run.
