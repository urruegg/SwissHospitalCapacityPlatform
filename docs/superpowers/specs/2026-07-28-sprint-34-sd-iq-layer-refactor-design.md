# Sprint 34 — SD.md IQ-Layer Refactor (Design Spec)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rueegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | n/a (initial version) |

> **Curavias** is the Swiss AI-powered patient-flow and hospital-capacity
> platform — a Microsoft Frontier-Firm reference implementation grounded on
> Fabric IQ, Foundry IQ, and Work IQ.

## 1. Purpose

Refactor `docs/SD.md` so the Curavias solution design is framed around the
Microsoft **IQ operating-model layers**, with capabilities per layer and an
explicit **MVP vs Target full-scope** split (color-coded). This makes the SD
customer-ready and consistent with the Frontier-Firm framing already adopted in
`GLOSSARY.md`, while preserving every existing requirement mapping and anchor.

This spec is the approved output of the Sprint 34 brainstorming session for the
SD refactor. The interactive model was validated screen-by-screen in the
visual companion; this document is the written, locked version of that model.

## 2. The locked model

Five stacked IQ layers plus one cross-cutting **Process IQ** spine (the
patient-flow journey through the six role copilots). Green = **MVP** (built /
demoable now); dashed blue = **Target** (full-scope roadmap).

### 2.1 Process IQ — cross-cutting spine (patient-flow journey)

`OOA → DCA → BMCA → ORSA → SBA → CSA`. Golden thread:
*Medicine A → 102% occupancy in 72h → site −16 beds* — one signal steered
through every role. Process IQ is a spine, **not** a sixth stacked layer:
Fabric IQ signals steer it, Work IQ renders it.

### 2.2 Capability split per layer

| Layer | Tagline | MVP capabilities (green) | Target capabilities (dashed) |
| ----- | ------- | ------------------------ | ---------------------------- |
| **1 · Work IQ** | user experience & role-based actionable-insight control plane | Fluent UI command center; In-app Copilot rail; Role surfaces (6 copilots); Agent-boss HITL approval | Work IQ M365 context (read-only) |
| **2 · Foundry IQ** | orchestrated role agents grounded in closed-loop learning | Copilot orchestrator; Agents per role (×6 capacity + PO + BVA); Knowledge base (human work-instruction grounding); Grounded on GroundedChunk; Closed-Loop Learning (capture→eval→backlog) | — |
| **3 · Fabric IQ** | ontology, semantic data & steering signals to downstream systems | Medallion + Direct Lake model; Data Agents (`da_hospital_capacity`); Data Quality Agent gate + trust score; Internal + external signals → Process IQ | Fabric IQ ontology (GA-gated); Ingestion ↔ KIS / Epic / SAP; On-prem to cloud integration |
| **4 · DevSecOps IQ** | a product team of agents that build agents, gated by a human boss | Human agent boss (gated delivery); GitHub delivery plane; GitHub CLI Copilot; MCP allow-list; Functional-role agents build their Foundry-IQ relatives; Dev + Sec + Ops role agents | — |
| **5 · Governance IQ** | NFR guardrails spanning every layer | Zero Trust · Swiss residency · advisory-only · no-PHI; Evidence-first audit | DSG / CH-C01..C10 full control pack; Purview enforced |

### 2.3 Design principles applied per layer

- **Work IQ** — role-based least-surface UX; advisory-only framing with
  citations; every actionable output HITL-gated by a human agent boss.
- **Foundry IQ** — grounded-only responses over the `GroundedChunk` contract;
  orchestration over monolith (one agent per role, bounded scope); closed-loop
  learning (capture → eval → curated backlog).
- **Fabric IQ** — medallion quality layering with the Data Quality Agent as a
  hard gate; signals steer the process, not the UI; ontology GA-gated
  (GA-only in the MVP critical path); residency enforced by data class.
- **DevSecOps IQ** — agents build agents under a human gate; GitHub-native
  delivery + MCP allow-list; least-privilege; evidence-first delivery trail.
- **Governance IQ** — NFR boundaries expressed as guardrails that span every
  layer; Zero Trust default; Swiss-first residency; evidence-first audit;
  Purview enforcement planned.

## 3. Scope of edits

### 3.1 `docs/SD.md` (MINOR bump, additive — no anchor breaks)

Add a new top-level section **"IQ-Layered Solution Design (Operating Model)"**
after *Solution Overview*, containing:

1. A **color-coded layered diagram** (Mermaid `flowchart`, using `classDef` fills
   for MVP green / Target dashed) as the at-a-glance visual. This is the
   Markdown-renderable, GitHub-native translation of the locked HTML mockup —
   the mockup itself stays as the brainstorming source artefact.
2. The **capability split table** (§2.2) — the accessible, color-independent
   detail (MVP vs Target column) that carries the full capability list.
3. The **per-layer design & design principles** (§2.3), one short subsection per
   layer, each stating responsibilities, key controls, and the principle(s)
   applied.
4. The **Process IQ spine** narrative (§2.1) with the golden-thread example.

Targeted edits to existing content (kept in place to preserve anchors):

- **Out of Scope** — revise the stale item *"Foundry-hosted runtime agents"*:
  Foundry IQ orchestrated agents are now MVP (Foundry Agent Service is deployed
  per `ADR-0032`). Reframe the out-of-scope boundary to what remains out
  (e.g. autonomous/non-HITL agent action), and cross-reference Design
  Principle 7 + `ADR-0008` for the runtime-pattern nuance.
- **Design Principles** — add a short pointer that principles are now also
  presented per IQ layer in the new section (no principle removed or renumbered).
- **Solution Overview → Logical Domains** — add an *IQ layer* column mapping each
  existing logical domain to its IQ layer, so the two views stay reconciled.

Existing section headings (`Core Component Design`, its five numbered
sub-layers, `End-to-End Flow`, etc.) are **retained unchanged** to avoid
anchor-breaking (which would be a MAJOR change requiring an ADR). The new
IQ-layer section is the primary customer-facing framing; the existing
component design remains as the detailed engineering view and is cross-linked.

Version: `1.5.1 → 1.6.0` (MINOR — additive section + reconciling edits).

### 3.2 `docs/GLOSSARY.md` (MINOR bump — three new IQ terms)

Add to **§1.2 Microsoft IQ vocabulary**:

- **Process IQ** — the patient-flow journey layer: the sequence of role copilots
  (OOA → DCA → BMCA → ORSA → SBA → CSA) through which a single capacity signal is
  steered end to end. A cross-cutting operating-model spine, not a stacked
  platform layer; steered by Fabric IQ signals and rendered by Work IQ.
- **DevSecOps IQ** — the product-team-of-agents layer: functional-role agents
  that build their Foundry-IQ relatives, plus Dev / Sec / Ops role agents,
  delivered through the GitHub delivery plane, GitHub CLI Copilot, and the MCP
  allow-list, and gated by a human agent boss.
- **Governance IQ** — the NFR-guardrail layer that spans every other layer:
  Zero Trust, Swiss residency, advisory-only, no-PHI, evidence-first audit, the
  DSG / CH-C01..C10 control model, and (planned) Purview enforcement.

Add a one-line disambiguation to the existing **Work IQ** entry: in the SD
operating-model layering, *Work IQ* also names the **experience & role-based
control-plane layer** (Fluent UI + Copilot rail + role surfaces), which consumes
the narrowly-scoped M365 Work IQ signal defined here.

Version: `1.0.0 → 1.1.0` (MINOR — additive terms). Update the referencing note
if needed.

### 3.3 Out of scope for this PR

- No rename/removal of existing SD headings (would be MAJOR + ADR).
- No change to FR/NFR IDs. New capabilities map to existing requirements; no new
  requirement is introduced. If traceability gaps surface, they are logged, not
  invented here.
- The HTML visual companion mockup is a brainstorming artefact under
  `.superpowers/` (git-ignored); it is not committed.

## 4. Traceability

The refactor is presentational/additive and maps to existing requirements:

- Doc-alignment / terminology: `NFR-DOC-001` (glossary alignment), Sprint 34
  documentation-quality NFR family.
- Layer capabilities map to existing FRs/NFRs already covered by SD
  (`FR-GOV-*`, `NFR-SEC-*`, `NFR-COMP-*`, `FR-ONB-*`, etc.). No new IDs.

The PR description lists the exact FR/NFR IDs advanced (traceability contract,
copilot-instructions §6).

## 5. Validation

Doc gates on every edited file:

- `python scripts\lint\check_mojibake.py docs\SD.md docs\GLOSSARY.md`
- `npx --yes markdownlint-cli2 "docs/SD.md" "docs/GLOSSARY.md"`
- Mermaid render check on the new SD diagram
  (`npx --yes @mermaid-js/mermaid-cli@11 -i docs\SD.md -o <tmp>`; clean stray
  outputs afterwards).
- Link presence check (`markdown-link-check` is broken locally; verify targets
  with `Test-Path`).

## 6. Delivery

One issue → one branch → one squash PR. Doc-only change. Never self-merge; a
human merges on green. The pre-existing `What-if PROD` CI check fails ~2s on all
doc PRs (no PROD OIDC in the demo tenant) and is non-blocking.

## 7. Acceptance criteria

1. SD.md presents the five IQ layers + Process IQ spine, with a color-coded
   Mermaid diagram and the MVP-vs-Target capability table.
2. Each layer has a short design + design-principles subsection.
3. The stale "Foundry-hosted runtime agents" out-of-scope item is reconciled to
   deployed reality with an ADR-0032 / ADR-0008 cross-reference.
4. GLOSSARY.md defines Process IQ, DevSecOps IQ, Governance IQ and disambiguates
   Work IQ; SD terminology matches the glossary (NFR-DOC-001).
5. All doc gates pass; version headers bumped (SD 1.6.0, GLOSSARY 1.1.0) with
   `Previous Version` + `Date` updated.
6. No existing SD anchor is broken; no FR/NFR ID renamed.
