# Curavias — Glossary and Documentation Standard

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | 1.0.0 (initial version); this bump adds Process IQ, DevSecOps IQ, and Governance IQ to the IQ vocabulary and disambiguates Work IQ for the SD operating-model layering |

> **Curavias** is the Swiss AI-powered patient-flow and hospital-capacity
> platform — a Microsoft Frontier-Firm reference implementation grounded on
> Fabric IQ, Foundry IQ, and Work IQ.

## Executive summary

This document is the shared terminology source of truth for the Curavias
documentation set, plus the customer-ready authoring standard every main doc
follows. It defines the product anchor name, the Microsoft **IQ** vocabulary
(Fabric IQ, Foundry IQ, Work IQ, Copilot IQ), and the **Frontier Firm**
operating-model framing once, so every in-scope document uses the same terms and
the same customer-ready presentation. It changes no technical decision — it
standardizes how the platform is named and described.

This is a Sprint 34 (Documentation Alignment) foundation artefact. It is
referenced by the [Sprint 34 design spec](superpowers/specs/2026-07-28-sprint-34-doc-alignment-design.md)
and paired with the [canonical diagram library](architecture/diagram-library.md).

## 1. Terminology (source of truth)

Each term below has one approved spelling and definition. Use these exact forms
in every in-scope document.

### 1.1 Product and operating model

* **Curavias** — the Swiss AI-powered patient-flow and hospital-capacity
  platform; the product brand and the anchor name used across all docs. A
  descriptive phrasing is allowed once per doc as an appositive: *"Curavias, the
  Swiss AI-powered patient-flow and hospital-capacity platform."* Curavias is an
  **advisory-only showcase on synthetic data** — it *previews / recommends*,
  never *decides / diagnoses* — and is **not a medical device** (see
  [CURAVIAS-PRODUCT-STATUS.md](CURAVIAS-PRODUCT-STATUS.md)).
* **Frontier Firm** — Microsoft's Work Trend Index operating model: organisations
  built around **human + AI-agent teams**, where agents act as digital teammates,
  humans take on **agent boss** roles, and work is measured in part by the
  **human-agent ratio**. Curavias is positioned as a **Frontier-Firm reference
  implementation**. This is operating-model framing — *not* "frontier models"
  capability framing.
* **Agent boss** — a human who directs, supervises, and is accountable for a team
  of AI agents; the human side of every human-in-the-loop (HITL) decision in
  Curavias.
* **Human-agent ratio** — the Work Trend Index measure of how many AI agents a
  human oversees within a team; used to describe how Curavias scales capacity
  work across human + agent teams.

### 1.2 Microsoft IQ vocabulary

* **Fabric IQ** — the Microsoft Fabric ontology and semantic backbone that
  grounds the Curavias data estate (GA-gated per
  [ADR-0014](adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md)). It sits over the Gold
  medallion layer and the Direct Lake semantic model.
* **Foundry IQ** — the Azure AI Foundry knowledge and agent domain that grounds
  the Curavias agents (per [ADR-0043](adr/0043-product-owner-agent-foundry-iq-domain.md)).
  It serves grounded, cited answers over the shared knowledge classes.
* **Work IQ** — the Microsoft 365 work-context signal source (meetings, mail,
  meeting-recording transcripts) consumed **read-only** via the `work-iq-mcp`
  server for review-session and email-feedback intake. In the SD operating-model
  layering, *Work IQ* also names the **experience and role-based control-plane
  layer** (Fluent UI + Copilot rail + role surfaces), which consumes this
  narrowly-scoped M365 Work IQ signal.
* **Copilot IQ** — Copilot-surfaced intelligence in the experience layer: the
  in-app Curavias copilot rail and Copilot-mediated interactions with the
  platform's agents.
* **Process IQ** — the patient-flow journey layer: the sequence of role copilots
  (OOA → DCA → BMCA → ORSA → SBA → CSA) through which a single capacity signal is
  steered end to end. A cross-cutting operating-model spine, not a stacked
  platform layer; steered by Fabric IQ signals and rendered by Work IQ.
* **DevSecOps IQ** — the product-team-of-agents layer: functional-role agents
  that build their Foundry-IQ relatives, plus Dev / Sec / Ops role agents,
  delivered through the GitHub delivery plane, GitHub CLI Copilot, and the MCP
  allow-list, and gated by a human agent boss.
* **Governance IQ** — the NFR-guardrail layer that spans every other layer: Zero
  Trust, Swiss residency, advisory-only, no-PHI, evidence-first audit, the
  DSG / CH-C01..C10 control model, and (planned) Purview enforcement.

### 1.3 Data and delivery vocabulary

* **Medallion** — the Bronze / Silver / Gold lakehouse layering pattern:
  raw-ingested **Bronze**, conformed and quality-gated **Silver**, and
  analytics-ready **Gold** Delta tables that feed the Direct Lake semantic model
  and Fabric IQ.
* **Direct Lake** — the Power BI storage mode that reads Gold Delta tables
  directly from OneLake without import or DirectQuery, backing the Curavias
  semantic model.
* **Advisory-only** — the governing product doctrine: Curavias previews and
  recommends; it never takes an autonomous clinical or operational decision. Every
  actionable output is human-approved (agent boss + HITL).

## 2. Anchoring rule

Every in-scope document references the product as **Curavias**. The one-line
**product anchor** (below) appears as a blockquote at the top of every in-scope
document, immediately under the version-header table.

> **Curavias** is the Swiss AI-powered patient-flow and hospital-capacity
> platform — a Microsoft Frontier-Firm reference implementation grounded on
> Fabric IQ, Foundry IQ, and Work IQ.

## 3. Customer-ready doc template

Every in-scope document adopts the structure below. It **extends** — never
replaces — the [§9 Document Versioning](../.github/copilot-instructions.md)
version header. Copy this block verbatim into WS-1..4 docs.

```markdown
# Curavias — <Doc Purpose>

| Field | Value |
| ----- | ----- |
| **Version** | X.Y.Z |
| **Date** | YYYY-MM-DD |
| **Author** | <author> |
| **Status** | Draft \| Reviewed |
| **Previous Version** | <prior> (<short hint>) |

> **Curavias** is the Swiss AI-powered patient-flow and hospital-capacity
> platform — a Microsoft Frontier-Firm reference implementation grounded on
> Fabric IQ, Foundry IQ, and Work IQ.

## Executive summary

<2-4 plain-language sentences a non-engineer customer stakeholder can read:
what this document covers and why it matters.>

## <Body>

<existing content, edited for consistent terminology (§1), plain professional
wording, and minimal internal jargon; canonical diagram(s) from the diagram
library embedded where they aid comprehension.>
```

### 3.1 Template rules

* **Title** — `# Curavias — <Doc Purpose>` (Curavias-anchored).
* **Version header** — unchanged per §9; every edit bumps the version and updates
  `Previous Version` and `Date` together.
* **Product anchor line** — the exact blockquote from §2, one sentence.
* **Executive summary** — 2-4 plain-language sentences for a customer stakeholder.
* **Body** — existing content, terminology-aligned to §1, customer-ready wording,
  canonical diagram(s) embedded per the
  [diagram library](architecture/diagram-library.md).
* **Do not break anchors** — renaming a top-level heading that other docs
  deep-link to is a MAJOR change and is avoided; if unavoidable, update the
  referencing doc in the same PR.

## 4. Scope

In scope for the terminology and template standard: the 14 top-level solution
docs (PRD, ARCHITECTURE, AI, SECURITY, DATA, INFRASTRUCTURE, COMPLIANCE,
OPERATIONS, ALM_PLAN, TEST, SD, BVA, DEV_WORKFLOW, CURAVIAS-PRODUCT-STATUS), the
root `README.md`, and `AGENTS.md`. Out of scope (historical / point-in-time):
`docs/specs/**`, `docs/adr/**`, `docs/sprints/**`, `docs/reviews/**`,
`docs/superpowers/**` — referenced, never rewritten.
