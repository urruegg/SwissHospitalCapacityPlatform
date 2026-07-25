# Curavias Product Owner Agent — Proposal

**Backstage-Integrated, Source-Grounded Product Intelligence for the Curavias Platform**
Prepared for Urs Rüegg · Innovation Hub · Draft v1.2

> **v1.2 (2026-07-25) — two further requirements + reviews emphasis.** (5) The
> **North Star ontology / Fabric Data Agent is added as a fourth knowledge
> source (Class D)** — a semantic query surface to ask *data* questions across
> the underlying data products, not just metadata. (6) The PO Agent is
> **embedded in the Curavias App as a Copilot rail on the START and BACKSTAGE
> surfaces**, using the exact per-role Copilot-rail pattern the MAIN boards
> already ship (docked right rail, proactive default, status/confidence/
> citations). The interview-derived **`docs/reviews/` AMA sessions** (hospital
> ops lead, COO, CTO mentor, CAF/WAF, HCC North Star, …) are called out
> explicitly as a first-order Class A source. Previous: Draft v1.1 (Foundry IQ
> Knowledge Layer + daily GitHub→ADLS refresh + live-proof + BVA/TCO cost
> product).
>
> **v1.1 (2026-07-25) — reframed on four review requirements.** (1) The
> foundation is a shared **Foundry IQ Knowledge Layer** that serves multiple
> knowledge domains; the Product Owner is domain #1 and the same layer later
> grounds any other agent role. (2) The document corpus is refreshed **daily
> from GitHub into Azure Storage**, reusing the platform's proven master-data
> landing pattern. (3) **Live-proof validation** is a first-class knowledge
> source — answers are checked against the *actually deployed* Azure / Fabric /
> Foundry state, not only the docs. (4) A **BVA / TCO cost data product** grounds
> every cost answer on effective PROD Azure cost plus the GitHub Copilot token
> cost of building and running the platform. Previous: Draft v1.0
> (documentation-only grounding, Azure AI Search MVP index).

---

## 1. Vision and Purpose

## 1.1 Vision

The **Curavias Product Owner Agent (PO Agent)** is the authoritative, source-grounded voice of the Curavias platform. It answers any product question — from a developer's "which data contract does the discharge agent consume?" to a CEO's "what is our defensible differentiation?" — with a trusted, cited answer drawn only from the platform's own governed documentation, never from guesswork.

It embodies the same discipline the platform itself is built on: **advisory-only, human-in-the-loop, retrieval-grounded, region-pinned, and fully auditable.** The PO Agent is not a replacement for the Product Owner; it is the Product Owner's always-on, always-cited memory.

## 1.2 Purpose

- Give every audience — internal teams, partners, and executive stakeholders — a **single, consistent, traceable answer** to product questions, replacing tribal knowledge, stale slides, and inconsistent verbal answers.
- Make the platform's rich governance corpus (PRD, SD, ARCHITECTURE, AI, COMPLIANCE, SECURITY, DATA, BVA, TCO, ADRs, roadmap, sprints, reviews) **usable in seconds** rather than requiring a document hunt.
- **Refuse to invent.** Where the corpus is silent or a decision is still "proposed" or "requires validation," the agent says so and points to the gap — turning unknowns into a backlog rather than a bluff.

## 1.3 Why now

The Curavias programme already runs an AI reviewer pattern (the "AMA reviewer prompt") that reads session transcripts, extracts decisions, performs drift analysis against the baseline, and emits structured, traceable reviews. The PO Agent is the natural next step in that pattern: from *reviewing* the design to *answering questions about* the design, on demand, for everyone.

> **Assumption A1 — "Backstage" = the Curavias App surface.** Per the latest
> requirement, *Backstage* refers to the **BACKSTAGE surface of the Curavias
> App** (the START / MAIN / BACKSTAGE React / Fluent-v9 shell), not the Spotify
> Backstage IDP. The PO Agent is embedded as an in-app **Copilot rail** on the
> **START** and **BACKSTAGE** surfaces, reusing the same per-role Copilot-rail
> pattern the MAIN boards already ship (Section 8). A Spotify Backstage plugin
> remains a possible *additional* surface, but the primary target is the
> Curavias App itself.

## 1.4 Foundation — a shared, multi-domain knowledge layer

The PO Agent is **not** a bespoke, single-purpose index. It is the first
*domain* mounted on a shared **Foundry IQ Knowledge Layer** — an Azure AI
Foundry knowledge surface (knowledge sources + agentic retrieval) that any
platform agent can ground on.

- **Domain #1 = Product Owner.** The knowledge domain delivered by this
  proposal: the governed product corpus, the live-proof view, the cost
  data product, and the ontology query surface (Section 6).
- **Reusable for any agent role.** The same layer later serves additional
  domains — a *Compliance* domain for `compliance-agent`, a *Data* domain for
  `data-quality-agent`, an *Operations* domain for the runtime copilots — each
  an additively-registered knowledge source, not a new platform.
- **One governance envelope.** Region-pinning, classification-aware ingestion,
  authorisation-aware retrieval, and the audit trail are implemented **once**
  at the layer and inherited by every domain. Adding a domain is a governed,
  Git-first, CODEOWNERS-reviewed act — never a parallel stack.

This reframes Assumption A5: the retrieval foundation is the Foundry IQ
Knowledge Layer (which composes Azure AI Search + OneLake underneath), chosen
so the investment compounds across agent roles instead of being spent on one.

---

## 2. Business Value Proposition

| Value lever | What it delivers | Who benefits most |
|---|---|---|
| **Faster, consistent answers** | Seconds-to-answer on any product question, identical regardless of who asks | All personas; Sales/Pre-Sales especially |
| **Trust through citation** | Every answer links to the exact source (doc, section, ADR, contract) | Executives, Partners, Customers |
| **Reduced key-person risk** | Product knowledge is no longer trapped in one Product Owner's head | Leadership, Delivery |
| **Faster deal cycles** | Pre-Sales and Partners self-serve accurate architecture, compliance, and TCO answers | Sales, Partners, CFO |
| **Governance dividend** | Reuses the platform's existing evidence/traceability model — answers double as audit artefacts | CISO, CLO, CDO |
| **"Gap radar"** | Systematically surfaces where documentation is missing or a decision is unratified | Product, Engineering |

**Headline proposition:** the PO Agent converts an already-rigorous but hard-to-navigate governance corpus into an instantly queryable, self-citing product brain — shortening sales and onboarding cycles while *strengthening* (not diluting) compliance posture, because every answer is grounded and logged.

> **Assumption A2 — quantified ROI.** A defensible ROI figure (hours saved per persona, deal-cycle reduction) requires baseline measurement that does not yet exist in the corpus. This proposal deliberately does **not** state a CHF ROI; establishing it is an MVP success-metric activity (Section 14), mirroring the platform's own T0 baseline-capture discipline.

---

## 3. User Personas

## 3.1 Internal and partner audiences

| Persona | What they ask the agent for | Dominant need |
|---|---|---|
| **Product Manager** | Scope, backlog rationale, requirement traceability, roadmap sequencing | Decision provenance |
| **Solution Architect** | Architecture patterns, ADRs, integration boundaries, GA constraints | Precision + diagrams |
| **Developer** | Data contracts, agent responsibilities, APIs, test gates, "how do I…" | Task-level specificity |
| **Customer Success** | Operating model, KPIs, adoption playbooks, known limitations | Outcome framing |
| **Sales / Pre-Sales** | Value story, differentiation, compliance posture, indicative TCO | Confident, cited, non-technical |
| **Partner** | Integration/extension points, co-sell boundaries, IP model | Scoped, boundary-aware |
| **Executive stakeholder** | Strategy, risk, cost, compliance at a glance | Concise, board-ready |

## 3.2 Executive personas — deep analysis (the challenging questions)

Each executive is analysed on five axes: **primary concerns, key questions, required knowledge sources, expected response style, and risk of inaccurate answers.** These personas are the highest-stakes users — a wrong answer here has strategic, financial, or legal consequences, so the agent applies its strictest grounding and "defer-don't-guess" behaviour to them.

### CEO — Chief Executive Officer
- **Primary concerns:** strategic differentiation, market and scale opportunity, ROI and payback, reputational and regulatory risk, positioning versus incumbents (VR&P Integral Capacity Management, Epic).
- **Key questions:** *"Where does the value come from and how do we defend it? What is the path to scale across cantons and providers? What could damage our — or a customer's — reputation?"*
- **Required knowledge sources:** BVA artefacts, product roadmap, tiered SKU framework (T0→T3+), the Hospital Command Center repositioning narrative, competitor/gap analyses, KPI/value-case framework.
- **Expected response style:** concise, outcome-first, board-ready; three to five headline figures with explicit ranges; strategic framing; evidence available on request, not by default.
- **Risk of inaccurate answers:** an overstated ROI or fabricated market claim drives a bad investment or a public commitment that cannot be met — direct credibility and reputational damage; a wrong differentiation claim misdirects strategy.

### COO — Chief Operating Officer
- **Primary concerns:** operational adoption, throughput gains (OR utilisation, discharge-before-noon, bed occupancy), the operating model, change management, staffing.
- **Key questions:** *"How does it actually improve OR–bed–staffing coordination? What is the operating model — cadences, RACI, playbooks? What is the adoption risk and how is it mitigated?"*
- **Required knowledge sources:** OPERATIONS documentation, the HCC operating-model findings, the operational-outcome KPI framework (NFR-KPI-*), the Kispi case study, sprint/backlog.
- **Expected response style:** pragmatic; "process + tool together"; concrete before/after operational deltas; honest about the "great dashboard, no adoption" failure mode.
- **Risk of inaccurate answers:** over-promising operational gains sets unrealistic targets and erodes clinician trust; quoting an outcome without a baseline misleads the change programme.

### CIO — Chief Information Officer
- **Primary concerns:** architecture fit, integration with existing systems (KIS / Epic) *without touching primary systems*, minimal invasiveness, Swiss-region operation, run cost and support, vendor lock-in, GA maturity.
- **Key questions:** *"How does it integrate without accessing our primary systems? What sits on the data layer? Is everything GA — what is the Fabric IQ preview exposure? What is the run/support model?"*
- **Required knowledge sources:** ARCHITECTURE, INFRASTRUCTURE, integration and data-layer design, the GA-only and Swiss-region ADRs (ADR-0001, ADR-0003/0004, ADR-0014).
- **Expected response style:** precise, architecture-diagram-backed, ADR-cited; explicit GA-versus-preview status on every component.
- **Risk of inaccurate answers:** an inaccurate integration or GA claim leads to a failed PoC or an unsupported preview dependency reaching production; a wrong lock-in assessment misinforms platform strategy.

### CFO — Chief Financial Officer
- **Primary concerns:** total cost of ownership, cost drivers, per-provider cost, ROI timeline and payback, opex versus capex, sensitivity of Azure OpenAI and Fabric costs at scale.
- **Key questions:** *"What is the fully-loaded TCO? Cost per provider, and at N providers? Payback period? What drives cost and how sensitive is it to volume?"*
- **Required knowledge sources:** BVA (the ~CHF 760,000/yr Azure envelope; agent-platform additive ~CHF 260–410k/yr), TCO analyses, sizing assumptions (Fabric capacity, OpenAI TPM, Container Apps), tiered-SKU economics.
- **Expected response style:** numbers with **explicit ranges and stated assumptions**; always cite the basis; never a bare point estimate; defer where TCO artefacts are incomplete.
- **Risk of inaccurate answers:** the single most dangerous place to hallucinate — a fabricated or stale cost figure drives a wrong budget or pricing decision, and an unqualified point estimate manufactures false precision. The agent must present cost as ranges-with-assumptions and refuse to extrapolate beyond the artefacts.

### CTO — Chief Technology Officer
- **Primary concerns:** technical strategy, agent-architecture rationale, agent-versus-service discipline, GA constraints, extensibility and ontology, MLOps, model availability, the simulation engine.
- **Key questions:** *"Why eight agents, and which are genuinely agents versus deterministic services? What is the orchestration model? What gates Fabric IQ? Are the required models available in Switzerland? How does the simulation engine work?"*
- **Required knowledge sources:** AI and SD documents (agent design, Planner-Executor pattern), ADRs, the North Star ontology analysis, MLOps/OPERATIONS.
- **Expected response style:** deep technical, trade-off tables, ADR-referenced; clearly distinguishes **decided / proposed / to-validate.**
- **Risk of inaccurate answers:** a wrong architecture or decision claim causes rework or a misinformed build; presenting a "proposed" or "GA-gated" item as "shipped" breaks the GA-only critical-path constraint.

### CISO — Chief Information Security Officer
- **Primary concerns:** Zero Trust, data residency, PHI handling, secondary re-identification, provenance, human-in-the-loop, attack surface, secrets, incident response, policy-as-code.
- **Key questions:** *"Where does PHI live and can it ever leave Switzerland? Managed identity with no static secrets? Cross-border deny-by-default? Re-identification via quasi-identifiers? DSR and incident timing? Policy-as-code coverage?"*
- **Required knowledge sources:** SECURITY, COMPLIANCE, ADR-0003/0004, controls CH-C02/CH-C05, the CAF/WAF review, the external-signal provenance/trust-tier model.
- **Expected response style:** control-by-control, evidence-linked; states **aligned / partial / requires-validation** honestly; never asserts a control is *enforced* without linked evidence.
- **Risk of inaccurate answers:** a false "compliant / enforced" claim creates real regulatory and breach exposure; downplaying residency or re-identification risk is a safety and compliance failure.

### CDO — Chief Data Officer
- **Primary concerns:** data governance, metadata quality and completeness (the platform's acknowledged single-point-of-failure), stewardship and ownership, lineage, data contracts, classification, pseudonymisation, the ontology.
- **Key questions:** *"What is the metadata taxonomy and who owns it? What are the data contracts and quality gates? How are lineage and classification enforced? How do pseudonymisation and the KIS/planning split work? Who is the semantic owner?"*
- **Required knowledge sources:** DATA, the 2026-06-29 capacity-metadata framework, the DC-* contract family, North Star ontology governance (OBO principles, semantic owner, reference↔operational crosswalk), Purview lineage.
- **Expected response style:** governance-structured; ties every claim to a contract, steward, or control; explicitly surfaces the metadata-quality dependency.
- **Risk of inaccurate answers:** overstating data-governance maturity hides the metadata-quality single-point-of-failure and can rationalise wrong bed allocations downstream; a wrong stewardship or lineage claim misleads a data-governance audit.

### CLO — Chief Legal Officer
- **Primary concerns:** legal basis (federal versus cantonal), nDSG/KVG/EPDG applicability, Software-as-a-Medical-Device (Swissmedic) classification, data-processing agreements, third-party licensing (SNOMED CT, weather/hazard feeds), EU AI Act risk classification, liability for AI recommendations.
- **Key questions:** *"What is the legal basis per canton and is it validated? Is any agent SaMD? What is our AI-Act risk class? Are DPAs in place? Who is liable for an AI recommendation? Are external-signal licences production-cleared?"*
- **Required knowledge sources:** COMPLIANCE, the canton legal-applicability matrix (currently proposed/open), the SaMD analysis from the CTO-mentor review, the external-signal licence list, contracts/DPAs.
- **Expected response style:** precise; cite the specific instrument and its **status**; strictly separate "established" from "requires legal validation"; **never render a legal conclusion** — surface sourced facts and defer to counsel.
- **Risk of inaccurate answers:** a wrong legal assertion ("canton X is covered", "not SaMD", "AI-Act low-risk") creates direct regulatory and liability exposure. The agent must present legal material as **facts + explicit open questions**, never as advice.

**Cross-executive rule:** for the CFO, CISO, and CLO especially, the agent is configured to *prefer refusal-with-pointer over inference*. A "we don't have validated evidence for that yet — here is the open item" answer is always correct; a confident guess is a liability.

---

## 4. Core Use Cases

1. **Ask-the-product Q&A** — natural-language question → cited answer, role-aware in depth and tone.
2. **Compliance & security lookups** — "Is PHI ever processed outside Switzerland?" → control-by-control answer with CH-control and ADR citations and honest status.
3. **Architecture & integration queries** — "How does an agent get bed-state data?" → data-flow, contract, and pattern citations.
4. **Cost & value questions** — "What's the indicative TCO envelope?" → BVA-grounded ranges with assumptions; refusal to extrapolate beyond artefacts.
5. **Roadmap & backlog** — "When does the OR module land and what gates it?" → sprint/roadmap citations with decided/proposed status.
6. **Sales / pre-sales enablement** — "Give me a three-line differentiation vs VR&P" → grounded, non-technical narrative.
7. **Onboarding** — "I'm a new developer, walk me through the agent set" → guided, source-linked orientation.
8. **Executive briefing** — persona-tuned summaries (CEO/CFO/CISO/…) with one-click drill-down to evidence.
9. **Gap discovery** — "What's undocumented or unratified about the simulation engine?" → the agent enumerates open questions and "requires-validation" items.
10. **Documentation quality feedback loop** — logged unanswered/low-confidence questions become a documentation backlog.
11. **Live-proof validation** — the agent answers "what is *actually* running" by
    reading the deployed state read-only and reconciling it against the docs
    (detailed in Section 6.3). Representative questions, each resolving to a live,
    provenance-stamped read:
    - *"Show me what services and regions are currently deployed and their status."* → Azure Resource Graph over SIT/PROD (via `azure-mcp`, read-only), reconciled to `docs/region-availability.yaml`.
    - *"Show me the BOM of Azure services in the PROD resource group."* → live Resource Graph inventory cross-checked against `docs/bom.yaml` (SKU-drift precedent: `F64 → F2` corrected via `az resource show`, ADR-0037).
    - *"Show me the Fabric ontology model, top level."* → Fabric REST read of the `ont_hospital_capacity` top-level concepts.
    - *"Show me the Fabric data pipelines — event-based and process-based."* → Fabric REST listing of Eventstream lanes vs. Data pipeline items.
    - *"Show me the agents currently in Foundry and their status."* → Foundry Agent Service API (the 8 platform agents; portal *Running* state).
12. **Cost & TCO validation** — cost answers are grounded on a maintained data
    product, not a slide: *"What is our current run cost and how does it track BVA?"*
    → effective PROD Azure cost (Cost Management) + the GitHub Copilot token cost of
    building and maintaining the platform *with its agents*, reconciled to the
    BVA/TCO baseline with explicit ranges and as-of stamps (Section 6.4).

---

## 5. Functional Capabilities

- **Role-aware answering** — adjusts depth, vocabulary, and framing to the caller's persona/role (from their Entra identity or a selected "answer as" mode).
- **Grounded generation with mandatory citations** — no claim without a source; inline links to doc, section, ADR, or contract.
- **Confidence + status labelling** — every answer tagged (e.g. *Verified / Partial / Requires validation*), mirroring the review corpus's own status vocabulary.
- **Refusal-and-redirect** — when unsupported, the agent states the gap and points to the owner or backlog rather than inventing.
- **Multi-source synthesis** — combines architecture + compliance + cost sources into one coherent, still-cited answer.
- **Follow-up / conversational context** — retains thread context within a session (no cross-user memory of sensitive content by default).
- **Freshness awareness** — surfaces the version/commit and date of each cited source so users know how current an answer is.
- **Advisory-only guardrail** — the agent never takes an action (no writes, no external sends); it answers and, at most, drafts. This inherits the platform's HITL doctrine.
- **Feedback capture** — thumbs up/down + "this was wrong/outdated" routes to the documentation backlog.

---

## 6. Knowledge Grounding Strategy

## 6.1 Four knowledge-source classes on one layer

The Foundry IQ Knowledge Layer (Section 1.4) grounds the Product Owner domain
on **four** complementary source classes. The document corpus tells you what
the platform *says*; live-proof tells you what it *does*; the cost data product
tells you what it *costs*; and the ontology query surface lets you ask what the
*data itself* reports. An answer may synthesise all four — always cited,
always provenance- and freshness-stamped.

| Class | Source class | Nature | Answers questions like |
|---|---|---|---|
| **A** | Governed document corpus | Static, versioned, chunked + indexed | scope, architecture, compliance, roadmap |
| **B** | Live-proof validation | Dynamic, read-only queries at answer time | what is deployed, ontology/pipeline/agent state |
| **C** | Cost data product | Curated data product (BVA + effective cost) | run cost, TCO, budget variance vs BVA |
| **D** | Ontology query surface | Semantic NL-query over the data via the ontology | how many staffed beds, which gold table, concept lineage |

## 6.2 Class A — the governed document corpus (GitHub, daily-refreshed)

| Source class | Concrete artefacts | Primary consumers |
|---|---|---|
| Solution stack & architecture | ARCHITECTURE, SD, INFRASTRUCTURE, AI, ADRs | Architect, CTO, CIO |
| Requirements & backlog | PRD, sprint plans, roadmap, traceability matrix | PM, CEO, COO |
| Business value & cost | BVA, TCO analyses, tiered-SKU framework | CEO, CFO |
| Security & compliance | SECURITY, COMPLIANCE (CH-C01..C10), canton legal matrix | CISO, CLO |
| Data & semantics | DATA, capacity-metadata framework, DC-* contracts, North Star ontology | CDO, Architect |
| Operations & implementation | OPERATIONS, TEST, ALM_PLAN, runbooks | Customer Success, COO |
| Review evidence (interviews) | `docs/reviews/` AMA sessions — hospital-ops-lead, COO, CTO-mentor, CAF/WAF, SD, HCC North Star, capacity-metadata, trusted-external-signals, CSA-cantonal (the interview-derived corpus this proposal itself is grounded in) | All |
| GitHub repository | README, code docs, TechDocs, PR/ADR history | Developer, Architect |
| Prototype / UX | the Curavias clickable prototype | PM, Sales, Customer Success |

> **Interviews are first-order.** The `docs/reviews/` AMA sessions are not a
> footnote — they are the primary capture of stakeholder and expert
> **interviews** (hospital operations lead, COO, CTO mentor, CAF/WAF assessors,
> HCC North Star, capacity-metadata, …) and directly ground the executive
> personas in Section 3.2. They are ingested with the same daily refresh and
> provenance stamping as every other Class A artefact, and a persona answer that
> leans on an interview cites the exact review session and date.

**Daily refresh — reuse the master-data landing pattern.** The corpus is not
scraped ad hoc; it is landed on a schedule exactly as the platform already
lands master data (Sprint 23):

1. **GitHub → Azure Storage (daily).** A scheduled job snapshots the governed
   docs tree from GitHub into an ADLS Gen2 landing zone under the folder
   convention `landing/curavias-product-corpus/<source>/<yyyy-mm-dd>/` — the
   same `st…masterdata` account shape, managed-identity write, and
   diagnostic-to-Log-Analytics posture as the org/skills master-data landing.
2. **OneLake shortcut.** A OneLake shortcut exposes the landing container to
   Fabric so the corpus sits beside the platform's other data products (no
   copy, no second source of truth).
3. **Chunk + tag → knowledge source.** A Fabric/notebook step chunks on
   heading/ADR/contract boundaries, applies the governance tags
   (classification, residency, status, version/commit, date), gates out any
   PHI-classified content, and publishes to the Foundry IQ knowledge source.
4. **Provenance-complete + dated.** Every chunk carries its landing date and
   source commit so the UX can show "as-of" and flag staleness.

This makes freshness a *scheduled guarantee* (daily) rather than a hope, and
reuses infrastructure and runbooks the platform already operates.

## 6.3 Class B — live-proof validation (the deployed state as a source)

Documents describe intent; **live-proof** grounds answers on the *actual*
deployed state via read-only probes, so "what is running" is never a stale
claim. This is the same tiered-liveness pattern the Curavias app already uses
for its Evidence view (Azure Resource Graph + GitHub API + Fabric/Foundry
pings), promoted here to a knowledge source.

| Live-proof question | Read-only source | Reconciled against |
|---|---|---|
| Deployed services + regions + status | Azure Resource Graph via `azure-mcp` (read) | `docs/region-availability.yaml` |
| BOM of Azure services in PROD RG | Resource Graph inventory of the PROD resource group | `docs/bom.yaml` |
| Fabric ontology model, top level | Fabric REST — `ont_hospital_capacity` concepts | ontology docs / crosswalk |
| Fabric data pipelines (event- vs process-based) | Fabric REST — Eventstream lanes vs Data pipeline items | `docs/ARCHITECTURE.md` |
| Foundry agents + status | Foundry Agent Service API (8 agents, Running) | `AGENTS.md` §1 registry |

- **Read-only, no mutation.** Live-proof strictly inherits a `read` ceiling —
  it lists, gets, and queries; it never provisions, changes, or deletes.
- **Reconcile-and-flag.** When live state diverges from the documented
  baseline (e.g. a SKU or region drift), the agent reports **both**, flags the
  divergence, and points to the owning doc/ADR — turning drift into a visible,
  actionable fact rather than hiding it.
- **Graceful degradation.** If a live read fails, the agent falls back to the
  committed baseline flagged `snapshot` (never blanks the answer) and says so.

## 6.4 Class C — the BVA / TCO cost data product

Cost is the highest-stakes place to guess (CFO risk R1). So cost answers are
grounded on a **maintained data product**, not on prose. It fuses the existing
BVA model with two effective-cost feeds:

| Cost feed | Source | Grounds |
|---|---|---|
| Effective PROD Azure cost | Azure Cost Management for the PROD subscription/RG (via `azure-mcp`, read) | actual run-rate, budget variance vs the BVA ~CHF 760k/yr Azure envelope |
| Build & maintain cost | GitHub Copilot token/usage cost consumed building and running the platform *with its agents* | the "cost to build/operate with agents" the BVA one-time + run lines currently estimate |
| BVA baseline + KPI catalogue | `docs/BVA.md`, ADR-0025 KPI catalogue (`bva_kpi.py` ↔ `bva_measures.tmdl`) | the ROM baseline, ranges, and sensitivity the effective cost is compared to |

- **Ranges with assumptions, never bare point estimates.** The agent presents
  effective cost against the BVA ROM band (±30%) with the as-of date of each
  feed, and refuses to extrapolate beyond the maintained product.
- **Closes the CFO gap by construction.** Wiring a live cost feed to the BVA
  baseline is what downgrades Gap G5 and risk R1 from "prose can be stale" to
  "answer is reconciled to actuals".

## 6.5 Class D — the ontology as a query surface (query the data itself)

Classes A–C answer from documents, deployed-state metadata, and cost. **Class D
lets the agent query the *data itself*** — semantically — through the platform's
own **North Star ontology / Fabric Data Agent** (`da_hospital_capacity`), the
read-only ontology + semantic-model query surface the platform already publishes
(ADR-0033, ADR-0034). Instead of hard-coding table names, a question like *"how
many staffed ICU beds does the ontology model report, and which gold table backs
it?"* resolves against ontology concepts and their bindings.

| Aspect | Detail |
|---|---|
| Surface | `da_hospital_capacity` Fabric Data Agent over the MVO ontology + capacity semantic model (read-only) |
| What it grounds | data questions across the underlying gold data products, expressed in ontology concepts (Facility → Ward → Bed → Encounter, OR slot, capacity units) |
| Ceiling | `read` — natural-language-to-query over governed synthetic data; no writes, no PHI (ADR-0016) |
| Reuse | the exact grounding tool the Foundry `ooa-agent` already consumes (`fabric-data-agent`), not a new capability |

- **Concept-level, not string-level.** Answers cite the ontology concept and the
  gold binding, so a data answer is traceable to a defined entity — the same
  explainability discipline as the clinical copilots.
- **GA-gated for production, demo-live now.** Operational ontology grounding
  inherits the Fabric IQ Switzerland-region GA gate (ADR-0014); the
  `da_hospital_capacity` demo artefact (westus2, synthetic) makes Class D
  demonstrable today (ADR-0034) while production Swiss grounding waits on GA.

## 6.6 Grounding principles

- **Single source of truth = the governed repository.** The agent grounds only on ingested, versioned artefacts — never on the open web or model pre-training for product facts.
- **Classification-aware ingestion.** Each artefact carries the platform's governance tags (classification, residency, legal basis). PHI-classified content is excluded from the PO Agent's index entirely — the corpus is documentation, not patient data.
- **Status-preserving.** Ingestion preserves each item's decided/proposed/requires-validation status so the agent can echo it.
- **Provenance-complete.** Every chunk retains source path, section anchor, version/commit, and date.

> **Assumption A3 — corpus access.** Direct ingestion assumes the PO Agent is granted read access to the GitHub repository and the docs tree. The clickable prototype (a local file at build time) and the live repository state were **not** directly inspected for this proposal; grounding here derives from the AMA review corpus, which extensively cites those repository documents. Confirm ingestion connectors and access scopes before build (Section 13, Gap G1).

---

## 7. Retrieval and Citation Strategy

## 7.1 Retrieval

- **Hybrid retrieval** — vector (semantic) + keyword/BM25 over chunked, metadata-tagged artefacts, so both "explain the discharge flow" and exact-term queries ("CH-C05", "DC-AI-FORECAST-v1") resolve.
- **Metadata filtering** — retrieval respects source class, status, and the caller's role/authorisation (e.g. a Partner does not retrieve internal-only cost detail).
- **Structure-aware chunking** — chunk on headings/ADR/contract boundaries so a citation points to a meaningful unit, not a mid-sentence fragment.
- **Re-ranking** — a re-rank pass promotes the most authoritative, most recent source when several match.
- **Class routing (A/B/C/D).** The orchestrator decides whether a question needs the document corpus (A), a live-proof read (B), the cost data product (C), an ontology data query (D), or a synthesis. Live-proof, cost, and ontology queries are resolved as **typed, read-only tool calls at answer time**, then cited exactly like a document chunk (source + as-of + live/snapshot badge; Class D also cites the ontology concept + gold binding).

## 7.2 Citation

- **Every substantive claim carries an inline citation** to the exact artefact + section/anchor + version. This mirrors the platform's own explainability agent (EAA) discipline: what was said, why, from which source, and when.
- **No-source → no-claim.** If retrieval returns nothing above a confidence threshold, the agent returns "not documented / requires validation" plus the nearest related material and the likely owner.
- **Grounded-answer contract.** A response is only emitted if ≥ N supporting chunks clear the relevance threshold; otherwise it degrades to a transparent partial answer. (Threshold tuned in MVP.)
- **Answer-as-evidence.** Each answer (question, retrieved sources, citations, confidence, timestamp, caller role) is logged as an audit artefact — reusing the platform's evidence model, so PO-Agent answers are themselves traceable.

---

## 8. Backstage User Experience Design

The PO Agent is embedded **in the Curavias App** as a per-role **Copilot rail**
on the **START** and **BACKSTAGE** surfaces — the *same* pattern the MAIN boards
(OOA / BMCA / DCA / ORSA / SBA / CSA) already ship, so it feels native, not
bolted-on:

- **Same rail as the MAIN agents.** A docked, full-height right rail
  (`AgentPlane.tsx` → `useAgentInvoker('product-owner')` + `ConversationView`;
  48px icon rail ↔ 360px panel) rendered on START and BACKSTAGE. It is never an
  overlay and never empty.
- **Proactive default state.** On load the rail opens on a role-tuned "here's
  what's current" read (e.g. on BACKSTAGE: "3 services drifted from the BOM —
  ask me why"), mirroring the MAIN boards' proactive first card.
- **Insight-driven questions.** Clicking a card on START (a role launcher, a KPI
  tile) or BACKSTAGE (an evidence card, an RBAC row) routes a pre-formed
  question into the rail — the same left-plane → recommendation flow the MAIN
  boards use.
- **Entry point:** the Copilot rail plus an ambient "Ask the Product Owner"
  box on the START executive overview and the BACKSTAGE Nachweise / Evidence tab.
- **Answer card:** the response renders as a card with (a) the answer, (b) a **status chip** (Verified / Partial / Requires validation), (c) a **confidence indicator**, and (d) a **Sources** list of clickable citations that deep-link into TechDocs / the repo.
- **Persona toggle:** an optional "Answer as: Developer / Architect / Sales / Executive" selector that reshapes depth and tone; defaults to the role inferred from the signed-in identity.
- **Executive mode:** a compact, board-ready layout — headline answer, three supporting bullets, and a single "show evidence" expander.
- **Drill-down:** every citation is a link; TechDocs pages open in-portal, ADRs/contracts open at the anchor.
- **Feedback affordance:** thumbs + "flag as outdated/incorrect," which files a documentation-backlog item.
- **Transparency banner:** a persistent, unobtrusive "AI-generated · advisory only · verify before acting" label — satisfying the platform's "AI recommendations must remain recognisable as such" rule.
- **Accessibility & language:** the corpus is mixed German/English; the UX supports asking in either and shows the source language of each citation.

> **Assumption A4 — auth handoff.** The Curavias App already authenticates users via Entra ID; the Copilot rail reuses that identity for role-aware answering and authorisation — exactly as the MAIN-board agent rails do. A Spotify Backstage plugin, if later added as an extra surface, would reuse the same identity handoff.

---

## 9. Security and Governance Considerations

- **No PHI in scope.** The PO Agent indexes documentation only; PHI-classified content is excluded at ingestion. This keeps the agent firmly in the platform's "non-PHI, light-residency" class.
- **Swiss-region inference.** Generation runs on Azure OpenAI in Switzerland North, honouring ADR-0003/0004; no global/data-zone routing — even though the content is non-PHI, this preserves one consistent sovereign posture.
- **Zero Trust & identity.** Entra ID auth; managed identity for all service-to-service calls; no static secrets (Key Vault); least-privilege access to the index.
- **Authorisation-aware retrieval.** Answers are filtered by the caller's entitlement — internal-only cost/security detail is not exposed to Partners or unauthenticated users.
- **Full audit trail.** Every question, retrieval set, citation, confidence, and caller identity is logged (reusing the EAA/audit-store pattern), giving a complete "who asked what, answered from where" record.
- **Policy-as-code alignment.** Ingestion, residency, and deployment-type restrictions are expressed as Azure Policy / CI checks, consistent with the platform's governance-first, Git-first model.
- **Prompt-injection defence.** Retrieved content and any external input are treated as untrusted; the agent will not follow instructions embedded in documents, and outputs are constrained to answering, never acting.
- **Change control.** The agent's system prompt, retrieval config, and allow-listed sources are versioned in Git under CODEOWNERS review — the agent's behaviour is itself governed like any other platform component.

---

## 10. Responsible AI Considerations

- **Advisory-only, human-in-the-loop.** The agent informs; humans decide and act. It never triggers a workflow, sends a message, or modifies a system.
- **Grounded, not generative-from-memory.** Product facts come only from the corpus; the model's parametric knowledge is used for language, not for claims.
- **Transparency.** Answers are labelled AI-generated and carry confidence + status; citations make every claim checkable.
- **Honesty about uncertainty.** "Requires validation / not documented" is a first-class answer, especially for CFO/CISO/CLO questions.
- **Fairness & scope.** The agent answers product questions; it declines to evaluate individuals' performance or to make legal, clinical, or investment decisions — it surfaces sourced facts and defers.
- **No legal/clinical advice.** For CLO-class questions it returns facts + open items and an explicit "consult counsel" boundary; it never asserts a legal or medical conclusion.
- **Explainability by construction.** The same evidence-bundle pattern the platform uses for its clinical agents is reused, so a reviewer can reconstruct any answer.
- **Bias & drift monitoring.** Low-confidence and flagged answers are reviewed; the corpus and retrieval config are refreshed as the product evolves.

---

## 11. High-Level Architecture

## 11.1 The knowledge layer (foundation)

```text
Foundry IQ Knowledge Layer (shared, multi-domain)  -  Product Owner = domain #1

  Class A  Governed document corpus     GitHub --daily--> ADLS Gen2 landing
           (PRD/SD/ARCH/AI/SEC/DATA...)   --> OneLake shortcut --> chunk + tag
                                          --> Foundry IQ knowledge source
  Class B  Live-proof (read-only)        Azure Resource Graph | Fabric REST |
           (the deployed state)           Foundry Agent API  (answer-time reads)
  Class C  Cost data product             effective PROD Azure cost + Copilot
           (BVA / TCO)                     token cost  -->  reconciled to BVA
  Class D  Ontology query surface        da_hospital_capacity Fabric Data Agent
           (semantic data access)         --> query gold via ontology concepts

  (the same layer later serves Compliance / Data / Operations domains)
```

The **runtime view** below shows how a single query flows through this layer.
Its *Knowledge Plane* box is exactly this Foundry IQ Knowledge Layer; **Class B
live-proof, Class C cost, and Class D ontology queries resolve as read-only tool
calls at answer time**, then are cited like any document chunk. In that runtime
box, *EXPERIENCE* is the Curavias App Copilot rail on START / BACKSTAGE (the
MAIN-board rail pattern), not a standalone plugin.

```text
 ┌─────────────────────────────────────────────────────────────────────┐
 │ EXPERIENCE — Backstage plugin (React) + "Ask the Product Owner"      │
 │ Entra-auth, role-aware, answer card w/ status·confidence·citations   │
 └───────────────────────────────┬─────────────────────────────────────┘
                                 │ HTTPS / REST
 ┌───────────────────────────────▼─────────────────────────────────────┐
 │ PO AGENT RUNTIME (Azure Container Apps, Switzerland North)           │
 │  • Orchestrator (query → retrieve → ground → answer → cite)          │
 │  • Guardrails: authz filter, advisory-only, injection defence        │
 │  • Grounded-answer contract + confidence/status labelling            │
 └───────────┬───────────────────────────────────┬─────────────────────┘
             │                                   │
   ┌─────────▼──────────┐            ┌───────────▼───────────────────────┐
   │ RETRIEVAL          │            │ GENERATION                        │
   │ Hybrid index       │            │ Azure OpenAI (Switzerland North,  │
   │ (vector + keyword) │            │ Standard/Regional Provisioned)    │
   │ metadata-filtered  │            │ grounded, advisory-only prompt    │
   └─────────┬──────────┘            └───────────────────────────────────┘
             │
   ┌─────────▼──────────────────────────────────────────────────────────┐
   │ KNOWLEDGE PLANE — governed corpus                                   │
   │  Ingestion pipeline (GitHub Actions / Fabric) → chunk + tag         │
   │  (classification, residency, status, version) → index               │
   │  Sources: repo docs, ADRs, DC-* contracts, BVA/TCO, reviews,        │
   │  roadmap, TechDocs, prototype notes  (PHI excluded)                 │
   └─────────┬──────────────────────────────────────────────────────────┘
             │
   ┌─────────▼──────────────────────────────────────────────────────────┐
   │ GOVERNANCE & OPS (cross-cutting)                                    │
   │  Entra ID + Managed Identity + Key Vault · Azure Policy             │
   │  Purview lineage · Audit store (question→sources→answer)            │
   │  Monitor / Log Analytics / App Insights                            │
   └─────────────────────────────────────────────────────────────────────┘
```

The design deliberately **extends the existing Curavias platform pattern rather than introducing a parallel one**: same runtime (Container Apps), same region posture, same identity model, same audit/evidence discipline, same advisory-only guardrail. This keeps the PO Agent inside the platform's proven governance envelope. Crucially, the Knowledge Plane is the **shared Foundry IQ Knowledge Layer** with its three source classes (§6) — so standing up the PO Agent also stands up the reusable foundation for every later agent-role domain.

---

## 12. Recommended Technology Components

| Layer | Recommended (GA-first) | Notes / status |
|---|---|---|
| Experience | Curavias App Copilot rail (React / Fluent v9) on START + BACKSTAGE | Same per-role rail pattern as the MAIN boards (`AgentPlane` / `useAgentInvoker`); A1 |
| Agent runtime | Azure Container Apps, Switzerland North | Mirrors platform agent hosting |
| Generation | Azure OpenAI (Switzerland North, Standard/Regional Provisioned) | Honours ADR-0003/0004; confirm model availability (Gap G2) |
| Knowledge layer | **Foundry IQ Knowledge Layer** — knowledge sources over Azure AI Search (hybrid vector+keyword) + OneLake | Shared, multi-domain foundation; PO Agent = domain #1 (A5, A7) |
| Corpus refresh | Daily GitHub → ADLS Gen2 landing → OneLake shortcut → chunk/tag → knowledge source | Reuses the Sprint 23 master-data landing pattern; managed-identity write, scheduled |
| Live-proof (Class B) | Azure Resource Graph via `azure-mcp` (read), Fabric REST, Foundry Agent Service API | Read-only answer-time reads; reconciled to `bom.yaml` / `region-availability.yaml` / `AGENTS.md` |
| Cost data product (Class C) | Azure Cost Management (PROD, via `azure-mcp`) + GitHub Copilot token cost + BVA model (ADR-0025) | Grounds cost/TCO answers on actuals + ROM baseline |
| Ontology query (Class D) | North Star ontology / `da_hospital_capacity` Fabric Data Agent (read-only) | Semantic NL-query over gold; GA-gated (ADR-0014), demo-live (ADR-0033 / ADR-0034) |
| Identity | Entra ID + Managed Identity + PIM | No static secrets |
| Secrets | Azure Key Vault | Secretless runtime |
| Lineage/catalog | Microsoft Purview | Reuses platform lineage |
| Audit store | Cosmos DB / Azure SQL | Reuses EAA-style evidence model |
| Observability | Azure Monitor + Log Analytics + App Insights | Confidence/latency/citation-coverage metrics |
| Policy | Azure Policy + CI conformance checks | Residency + deployment-type enforcement |

> **Assumption A5 — knowledge foundation.** The retrieval foundation is the **Foundry IQ Knowledge Layer** (knowledge sources composing Azure AI Search + OneLake underneath), chosen so the investment is a *shared, multi-domain* asset (Section 1.4) rather than a bespoke single-purpose index. Azure AI Search remains the GA hybrid-retrieval engine beneath it. **Operational ontology grounding** (Class A/B against the North Star ontology) still inherits the **Fabric IQ Switzerland-region GA gate (ADR-0014)** and stays off the MVP critical path until GA-validated; MVP grounding uses the document corpus + live-proof + cost product, none of which require Fabric IQ ontology GA.
>
> **Assumption A7 — Foundry IQ availability.** Foundry IQ Knowledge (Azure AI Foundry knowledge sources / agentic retrieval) must be confirmed available and GA-eligible in (or compliant-routing to) Switzerland North for the target subscription before it sits on the MVP critical path. Until confirmed, the MVP can run on Azure AI Search directly and be lifted onto the Foundry IQ layer once availability is verified (Gap G11).

---

## 13. Risks and Mitigation Strategies

| # | Risk | Impact | Mitigation |
|---|---|---|---|
| R1 | **Hallucinated answer** to a high-stakes (CFO/CISO/CLO) question | Financial / regulatory / legal harm | Grounded-answer contract; no-source→no-claim; confidence threshold; refusal-and-redirect; audit log. **Cost answers additionally grounded on the Class C data product (§6.4)** — reconciled to actuals, ranges-with-assumptions only |
| R2 | **Stale corpus** — answer cites out-of-date doc | Wrong decisions, lost trust | Freshness stamps on every citation; scheduled re-ingestion on commit; "as-of" shown in UX |
| R3 | **Over-permissioned retrieval** exposes internal cost/security detail to Partners | Confidentiality breach | Authorisation-aware retrieval; role-scoped indexes; entitlement tests in CI |
| R4 | **Prompt injection** via a poisoned document | Guardrail bypass | Treat retrieved content as untrusted; instruction-stripping; advisory-only (no action surface) |
| R5 | **Fabric IQ / model preview dependency** reaches production | Delivery + compliance risk | GA-only critical path (ADR-0001); gate operational ontology grounding on GA (ADR-0014) |
| R6 | **PHI leakage** into the index | Severe compliance breach | Exclude PHI-classified content at ingestion; classification gate in pipeline; residency policy |
| R7 | **Legal over-reach** — agent gives a legal/clinical conclusion | Liability | Hard boundary: facts + open items + "consult counsel"; CLO-mode guardrail |
| R8 | **Adoption failure** — users revert to asking people | Value not realised | Backstage-native placement; measurably faster than a doc hunt; feedback loop; exec-mode value |
| R9 | **Documentation gaps** produce many "not documented" answers | Perceived low value | "Gap radar" turns gaps into a backlog; report coverage; prioritise high-traffic gaps |
| R10 | **Answer inconsistency** across sessions/personas | Erodes "authoritative source" claim | Deterministic retrieval + low-temperature generation; golden-question regression tests |
| R11 | **Live-proof read failure or over-scope** — a Class B probe errors, or reads more than intended | Wrong "what's deployed" answer; excess access | Strict `read` ceiling + least-privilege scopes; graceful degradation to `snapshot` baseline; never mutate |
| R12 | **Cross-domain leakage** on the shared layer — one domain's restricted content surfaces to another | Confidentiality breach | Per-domain knowledge sources + authorisation-aware retrieval scoped by domain + caller entitlement; entitlement tests in CI |
| R13 | **Stale cost feed** — effective Azure/Copilot cost lags reality | Misleading TCO answer | As-of stamp on every cost feed; daily/near-real-time refresh; present against BVA ROM band, refuse extrapolation |

---

## 14. Success Metrics and KPIs

### Adoption & usage
- Weekly active users by persona; questions/user; share of product questions answered by the agent versus routed to a human.

### Answer quality
- **Citation coverage** (% of claims with a valid source) — target ≥ 95%.
- **Grounded-refusal rate** — % of unanswerable questions correctly refused rather than guessed (higher is safer).
- Human-rated answer accuracy on a golden-question set, by persona; thumbs-up rate.
- Hallucination incidents (target: zero for CFO/CISO/CLO classes).

### Efficiency
- Time-to-answer versus baseline document hunt; Pre-Sales/Partner self-serve rate; onboarding ramp-time reduction.

### Governance
- % answers with complete audit record (target 100%); authorisation-violation incidents (target zero).

### Documentation health ("gap radar")
- Number and resolution rate of documentation gaps surfaced; corpus freshness (median age of cited sources).

### Live-proof & cost fidelity
- Corpus refresh freshness — % of days the GitHub → ADLS daily landing ran successfully (target ≥ 99%); median corpus age (target ≤ 24h).
- Live-proof success rate — % of Class B questions answered from a live read vs degraded to `snapshot`; drift items surfaced and resolved.
- Cost-answer fidelity — variance between the agent's stated run-rate and effective PROD Azure + Copilot cost (target within the BVA ±30% band, with as-of stamp).

> **Assumption A6 — baselines.** Efficiency and ROI KPIs require a **T0 baseline** (mirroring the platform's own potential-analysis discipline). Capturing that baseline is an explicit MVP activity; targets above are directional until baselined.

---

## 15. MVP Scope and Future Roadmap

## 15.1 MVP (first slice)

- **Foundation:** the **Foundry IQ Knowledge Layer** stood up as a shared,
  multi-domain surface with the **Product Owner as domain #1** (Section 1.4).
- **Class A corpus:** repo docs (PRD, SD, ARCHITECTURE, AI, COMPLIANCE,
  SECURITY, DATA, BVA, ADRs, reviews) landed via the **daily GitHub → ADLS →
  OneLake refresh** (master-data pattern), PHI excluded.
- **Class B live-proof (read-only):** the five reference questions of Section 6.3
  — deployed services/regions/status, PROD-RG BOM, Fabric ontology top level,
  Fabric pipelines (event/process), Foundry agents + status.
- **Class C cost product:** effective PROD Azure cost + GitHub Copilot token cost
  reconciled to the BVA/TCO baseline (Section 6.4).
- **Class D ontology query (demo-live):** semantic data questions via
  `da_hospital_capacity` (Section 6.5); production Swiss grounding stays
  GA-gated (ADR-0014).
- **Capabilities:** grounded Q&A with mandatory citations, status + confidence
  labelling, refusal-and-redirect, audit logging.
- **Personas:** Developer, Architect, PM internally + a single **Executive mode**;
  role-aware depth.
- **Surface:** Curavias App Copilot rail on **START** + **BACKSTAGE** (MAIN-board
  rail pattern), Entra-authenticated.
- **Runtime/region:** Container Apps + Azure OpenAI in Switzerland North; Foundry
  IQ Knowledge Layer (Azure AI Search + OneLake) beneath.
- **Governance:** authorisation-aware, per-domain retrieval; full audit trail;
  golden-question regression tests; "AI-generated · advisory" banner.

## 15.2 Roadmap (post-MVP)

1. **Full persona tuning** — dedicated CEO/COO/CIO/CFO/CTO/CISO/CDO/CLO answer modes with the per-persona guardrails in Section 3.2.
2. **Partner/external tier** — a hardened, entitlement-scoped surface for co-sell partners.
3. **Live freshness** — commit-triggered re-ingestion and "answer changed since you last asked" notifications.
4. **Ontology grounding** — once Fabric IQ reaches Switzerland-region GA (ADR-0014), promote **Class D** from the westus2 demo artefact to production Swiss grounding, and add the North Star ontology as a Class A source for concept-level consistency and lineage (Class B already reads the ontology *top level* live in MVP; this deepens it to full concept-and-data grounding).
5. **Proactive briefings** — scheduled, persona-tuned "what changed this sprint" digests (advisory, opt-in).
6. **Additional knowledge domains** — mount further domains on the same layer for other agent roles (Compliance for `compliance-agent`, Data for `data-quality-agent`, Operations for the runtime copilots), each an additively-registered knowledge source under CODEOWNERS review.
7. **Deeper cost modelling** — extend the Class C data product from run-rate + Copilot token cost to per-provider / per-tier TCO and forecast, wired to maintained models.
8. **Multilingual parity** — first-class German/English answering with source-language transparency.

---

## 16. Assumptions and Gaps that Block Production

## 16.1 Assumptions (stated, not invented)

- **A1** — "Backstage" = the **Curavias App BACKSTAGE surface** (+ START); the PO Agent ships as an in-app Copilot rail using the MAIN-board pattern (a Spotify Backstage plugin is an optional extra surface).
- **A2** — No quantified CHF ROI is asserted; it requires baseline capture.
- **A3** — Grounding derives from the AMA review corpus that cites the repo docs; the live repo and the clickable prototype were not directly inspected.
- **A4** — Backstage/Entra provides the identity used for role-aware answering.
- **A5** — The foundation is the shared, multi-domain **Foundry IQ Knowledge Layer** (Azure AI Search + OneLake beneath); operational ontology grounding stays GA-gated (ADR-0014) and off the MVP critical path.
- **A6** — Efficiency/ROI KPIs are directional until a T0 baseline exists.
- **A7** — Foundry IQ Knowledge availability/GA in (or compliant-routing to) Switzerland North must be confirmed; MVP can run on Azure AI Search directly and be lifted onto the layer once verified (G11).

## 16.2 Gaps that must close before production

| Gap | Why it blocks production |
|---|---|
| **G1 — Corpus access & daily-refresh pipeline** | Read access to the GitHub repo and docs tree, **plus the scheduled GitHub → ADLS Gen2 landing + OneLake shortcut + chunk/tag pipeline** (master-data pattern), must be provisioned and access-scoped. Without it there is no grounding. |
| **G2 — Model availability in Switzerland North** | The required Azure OpenAI model(s) must be confirmed available in the Swiss region (the platform's own open item); otherwise generation cannot honour residency. |
| **G3 — Authorisation model** | The entitlement mapping (who may see cost/security/internal detail) must be defined and enforced before any Partner/external exposure. |
| **G4 — PHI-exclusion gate** | An automated classification gate proving no PHI-classified content enters the index is mandatory before go-live. |
| **G5 — Cost data product wiring** | Largely addressed by Class C (§6.4): CFO-grade answers require the effective PROD Azure cost feed + GitHub Copilot token cost wired to the BVA/TCO baseline. The *feeds and reconciliation* must be built and access-scoped; until then cost answers stay ROM-band-only. |
| **G6 — Canton legal-applicability matrix** | CLO/CISO answers about legal basis remain "requires validation" until the canton-by-canton matrix (an open platform item) is completed. |
| **G7 — Golden-question & evaluation harness** | A per-persona evaluation set (accuracy, citation coverage, refusal correctness) must exist before trusting the agent as the "authoritative source." |
| **G8 — Prototype & live-repo verification** | The clickable prototype and current repo state must be directly ingested and verified, not inferred from the review corpus. |
| **G9 — Live-proof read scopes** | Class B needs least-privilege, read-only scopes for Azure Resource Graph (`azure-mcp`), Fabric REST, and the Foundry Agent API, granted and audited before live-proof answers are trusted. |
| **G10 — Copilot token-cost telemetry** | The GitHub Copilot token/usage cost signal for building and maintaining the platform must be exportable and access-scoped for the Class C feed; confirm the available granularity (per-agent / per-period) before promising it in cost answers. |
| **G11 — Foundry IQ availability in Switzerland North** | Foundry IQ Knowledge must be confirmed available/GA-eligible (or compliant-routing) in the Swiss region for the target subscription; otherwise the MVP runs on Azure AI Search directly until the lift (A7). |
| **G12 — Ontology query surface (Class D) GA** | Production Swiss ontology-data grounding is GA-gated (ADR-0014); MVP relies on the westus2 `da_hospital_capacity` demo artefact (ADR-0034). Class D data answers are therefore demo-scoped until Fabric IQ reaches Swiss GA. |
| **G13 — Curavias App integration slot** | The START / BACKSTAGE Copilot rail must be wired to `useAgentInvoker('product-owner')` + `AgentPlane`, reusing the MAIN-board rail; this needs an app-team integration slot and a registered `product-owner` agent id. |

**Production-readiness verdict:** the design sits squarely inside the platform's proven governance envelope and is low-risk architecturally, but **production deployment is blocked until G1–G4, G7, G9, and G13 are closed**; CFO/CLO/CISO answer quality remains capped until G5–G6 close (G5 now largely a wiring task via the Class C cost product), and Class D ontology-data answers stay demo-scoped until G12 closes. The honest MVP posture is: ship for internal, authenticated technical users first — as a Curavias App Copilot rail on START / BACKSTAGE, on the shared Foundry IQ Knowledge Layer with the daily corpus refresh (interviews included), read-only live-proof, the cost data product, and demo-live ontology query; gate executive-facing and partner-facing modes behind the closure of the corresponding gaps.
