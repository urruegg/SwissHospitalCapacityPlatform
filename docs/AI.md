# AI

| Field | Value |
| ----- | ----- |
| **Version** | 0.4.1 |
| **Date** | 2026-06-01 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | 0.4.0 (PHI in-country controls and Foundry/Fabric IaC coverage baseline) |

## Purpose

This document defines the AI architecture approach for the Swiss Hospital
Capacity Platform with a GA-only service baseline and Swiss data residency
controls.

## Scope and Constraints

- React-based frontend is the mandatory MVP copilot channel.
- Agent runtime is application-hosted on Azure services, not Foundry-hosted
  agent resources.
- GA services only for MVP critical path.
- Strict Swiss in-country processing for PHI inference.
- PHI inference must use Standard/Regional deployments in Switzerland regions
  only.

## AI Use Cases

1. Bed and flow status Q and A for command-center users.
2. Forecast-aware operational recommendations with traceable grounding.
3. Discharge coordination support with auditable rationale and timestamps.
4. Role-based conversational assistance across operations personas.

## GA Service Baseline (Non-Foundry-Hosted Agents)

### Recommended Reference Design

| Domain | Recommended GA Service Pattern | Notes |
| ------ | ------------------------------ | ----- |
| Frontend channel | Azure Static Web Apps (React) or Azure App Service (web) | Choose App Service if unified hosting model is preferred |
| Agent API runtime | Azure Container Apps (HTTP API) | Use autoscaling and minimum replicas for predictable latency |
| Background agent workers | Azure Container Apps jobs or worker apps | Offload long-running tools and non-interactive tasks |
| AI model inference | Azure OpenAI Standard/Regional deployments | For PHI-sensitive traffic, Switzerland regions only |
| Conversation/session cache | Azure Cache for Redis | Reduce repeated grounding and improve response latency |
| Durable conversation and audit store | Azure Cosmos DB or Azure SQL | Store conversation metadata, citations, and action logs |
| Async orchestration | Azure Service Bus queues/topics | Isolate spikes and smooth downstream dependency pressure |
| Secrets and credentials | Azure Key Vault with managed identity | No secrets in code or config files |
| Observability | Application Insights + Log Analytics + Azure Monitor alerts | Track latency, token use, failures, and user-impacting events |

### Why this design

- Keeps the agent runtime fully under provider control.
- Avoids dependency on preview-only or non-GA orchestration paths.
- Supports React-first MVP operations while preserving one shared backend
  contract for optional post-MVP channels.

## Capacity-Based Hosting Guidance

Based on architecture assumptions:

- 120 peak concurrent users
- 8000 copilot turns per day
- P95 interactive response objective under 4 seconds

### Synchronous vs asynchronous split

1. Synchronous path:
  user request, grounding retrieval, model call, response with citations.
2. Asynchronous path:
  expensive enrichments, partner lookups, long-running planning tasks.

This split protects interactive latency while preserving functional depth.

### Initial sizing guidance for pilot

| Component | Initial Baseline | Scale Strategy |
| --------- | ---------------- | -------------- |
| Agent API on Container Apps | 6 minimum replicas, 20 max replicas, 1 vCPU/2 GiB each | Scale on HTTP concurrency and CPU; keep min replicas during business hours |
| Worker runtime | 2 minimum replicas, 10 max replicas | Scale on queue depth and processing latency |
| Redis | Standard tier with zone-redundant option where supported | Monitor hit ratio and memory pressure |
| Service Bus | Premium when strict isolation and predictable throughput are required | Scale messaging units as queue latency grows |

Notes:

- Baseline above is a starting point, not a final production commitment.
- Final sizing must be validated with load tests against real prompts,
  grounding size, and model token profiles.

## Swiss Data Residency and Compliance Controls

1. Deploy PHI-sensitive AI paths only in Switzerland North and/or Switzerland
  West.
2. Use Azure OpenAI Standard or Regional Provisioned deployment types only for
  PHI-sensitive scenarios.
3. Block Global, Data Zone, and Developer deployment types for
  PHI-sensitive inference paths.
4. Disable PHI cross-region failover by default, including Switzerland North to
  Switzerland West failover, unless a compliance-approved runbook exists.
5. Keep audit records of prompt metadata, grounding identifiers, response IDs,
  timestamps, and user role context.

Related architecture decisions:

- `AR-D-003` and `AR-D-004` in `docs/ARCHITECTURE.md`
- `ADR-0003` and `ADR-0004` in `docs/adr/`

## IaC Coverage Assessment for Foundry and Fabric

### Coverage Matrix

| Domain | IaC Coverage Status | Tooling Evidence | Notes and Gaps |
| ------ | ------------------- | ---------------- | -------------- |
| Foundry and Azure OpenAI account provisioning | Full | Bicep and ARM support via Microsoft.CognitiveServices/accounts; Terraform azurerm_cognitive_account | Includes network controls, identity, CMK, project management flags |
| Model deployment provisioning | Full | Bicep and ARM support via Microsoft.CognitiveServices/accounts/deployments; Terraform azurerm_cognitive_deployment | Deployment type and SKU can be codified |
| Deployment-type compliance guardrails | Full | Azure Policy support for restricting deployment SKUs and types | Enforce Standard/Regional-only for PHI routes |
| Foundry account and project base setup | High | Azure quickstart templates for standard and network-secured setup | Used for model hosting and controls only; app runtime remains self-hosted |
| Fabric capacity infrastructure | High | Terraform azurerm_fabric_capacity; Azure Fabric capacity REST APIs | Capacity layer is automatable and policy-governable |
| Fabric workspace item lifecycle | Partial (hybrid) | Fabric Git integration, deployment pipelines, Fabric REST APIs, Fabric Terraform provider references | Not all item types are GA; several remain preview (including Ontology and Data Agents) |

### IaC Conclusion

1. Foundry and Azure OpenAI infrastructure is IaC-ready for production using
  Bicep or Terraform.
2. Fabric capacity is IaC-ready, but Fabric item-level lifecycle is hybrid:
  Git integration plus deployment pipelines plus REST automation.
3. Full end-to-end declarative IaC coverage for all Fabric items is not yet
  uniformly GA due to item maturity differences.

### Recommended Implementation Model

1. Infrastructure lane:
  Bicep or Terraform for resource groups, networking, identities,
  Cognitive Services accounts, model deployments, monitoring, and policy.
2. Fabric content lane:
  Git integration and deployment pipelines for supported GA item types,
  with REST automation for promotion orchestration.
3. Governance lane:
  Azure Policy blocks non-compliant Foundry deployment types for PHI inference
  and enforces region restrictions.

## Model and Prompt Governance

1. Maintain versioned system prompts and policy prompts in Git.
2. Require change approval for prompt updates affecting clinical or
  operational recommendations.
3. Enforce grounded responses with source references and timestamp metadata.
4. Keep role-aware prompt templates and explicit refusal behavior for
  out-of-scope or unsafe requests.
5. Separate prompt bundles by environment (DEV, SIT, PROD) with promotion gates.

## Evaluation

### Online SLO Metrics

- P50, P95, P99 end-to-end response latency.
- Error rate by route and dependency.
- Grounding retrieval latency and cache hit ratio.
- Token consumption per request class.

### Quality and Safety Metrics

- Citation coverage rate for user-visible responses.
- Hallucination and unsupported-claim rate from sampled reviews.
- Actionability score for operations users.
- Refusal correctness for restricted request categories.

### Load Validation Plan

1. Run baseline test at 40 concurrent users.
2. Run target test at 120 concurrent users.
3. Run burst test at 180 concurrent users for 10-minute windows.
4. Verify degradation behavior and queue backpressure handling.
5. Tune autoscale thresholds and minimum replica counts from observed P95/P99.
