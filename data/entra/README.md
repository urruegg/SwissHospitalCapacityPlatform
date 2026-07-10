# Entra demo-org master data (CSV artefacts)

| Field | Value |
| ------- | ------- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-10 |
| **Author** | GitHub Copilot |
| **Status** | Draft for review |
| **Previous Version** | — (initial) |

Portable, tenant-agnostic **master data** for the Swiss Hospital Capacity
Platform Entra demo organisation: organisations (hospital contexts), app roles,
security groups, and users (personas). These CSVs are the human-reviewable
source an IaC script can replay to (re)create the orgs, users, and security
roles in Microsoft Entra — including a future **tenant migration**.

They complement (and are reconciled against) the deploy source of truth, the
Microsoft Graph Bicep modules under
[`infra/modules/entra/`](../../infra/modules/entra/README.md) and their
parameter files `parameters/{sit,prod}.bicepparam`.

> **Why CSV master data as well as Bicep?** The Bicep `bicepparam` files embed
> the current tenant's UPN domain (`@mngenvmcap164444.onmicrosoft.com`) inline.
> These CSVs deliberately store only the **local** UPN part (`upn_local`) and
> tenant-agnostic attributes, so a migration to a new tenant is a domain swap at
> generation time rather than a hand-edit of every identity. This closes the
> S12.10 DoD gap identified by the
> [2026-07-10 sprint review](../../docs/sprints/2026-07-10-sprints-11-16-review-checklist.md)
> and is the prerequisite the issue asked for before any SIT→PROD promotion.

## Files

| File | Rows | Purpose |
| ---- | ---- | ------- |
| [`organizations.csv`](organizations.csv) | 5 | Hospital contexts (`USZ`, `LUKS`, `Zollikerberg`) plus the two logical scopes (`Aggregated`, `All`). Columns: `org_key`, `display_name`, `org_type`, `canton`, `scope`. |
| [`app-roles.csv`](app-roles.csv) | 17 | Full app-role catalog: 2 super (`HCC.SuperAdmin`, `HCC.GuestReadOnly`) + 15 operational/governance. Columns: `role_value`, `display_name`, `category`, `description`. Mirrors [`app-roles.bicep`](../../infra/modules/entra/app-roles.bicep). |
| [`security-groups.csv`](security-groups.csv) | 17 | One security group per app role. Columns: `group_name`, `mail_nickname`, `backing_role`, `env_scope`, `description`. Mirrors [`security-groups.bicep`](../../infra/modules/entra/security-groups.bicep). |
| [`users.csv`](users.csv) | 23 | 21 demo personas + 2 super. Columns: `upn_local`, `display_name`, `app_role`, `default_hospital`, `usage_location`. Full UPN = `{upn_local}@{tenant-domain}`; `mailNickname` == `upn_local`. |

## Conventions

- **Group naming.** Per design decision D-6 (shared users across SIT and PROD in
  the same tenant), there is **one** security group per role, named after the
  role value (`env_scope = shared`); environment scoping is done in-app via the
  `env` claim, not by cloning identities or groups. `mail_nickname` is the role
  value with `.` replaced by `-` (matches `security-groups.bicep`).
- **Passwords are never stored here.** As with the Bicep modules, a temporary
  password is supplied securely at apply time and users reset it on first
  sign-in. No CSV column carries a credential.
- **Domain is a migration parameter.** `users.csv` stores `upn_local` only. The
  active tenant domain lives in the Bicep `allowedUpnDomain` guard
  ([`users.bicep`](../../infra/modules/entra/users.bicep)); on migration, update
  that guard and regenerate the deploy parameters — the CSV rows carry over
  unchanged.

## Validation gate

[`validate_entra_master_data.py`](validate_entra_master_data.py) is a
dependency-free (Python 3 standard library only) gate that checks internal
consistency and reconciles the CSVs against the persona seed
(`data/synthetic/personas.csv`) and both `bicepparam` files:

```bash
# From the repository root
python3 data/entra/validate_entra_master_data.py
python3 -m unittest discover -s data/entra/tests -v
```

The gate fails if, for example, a user references an unknown role or hospital, a
role has no backing group, the user/role/group counts drift, or the CSV set
diverges from the persona seed or the Bicep parameter files. It runs in CI via
[`.github/workflows/entra-master-data.yml`](../../.github/workflows/entra-master-data.yml).

## Using the master data in an IaC migration

An IaC script (Bicep parameter generator, Graph PowerShell, or Terraform)
consumes these CSVs as follows:

1. Read `app-roles.csv` → application `appRoles` catalog.
2. Read `security-groups.csv` → one security group per role.
3. Read `users.csv` → one user per row, UPN = `{upn_local}@{target-tenant-domain}`,
   `mailNickname = upn_local`, `usageLocation` from the row.
4. Assign each user to the group whose `backing_role` == the user's `app_role`.
5. Use `organizations.csv` to seed the in-app hospital-context switcher and the
   Power BI RLS / Fabric row filters keyed by `default_hospital`.

> **Deploy gate reminder.** Creating these objects in Entra is a `deploy`-ceiling
> action per [AGENTS.md §4](../../AGENTS.md#4-confirmation-rule-for-deploy--delete):
> post the `az deployment sub what-if` output, wait for an `approved-to-apply`
> reply, then apply. Generating and validating these CSVs is a `write`-ceiling
> action and needs no such gate.
