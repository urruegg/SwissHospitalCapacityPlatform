# Curavias Product Owner Agent - context-ask story backlog

| Field | Value |
| ------- | ------- |
| **Version** | 1.0.0 |
| **Date** | 2026-08-07 |
| **Author** | Urs Rueegg |
| **Status** | Draft |
| **Previous Version** | none |

> **Scope**: This is a **backlog for a future Product Owner Agent validation
> sprint** - it is documentation only. No context-ask wiring is implemented in
> code in the changes 1-9 sprint that produced it. Each row below story-types a
> single clickable context ask surfaced in the START and BACKSTAGE narrative
> planes so a later sprint can wire, ground, and test it against the
> `product-owner-agent`.
>
> **Source**: transcribed from the changes 1-9 design spec
> [2026-08-07-start-backstage-restructure-changes-1-9-design.md](../specs/2026-08-07-start-backstage-restructure-changes-1-9-design.md)
> section 3.9 (Workstream D), which captured the in-character
> `product-owner-agent` review of every section's context ask.
>
> **Advisory-only**: every answer the PO Agent returns is advisory, cited, and
> synthetic / no-PHI. The four knowledge classes are the frozen
> [ADR-0043](../../adr/0043-product-owner-agent-foundry-iq-domain.md) contract:
> **A** `retrieveCorpus` (repository / solution documentation), **B** `liveProof`
> (PROD service-stack evidence), **C** `costAnswer` (BVA gold measures),
> **D** `ontologyQuery` (Fabric semantic model / ontology).

## 1. How to read this backlog

Each grounded context ask becomes one validation story of the shape:

> **As a** C-level or hospital-operations user, **I want** to click a section's
> context ask, **so that** I get a cited PO Agent answer without leaving the
> narrative.
>
> **Acceptance**: the answer returns `GroundedChunk[]` from the expected
> knowledge class(es); every claim cites a `sourceRef`; a class-D answer also
> carries `conceptRef` + `goldBinding`; a failed live proof (class B) returns
> `partial` / `requires-validation` rather than uncited demo copy.

Column meanings:

- **Story ID** - stable id for the future sprint (`PO-CTX-NNN` grounded asks;
  `PO-REF-NNN` refusals).
- **Section** - plane + section where the ask is clickable.
- **Context ask** - the exact user-facing question.
- **Knowledge class** - expected source class(es) A / B / C / D. A trailing `!`
  marks an ask that must degrade to `requires-validation` when live evidence is
  unavailable.
- **Grounding source** - where the grounded answer is retrieved from.
- **Acceptance note** - the class-specific check the future sprint must assert.

## 2. START plane context asks

| Story ID | Section | Context ask | Knowledge class | Grounding source | Acceptance note |
| --- | --- | --- | --- | --- | --- |
| PO-CTX-001 | START / Hero | Is this real, safe, and not a medical device? | A (+B) | Doc corpus (governance / advisory-only posture); optional PROD posture proof | Cites advisory-only + not-a-medical-device statements from docs; B proof optional, never fabricated |
| PO-CTX-002 | START / Hero | Where does our data live? | A + B | Doc corpus (residency / region ADRs) + PROD region evidence | Cites residency decision; B confirms live region or returns `partial` |
| PO-CTX-003 | START / Challenger | Which review session raised this concern? | A | Doc corpus (review-session records) | Cites the specific review-session `sourceRef`; no invented attribution |
| PO-CTX-004 | START / Challenger | What product decision changed because of this feedback? | A | Doc corpus (decisions / ADRs / sprint notes) | Cites the decision record tied to the feedback item |
| PO-CTX-005 | START / Vision | Why cura + via? | A | Doc corpus (brand / vision narrative) | Cites the etymology / vision source; brand copy quoted verbatim |
| PO-CTX-006 | START / Vision | Which promises are non-negotiable: Swiss, human, advisory? | A | Doc corpus (guardrails / principles) | Cites each non-negotiable from the governance corpus |
| PO-CTX-007 | START / Work-chart | How does Curavias change the org chart into a work chart? | A | Doc corpus (operating-model narrative) | Cites the operating-model source; no unsourced claims |
| PO-CTX-008 | START / Work-chart | Why is this a Frontier Firm, not a dashboard? | A | Doc corpus (Frontier Firm positioning) | Cites the Frontier Firm fit narrative |
| PO-CTX-009 | START / Hospitals | Why these three synthetic hospitals? | A + D | Doc corpus (archetype rationale) + ontology (hospital dim) | A cites the synthetic-archetype rationale; D binds to the hospital concept |
| PO-CTX-010 | START / Hospitals | Which agents run each hospital, and what can they do? | A + B | Doc corpus (agent registry) + PROD agent evidence | A cites the agent roster; B confirms which agents are live or returns `partial` |
| PO-CTX-011 | START / Patient-path | What signal -> recommendation -> action -> HITL gate applies here? | A + D | Doc corpus (patient-flow narrative) + ontology (signal / action concepts) | A cites the flow; D binds signal / action / HITL concepts with `conceptRef` |
| PO-CTX-012 | START / Patient-path | Is 102% -> 94% computed or narrative? | D + A `!` | Ontology / gold measure + doc corpus | D must show `goldBinding` if computed; if no live binding, returns `requires-validation`, never asserted as computed |

## 3. BACKSTAGE plane context asks

| Story ID | Section | Context ask | Knowledge class | Grounding source | Acceptance note |
| --- | --- | --- | --- | --- | --- |
| PO-CTX-013 | BACKSTAGE / Company | What exactly is Curavias? | A | Doc corpus (product overview) | Cites the product definition source |
| PO-CTX-014 | BACKSTAGE / Company | Which PROD surfaces prove this exists? | B + A | PROD service-stack evidence + doc corpus | B enumerates live PROD surfaces; A cites what they should be; `partial` if a surface is unreachable |
| PO-CTX-015 | BACKSTAGE / BVA | What are ROI, payback, TCO, and confidence band? | C + A | BVA gold measures (`bva_*`) + doc corpus | C returns deterministic figures with `goldBinding`; A cites methodology; no LLM arithmetic |
| PO-CTX-016 | BACKSTAGE / BVA | Which value lever drives the build decision? | C + A | BVA gold measures (levers) + doc corpus | C cites the lever measure; A cites the decision framing |
| PO-CTX-017 | BACKSTAGE / Success-framework | How did one human plus agents deliver this? | A | Doc corpus (delivery-model narrative) | Cites the operating / delivery-model source |
| PO-CTX-018 | BACKSTAGE / Success-framework | Can we prove the sprint / PR claims? | A `!` | Doc corpus (sprint docs / PR trail) | Cites specific sprint / PR `sourceRef`; unverifiable claims return `requires-validation` |
| PO-CTX-019 | BACKSTAGE / Feedback-loop | For this domain, what signal / action / outcome is governed? | A + D | Doc corpus (feedback-loop narrative) + ontology | A cites the governed loop; D binds signal / action / outcome concepts |
| PO-CTX-020 | BACKSTAGE / Feedback-loop | Are outcomes measured today? | D / B `!` | Ontology / gold measure or PROD evidence | Returns measured value with `goldBinding` / live proof, else `requires-validation`; never claims measured without evidence |
| PO-CTX-021 | BACKSTAGE / Solution-design | Which IQ capabilities are MVP vs roadmap? | A | Doc corpus (solution-design / roadmap) | Cites the MVP-vs-roadmap source |
| PO-CTX-022 | BACKSTAGE / Solution-design | Which capabilities are live in PROD now? | B + A | PROD service-stack evidence + doc corpus | B confirms live capabilities; A cites intended set; `partial` on gaps |
| PO-CTX-023 | BACKSTAGE / DevSecOps-loop | Where are the human approval gates? | A | Doc corpus (governance / approval-gate model) | Cites the approval-gate definitions (for example `approved-to-apply`) |
| PO-CTX-024 | BACKSTAGE / DevSecOps-loop | What is actually deployed and healthy? | B | PROD service-stack evidence | Returns live deploy / health evidence; `partial` when a probe fails, never fabricated health |
| PO-CTX-025 | BACKSTAGE / Review-sessions | Who validated this and what changed? | A | Doc corpus (review-session records) | Cites reviewer + change `sourceRef` |
| PO-CTX-026 | BACKSTAGE / Review-sessions | What risks remain before customer adoption? | A | Doc corpus (risks / open items) | Cites the recorded residual risks |
| PO-CTX-027 | BACKSTAGE / PO-classes | Which class answers my question? | A | Doc corpus (PO knowledge-class model) | Cites the class definitions and routing rule |
| PO-CTX-028 | BACKSTAGE / PO-classes | Show the citation shape for ontology answers. | A + D | Doc corpus (citation contract) + ontology sample | A cites the `GroundedChunk` contract; D shows a `conceptRef` + `goldBinding` example |
| PO-CTX-029 | BACKSTAGE / Ninety-day | What happens in days 0-30, 30-60, 60-90? | A | Doc corpus (90-day roadmap) | Cites each phase from the roadmap source |
| PO-CTX-030 | BACKSTAGE / Ninety-day | What must be live before claiming value? | B + C + D | PROD evidence + BVA gold + ontology | B confirms live prerequisites; C cites the value measure; D binds the concept; `requires-validation` on any missing proof |

## 4. Explicit PO refusals (do NOT story-type as grounded)

These asks must be handled as refusals, not grounded answers. The future sprint
should assert the refusal wording, not a `GroundedChunk[]` result.

| Story ID | Refused ask | Reason | Expected behaviour |
| --- | --- | --- | --- |
| PO-REF-001 | Will our hospital reach 94% occupancy? | Needs customer-specific data the platform does not hold | Refuse; explain synthetic-only scope; offer a validation path, not a number |
| PO-REF-002 | Guarantee ROI / payback for us | Class C refuses beyond ROM / evidence-snapshot | Refuse a guarantee; offer the ROM / evidence band with its confidence caveat |
| PO-REF-003 | Show real patient examples | PHI refusal | Refuse; restate synthetic / no-PHI posture |
| PO-REF-004 | Is this legally certified for clinical use? | Status statement only, not a legal-certification guarantee | Return the not-a-medical-device status; refuse to assert legal certification |

## 5. Out of scope for this backlog

- No context-ask UI wiring, PO Agent tool calls, or grounding retrieval is
  built in the changes 1-9 sprint - this file is the input to a **separate**
  PO-agent validation sprint.
- Knowledge-class definitions and the `GroundedChunk` citation contract are
  owned by [ADR-0043](../../adr/0043-product-owner-agent-foundry-iq-domain.md)
  and the `product-owner-agent` pack; this backlog only maps asks to classes.
- Grounding-source specifics (exact doc paths, gold measures, PROD probes) are
  resolved during the validation sprint, not fixed here.
