# ADR-0033 — Fabric Data Agent as the Foundry grounding tool

| Field | Value |
| ----- | ----- |
| **Status** | Proposed |
| **Date** | 2026-07-17 |
| **Author** | Urs Rüegg |
| **Related** | [ADR-0014 (Fabric IQ ontology backbone)](0014-fabric-iq-ontology-target-backbone-ga-gated.md), [ADR-0016 (no PHI in demo)](0016-no-phi-in-mvp-demo-scope.md), [ADR-0032 (Foundry control plane eastus2)](0032-foundry-control-plane-eastus2.md) |
| **Design source** | [Fabric IQ to Foundry readiness design §5](../superpowers/specs/2026-07-17-fabric-iq-foundry-readiness-design.md) |

## Context

Sprint 18 registered 8 Foundry agents in eastus2 with no grounding surface. The
Fabric IQ layer (ontology + Direct-Lake semantic model) is fronted by a read-only
Fabric Data Agent (agents/fabric-data-agent/AGENT.md) that enforces RLS + ADR-0016
PHI gate-3 and returns concept-level answers with `hcp:*` citations. The open
question is how Foundry agents consume that layer without bypassing the ontology,
RLS, or refusal rules.

## Decision

Adopt the **Fabric Data Agent as the primary grounding tool** for the operational
copilots. Each consuming agent binds it via a `groundingAgent` manifest block;
the orchestrator asks the Data Agent in natural language, uses its answer + `hcp:*`
citations as primary grounding, propagates `REFUSE:` verbatim, and degrades loudly
to table grounding if the Data Agent is unavailable. A Foundry IQ knowledge base is
a *secondary* source; `fabric-mcp` remains for *actions* only. The binding is
region-agnostic (endpoint + workspace from env), so it lifts westus2 -> eastus2
unchanged.

The Fabric data-agent tool is a **Foundry-native connection, not a new MCP server**
— no `.github/copilot/mcp.json` allow-list change.

## Consequences

- **Positive:** preserves ontology + RLS + refusal investment at the consumption
  edge; region-agnostic; no new MCP server; strengthens NFR-AI-002/003/004.
- **Negative / risks:** depends on Fabric-data-agent-as-Foundry-tool maturity
  (verify at build; fallback = `fabric-mcp` query path); Data Agent availability is
  now on the grounding hot path (mitigated by loud degradation to table grounding).

## Review triggers

- Fabric data-agent-as-Foundry-tool GA/preview status changes.
- The grounding-contract precedence (primary/secondary/actions) is revised.
