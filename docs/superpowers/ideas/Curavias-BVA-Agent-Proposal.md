# Curavias BVA Agent — Proposal

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rueegg |
| **Status** | Draft — for backlog grooming |
| **Previous Version** | n/a (initial idea) |

> **Type:** New-sprint starting point — a Business Value Assessment (BVA)
> competency agent for ROI and TCO, grounded on effective PROD/SIT Azure cost
> plus the GitHub Copilot cost of building and running the platform.
>
> **Builds on:** the [BVA ROM baseline](../../BVA.md), the
> [Sprint 15 BVA Evidence Data Product](../specs/2026-07-09-sprint-15-bva-design.md)
> (FOCUS-shaped synthetic seed + C-suite views + stretch `bva-agent`), the
> [BVA KPI catalog (ADR-0025)](../../adr/0025-bva-kpi-catalog.md), the
> [Product Owner Agent proposal](Curavias-Product-Owner-Agent-Proposal.md)
> (which already names a "BVA / TCO cost data product" grounding source), and
> the newly-seeded real cost evidence in
> [docs/agent_cost.md](../../agent_cost.md) + [BOM annex](../../agent-cost-bom.md).
>
> **Inherits the platform doctrine:** advisory-only + HITL, Swiss-region-pinned
> inference, GA-only critical path, contract-first, provenance-complete, fully
> audited. The BVA Agent **never changes cloud spend or resources** — it reads,
> models, and recommends.

---

## 1. Context — why a BVA Agent, now

Three forces converge:

1. **The COO review** ([2026-07-24 AMA](../../reviews/2026-07-24-ama-coo-review.md))
   framed the business case on *public data across a few hospitals/cantons* and
   stressed that value realisation hinges on operational KPIs (OR utilisation
   >= 85%, discharge timeliness, avoided transfers) — i.e. a defensible ROI/TCO
   narrative is a first-class deliverable, not an afterthought.
2. **We now have real evidence.** [docs/agent_cost.md](../../agent_cost.md)
   captures authoritative weekly Azure spend (USD 491.11 across 2026-06-29 ->
   2026-07-27, snapshot 2026-07-28) with a full 144-resource
   [BOM](../../agent-cost-bom.md), plus Copilot build/run telemetry
   (~246k AIU). Today this is refreshed by hand; it should be an agent
   competency.
3. **The BVA data product exists** ([Sprint 15](../specs/2026-07-09-sprint-15-bva-design.md))
   with plan-vs-actual KPIs and C-suite views, and explicitly parks a stretch
   `bva-agent`. This proposal is that agent, fully specified.

## 2. Relationship to the "GitHub BVA agent" (two-tier design)

The user's intent — *"a BVA Agent linked to the GitHub BVA agent later"* — maps
to a deliberate two-tier split:

| Tier | Name | Runtime | Owns | This proposal |
| --- | --- | --- | --- | --- |
| **A — repo-native** | `bva-agent` (GitHub Copilot coding agent per ADR-0002, the runtime decision) | GitHub Copilot coding agent + MCP | The **evidence + model in the repo**: refreshes `docs/agent_cost.md`, the BOM annex, and reconciles them against the `docs/BVA.md` ROM; opens PRs with variance findings | **In scope now** |
| **B — in-product** | Live BVA / TCO copilot rail | Curavias App (Backstage/Evidence surface, Sprint 15 data product) | The **live board-facing** cost + value cards, grounded on Tier A evidence and the FOCUS data product | Linked later |

Tier A is the "GitHub BVA agent": it lives in this repo, uses `github-mcp`
plus read-only `azure-mcp` and `fabric-mcp`, and produces auditable
GitHub-native artefacts. Tier B consumes Tier A's curated evidence. This
proposal delivers Tier A and defines the hand-off contract to Tier B.

## 3. Purpose and scope

A read-only **financial-evidence agent** that keeps the platform's ROI/TCO
picture current, defensible, and reconciled.

**In scope:**

* Ingest **authoritative Azure cost** (Cost Management `ActualCost`, and the
  FOCUS export used by the Sprint 15 data product) per service, per resource
  group, per resource, weekly and monthly.
* Ingest **Copilot build/run cost** (session-store AIU + token telemetry now;
  GitHub billing usage API once a `Plan:read` token exists).
* Maintain the **BOM** and map every billed line to a BOM entry (drift = new,
  removed, or unexpectedly-costing resources).
* **Reconcile plan vs actual** against the `docs/BVA.md` ROM model and the
  [ADR-0025](../../adr/0025-bva-kpi-catalog.md) KPI catalog; compute variance
  and unit economics (cost per forecast run, per Copilot turn, per bed-day, per
  active hospital).
* Produce **evidence PRs**: refreshed cost tables, a variance narrative, and
  board-ready summaries feeding the BVA cards.

**Out of scope:** changing any Azure resource or spend (no `deploy`/`delete`),
setting budgets, procurement commitments, and any autonomous action — every
output is advisory and human-gated.

## 4. Knowledge and data sources

| Class | Source | Access |
| --- | --- | --- |
| A | Azure Cost Management `ActualCost` (subscription 1) | `azure-mcp` (read) / `az rest` |
| A | FOCUS cost export (Sprint 15 BVA data product) | `fabric-mcp` (read) |
| B | Copilot session-store telemetry (AIU + tokens) | session store (read) |
| B | GitHub billing usage API (`Plan:read`) | `gh api` (token-gated) |
| C | `docs/BVA.md` ROM model, `docs/agent_cost.md`, BOM annex | `github-mcp` (read) |
| C | ADR-0025 BVA KPI catalog, PRD FR/NFR | `github-mcp` (read) |
| D | Operational KPIs (OR utilisation, discharge, forecast counts) | `fabric-mcp` (read, Gold) |

All cloud/LLM-returned values are **untrusted input**, re-validated at each
tool boundary; nothing is written outside the repo.

## 5. Agent journeys

* **Weekly cost close.** Pull `ActualCost` + telemetry -> refresh weekly
  tables + BOM -> flag settling weeks -> open a PR with the diff and a one-line
  variance summary.
* **ROI/TCO refresh.** Recompute plan-vs-actual vs `docs/BVA.md` ROM ->
  update the 3-year TCO actuals column -> narrate drivers (e.g. "Fabric ~45% of
  spend").
* **Cost-anomaly alert.** Week-over-week service jump beyond a threshold ->
  issue with the offending resource(s) and probable cause (from BOM + tags).
* **Board pack.** On request, assemble the CFO/CIO/COO BVA cards from the
  latest curated evidence for the Sprint 14 presenter whiteboard / Power BI app.

## 6. Draft requirements (to promote into PRD §7)

### Functional

* **FR-BVA-A-001** — Ingest Azure `ActualCost` for subscription 1 at Daily
  granularity and aggregate to ISO weeks by service, resource group, resource.
* **FR-BVA-A-002** — Maintain the full BOM and reconcile every billed line to a
  BOM entry; report drift.
* **FR-BVA-A-003** — Ingest Copilot AIU/token telemetry weekly; ingest GitHub
  billing usage when a `Plan:read` token is present.
* **FR-BVA-A-004** — Reconcile actual vs `docs/BVA.md` ROM and ADR-0025 KPIs;
  emit variance + unit economics.
* **FR-BVA-A-005** — Deliver all outputs as GitHub PRs/issues (evidence +
  narrative); never mutate cloud.
* **FR-BVA-B-001** *(Tier B, later)* — Serve curated BVA/TCO cards to the
  Curavias App copilot rail from Tier A evidence.

### Non-functional

* **NFR-BVA-001** — Read-only cloud posture; side-effect ceiling `write`
  (repo only); `azure-mcp`/`fabric-mcp` used at `read`.
* **NFR-BVA-002** — Provenance-complete: every figure cites its query, snapshot
  date, and currency; settling weeks marked provisional.
* **NFR-BVA-003** — No secrets in artefacts; `Plan:read` token supplied via
  GitHub Actions secret, never committed.
* **NFR-BVA-004** — Swiss-region / GA doctrine honoured; demo figures labelled
  PoT (`westus2`, synthetic) per ADR-0013.

## 7. Fit within the existing agent set (proposed registry row)

| Agent | Owner | Trigger | MCP servers | Side-effect ceiling |
| --- | --- | --- | --- | --- |
| `bva-agent` | @urruegg | `@bva-agent` mention, a BVA/cost issue, or a scheduled weekly-close workflow | `github-mcp`, `azure-mcp` (read), `fabric-mcp` (read) | `write` (repo); `read` (azure/fabric) |

No new MCP server is required — `azure-mcp`, `github-mcp`, and `fabric-mcp`
already exist in the allow-list. The GitHub billing usage API is reached via
`gh` with a token-gated `Plan:read` scope, not a new MCP server.

## 8. Assumptions and open questions

* **A1** — "GitHub BVA agent" = the Tier A repo-native `bva-agent`; Tier B is
  the in-product rail. *Confirm this framing.*
* **A2** — A `Plan:read` fine-grained PAT can be provisioned as a GitHub Actions
  secret for authoritative Copilot billing; until then, telemetry (AIU/tokens)
  is the proxy and the `$`/AIU rate is unknown.
* **A3** — The FOCUS export from the Sprint 15 data product is the join point
  between real `ActualCost` and the BVA dashboard; confirm its refresh cadence.
* **A4** — ROM values in `docs/BVA.md` are CHF; actuals are USD. A single
  reporting currency + FX assumption must be fixed for plan-vs-actual.
* **A5** — Resolved: numbered **Sprint 33** (leaving 31/32 reserved for the
  closed-loop breadth/hardening track). Design spec:
  [2026-07-28-sprint-33-curavias-bva-agent-design.md](../specs/2026-07-28-sprint-33-curavias-bva-agent-design.md).

## 9. Definition of done (proposed sprint)

* `agents/bva-agent/AGENT.md` + `golden-tasks.md` (>= 1 happy-path weekly-close
  fixture, >= 1 refusal fixture for a spend-mutation request), registry row in
  `AGENTS.md`.
* A repeatable weekly-close that reproduces `docs/agent_cost.md` +
  `agent-cost-bom.md` from live `ActualCost` (this proposal's tables are the
  first golden output).
* Plan-vs-actual variance appended to `docs/BVA.md` (actuals column) behind a
  human-reviewed PR.
* The FR-BVA and NFR-BVA requirements promoted into `docs/PRD.md` §7.

## 10. Seed evidence (already in the repo)

* [docs/agent_cost.md](../../agent_cost.md) — weekly Azure spend (by service,
  RG, resource) + Copilot telemetry.
* [docs/agent-cost-bom.md](../../agent-cost-bom.md) — full 144-resource BOM.

These two files are the BVA Agent's first curated output, produced by hand
this sprint; the agent's job is to keep them — and the ROI/TCO model they feed
— continuously current.
