# Decision-Tier Live Apply (In-VNet Cosmos + Foundry) Runbook

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-07-26 |
| **Author** | GitHub Copilot |
| **Status** | Draft — plan only; the live-apply step is `approved-to-apply`-gated |
| **Previous Version** | 1.0.0 (initial runbook; Option A shared-image assumption) |

> ## Hard gate — the live apply is HITL-gated (AGENTS.md §4)
>
> The `caj-decision-apply-ihzhhpf-sit` Container Apps Job ships **plan-first**:
> its default command runs both decision CLIs in `--action plan` (dry-run) mode
> and mutates nothing. A live apply happens **only** when an operator with repo
> write access explicitly overrides the job command at start time and passes
> `--approved-to-apply <their-github-handle>`. No approver handle is baked into
> the image, the Bicep, or this runbook. The agent (a bot) cannot self-approve.

## Purpose

Run the merged Sprint 26 WS-C apply CLIs — `coordination.seed_live` (writes the
six-role `plans` / `proposed_actions` documents to SIT Cosmos) and
`foundry.register_decision_tier` (registers the decision-tier tool on the six
eastus2 Foundry agents) — from **inside the SIT VNet**, where the private
Cosmos endpoint and the Foundry data plane are reachable.

## Scope

### In scope

- Executing the plan-first (dry-run) job to preview the six-role seed + the
  six-agent Foundry registration.
- Executing the HITL-gated live apply against `cosmos-csa-ihzhhpf-sit` and the
  `ai-ihzhhpf-sit-eastus2` Foundry project.
- Verifying the resulting Cosmos documents and Foundry tool registration.

### Out of scope

- Any change to the decision-lane code or contracts (shipped in PR #382).
- Deploying the Cosmos containers themselves (already live via
  `cd-infra-deploy-sit`).
- Running the apply from a laptop or a hosted GitHub runner — the private
  endpoint ([ADR-0029](../adr/0029-agent-host-cosmos-reachability.md)) makes
  that impossible by design.

## Prerequisites

Mandatory prerequisites:

1. The `caj-decision-apply-ihzhhpf-sit` job is deployed. **This PR sets**
   `enableDecisionApplyJobModule = true` (alongside the already-set
   `enableAgentHostModule` and `enableCsaCosmosModule`) in
   `infra/environments/sit.bicepparam`; merging it lets the approval-gated
   `cd-infra-deploy-sit` run create the job.
2. The job runs the **decision-CLI-enabled** image. **This PR pins it** via
   `decisionApplyJobImage = 'cri75lbu5sj4hza.azurecr.io/hcc-agent-host:2b83a49'`
   in `sit.bicepparam` — the image built by `ci-build-agent-host.yml` on the
   #388 merge (it watches `data-platform/decision/**`), which contains
   `data-platform/decision/`. This pins **only the job** (Option B); the running
   agent-host Container App stays on `agentHostImage` (`:b796961`), untouched.
3. **One-time RBAC**: the reused agent-host MI (`id-ca-agent-host-ihzhhpf-sit`)
   needs `Cognitive Services User` on the eastus2 Foundry account for the
   Foundry registration (workstream C). It already holds `Cosmos DB Built-in
   Data Contributor` (granted in `infra/modules/cosmos/csa.bicep`) for the
   Cosmos seed (workstream B):

   ```bash
   mi_principal=$(az identity show -g rg-ihzhhpf-sit -n id-ca-agent-host-ihzhhpf-sit --query principalId -o tsv)
   foundry_id=$(az cognitiveservices account show -g rg-ihzhhpf-sit -n ai-ihzhhpf-sit-eastus2 --query id -o tsv)
   az role assignment create \
     --assignee-object-id "$mi_principal" \
     --assignee-principal-type ServicePrincipal \
     --role "Cognitive Services User" \
     --scope "$foundry_id"
   ```

4. An operator with **repo write access** who supplies their GitHub handle as
   the `approved-to-apply` approver (verified out of band via `github-mcp`).

Repository prerequisites already in place:

1. `coordination.seed_live`, `coordination.cosmos_store`,
   `foundry.register_decision_tier`, and `foundry.live_factory` (merged; PR #382
   and this PR).
2. The `plans` (`/episode_key`) and `proposed_actions` (`/plan_id`) containers,
   live in `cosmos-csa-ihzhhpf-sit` / `csa`.

## Security and Compliance Guardrails

1. Plan-first: never skip the dry-run step; confirm the previewed documents +
   agent set before the live apply.
2. The live apply command must include `--approved-to-apply <human-handle>`; the
   CLIs refuse an empty or bot (`*[bot]`, `copilot`) approver
   ([AGENTS.md §4](../../AGENTS.md#4-confirmation-rule-for-deploy--delete)).
3. RBAC-only, no keys: `disableLocalAuth=true` on Cosmos; the job authenticates
   as the agent-host MI via `AZURE_CLIENT_ID` + `DefaultAzureCredential`.
4. Synthetic data only, no PHI ([ADR-0016](../adr/0016-no-phi-in-mvp-demo-scope.md)).
5. Never echo tokens or connection strings into job logs or this runbook.

## Operational Procedure

### Step 1: Dry-run (plan) execution

Start the job with its **default** command (no override) to preview both CLIs:

```bash
az containerapp job start -n caj-decision-apply-ihzhhpf-sit -g rg-ihzhhpf-sit
```

Expected outcome:

1. Execution `Succeeded`.
2. Logs show `seed_live` printing five proposed plans / five actions and the
   `register_decision_tier` plan for all six agents.
3. No Cosmos or Foundry mutation (both CLIs ran `--action plan`).

Fetch logs:

```bash
az containerapp job execution list -n caj-decision-apply-ihzhhpf-sit -g rg-ihzhhpf-sit \
  --query "[0].name" -o tsv
```

### Step 2: Live apply (HITL-gated)

Override the job command so both CLIs run `--action apply` with the operator's
handle. Replace `<operator-handle>` with the approving operator's GitHub handle:

```bash
az containerapp job start -n caj-decision-apply-ihzhhpf-sit -g rg-ihzhhpf-sit \
  --command "/bin/sh" \
  --args "-c","cd /app/data-platform/decision && python -m coordination.seed_live --action apply --approved-to-apply <operator-handle> && for r in ooa dca bmca orsa sba csa; do python -m foundry.register_decision_tier --action apply --role \$r --approved-to-apply <operator-handle>; done"
```

Expected outcome:

1. Execution `Succeeded`.
2. `seed_live` wrote the six-role `plans` + `proposed_actions` documents.
3. `register_decision_tier` registered `decision_tier_coordination_<role>` on
   each of the six agents (idempotent — re-runs report `toolAlreadyPresent`).

### Step 3: Verify

Cosmos (control-plane count is sufficient; data-plane read is in-VNet):

```bash
az cosmosdb sql container show -a cosmos-csa-ihzhhpf-sit -g rg-ihzhhpf-sit -d csa -n plans -o table
az cosmosdb sql container show -a cosmos-csa-ihzhhpf-sit -g rg-ihzhhpf-sit -d csa -n proposed_actions -o table
```

Foundry (assistants list should show the six agents; each decision-tier agent
carries the `decision_tier_role` metadata):

```bash
token=$(az account get-access-token --resource https://cognitiveservices.azure.com --query accessToken -o tsv)
curl -s -H "Authorization: Bearer $token" \
  "https://ai-ihzhhpf-sit-eastus2.services.ai.azure.com/api/projects/ai-ihzhhpf-sit-eastus2-project/assistants?api-version=2025-05-15-preview" \
  | python -c "import sys,json; [print(a['name'], a.get('metadata',{}).get('decision_tier_role')) for a in json.load(sys.stdin).get('data',[])]"
```

## Handoff to Next Process

After a successful live apply, proceed with:

- End-to-end demo of the live propose → HITL approve → deterministic recompute
  thread against SIT Cosmos.
- Updating the Sprint 26 design spec §9 status if the golden thread is verified
  live.

## Troubleshooting

If the Cosmos seed fails with a network/timeout error:

1. Confirm the job ran on the agent-host CAE (VNet-integrated) — check the
   `environmentId` on the job resource.
2. Confirm `CSA_COSMOS_ENDPOINT` resolves to the private IP from inside the VNet
   (the private DNS zone `privatelink.documents.azure.com` must be linked).

If the Foundry registration fails with 401/403:

1. Confirm the one-time `Cognitive Services User` grant (Prerequisite 3) landed
   and has propagated.
2. Confirm `AZURE_CLIENT_ID` matches `id-ca-agent-host-ihzhhpf-sit`.

If a CLI refuses with an approver error:

1. The handle was empty or bot-like — re-run with a human operator's handle.

## Evidence Checklist

Before closing this runbook execution:

- [ ] Step 1 dry-run execution `Succeeded` with plan output captured.
- [ ] Approver handle (repo-write human) recorded for the live apply.
- [ ] Step 2 live apply execution `Succeeded`.
- [ ] `plans` + `proposed_actions` show the seeded documents.
- [ ] Six Foundry agents carry the `decision_tier_coordination_<role>` tool.
