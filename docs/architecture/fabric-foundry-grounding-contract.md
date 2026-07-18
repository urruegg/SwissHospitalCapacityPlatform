# Fabric to Foundry Grounding Contract

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-17 |
| **Author** | Urs Rüegg |
| **Status** | Draft for review |
| **Previous Version** | n/a (new — Slice 0) |
| **Related** | [ADR-0033](../adr/0033-fabric-data-agent-as-foundry-grounding-tool.md), [Fabric IQ to Foundry readiness design §5](../superpowers/specs/2026-07-17-fabric-iq-foundry-readiness-design.md) |

## Grounding precedence

Every operational copilot (bmca, ooa, dca, orsa, sba, csa) resolves grounding in
this order:

1. **Fabric Data Agent** — *primary*. Concept-level NL query over the MVO ontology
   + Direct-Lake semantic model. RLS + ADR-0016 PHI gate-3 enforced.
2. **Foundry IQ knowledge base** — *secondary*. Unstructured / document context.
3. **`fabric-mcp`** — *actions only*. Trigger notebooks, data-quality checks. Never
   the grounding path when the Data Agent can serve the query.

## Citation contract

A grounded answer MUST cite at least one `hcp:*` ontology entity
(`FR-ONT-004`, `NFR-AI-002/004`), e.g.
`Grounded on: dim_ward_capacityunit, hcp:CapacityUnit, hcp:Bed`.

## Refusal propagation

The Fabric Data Agent `REFUSE:` codes (agents/fabric-data-agent/AGENT.md §4) flow
through the consuming agent **verbatim**. The agent MUST NOT rewrite, soften, or
route around a refusal, and MUST NOT consult the chat model after a refusal.

## Degradation (fail loud, never silent)

If the Fabric Data Agent is unavailable, the agent degrades to table grounding and
prefixes the answer with an explicit `grounding degraded` notice. It MUST NOT answer
ungrounded.

## Configuration (region-agnostic)

The binding is declared per agent as a `groundingAgent` manifest block. The Data
Agent endpoint and workspace id come from environment variables
(`FABRIC_DATA_AGENT_ENDPOINT`, `FABRIC_WORKSPACE_ID`), so the same binding lifts
from westus2 (Slice 0) to eastus2 (Phase 2) without edits.

## Verification

Each consuming agent carries a happy-path grounded golden task (answer + `hcp:*`
citation) and a refusal-propagation golden task. See
`agents/ooa-agent/golden-tasks.md` for the Slice 0 reference fixtures.
