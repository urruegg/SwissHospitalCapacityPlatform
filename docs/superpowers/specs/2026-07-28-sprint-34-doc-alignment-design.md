# Sprint 34 — Curavias Documentation Alignment (Curavias anchor + IQ/Frontier Firm terminology + canonical mermaid) — Design Spec

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft for review |
| **Previous Version** | n/a (initial version) |
| **Sprint** | Sprint 34 — Curavias Documentation Alignment |
| **Issue** | [#505](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/505) (tracker); [#506](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/506) (WS-0 foundations) |
| **Builds on** | [CURAVIAS-PRODUCT-STATUS](../../CURAVIAS-PRODUCT-STATUS.md); [ARCHITECTURE](../../ARCHITECTURE.md); [copilot-instructions §9 Document Versioning](../../../.github/copilot-instructions.md); the `document-authoring` skill |
| **Related ADRs** | ADR-0002 (runtime = Copilot coding agent); ADR-0013 (US demo scope); ADR-0014 (Fabric IQ ontology backbone, GA-gated); ADR-0016 (no PHI in demo); ADR-0043 (PO Agent Foundry IQ domain). No decision reversal — this sprint is documentation-quality only and reverses no ADR. |
| **Runtime posture** | Documentation-only initiative. No code, no infra, no ADR reversal. Every doc edit passes mojibake + markdownlint gates and follows §9 SemVer version bumps. Human-performed PR merges; advisory-only product doctrine unchanged. |

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Context and problem statement](#2-context-and-problem-statement)
3. [Decisions taken (brainstorm outcomes)](#3-decisions-taken-brainstorm-outcomes)
4. [Scope and non-goals](#4-scope-and-non-goals)
5. [WS-0 — Foundations (glossary + doc template + canonical mermaid library)](#5-ws-0--foundations-glossary--doc-template--canonical-mermaid-library)
6. [Terminology and anchoring standard](#6-terminology-and-anchoring-standard)
7. [Customer-ready doc template](#7-customer-ready-doc-template)
8. [Canonical mermaid diagram library](#8-canonical-mermaid-diagram-library)
9. [Workstream decomposition (WS-1..4 by lane)](#9-workstream-decomposition-ws-14-by-lane)
10. [Governance, acceptance, DoD](#10-governance-acceptance-dod)
11. [Risks and open questions](#11-risks-and-open-questions)
12. [Sequencing summary](#12-sequencing-summary)

---

## 1. Goal and desired end state

Make the main Curavias solution documentation **stringent, internally consistent,
and customer-ready** — anchored on the **Curavias** product name and described
with Microsoft **IQ** terminology (**Fabric IQ**, **Foundry IQ**, **Work IQ**,
Copilot IQ) and Microsoft **Frontier Firm** operating-model framing, with a
refreshed **canonical mermaid diagram set** embedded where it aids comprehension.

Desired end state:

- A shared **`docs/GLOSSARY.md`** defines Curavias, the IQ terms, Frontier Firm,
  and the recurring solution vocabulary once; every in-scope doc uses those terms
  consistently.
- A standardized, **customer-ready doc template** (branded header block, one-line
  product anchor, executive summary, plain professional wording) is applied to
  every in-scope document.
- A **canonical mermaid library** (system context, medallion data flow, agent
  topology/orchestration, deployment/region, key sequence) is authored once and
  embedded in the relevant docs; existing diagrams are refreshed to match.
- The root **README.md** is elevated to a **customer-facing hero / at-a-glance**
  landing surface for the Curavias platform.
- Every in-scope doc passes the mojibake + markdownlint gates and carries a
  correct §9 SemVer version bump.

## 2. Context and problem statement

The repository already uses IQ terminology heavily (Fabric IQ / Foundry IQ /
Work IQ appear across specs and ADRs), and `CURAVIAS-PRODUCT-STATUS.md` models
the Curavias brand anchor well. But the **main solution docs are inconsistent**:

- The product is titled descriptively ("Swiss AI-Powered Patient Flow and
  Hospital Capacity Platform") in most design docs, while **Curavias** is the
  brand — applied consistently only in `CURAVIAS-PRODUCT-STATUS.md`.
- Several main docs (PRD, AI, SECURITY, DATA, COMPLIANCE, OPERATIONS, TEST, SD)
  carry **no mermaid diagram** at all; existing diagrams differ in style.
- **Frontier Firm** framing is not yet used to position Curavias as a Microsoft
  Frontier-Firm reference implementation (human + AI-agent teams).
- Header blocks, executive framing, and wording vary doc-to-doc; the surface is
  engineering-internal rather than customer-ready.

This sprint standardizes those four dimensions — anchor, terminology, diagrams,
customer-ready presentation — without changing any technical decision.

## 3. Decisions taken (brainstorm outcomes)

| # | Decision |
| - | -------- |
| D1 | **Scope = 16 main docs**: the 14 top-level `docs/*.md` solution docs (PRD, ARCHITECTURE, AI, SECURITY, DATA, INFRASTRUCTURE, COMPLIANCE, OPERATIONS, ALM_PLAN, TEST, SD, BVA, DEV_WORKFLOW, CURAVIAS-PRODUCT-STATUS) + root **README.md** + **AGENTS.md**. `docs/specs/**`, `docs/adr/**`, `docs/sprints/**`, `docs/reviews/**`, `docs/superpowers/**` are out of scope (historical / point-in-time). |
| D2 | **Frontier = Microsoft "Frontier Firm"** operating-model framing (Work Trend Index): human + AI-agent teams, agents as digital teammates, "agent boss" roles, human-agent ratio. Curavias is positioned as a **Frontier-Firm reference implementation**. Not "frontier models" capability framing. |
| D3 | **Full standard**: introduce a shared **glossary doc** AND a standardized **customer-ready doc template** applied to every in-scope doc. Not a lighter inline-only touch. |
| D4 | **Curated canonical mermaid library**: define a canonical diagram set (system context / C4-context, medallion Bronze/Silver/Gold data flow, agent topology / orchestration, deployment / region, key sequence flows), author once, embed where relevant, and refresh existing diagrams to match. |
| D5 | **Customer-ready look & feel and wording** is a first-class requirement: branded header block, one-line product anchor, executive summary, plain professional language, minimal internal jargon and sprint-internal references in the customer-facing surface. |
| D6 | **Delivery = dedicated sprint**, delegated via its own worktree/session (Sprint 28/33 pattern): **WS-0 foundations first** (glossary + template + canonical mermaid library + terminology decisions), then **WS-1..4** apply the standard per-doc. |
| D7 | **Workstream grouping = by architecture lane** (Approach A), mirroring the repo's lane doctrine, so each WS is independently reviewable and lane-scoped. |
| D8 | **README is the hero surface**: elevated to a customer-facing, at-a-glance landing page for Curavias (what it is, who it serves, the IQ/Frontier-Firm story, a context diagram, and navigation into the deeper docs). |

## 4. Scope and non-goals

**In scope (16 docs).** `docs/`: PRD, ARCHITECTURE, AI, SECURITY, DATA,
INFRASTRUCTURE, COMPLIANCE, OPERATIONS, ALM_PLAN, TEST, SD, BVA, DEV_WORKFLOW,
CURAVIAS-PRODUCT-STATUS; plus root **README.md** and **AGENTS.md**. Two new
foundation docs are created: `docs/GLOSSARY.md` and the canonical mermaid library
(`docs/architecture/diagram-library.md`).

**Out of scope.** `docs/specs/**`, `docs/adr/**`, `docs/sprints/**`,
`docs/reviews/**`, `docs/superpowers/**`. They may be referenced but are not
rewritten. If alignment surfaces a factual contradiction with an ADR, cite the
ADR — do not edit it (a MAJOR doc change that reverses a recorded decision would
require its own ADR per §9, and is explicitly not part of this sprint).

**Non-goals.** No change to technical decisions, architecture, security posture,
or product doctrine (advisory-only showcase, synthetic / no-PHI, not a medical
device). No code, no infra, no new requirements semantics — only wording,
structure, terminology, diagrams, and branding.

## 5. WS-0 — Foundations (glossary + doc template + canonical mermaid library)

WS-0 is the frozen foundation every other workstream builds against. It delivers:

1. **`docs/GLOSSARY.md`** — the shared terminology source of truth (§6).
2. **The customer-ready doc template** — captured in this spec (§7) and as a
   short reusable snippet block referenced by the glossary; defines the standard
   header, product anchor line, and executive-summary convention.
3. **`docs/architecture/diagram-library.md`** — the canonical mermaid library
   (§8): the five diagrams authored once, each with a short `embed me in: <docs>`
   note, so WS-1..4 copy the canonical source rather than inventing variants.
4. **A terminology decision record** in the glossary: the exact approved spelling
   and definition of Curavias, Fabric IQ, Foundry IQ, Work IQ, Copilot IQ,
   Frontier Firm, agent boss, human-agent ratio, medallion, advisory-only.

WS-0 lands as **Plan 1** and merges first; WS-1..4 land as follow-on plans the
delegated session proposes after WS-0 merges.

## 6. Terminology and anchoring standard

`docs/GLOSSARY.md` defines each term once with an approved definition. Baseline
definitions (to be refined in WS-0):

- **Curavias** — the Swiss AI-powered patient-flow and hospital-capacity
  platform; the product brand and the anchor name used across all docs.
- **Fabric IQ** — the Microsoft Fabric ontology + semantic backbone that grounds
  the data estate (GA-gated per ADR-0014).
- **Foundry IQ** — the Azure AI Foundry knowledge/agent domain that grounds the
  agents (per ADR-0043).
- **Work IQ** — the Microsoft 365 work-context signal source (meetings, mail,
  transcripts) consumed read-only via `work-iq-mcp`.
- **Copilot IQ** — Copilot-surfaced intelligence in the experience layer.
- **Frontier Firm** — Microsoft's Work Trend Index operating model: human +
  AI-agent teams, agents as digital teammates, "agent boss" roles, and a
  human-agent ratio. Curavias is a **Frontier-Firm reference implementation**.

**Anchoring rule.** Every in-scope doc references the product as **Curavias**
(descriptive phrasing allowed once, as an appositive: "Curavias, the Swiss
AI-powered patient-flow and hospital-capacity platform"). The one-line product
anchor (below) appears at the top of every in-scope doc.

## 7. Customer-ready doc template

Every in-scope doc adopts this structure (extending, not replacing, the §9
version header):

1. **Title** — `# Curavias — <Doc Purpose>` (Curavias-anchored).
2. **Version header table** — unchanged per §9 (Version/Date/Author/Status/
   Previous Version); every edit bumps the version.
3. **Product anchor line** (blockquote, one sentence) — e.g. *"**Curavias** is the
   Swiss AI-powered patient-flow and hospital-capacity platform — a Microsoft
   Frontier-Firm reference implementation grounded on Fabric IQ, Foundry IQ, and
   Work IQ."*
4. **Executive summary** — 2-4 plain-language sentences a non-engineer customer
   stakeholder can read: what this doc covers and why it matters.
5. **Body** — existing content, edited for consistent terminology, plain
   professional wording, and minimal internal jargon; canonical diagram(s)
   embedded where they aid comprehension.

The template must not break existing anchor links (renaming a top-level heading
that other docs deep-link to is a MAJOR change and is avoided; if unavoidable,
the referencing doc is updated in the same PR).

## 8. Canonical mermaid diagram library

Five canonical diagrams, authored once in `docs/architecture/diagram-library.md`
and embedded where relevant:

1. **System context (C4 L1)** — Curavias in its ecosystem: acute hospitals,
   rehab, Spitex, insurer-linked coordination, clinicians; Azure + Fabric IQ +
   Foundry IQ + Work IQ; GitHub delivery plane. Embed in: README, ARCHITECTURE,
   PRD, CURAVIAS-PRODUCT-STATUS.
2. **Medallion data flow** — file upload -> Bronze -> Silver -> Gold -> Direct
   Lake semantic model -> Fabric IQ ontology -> Foundry IQ / Data Agent grounding.
   Embed in: DATA, ARCHITECTURE, INFRASTRUCTURE.
3. **Agent topology / orchestration** — App copilot orchestrator over the PO,
   BVA, and capacity copilots (bmca / ooa / dca / orsa / sba / csa) plus
   supporting agents; Work IQ context; the Frontier-Firm human + agent team.
   Embed in: ARCHITECTURE, AI, AGENTS.
4. **Deployment / region** — as-deployed demo (PROD switzerlandnorth single
   region; SIT westus2 / eastus2 per ADR-0013/0032) vs target-GA (Switzerland
   North primary + Switzerland West failover). Embed in: INFRASTRUCTURE,
   ALM_PLAN, CURAVIAS-PRODUCT-STATUS.
5. **Key sequence** — user question in the Curavias App -> orchestrator ->
   sub-agent(s) -> deterministic/grounded cited answer with HITL. Embed in:
   ARCHITECTURE, AI, OPERATIONS.

Existing diagrams (ARCHITECTURE, INFRASTRUCTURE, ALM_PLAN, and
`architecture/app-iq-data-access-pattern.md`) are refreshed to match the library
style. Mermaid is copied from the canonical source (GitHub markdown cannot
transclude), so the library note records where each diagram is embedded to keep
copies in sync.

## 9. Workstream decomposition (WS-1..4 by lane)

WS-0 (foundations) first, then WS-1..4 apply the standard per lane. Each WS is a
separate work-package issue and a small, lane-scoped squash PR.

| WS | Lane | Docs |
| -- | ---- | ---- |
| **WS-0** | Foundations | `docs/GLOSSARY.md`, `docs/architecture/diagram-library.md`, the template (this spec) |
| **WS-1** | Governance | SECURITY, COMPLIANCE, AI |
| **WS-2** | Architecture / Data / Infra | ARCHITECTURE, INFRASTRUCTURE, DATA, ALM_PLAN |
| **WS-3** | Product / Experience (customer-facing) | **README (hero)**, CURAVIAS-PRODUCT-STATUS, PRD, BVA, SD |
| **WS-4** | Ops / Dev | OPERATIONS, TEST, DEV_WORKFLOW, AGENTS |

**Sequencing:** WS-0 first (freezes glossary + template + diagram library). Then
WS-3 (the customer-facing hero surface) is prioritized so the polished landing
experience lands early, followed by WS-2, WS-1, WS-4 — each independently
mergeable. The README hero page and the system-context diagram are the headline
customer-visibility deliverable.

## 10. Governance, acceptance, DoD

**Requirements (added to PRD §7 in WS-3):** `NFR-DOC-001` documentation is
Curavias-anchored and terminology-consistent; `NFR-DOC-002` main docs are
customer-ready (header, anchor line, exec summary, plain wording);
`NFR-DOC-003` canonical mermaid coverage on the docs that warrant it;
`NFR-DOC-004` all edits pass mojibake + markdownlint and §9 version bumps.

**Per-doc Definition of Done:**

- Curavias-anchored title + product anchor line + executive summary present.
- Terminology matches `docs/GLOSSARY.md` (Fabric IQ / Foundry IQ / Work IQ /
  Frontier Firm used correctly).
- Canonical diagram(s) embedded where the library specifies, copied from the
  canonical source.
- Plain, customer-ready wording; internal-only jargon minimized.
- `python scripts/lint/check_mojibake.py <files>` clean; `npx --yes
  markdownlint-cli2 "<files>"` clean; §9 SemVer version + Previous Version bumped;
  cross-doc links pass `markdown-link-check`.

**Sprint acceptance:** all 16 in-scope docs meet the per-doc DoD; `GLOSSARY.md`
and `diagram-library.md` exist and are referenced; README renders as a
customer-ready hero page; no technical decision or ADR was changed.

## 11. Risks and open questions

- **R1 — anchor-link breakage.** Renaming top-level headings can break deep
  links from out-of-scope docs. Mitigation: prefer additive headers; if a rename
  is unavoidable, update referencing docs in the same PR and treat as MAJOR.
- **R2 — mermaid duplication drift.** Copied diagrams can diverge. Mitigation:
  the library note records every embed location; WS PRs update all copies.
- **R3 — over-marketing.** Customer-ready wording must not overstate maturity or
  contradict the advisory-only / synthetic / no-PHI doctrine. Mitigation: the
  product doctrine statements in CURAVIAS-PRODUCT-STATUS are authoritative and
  copied verbatim where claims are made.
- **R4 — scope creep into specs/ADRs.** Mitigation: hard scope boundary (§4);
  out-of-scope docs are referenced, never rewritten.
- **Q1 (open):** should `GLOSSARY.md` also be linked from
  `.github/copilot-instructions.md` "Key Documentation" table? Proposed: yes, in
  WS-4 as a one-line additive edit (MINOR bump on that file).

## 12. Sequencing summary

1. **WS-0 (Plan 1)** — glossary + doc template + canonical mermaid library +
   terminology decisions. Merges first.
2. **WS-3** — README hero + CURAVIAS-PRODUCT-STATUS + PRD + BVA + SD (customer
   surface first).
3. **WS-2** — ARCHITECTURE + INFRASTRUCTURE + DATA + ALM_PLAN.
4. **WS-1** — SECURITY + COMPLIANCE + AI.
5. **WS-4** — OPERATIONS + TEST + DEV_WORKFLOW + AGENTS (+ optional
   copilot-instructions glossary link).

Each workstream is its own human-reviewed squash PR off the latest `main`. Never
self-merge; wait for green required checks.
