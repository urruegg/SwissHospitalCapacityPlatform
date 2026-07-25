# ADR-0043: Curavias Product Owner Agent as Foundry IQ Knowledge-Layer Domain #1

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-25 |
| **Author** | Urs Rüegg |
| **Decision-makers** | @urruegg |
| **Consulted** | Sprint 28 brainstorm (2026-07-25); [Sprint 28 design spec](../superpowers/specs/2026-07-25-sprint-28-product-owner-agent-design.md); idea pack [`Curavias-Product-Owner-Agent-Proposal.md`](../ideas/Curavias-Product-Owner-Agent-Proposal.md) (Draft v1.2); Microsoft Learn (Foundry IQ / Azure AI Search agentic retrieval, 2026-07-25) |
| **Issue** | [#377](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/377) |

## Context

Sprint 28 builds the **Curavias Product Owner Agent (PO Agent)** — the
authoritative, source-grounded, advisory-only voice of the platform, embedded in
the Curavias App as a Copilot rail (see the
[design spec](../superpowers/specs/2026-07-25-sprint-28-product-owner-agent-design.md)).

The PO Agent answers product questions (personas CEO/COO/CIO/CFO/CTO/CISO/CDO/CLO
plus Developer/Architect/PM/Partner) grounded on four knowledge-source classes:

- **Class A** — governed corpus (daily GitHub → ADLS → OneLake → knowledge source, PHI-excluded, interviews first-order);
- **Class B** — live-proof read-only probes (Resource Graph / Fabric REST / Foundry Agent API) with reconcile-and-flag;
- **Class C** — BVA/TCO cost data product (effective PROD Azure cost + GitHub Copilot token cost, reconciled to the BVA / [ADR-0025](0025-bva-kpi-catalog.md));
- **Class D** — ontology query surface via the `da_hospital_capacity` Fabric Data Agent ([ADR-0034](0034-fabric-iq-demo-scope-artefacts.md)).

The open architectural question is **what retrieval foundation** the PO Agent
sits on, and whether that foundation is PO-Agent-specific or a **shared layer**
that later serves other agent roles (Compliance, Data, Operations, ...). The
Sprint 28 brainstorm (decision D2) resolved this in favour of a shared,
managed enterprise knowledge layer.

Microsoft Learn (checked 2026-07-25) confirms **Foundry IQ** is a managed
enterprise **Knowledge Layer** over **Azure AI Search** (hybrid vector + keyword,
agentic retrieval) + **Azure OpenAI**, and that Azure AI Search is **GA** in
Switzerland North while some Foundry IQ agentic-retrieval features (portal /
preview API) are **Preview**. The product owner accepted Preview services in
PROD to "show the art of the possible" (design decision D3).

## Decision

**The Curavias Product Owner Agent is registered as domain #1 on a shared
Foundry IQ Knowledge Layer.**

1. **Shared Knowledge Layer, not a bespoke retriever.** Retrieval for the PO
   Agent runs on **Foundry IQ** as the managed enterprise Knowledge Layer, with
   **Azure AI Search** (GA, Switzerland North) as the substrate beneath it and
   **Azure OpenAI** (swn) for query planning + synthesis. The layer is
   **multi-domain by construction**: the PO Agent is the first registered domain;
   additional domains (Compliance, Data, Operations) mount on the same layer to
   prove reuse without re-provisioning the substrate.
2. **PO Agent = domain #1.** The `product-owner` agent is registered in the
   Foundry Agent Service (GA, per [ADR-0032](0032-foundry-control-plane-eastus2.md))
   and bound to the Foundry IQ knowledge base as its retrieval surface. Its four
   class tools (A/B/C/D) return a uniform **`GroundedChunk`** the citation layer
   renders identically (frozen contract — see the
   [contracts spec](../superpowers/specs/2026-07-25-sprint-28-po-agent-contracts.md)).
3. **Preview accepted in PROD (Switzerland North), scoped.** Only two pieces are
   Preview: Foundry IQ agentic-retrieval (portal / preview API) and Fabric IQ +
   the `da_hospital_capacity` Fabric Data Agent (Class D). Both are accepted per
   design D3 under the standing [ADR-0006](0006-preview-features-non-production-rule.md)
   / [ADR-0042](0042-prod-switzerland-north-ga-target-standing-preview-exception.md)
   exception. Class D is feature-flagged and degrades to `snapshot`; the Search
   REST API version is pinned to contain preview drift (design risk R2).
4. **Advisory-only, grounded, auditable.** The PO Agent never mutates a system
   (side-effect ceiling `write`; advisory answers + drafts only), answers only
   from the four classes with mandatory citations, and logs every question →
   retrieved chunks → citations → confidence → caller to the Cosmos audit store.
   This preserves the runtime decision in
   [ADR-0002](0002-runtime-is-github-copilot-coding-agent.md) and the
   Fabric-to-Foundry grounding seam in
   [ADR-0033](0033-fabric-data-agent-as-foundry-grounding-tool.md).

## Consequences

**Positive:**

- One managed, GA-substrate Knowledge Layer serves many agent domains; the PO
  Agent proves the pattern and additional domains reuse it at marginal cost.
- Uniform `GroundedChunk` contract lets the four heterogeneous classes (corpus,
  live-proof, cost, ontology) render citations identically and lets Wave-2
  workstreams build to a frozen interface in parallel.
- Grounding + audit + advisory-only posture keeps the PO Agent inside the
  platform's Responsible-AI envelope (`NFR-AI-*`, `NFR-POA-001..004`).

**Negative / risks:**

- Foundry IQ agentic-retrieval preview API and Fabric IQ / Data Agent Preview
  carry no production SLA and the latter is per-capacity gated (issue #270);
  mitigated by feature-flag + `snapshot` degradation + pinned Search API version.
- Class D currently reads the westus2 `da_hospital_capacity` demo artefact
  ([ADR-0034](0034-fabric-iq-demo-scope-artefacts.md)); the residency caveat is
  documented and follows Fabric IQ Switzerland North GA
  ([ADR-0014](0014-fabric-iq-ontology-target-backbone-ga-gated.md)).
- A shared layer risks cross-domain leakage; mitigated by per-domain knowledge
  sources + authorisation-aware retrieval + entitlement tests (design R3).

## Alternatives considered

| Alternative | Why not |
|-------------|---------|
| Bespoke per-agent retriever (raw Azure AI Search index, no Knowledge Layer) | Loses the managed agentic-retrieval surface and forces every future domain to rebuild retrieval; contradicts the "art of the possible" direction (D2). |
| Wait for Foundry IQ agentic-retrieval GA before building | Blocks the sprint on an unknown timeline; the GA substrate (Azure AI Search) is available today and Preview is accepted per D3. |
| Fabric IQ ontology as the sole retrieval foundation | Fabric IQ is Preview + per-capacity gated (#270) and residency-caveated (westus2 demo artefact); unsuitable as the whole foundation, so it is scoped to Class D only. |

## References

- [Sprint 28 design spec](../superpowers/specs/2026-07-25-sprint-28-product-owner-agent-design.md)
- [Sprint 28 PO Agent contracts](../superpowers/specs/2026-07-25-sprint-28-po-agent-contracts.md)
- [ADR-0002 — Runtime is GitHub Copilot coding agent](0002-runtime-is-github-copilot-coding-agent.md)
- [ADR-0014 — Fabric IQ ontology target backbone (GA-gated)](0014-fabric-iq-ontology-target-backbone-ga-gated.md)
- [ADR-0025 — BVA KPI catalog](0025-bva-kpi-catalog.md)
- [ADR-0032 — Foundry control plane in eastus2](0032-foundry-control-plane-eastus2.md)
- [ADR-0033 — Fabric Data Agent as Foundry grounding tool](0033-fabric-data-agent-as-foundry-grounding-tool.md)
- [ADR-0034 — Fabric IQ demo-scope artefacts](0034-fabric-iq-demo-scope-artefacts.md)
- [ADR-0037 — PROD region Switzerland North greenfield](0037-prod-region-switzerland-north-greenfield.md)
- [ADR-0042 — PROD Switzerland North GA-target + standing Preview exception](0042-prod-switzerland-north-ga-target-standing-preview-exception.md)
- Issue [#377](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/377); issue #270 (Fabric IQ per-capacity gate)
