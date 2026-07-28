# ADR-0056: BVA Agent — deterministic ROI/TCO computation as a typed tool, cost data product via the master-data pattern, peer to PO under the App orchestrator

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg |
| **Decision-makers** | @urruegg |
| **Related** | [Sprint 33 BVA Agent design](../superpowers/specs/2026-07-28-sprint-33-curavias-bva-agent-design.md), [Sprint 33 WS-G0 contracts](../superpowers/specs/2026-07-28-sprint-33-bva-agent-contracts.md), [Sprint 33 WS-B plan](../superpowers/plans/2026-07-28-sprint-33-bva-agent-ws-b-engine.md), [ADR-0008](0008-agent-runtime-pattern-scope-and-selection.md) (runtime), [ADR-0013](0013-temporary-us-region-demo-scope.md) (US demo scope), [ADR-0016](0016-no-phi-in-mvp-demo-scope.md) (no PHI), [ADR-0025](0025-bva-kpi-catalog.md) (BVA KPI catalog), [ADR-0043](0043-product-owner-agent-foundry-iq-domain.md) (PO Agent Foundry IQ domain), [ADR-0053](0053-dqa-trust-score-model.md) (deterministic-not-LLM precedent), [issue #489](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/489), [#501](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/501) |

## Context

Sprint 33 adds a **Business Value Assessment (BVA) Agent**: an advisory-only
copilot that answers ROI, TCO, payback, and onboarding-value questions for the
Curavias platform, and captures the resulting **Opportunity** for the pipeline
view. Two design tensions had to be settled once, up front, because multiple
downstream artefacts (the calc engine, the agent pack, the Cosmos store, the
gold projection, the orchestrator fan-out) depend on them:

1. **Where does the arithmetic live?** ROI/TCO figures used in a customer-facing
   value conversation must be reproducible, auditable, and defensible. An LLM
   that "estimates" a payback period is neither reproducible nor citable.
2. **How does BVA relate to the Product Owner (PO) Agent?** An onboarding
   question ("should we onboard Hospital X?") is simultaneously a numbers
   question (ROI/TCO) and a judgement question (go/no-go). Both must be answered
   coherently without one agent silently overriding the other.

The demo remains a westus2, synthetic-data showcase with no PHI
([ADR-0013](0013-temporary-us-region-demo-scope.md),
[ADR-0016](0016-no-phi-in-mvp-demo-scope.md)); demo figures are labelled
proof-of-technology.

## Decision

1. **Deterministic computation posture — no LLM arithmetic (D6).** All BVA
   arithmetic is performed by a **deterministic Python calc engine** exposed as a
   single typed tool, `bva.simulate(baseline, delta) -> BvaSimulationResult`
   (`data-platform/bva/`). The engine is a pure function of its inputs: it uses a
   fixed `asOf`, never `datetime.now()`, and never delegates math to the model.
   The LLM only slot-fills inputs, selects the tool, and renders the tool's
   output; it emits no computed figure of its own. This mirrors the
   deterministic-not-LLM precedent set for the DQA Trust Score
   ([ADR-0053](0053-dqa-trust-score-model.md)).

2. **Every figure is a cited Class-C `GroundedChunk` (D3 deepening).** Each
   number the agent surfaces carries a `citation.sourceRef` back to a gold
   measure, a `bva.simulate` metric, or an input slot, plus snapshot date and
   currency. Figures the model cannot cite are refused, not guessed. The frozen
   shape is the Sprint 28 `GroundedChunk`, reused verbatim so the PO ↔ BVA
   hand-off composes cleanly.

3. **Cost data product via the master-data pattern (D7).** The cost basis is
   built with the existing **master-data-via-file** pattern end to end: git CSVs
   → CI gate → medallion → Direct Lake `sm_bva` semantic model → ontology +
   Fabric IQ Data Agent grounding. Team cost = Copilot AIU/token spend plus human
   elective hours × a configured role rate; everything is **standardized in CHF**
   with an explicit FX line for USD Azure/BOM actuals (D2).

4. **Opportunity persistence in Cosmos, projected to gold (D4).** The **Cosmos DB**
   operational store (reusing `cosmos-mcp`) is the **system-of-record** for an
   Opportunity; a one-way, `asOf`-timestamped projection into a gold
   `bva_opportunity` table serves analytics/reporting. Cosmos is authoritative
   for the app; gold is analytics-only.

5. **Peer-to-PO topology under the App orchestrator (D3).** The Curavias App
   copilot is the **orchestrator**; PO and BVA are **peer** typed sub-agents. For
   an onboarding question the orchestrator invokes **both**: **BVA owns the
   numbers**, **PO owns the go/no-go (or conditional) verdict** informed by those
   numbers. Neither agent issues the other's answer.

6. **Advisory-only, human-gated lifecycle.** BVA has side-effect ceiling `write`:
   GitHub comments/PRs and Cosmos Opportunity upserts only. Cloud access is
   read-only (Fabric `query`); there is **no deploy/delete tool and no
   `approved-to-apply` gate on BVA itself**. Advancing an Opportunity past
   `qualified` (`onboarding`/`won`/`lost`) is **human-only**, and any downstream
   apply, spend, budget, or resource change is routed to a human-owned process or
   UC1 issue.

## Consequences

- **Positive.** ROI/TCO answers are reproducible and auditable: same inputs →
  same figures, each carrying a citation. Suitable for a governed value
  conversation. The PO ↔ BVA seam is unambiguous — numbers vs verdict — so the
  orchestrator composes one coherent onboarding answer without contention.
  Reusing the master-data pattern and `cosmos-mcp` means **no MCP allow-list
  change** and no new runtime infrastructure; SIT/PROD parity follows the shared
  master-data load (NFR-BVA-004).
- **Negative / trade-offs.** Benefit KPIs (capacity gain, LoS/bed-blocking
  avoidance) are ROM planning estimates
  ([ADR-0025](0025-bva-kpi-catalog.md)); modelled benefits are marked
  `requires-validation` and surfaced with a low/base/high sensitivity band. The
  GitHub billing $/AIU (and CHF) rate is not yet authoritative without a
  `Plan:read` token; FX and rate assumptions live in cited master-data CSVs and
  are refined when the token exists. A one-way Cosmos → gold projection can lag;
  gold is explicitly analytics-only and timestamped `asOf` to make the lag
  observable.

## Alternatives considered

- **LLM-computed ROI/TCO.** Rejected: not reproducible, not citable, and
  ungovernable for a customer-facing value claim.
- **BVA subsumes the go/no-go verdict.** Rejected: conflates deterministic
  numbers with product judgement and duplicates the PO Agent
  ([ADR-0043](0043-product-owner-agent-foundry-iq-domain.md)).
- **A bespoke Opportunity datastore.** Rejected: Cosmos already exists in the
  allow-list; a new store would add infrastructure and an allow-list change for
  no benefit.
