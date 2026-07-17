# ADR-0032: Foundry Control Plane Deployed in eastus2

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-17 |
| **Decision-makers** | @urruegg |
| **Consulted** | SIT evidence analysis session (2026-07-17) |

## Context

The Swiss Hospital Capacity Platform requires Microsoft Foundry Agent Service to register and operate 8 operational copilot agents (bmca, ooa, dca, orsa, sba, csa, data-quality, onboarding). The current SIT environment is deployed in `westus2`.

Evidence gathered 2026-07-17 revealed a critical blocker:

| Metric | westus2 | eastus2 |
|--------|---------|---------|
| OpenAI models available | **0** | 122 |
| GA OpenAI models | 0 | 88 |
| Total TPM quota | 5,000 (non-OpenAI only) | 5,800,000 |
| Foundry Agent Service | ❌ Not listed | ✅ GA supported |
| GPT-5 family | ❌ | ✅ GA |
| o3 reasoning | ❌ | ✅ GA |

The MCAP tenant (`1337187a-4c41-4da9-8fca-731bba7a4329`) subscription (`66a9953a-df37-4c51-856c-9971b9bf3e03`) has **zero OpenAI quota in westus2**. The Foundry Agent Service data-plane API requires at least one deployed OpenAI model AND the region must be listed as supported. Neither condition is met in westus2.

A full compatibility analysis of all 22 SIT resource types confirmed **zero blocking gaps** in eastus2 — every resource type is GA.

## Decision

Deploy the **Microsoft Foundry control plane** (AI Services account + Foundry project + model deployments + agent registrations) in **eastus2**.

This creates a temporary cross-region topology:
- **westus2**: Container Apps (agent-host, app-fluent, sim), Cosmos DB, Event Hubs, Service Bus, Key Vault, VNet
- **eastus2**: AI Services + Foundry project + models + registered agents

The cross-region topology is acceptable for the demo/proof-of-technology scope per [ADR-0013](0013-temporary-us-region-demo-scope.md). Sprint 19 will collocate all PROD resources in eastus2.

## Alternatives considered

| Alternative | Why rejected |
|-------------|-------------|
| `switzerlandnorth` | 48 GA models (acceptable) but DataZone/ProvisionedManaged SKUs limited; Agent Service listed but requires validation; keeps Swiss sovereignty for future PROD |
| `swedencentral` | 90 GA models, EU-sovereign, but adds a third region to manage |
| Wait for westus2 quota | No timeline from Microsoft; blocks all agent work indefinitely |
| Move entire SIT to eastus2 now | Higher risk; do Foundry-only first (Sprint 18), full migration in Sprint 19 |

## Consequences

### Positive
- Unblocks agent registration immediately
- Access to 88 GA models including gpt-5, gpt-5-mini, o3
- Foundry Agent Service GA support — no Preview risk
- Sprint 19 will naturally collocate everything in eastus2

### Negative
- Cross-region latency (westus2 ↔ eastus2) for agent calls until Sprint 19
- Two regions to manage temporarily
- Does not resolve Swiss data sovereignty (acceptable per ADR-0013 demo scope, no PHI per ADR-0016)

### Neutral
- No impact on existing SIT resources in westus2
- No impact on PROD planning (Sprint 19 deploys fresh in eastus2)

## Compliance

- Per [ADR-0013](0013-temporary-us-region-demo-scope.md): US region acceptable for demo scope with synthetic data only
- Per [ADR-0016](0016-no-phi-in-mvp-demo-scope.md): no PHI ingested — data sovereignty not a blocking constraint
- Sunset path: when target services reach Swiss GA, migrate to `switzerlandnorth` (ADR-0013 expiry 2026-09-30)

## References

- [Sprint 18 Design Spec](../superpowers/specs/2026-07-17-sprint-18-foundry-eastus2-control-plane-design.md)
- [SIT Evidence Analysis (2026-07-17)](../sprints/sit-evidence-2026-07-17.md)
- [Microsoft Learn: Foundry Agent Service regions](https://learn.microsoft.com/en-us/azure/ai-services/agents/overview)
- [ADR-0013: Temporary US Region Demo Scope](0013-temporary-us-region-demo-scope.md)
