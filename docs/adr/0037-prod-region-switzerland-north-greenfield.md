# ADR-0037: PROD Region Pivot to Switzerland North (Greenfield Decommission-and-Rebuild)

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-21 |
| **Author** | Urs Rüegg |
| **Decision-makers** | @urruegg |
| **Supersedes (scoped)** | [ADR-0032](0032-foundry-control-plane-eastus2.md) (Foundry control plane in eastus2) and [ADR-0035](0035-fabric-iq-layer-region-westus2.md) (PROD Fabric IQ in westus2) — **for the PROD environment only**; both remain the record of the SIT-era topology and its rationale. |
| **Consulted** | SIT-vs-Switzerland-North evidence session (2026-07-21, live `az` against sub `66a9953a-df37-4c51-856c-9971b9bf3e03`); [ADR-0013](0013-temporary-us-region-demo-scope.md) sunset path; [ADR-0006](0006-preview-features-non-production-rule.md) preview rule |

## Context

[ADR-0013](0013-temporary-us-region-demo-scope.md) established a **temporary** US-region
demo scope (synthetic data only, no PHI per [ADR-0016](0016-no-phi-in-mvp-demo-scope.md)),
with an explicit sunset back to `switzerlandnorth` when the required services reach
sufficient maturity there. PROD subsequently landed split across two US regions:
Foundry in eastus2 ([ADR-0032](0032-foundry-control-plane-eastus2.md)) because westus2
had **zero** OpenAI quota, and Fabric in westus2 ([ADR-0035](0035-fabric-iq-layer-region-westus2.md))
because eastus2 Fabric quota was **zero**. Both decisions explicitly named
`switzerlandnorth` as the intended sovereign end-state.

A fresh, evidence-based feasibility check of `switzerlandnorth` was run on 2026-07-21
using live `az` queries against the tenant subscription, cross-checked against
Microsoft Learn region documentation. The picture has materially improved since the
ADR-0032 evaluation ("48 GA models, Agent Service listed but requires validation").

### Evidence (live `az`, sub `66a9953a-df37-4c51-856c-9971b9bf3e03`, as of 2026-07-21)

| Capability | Switzerland North finding | Command / source |
|------------|---------------------------|------------------|
| Fabric capacity | Region listed; quota **0 used / 512 limit** (eastus2 = **0/0**, the ADR-0035 blocker) | `Microsoft.Fabric/locations/switzerlandnorth/usages` |
| Azure OpenAI models | GA catalog present incl. `gpt-5`, `gpt-5-mini`, `o3`, `gpt-4.1`, `gpt-4o` | `az cognitiveservices model list -l switzerlandnorth` |
| Agent models (the 3 the SIT agents run) | `gpt-5`, `gpt-5-mini`, `o3` all deployable | deployment parity check vs `ai-ihzhhpf-sit-eastus2` |
| Foundry Agent Service | GA service; Switzerland North row = Responses ✅ / Agents ✅ / Class-A private-IP ❌ | Learn: Foundry Agent Service limits-quotas-regions |
| Fabric IQ Ontology / Data Agent | **Preview**, region-listed for CH North; subject to the per-capacity `FeatureNotAvailable` gate seen in issue #270 | Learn: Fabric region-availability + Data Agent; issue #270 |
| FHIR, Cosmos, Container Apps, Logic Apps, Key Vault, Log Analytics, Purview, Entra, Managed Identity, Storage, ML | All providers list Switzerland North | `az provider show` per namespace |

### The residency nuance (SKU = residency)

The three agent models are deployable in `switzerlandnorth` but the `az` SKU column
shows them as **`GlobalStandard`** (`gpt-5`, `gpt-5-mini`, `o3`) — inference routes to a
global pool, **not in-region**. Only **`Standard`/regional** SKUs keep data inside
Switzerland, and those are limited to **`gpt-4.1` / `gpt-4.1-mini` / `gpt-4o (2024-11-20)`**
plus embeddings. This tradeoff is **not binding under current scope** (synthetic data,
no PHI per ADR-0013/0016) but becomes decisive at real Swiss-PHI PROD.

## Decision

**PROD moves to `switzerlandnorth` as a greenfield, decommission-and-rebuild** — treated
operationally like a **disaster-recovery rebuild in a new region**, not a resource
migration.

1. **Decommission first.** Tear down **all** existing PROD resources in eastus2
   (`rg-ihzhhpf-prod-eastus2`) and the PROD Fabric capacity in westus2
   (`fabricihzhhpfprod`) before the new region is built, so PROD starts from a clean,
   single-region baseline. No data migration (all PROD data is synthetic and
   regenerated). This is a destructive action and is gated per
   [AGENTS.md §4](../../AGENTS.md) (`approved-to-apply` + human execution).
2. **Rebuild at SIT parity in `switzerlandnorth`.** Re-provision the full stack from
   the same Bicep modules that produce SIT, targeting a single region
   (`rg-ihzhhpf-prod` in `switzerlandnorth`): Fabric capacity + workspace + lakehouse +
   semantic model, AI Services + Foundry project + the 8 agents, Container Apps
   (agent-host + app-fluent + sim), Cosmos (platform + CSA), Event Hubs, Service Bus,
   Key Vault, VNet + private endpoints, Storage, Log Analytics, App Insights,
   Container Registry, Logic Apps, DNS + Entra app registrations.
3. **Maturity posture (GA-core + Preview-IQ).** Ship the GA-tier in-region. Run the
   Fabric IQ Ontology + Data Agent as **Preview** behind an [ADR-0006](0006-preview-features-non-production-rule.md)
   exception (they carry no production SLA and remain per-capacity gated, issue #270).
4. **Model posture.** For the current synthetic/no-PHI scope, keep the agents on
   `gpt-5`/`gpt-5-mini`/`o3` via `GlobalStandard`. Record that a strict Swiss-residency
   PROD would downgrade agents to `gpt-4.1`/`gpt-4o` (regional `Standard`) or accept the
   EU Data Zone boundary — decided at PHI-onboarding time, not now.

This **relaxes** the two-region US topology of ADR-0032/ADR-0035 for PROD and executes
the ADR-0013 sunset intent one step early, on the strength of the 2026-07-21 evidence.

## Decommission scope (evidence-based, live 2026-07-21)

* `rg-ihzhhpf-prod-eastus2` (eastus2): `ai-ihzhhpf-prod` + project, `appi-ihzhhpf-prod`,
  `ca-agent-host-ihzhhpf-prod`, `ca-app-fluent-ihzhhpf-prod`, `cae-app-fluent-ihzhhpf-prod`,
  `cae-ihzhhpf-prod`, `cosmos-ihzhhpf-prod`, `cosmos-csa-ihzhhpf-prod`, `crihzhhpfprod`,
  `evh-ihzhhpf-prod-q4nk`, `sb-ihzhhpf-prod-q4nk`, `kv-ihzhhpf-prod-q4nk`,
  `log-ihzhhpf-prod`, `vnet-platform-ihzhhpf-prod` (+ 3 NSGs), `id-*-ihzhhpf-prod` (3).
* westus2: `fabricihzhhpfprod` (Fabric F2 capacity) + its Fabric-plane artefacts (PROD
  workspace, lakehouse, semantic model, and the #270 ontology work).
* Managed workspace RG `ai_appi-ihzhhpf-prod_*_managed` (removed with its parent).

SIT is **untouched** (remains split westus2/eastus2 until a separate later decision).

## Consequences

**Positive:**

* Single-region PROD; no cross-region Foundry-to-Fabric hop.
* Executes the sovereign end-state (Swiss region) intended by ADR-0013; simplifies the
  eventual PHI story (residency already in-region for the GA-core).
* Clean greenfield removes accumulated two-region drift.

**Negative / risks:**

* Destructive teardown of a working PROD — mitigated by synthetic-only data, IaC
  reproducibility, and the DR-style rebuild runbook. Hard-gated by `approved-to-apply`.
* Fabric IQ Ontology/Data Agent remain **Preview** and may hit the #270 per-capacity
  gate on the new `switzerlandnorth` capacity (untested there) — IQ binding may lag the
  GA-core rebuild.
* Agent models are cross-geo (`GlobalStandard`) unless downgraded — acceptable now, an
  open item for PHI PROD.
* No network-secured "Class A" private-agent topology in Switzerland North.

## Alternatives considered

| Alternative | Why not (default) |
|-------------|-------------------|
| Keep PROD in eastus2/westus2 (status quo) | Perpetuates the two-region US topology ADR-0013 committed to sunset; no Swiss sovereignty. |
| Migrate resources in place US -> Switzerland North | Cosmos export/import, PE rewire, vector re-index; higher risk than a synthetic-data greenfield with zero portable state. |
| Wait for Fabric IQ / residency-tier GA in Switzerland North | Blocks the sovereign pivot on an unknown timeline; GA-core is already available today. |
| swedencentral (EU-sovereign, richer models) | Adds a non-Swiss region; fails the Swiss-residency intent. |

## Revisit criteria

* Revisit the **model posture** at PHI onboarding: if strict Swiss residency is required,
  move agents to regional `Standard` models or the EU Data Zone.
* Revisit the **IQ posture** when Fabric IQ Ontology + Data Agent reach GA in
  Switzerland North (retire the ADR-0006 exception).
* If the `switzerlandnorth` Fabric capacity hits the #270 `FeatureNotAvailable` gate for
  Ontology, track under issue #270 and keep the GA-core PROD independent of it.

## References

* [ADR-0013 — Temporary US-region demo scope](0013-temporary-us-region-demo-scope.md)
* [ADR-0032 — Foundry control plane in eastus2](0032-foundry-control-plane-eastus2.md)
* [ADR-0035 — PROD Fabric IQ layer in westus2](0035-fabric-iq-layer-region-westus2.md)
* [ADR-0006 — Preview features non-production rule](0006-preview-features-non-production-rule.md)
* [ADR-0016 — No PHI in MVP demo scope](0016-no-phi-in-mvp-demo-scope.md)
* `docs/region-availability.yaml` (refreshed 2026-07-21 with the `az`-verified facts above)
* Sprint 19 design + plan (retargeted to Switzerland North greenfield)
* Issue #270 — Fabric IQ Ontology per-capacity `FeatureNotAvailable` gate
