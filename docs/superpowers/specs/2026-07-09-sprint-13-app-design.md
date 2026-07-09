# Sprint 13 — App (Fluent UI primary, Rayfin parallel PoC) — Design Spec

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-09 |
| **Author** | Urs Rüegg |
| **Status** | Draft for review |
| **Previous Version** | — (initial) |
| **Roadmap** | [2026-07-09-sprints-11-16-roadmap-design.md](2026-07-09-sprints-11-16-roadmap-design.md) |
| **Anchor idea** | [docs/superpowers/ideas/Swiss-Hospital-Capacity-UX-Design-and-Roles.md](../ideas/Swiss-Hospital-Capacity-UX-Design-and-Roles.md) |
| **Brandkit** | [docs/brandkit/Helvion-Brand-Guide.md](../../brandkit/Helvion-Brand-Guide.md) |

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Scope — MVP (Fluent) and parallel PoC (Rayfin)](#2-scope--mvp-fluent-and-parallel-poc-rayfin)
3. [Architecture — repo layout and component boundaries](#3-architecture--repo-layout-and-component-boundaries)
4. [Rayfin PoC — comparison rubric and decision ADR](#4-rayfin-poc--comparison-rubric-and-decision-adr)
5. [Agent and skill mix](#5-agent-and-skill-mix)
6. [GitHub delegation](#6-github-delegation)
7. [Side-effect posture and approval gates](#7-side-effect-posture-and-approval-gates)
8. [Verification strategy](#8-verification-strategy)
9. [Risks and mitigations](#9-risks-and-mitigations)
10. [Dependencies](#10-dependencies)
11. [Definition of done](#11-definition-of-done)

---

## 1. Goal and desired end state

Two app codebases exist side-by-side:

- `apps/hcc-app-fluent/` — the **deployable baseline** (React + Fluent UI v9 + Brandkit tokens + MSAL against Sprint 12's app registration + Fabric-embedded reports).
- `apps/hcc-app-rayfin/` — a **time-boxed Rayfin-generated skeleton** for comparison.

Both bind to the same Sprint 12 identity and the same Sprint 11 agents. Sprint 13 exit produces a **decision ADR** picking one stack for Sprint 14+.

The Fluent baseline delivers:

- two-workspace shell (Main + Backstage) per UX design §3;
- top bar with hospital-context selector, role switcher (SIT-gated), search, user Persona;
- app rail with Main / Backstage / Home / Ask-Agent / Settings;
- **one reference operational whiteboard** — BedManager @ USZ (React Flow or tldraw base, 6 card types from UX §5.2);
- **one reference Backstage tab** — Roles & RBAC live view (reads Entra Graph read-only);
- MSAL auth against the S12 app registration with `roles` + `hospital` + `env` claim consumption;
- Fabric semantic model embedding with RLS;
- Copilot Drawer skeleton that invokes one Sprint 11 agent (BMCA) — proves the wiring.

---

## 2. Scope — MVP (Fluent) and parallel PoC (Rayfin)

### 2.1 In-scope MVP (Fluent baseline)

- App shell + top bar + rail per UX §3.2.
- Two workspaces (Main + Backstage) with routing.
- Hospital-context selector (USZ / LUKS / Zollikerberg / Aggregated).
- Role switcher — visible only when `env=sit` and current role includes `HCC.PlatformAdmin` or `HCC.DemoOperator`.
- **One operational whiteboard** — BedManager @ USZ, 6 card types (Power BI tile, Agent, KPI, Live-stream, Responsible, Scenario). Card layout persisted in-memory for Sprint 13; persistence lands in a follow-up.
- **One Backstage tab** — Roles & RBAC live view.
- MSAL v2 with dynamic scope acquisition per Sprint 11 agent MCP scope.
- Fabric semantic model embed (Direct Lake) with RLS by hospital.
- Copilot Drawer skeleton invoking BMCA.
- Multilingual UI framework in place (DE default, EN fallback); FR/IT wired in follow-up.
- Accessibility baseline (WCAG 2.1 AA) via axe-core.

### 2.2 Parallel PoC scope (Rayfin)

- Rayfin generates the same shell (Main/Backstage tabs, top bar).
- Same Brandkit theme tokens injected.
- Same one operational whiteboard (BedManager).
- **Time-boxed to 3 engineering-days.** If not producing comparable output by then, PoC stops and decision memo records "not evaluable in scope."
- Same Playwright smoke test used to prove parity.

### 2.3 Out-of-scope / deferred

- Full role coverage — only BedManager whiteboard in S13; the other 9 roles land in follow-up sprints.
- Full Backstage coverage — only Roles tab; Ontology / Agents / Processes / Data Contracts tabs deferred.
- Whiteboard save/load persistence (in-memory only in S13; Cosmos or Fabric-backed in a follow-up).
- Real ontology graph visualisation.
- Native mobile / Teams embedding.

---

## 3. Architecture — repo layout and component boundaries

```
apps/
├─ hcc-app-fluent/
│  ├─ src/
│  │  ├─ shell/           # top bar, app rail, workspace router
│  │  ├─ auth/            # MSAL provider, claim parsing, env detection
│  │  ├─ context/         # hospital + role context providers
│  │  ├─ workspaces/
│  │  │  ├─ main/         # role-tailored boards
│  │  │  │  └─ boards/bed-manager/  # the reference whiteboard
│  │  │  └─ backstage/
│  │  │     └─ tabs/roles/          # the reference Backstage tab
│  │  ├─ whiteboard/      # reusable component (React Flow or tldraw)
│  │  ├─ cards/           # 6 card types: PowerBI, Agent, KPI, LiveStream, Responsible, Scenario
│  │  ├─ copilot-drawer/  # right-side agent drawer
│  │  ├─ theme/           # Fluent v9 theme built from Brandkit tokens
│  │  └─ i18n/            # DE default + EN fallback
│  ├─ tests/
│  │  ├─ unit/
│  │  └─ e2e/             # Playwright smoke
│  ├─ Dockerfile
│  └─ package.json
└─ hcc-app-rayfin/        # parallel PoC (structure follows Rayfin conventions)
   └─ (generated)
```

**Component boundaries.**

- `shell` knows nothing about agents or Fabric — it composes workspaces.
- `whiteboard` is a pure component; cards are plugged in via a registry.
- `cards` each own their data-fetch (they call Fabric/Agents themselves via injected services).
- `copilot-drawer` is agent-agnostic; per-agent config lives in a manifest.
- `auth` is the single source of `roles`, `hospital`, `env` claims; everything else consumes.

---

## 4. Rayfin PoC — comparison rubric and decision ADR

The parallel PoC produces a decision memo at Sprint 13 exit: `docs/adr/00XX-fluent-vs-rayfin-decision.md`.

**Rubric (evenly weighted):**

| # | Criterion | How measured |
| --- | --- | --- |
| 1 | Build velocity | Hours from empty repo to shell + one board (each track) |
| 2 | Fluent UI parity | Manual walkthrough vs. reference Fluent v9 gallery |
| 3 | Brandkit fidelity | Design-token coverage vs. Brandkit spec |
| 4 | Customisation depth | Can we express the 6 card types? Can we build the Copilot Drawer? |
| 5 | Agent-drawer feasibility | Time to wire one Sprint 11 agent through the drawer |
| 6 | License and GA posture | GA / preview / experimental; commercial terms |
| 7 | Test tooling | Availability of unit + E2E + a11y tooling |
| 8 | Long-term maintenance | Community, docs, upgrade cadence |

**Decision output.** ADR includes: recommendation, evidence per criterion, dissent notes, rollback path.

---

## 5. Agent and skill mix

| Track | Superpowers skills | Domain skills |
| --- | --- | --- |
| Fluent baseline | `writing-plans`, `subagent-driven-development` (per-component subagents), `test-driven-development`, `verification-before-completion` | (evaluate installing `react-fluent-authoring` if it exists per [AGENTS.md skill-discovery rule](../../../AGENTS.md#skill-discovery--rule-of-engagement-v1140-2026-07-08); else user-scoped) |
| Rayfin PoC | Same Superpowers cycle | Rayfin's own CLI / skill if bundled |
| Copilot Drawer wiring | Same | (Foundry agent client patterns) |

---

## 6. GitHub delegation

| Asset | Path | Trigger |
| --- | --- | --- |
| Issue template — app component | `.github/ISSUE_TEMPLATE/app-component.yml` | Per-component work (shell, whiteboard, card, drawer, etc.) |
| Workflow — app build | `.github/workflows/app-build.yml` | On PR to `apps/**` — build + unit test both apps |
| Workflow — app E2E | `.github/workflows/app-e2e.yml` | Playwright smoke: sign in with `demo.guest`, land on Home |
| Workflow — app a11y | `.github/workflows/app-a11y.yml` | axe-core scan on merged PRs |
| Labels | `sprint-13`, `app-fluent`, `app-rayfin`, `rayfin-poc`, `decision-adr-required` | Applied by templates |
| CODEOWNERS | `.github/CODEOWNERS` | `apps/**` → @urruegg |

---

## 7. Side-effect posture and approval gates

| Action | Ceiling | Gate |
| --- | --- | --- |
| App source changes | `write` | Standard PR review |
| Container Apps redeploy | `deploy` | `approved-to-apply` per environment |
| Fabric semantic model changes for embed | `write` on prompt to Fabric owner (deploy remains with S10/S15 owner) | Coordinated PR |
| Rayfin CLI install / license acceptance | Consent | User approval |
| Env variables / secrets (App Configuration) | `deploy` | `approved-to-apply` |

---

## 8. Verification strategy

- **Unit tests** — auth claim parsing (roles/hospital/env), hospital-context switcher, whiteboard save/load (in-memory), card registry, i18n resolver.
- **Playwright E2E smoke** — sign in as `demo.guest` → land on Home → open Backstage → Roles tab → sign out. Runs in both apps.
- **Accessibility** — axe-core scan on all shell surfaces; WCAG 2.1 AA target; violations block merge.
- **Visual regression** — snapshot the Fluent theme output vs. Brandkit token expectations.
- **Contract test** — Copilot Drawer sends a canonical prompt to BMCA and asserts the response shape (no PHI, grounded citation shape, refusal signal handling).
- **Env-scoping test** — same identity signs in on SIT and PROD slot URLs; app reports the correct `env`.

---

## 9. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Rayfin PoC blocks main track | Hard time-box (3 days); Fluent is always the deployable |
| Whiteboard component choice (React Flow vs. tldraw vs. custom) locks us in | Decision recorded in a mini-ADR; choose one, document why; wrap behind a thin adapter so replacement is bounded |
| MSAL redirect loops during env-slot routing | E2E test covers sit + prod slot URLs |
| Copilot Drawer + Foundry region mismatch (westus2 per ADR-0013) | Route agent calls through a proxy so region change is a config, not code |
| Brandkit token mapping to Fluent v9 drifts | Automated visual-regression on the theme output |
| i18n coverage gap in DE default | Fallback to EN with a warning banner; missing-key logging pipeline |
| RLS misconfig lets `demo.guest` see hospital-specific data | E2E test with `demo.guest` claim verifies aggregated-only rows |

---

## 10. Dependencies

**In**: Sprint 11 (BMCA available for drawer wiring), Sprint 12 (identities + app registration).

**Out**: Sprint 14 (extends Backstage with Evidence tab), Sprint 15 (BVA cards render on presenter whiteboard *and* fallback Power BI embed), Sprint 16 (CSA wizard surface).

---

## 11. Definition of done

- [ ] `apps/hcc-app-fluent/` and `apps/hcc-app-rayfin/` both build in CI.
- [ ] Fluent app deployed to Container Apps SIT slot with MSAL sign-in verified.
- [ ] BedManager whiteboard renders 6 card types with mock data.
- [ ] Backstage Roles tab renders live app-role list from Entra Graph (read-only).
- [ ] Copilot Drawer invokes BMCA and shows a grounded reply for one canonical prompt.
- [ ] `app-build.yml`, `app-e2e.yml`, `app-a11y.yml` workflows green.
- [ ] Decision ADR (`docs/adr/00XX-fluent-vs-rayfin-decision.md`) merged and recommends one stack for Sprint 14+.
- [ ] Sprint 13 retro entry in [docs/sprints/superpowers-checkpoint-matrix.md](../../sprints/superpowers-checkpoint-matrix.md).
