# Sprint 12 — Organisation (Entra demo org in shared SIT+PROD tenant) — Design Spec

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-09 |
| **Author** | Urs Rüegg |
| **Status** | Draft for review |
| **Previous Version** | — (initial) |
| **Roadmap** | [2026-07-09-sprints-11-16-roadmap-design.md](2026-07-09-sprints-11-16-roadmap-design.md) |
| **Anchor idea** | [docs/superpowers/ideas/Swiss-Hospital-Capacity-UX-Design-and-Roles.md](../ideas/Swiss-Hospital-Capacity-UX-Design-and-Roles.md) §4 |
| **Tenant** | `MngEnvMCAP164444.onmicrosoft.com` per [ADR-0012](../../adr/0012-tenant-migration-to-mcap164444.md) |

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Scope](#2-scope)
3. [Architecture](#3-architecture)
4. [RBAC model — shared users, environment scoping in-app](#4-rbac-model--shared-users-environment-scoping-in-app)
5. [Two super roles](#5-two-super-roles)
6. [Persona catalog (21 demo + 2 super)](#6-persona-catalog-21-demo--2-super)
7. [Adoption telemetry contract](#7-adoption-telemetry-contract)
8. [Agent and skill mix](#8-agent-and-skill-mix)
9. [GitHub delegation](#9-github-delegation)
10. [Side-effect posture and approval gates](#10-side-effect-posture-and-approval-gates)
11. [Verification strategy](#11-verification-strategy)
12. [Risks and mitigations](#12-risks-and-mitigations)
13. [Dependencies](#13-dependencies)
14. [Definition of done](#14-definition-of-done)

---

## 1. Goal and desired end state

The migrated tenant `MngEnvMCAP164444.onmicrosoft.com` holds:

- 21 demo personas from the UX design + 2 super-role personas (`super.admin@…`, `demo.guest@…`);
- 15 Entra app roles (13 operational/governance + `HCC.SuperAdmin` + `HCC.GuestReadOnly`);
- 15 Entra security groups (one per app role) with group-based assignment to the app registration;
- role-assignment mappings that flow into the Sprint 13 app's `roles` claim;
- SIT-tenant sign-in verified for both super-role personas against the Sprint 13 app shell;
- adoption telemetry pipeline emitting nightly sign-in / role-usage events into Fabric Bronze.

**Critical operating constraint (user-supplied):** users are **shared** between SIT and PROD in the same tenant. Environment scoping is done in-app via an `env` claim + hospital-context, **not** by cloning identities.

---

## 2. Scope

### 2.1 In-scope MVP

- Bicep + Microsoft Graph provisioning modules under `infra/modules/entra/`.
- 15 app roles + 15 security groups + 23 personas (21 demo + 2 super) in SIT.
- App-role assignment via group-based assignment.
- Adoption telemetry: sign-in logs + role-usage events exported nightly to `Bronze/adoption/*.json`.
- `entra-whatif.yml` CI workflow for planned changes.

### 2.2 Out-of-scope / deferred

- PROD-batch provisioning (deferred to a follow-up PR after SIT verification).
- Cross-tenant B2B invites (Cantonal Viewer B2B is post-sprint).
- Conditional Access beyond baseline (MFA required, blocked legacy auth).
- PIM for super roles (deferred to a hardening sprint).
- Sign-in risk policies (baseline only in MVP).

---

## 3. Architecture

```text
infra/modules/entra/
├─ app-registration.bicep        # ihzhhpf-app registration (single, one URI per env)
├─ app-roles.bicep               # 15 appRoles (13 + 2 super)
├─ security-groups.bicep         # 15 groups, group-based assignment
├─ users.bicep                   # 23 personas (21 demo + 2 super)
├─ assignments.bicep             # persona ↔ group ↔ app-role mappings
├─ adoption-telemetry.bicep      # diagnostic settings → Log Analytics → Fabric shortcut
└─ conditional-access.bicep      # baseline MFA + block legacy auth
```

**Environment scoping (in-app, not in-tenant):**

```text
Same identity ─▶ signs in at app URL (SIT slot or PROD slot)
             ─▶ app reads `env` from slot config
             ─▶ combines `roles` claim × hospital-context × `env`
             ─▶ enforces data scope via Power BI RLS + Fabric row filters
```

---

## 4. RBAC model — shared users, environment scoping in-app

| Dimension | Source | Enforced by |
| --- | --- | --- |
| Role (what you can do) | `roles` claim from app registration | React app + agent MCP scopes |
| Hospital context (what data you see) | User default in Entra extension attribute + in-app switcher | Power BI RLS + Fabric row filters |
| Environment (sit vs prod) | Deployment slot URL + slot config `env` | App routing; **not** Entra |

**Consequence for telemetry.** All sign-in events land in a single Entra audit stream; the `env` tag comes from the slot the user hit, not from the identity. Fabric Bronze uses `env` to split data by environment.

---

## 5. Two super roles

Per the user's brief:

| App role | Purpose | Scope | Notable rules |
| --- | --- | --- | --- |
| `HCC.SuperAdmin` | Full read/write across all roles, hospitals, environments | Everything | Only 1–2 assignees; not used for daily ops; PIM in hardening sprint |
| `HCC.GuestReadOnly` | Read-only across all roles for demo tours | Read-only Main + Backstage | Cannot invoke agents; cannot switch context in ways that would mutate state; cannot open the CSA wizard |

Both super roles bypass hospital-context filtering (they see aggregated) but honour synthetic-vs-PHI classification (they see synthetic in SIT, may see PHI in PROD only with a distinct grant separately audited).

---

## 6. Persona catalog (21 demo + 2 super)

Domain suffix is pinned to `@…mcap164444.onmicrosoft.com`; UPNs use `firstname.lastname` per the UX design table. Names are demo personas, not real people.

| # | Display name | UPN (local) | App role | Hospital context |
| --- | --- | --- | --- | --- |
| 1 | Dr. Andrea Keller | andrea.keller | HCC.OperationsLead | USZ |
| 2 | Markus Frei | markus.frei | HCC.BedManager | USZ |
| 3 | Sandra Huber | sandra.huber | HCC.FlowManager | USZ |
| 4 | Dr. Thomas Brunner | thomas.brunner | HCC.EDLead | USZ |
| 5 | Nicole Baumann | nicole.baumann | HCC.ORCoordinator | USZ |
| 6 | Peter Schmid | peter.schmid | HCC.StaffingCoordinator | USZ |
| 7 | Claudia Steiner | claudia.steiner | HCC.DischargeCoordinator | USZ |
| 8 | Dr. Michael Weber | michael.weber | HCC.CrisisManager | USZ |
| 9 | Dr. Regula Bucher | regula.bucher | HCC.OperationsLead | LUKS |
| 10 | Stefan Zünd | stefan.zuend | HCC.BedManager | LUKS |
| 11 | Martina Achermann | martina.achermann | HCC.DischargeCoordinator | LUKS |
| 12 | Daniel Kaufmann | daniel.kaufmann | HCC.ORCoordinator | LUKS |
| 13 | Barbara Widmer | barbara.widmer | HCC.OperationsLead | Zollikerberg |
| 14 | Lukas Frei | lukas.frei | HCC.FlowManager | Zollikerberg |
| 15 | Dr. Christoph Vogt | christoph.vogt | HCC.Executive | Aggregated |
| 16 | Dr. Isabelle Girard | isabelle.girard | HCC.CantonalViewer | Aggregated |
| 17 | Urs Rüegg | urs.ruegg | HCC.PlatformAdmin | All |
| 18 | Elena Fischer | elena.fischer | HCC.OntologySteward | All |
| 19 | Rafael Moser | rafael.moser | HCC.AIGovernance | All |
| 20 | Sophie Meier | sophie.meier | HCC.DemoOperator | All |
| 21 | Hans Meier | hans.meier | HCC.Auditor | All |
| 22 | Super Admin (demo) | super.admin | **HCC.SuperAdmin** | All |
| 23 | Demo Guest (read-only) | demo.guest | **HCC.GuestReadOnly** | All (aggregated view only) |

---

## 7. Adoption telemetry contract

Feeds the Sprint 15 BVA dashboard.

```text
Entra sign-in logs ──(diagnostic setting)──▶ Log Analytics workspace
                                             │
                              Nightly export via Fabric Data Pipeline
                                             │
                                             ▼
                                Bronze/adoption/YYYY-MM-DD/*.json
                                             │
                              Silver typing (deduplication, role join, env tag)
                                             │
                                             ▼
                                Gold: Fact_ValueRealization (row per sign-in × role × hospital × env)
```

**Contract fields (Bronze row):** `userId`, `upn`, `appDisplayName`, `appId`, `signInTimestamp`, `env` (derived from app URL host), `resultType`, `ipAddress` (redacted to /24), `clientAppUsed`, `deviceDetail.trustType`, `location.countryOrRegion`.

**No PHI**. Sign-in logs contain UPN and IP only — both are non-PHI operational metadata.

---

## 8. Agent and skill mix

| Component | Superpowers skills | Domain skills |
| --- | --- | --- |
| Entra IaC modules | `writing-plans`, `test-driven-development`, `verification-before-completion` | Bicep best-practice, Microsoft Graph patterns |
| Adoption telemetry pipeline | Same + `subagent-driven-development` | `spark-authoring`, `e2e-medallion-architecture` |
| Sprint 11 `onboarding-agent` (stretch integration) | Same | (none) |

---

## 9. GitHub delegation

| Asset | Path | Trigger |
| --- | --- | --- |
| Issue template | `.github/ISSUE_TEMPLATE/entra-provisioning.yml` | Per persona/role/group work |
| Workflow — Entra what-if | `.github/workflows/entra-whatif.yml` | On PR to `infra/modules/entra/**` |
| Workflow — adoption refresh | `.github/workflows/adoption-refresh.yml` | Nightly export of sign-in logs to Fabric |
| MCP additions | `.github/copilot/mcp.json` | `entra-mcp` read-only entry |
| CODEOWNERS | `.github/CODEOWNERS` | `infra/modules/entra/**` → @urruegg |
| Labels | `sprint-12`, `entra`, `sit-batch`, `prod-batch`, `delete-confirmed` | Applied by templates and gates |

---

## 10. Side-effect posture and approval gates

| Action | Ceiling | Gate |
| --- | --- | --- |
| App registration create/update | `deploy` | `approved-to-apply` |
| User create in SIT | `deploy` | `approved-to-apply` (batched — one PR = one batch) |
| User create in PROD | `deploy` | `approved-to-apply` + explicit `prod-batch` label |
| Group creation and assignment | `deploy` | Rolled into the parent user PR |
| Diagnostic setting → Log Analytics | `deploy` | `approved-to-apply` |
| Fabric pipeline (adoption refresh) | `deploy` | `approved-to-apply` |
| Deletion of any principal | `delete` | Blocked unless explicit `approved-to-apply` + `delete-confirmed` label |

---

## 11. Verification strategy

- **`entra-whatif.yml`** shows planned adds/removes on every PR; diffs tenant vs. Bicep and fails if drift is detected.
- **End-to-end sign-in smoke** — `super.admin` and `demo.guest` can sign in against the Sprint 13 app shell (dry app; just auth callback).
- **Adoption pipeline smoke** — emits at least one nightly file within 24h of merge.
- **Env-scoping test** — same identity signs in to SIT and PROD slots; Fabric Bronze records the correct `env` tag both times.
- **RLS pre-check** — no identity has Power BI workspace admin except `super.admin`; `demo.guest` cannot edit reports.

---

## 12. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Shared SIT+PROD users leak demo test-clicks into "prod" telemetry | `env` claim segregates in Fabric; separate Bronze paths per environment |
| Graph write permission is broad (`Directory.ReadWrite.All`) | Time-boxed CI-only workload identity; user-triggered during batches only |
| Persona list drift (UX doc vs. tenant) | `entra-whatif.yml` diffs tenant vs. Bicep and fails on drift |
| Real people accidentally created | UPN domain pinned to `@…mcap164444.onmicrosoft.com`; refuse if UPN uses a real domain |
| `HCC.SuperAdmin` misuse | Only 1–2 assignees; PIM planned in hardening sprint; sign-in with the role logged separately |
| `HCC.GuestReadOnly` accidentally granted mutate paths | RBAC matrix explicitly excludes edit; automated test that Guest cannot POST/PUT/DELETE against app APIs |

---

## 13. Dependencies

**In**: ADR-0012 (tenant migration), Sprint 11 (agents exist so their MCP scopes can be role-mapped).

**Out**: Sprint 13 (app consumes `roles` + `hospital` claims), Sprint 15 (adoption telemetry feeds BVA), Sprint 11 stretch `onboarding-agent`.

---

## 14. Definition of done

- [ ] `infra/modules/entra/` modules committed and `az bicep build` green.
- [ ] `entra-whatif.yml` shows clean diff after last apply.
- [ ] 15 app roles + 15 groups + 23 personas provisioned in SIT.
- [ ] `super.admin` and `demo.guest` sign-in verified against the Sprint 13 app shell (or a dry auth callback if S13 not ready).
- [ ] Adoption telemetry pipeline emitting nightly files within 24h of merge.
- [ ] `env`-scoping smoke test green (same identity, two slots, two Bronze paths).
- [ ] PROD provisioning deferred to a follow-up PR explicitly labelled `prod-batch`.
- [ ] Sprint 12 retro entry in [docs/sprints/superpowers-checkpoint-matrix.md](../../sprints/superpowers-checkpoint-matrix.md).
