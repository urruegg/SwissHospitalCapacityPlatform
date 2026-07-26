# ADR-0044 — App data access via the IQ layer

| Field | Value |
| ----- | ----- |
| **Status** | Proposed |
| **Date** | 2026-07-26 |
| **Author** | Urs Rüegg (with Copilot) |
| **Sprint** | 27 (Curavias App UX Polish, tracker #365) |
| **Design source** | [App IQ data-access pattern](../architecture/app-iq-data-access-pattern.md), [Fabric to Foundry grounding contract](../architecture/fabric-foundry-grounding-contract.md) |
| **Related** | [ADR-0033](0033-fabric-data-agent-as-foundry-grounding-tool.md), [ADR-0034](0034-fabric-iq-demo-scope-artefacts.md), [ADR-0035](0035-fabric-iq-layer-region-westus2.md), [ADR-0014](0014-fabric-iq-ontology-target-backbone-ga-gated.md), [ADR-0013](0013-temporary-us-region-demo-scope.md), [ADR-0016](0016-no-phi-in-mvp-demo-scope.md) |

## Context

The internal app (`apps/hcc-app-fluent`) had two data paths. The **conversational**
path (chat / reco) was IQ-governed — Foundry agent host → Fabric Data Agent →
semantic model over Gold, with `hcp:*` citations and loud degradation (ADR-0033).
The **structured board** path read Gold directly via `golden-source-client`
(`VITE_GOLDEN_SOURCE_URL`) or served simulated fixtures, bypassing the IQ
semantic / ontology surface and carrying no citations. So "the app always works
on golden evidence via the IQ layer" was only partially true, and nothing
prevented a surface from fetching data ad hoc.

## Decision

Adopt a **single IQ-layer gateway** (`src/data/iq-client.ts`) as the only
golden-data ingress for the app. Board loaders and the agent manifest are thin
callers.

1. **Single ingress.** Only `iq-client.ts` may hold a golden-data endpoint or call
   `fetch`. Enforced by a vitest guard (`tests/unit/iq-ingress-guard.test.ts`)
   that scans `src/**`. (MSAL / Graph identity calls are not `fetch` and are out
   of scope.)
2. **Precedence** (mirrors the grounding contract / ADR-0033): structured facts →
   Fabric Data Agent / semantic model over Gold; conversational / knowledge →
   Foundry agent host; `fabric-mcp` is actions-only and never a read path.
3. **Evidence envelope.** Every structured read returns
   `{ provenance, citations, degraded }` (on `RoleBoardData`, additive optional
   fields). `provenance` reuses the frozen contract: `live` == golden evidence
   from the IQ layer, `simulated` == demo fixture. Structured reads carry ≥ 1
   `hcp:*` / `gold.*` citation.
4. **Fail loud.** If the golden source is configured but the read fails, the layer
   falls back to the fixture flagged `degraded: true`; the board renders a visible
   `grounding degraded` notice (`GroundingNotice`). Never render golden figures
   silently when the source is down.
5. **Config, not code.** Endpoints come from env (`VITE_GOLDEN_SOURCE_URL`,
   `VITE_AGENT_HOST_URL`) so westus2 (demo, ADR-0013/0035) lifts to
   eastus2 / switzerlandnorth without edits.

## Consequences

- **Positive:** every app read is governed and evidence-tagged (provenance +
  citations); no surface reads Gold ad hoc; region-agnostic; the board path can
  now carry `hcp:*` citations like the chat path; sets up real-data UX validation
  once `VITE_GOLDEN_SOURCE_URL` is wired in SIT.
- **Negative / follow-ups:** the board `live` path still uses the golden-source
  REST shape; full Fabric-Data-Agent natural-language structured queries are a
  follow-up once that endpoint is live. Demo stays `simulated` until the env is
  configured. Provenance keeps two values (`live` / `simulated`) rather than the
  doc's three (`golden` folded into `live`) to avoid breaking the frozen
  `RoleBoard` contract.

## Review triggers

- `VITE_GOLDEN_SOURCE_URL` wired in SIT (validate real-data UX + citations).
- The Fabric Data Agent structured-query contract is finalised.
- The precedence (primary / secondary / actions) is revised.
