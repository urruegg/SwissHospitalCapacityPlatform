# Decision-Tier Live Apply (In-VNet Cosmos + Foundry) Runbook

| Field | Value |
| ----- | ----- |
| **Version** | 1.3.0 |
| **Date** | 2026-07-26 |
| **Author** | GitHub Copilot |
| **Status** | Draft — procedure; the live-apply step is `approved-to-apply`-gated. WS-B Cosmos seed + WS-C Foundry registration were completed live on 2026-07-26 (all six agents carry `decision_tier_coordination_<role>`), so **re-runs must be Foundry-only** (see Step 2). |
| **Previous Version** | 1.2.0 (Foundry User RBAC + `--yaml` template-swap run method; corrected the wrong `seed_live` "idempotent" claim in 1.3.0 after the 2026-07-26 live apply) |

> ## Hard gate — the live apply is HITL-gated (AGENTS.md §4)
>
> The `caj-decision-apply-ihzhhpf-sit` Container Apps Job ships **plan-first**:
> its default command runs both decision CLIs in `--action plan` (dry-run) mode
> and mutates nothing. A live apply happens **only** when an operator with repo
> write access swaps the job template command to the `--action apply` chain
> (via `az containerapp job update --yaml`, see Step 2) and passes
> `--approved-to-apply <their-github-handle>`. No approver handle is baked into
> the image, the Bicep, or this runbook. The agent (a bot) cannot self-approve.
>
> **Mechanical note (verified 2026-07-26):** `az containerapp job start
> --command/--args` overrides are **silently ignored** in this environment — the
> job always runs its baked-in template command. The only reliable way to run
> the apply chain is to temporarily edit the job template's `sh -c` script token
> with `az containerapp job update --yaml`, `start`, then **revert** the template
> with the original YAML (Step 2). Always revert after the run so the job returns
> to its plan-first default (no drift).

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
2. The job runs the **decision-CLI-enabled** image. `decisionApplyJobImage` in
   `sit.bicepparam` pins **only the job** (Option B) to an `hcc-agent-host` image
   that contains `data-platform/decision/` (built by `ci-build-agent-host.yml`,
   which watches `data-platform/decision/**`). The running agent-host Container
   App stays on `agentHostImage` (`:b796961`), untouched.

   > **Corrected 2026-07-26:** the first live apply ran image `:2b83a49`, whose
   > `foundry/live_factory.py` targeted the wrong Foundry API (OpenAI *Assistants*
   > `/assistants` + `cognitiveservices.azure.com` scope) and 401'd. The fix
   > (Agent Service `/agents` + `ai.azure.com` scope) rebuilds a new image on
   > merge; **bump `decisionApplyJobImage` to that new merge-SHA tag and redeploy
   > SIT before re-running** the Foundry apply.
3. **One-time RBAC**: the reused agent-host MI (`id-ca-agent-host-ihzhhpf-sit`)
   needs the **`Foundry User`** role (role definition id
   `53ca6127-db72-4b80-b1b0-d745d6d5456d`; `Foundry Project Manager`
   `eadc314b-1a2d-4efa-be10-5d325db5065e` also works) on the eastus2 Foundry
   account for the Foundry Agent Service registration (workstream C). It already
   holds `Cosmos DB Built-in Data Contributor` (granted in
   `infra/modules/cosmos/csa.bicep`) for the Cosmos seed (workstream B):

   ```bash
   mi_principal=$(az identity show -g rg-ihzhhpf-sit -n id-ca-agent-host-ihzhhpf-sit --query principalId -o tsv)
   foundry_id=$(az cognitiveservices account show -g rg-ihzhhpf-sit -n ai-ihzhhpf-sit-eastus2 --query id -o tsv)
   az role assignment create \
     --assignee-object-id "$mi_principal" \
     --assignee-principal-type ServicePrincipal \
     --role "Foundry User" \
     --scope "$foundry_id"
   ```

   > **Corrected 2026-07-26:** `Cognitive Services User` (the 1.1.0 prereq) is the
   > wrong audience for the Agent Service data plane and returns **401** on
   > `POST /agents/{name}`. The Agents plane requires a bearer token for
   > `https://ai.azure.com/.default`, which `Foundry User` / `Foundry Project
   > Manager` grant — not `Cognitive Services User` or `Azure AI Developer`.
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

`az containerapp job start --command/--args` overrides are ignored here (Hard
gate note), so swap the job template command with `az containerapp job update
--yaml`, run it, then revert. Replace `<operator-handle>` with the approving
operator's GitHub handle.

1. **Capture the current template** (to revert to afterwards):

   ```bash
   az containerapp job show -n caj-decision-apply-ihzhhpf-sit -g rg-ihzhhpf-sit -o yaml > job.plan.yaml
   cp job.plan.yaml job.apply.yaml
   ```

2. **Edit `job.apply.yaml`** — in `properties.template.containers[0]`, change the
   **third `command` token** (the `sh -c` script string) to the apply chain,
   leaving the first two tokens (`/bin/sh`, `-c`) and everything else untouched.

   > **⚠ `seed_live` is NOT idempotent.** `coordination.seed_live --action apply`
   > calls `open_plan`, which raises `ValueError: plan already exists` (Cosmos
   > `409 Conflict`) when the WS-B `plans` documents are already present, and a
   > `&&` chain aborts there **before** the Foundry step ever runs. So the seed
   > step belongs **only on the very first apply** (empty Cosmos). Since the seed
   > was applied live on 2026-07-26, **every subsequent run must be Foundry-only.**

   **First apply only** (empty Cosmos — seed then register `ooa`):

   ```text
   cd /app/data-platform/decision && \
   python -m coordination.seed_live --action apply --approved-to-apply <operator-handle> && \
   python -m foundry.register_decision_tier --action apply --role ooa --approved-to-apply <operator-handle>
   ```

   **Re-run (Cosmos already seeded — Foundry-only, register `ooa`):**

   ```text
   cd /app/data-platform/decision && \
   python -m foundry.register_decision_tier --action apply --role ooa --approved-to-apply <operator-handle>
   ```

   > **Test ooa first.** Either chain above registers **only `ooa`**. Verify the
   > new `ooa-agent` version preserved its model/instructions/`fabric_dataagent`
   > tool and gained `decision_tier_coordination_ooa` (Step 3) **before** fanning
   > out. To fan out after ooa is confirmed, replace the `register_decision_tier`
   > line with (drop `ooa` from the list if it is already registered):
   > `for r in dca bmca orsa sba csa; do python -m foundry.register_decision_tier --action apply --role $r --approved-to-apply <operator-handle> || exit 1; done`

3. **Apply the template, run, and wait**:

   ```bash
   az containerapp job update -n caj-decision-apply-ihzhhpf-sit -g rg-ihzhhpf-sit --yaml job.apply.yaml
   az containerapp job start  -n caj-decision-apply-ihzhhpf-sit -g rg-ihzhhpf-sit
   ```

4. **Revert the template to plan-first** (mandatory — no drift):

   ```bash
   az containerapp job update -n caj-decision-apply-ihzhhpf-sit -g rg-ihzhhpf-sit --yaml job.plan.yaml
   ```

Expected outcome:

1. Execution `Succeeded`.
2. On a **first apply**, `seed_live` wrote the six-role `plans` +
   `proposed_actions` documents (`{"applied": true, "approvedBy":
   "<operator-handle>"}`). On a **Foundry-only re-run**, `seed_live` is not in the
   chain (the seed already exists — re-running it would fail with `plan already
   exists`).
3. `register_decision_tier` registered a new agent version carrying
   `decision_tier_coordination_<role>` on each agent (idempotent — re-runs report
   `toolAlreadyPresent` and do not append a duplicate tool).

### Step 3: Verify

Cosmos (control-plane count is sufficient; data-plane read is in-VNet):

```bash
az cosmosdb sql container show -a cosmos-csa-ihzhhpf-sit -g rg-ihzhhpf-sit -d csa -n plans -o table
az cosmosdb sql container show -a cosmos-csa-ihzhhpf-sit -g rg-ihzhhpf-sit -d csa -n proposed_actions -o table
```

Foundry (the Agent Service `/agents` list shows the eight platform agents; each
decision-tier agent's latest version carries the `decision_tier_role` metadata
and a `decision_tier_coordination_<role>` function tool):

```bash
token=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)
curl -s -H "Authorization: Bearer $token" \
  "https://ai-ihzhhpf-sit-eastus2.services.ai.azure.com/api/projects/ai-ihzhhpf-sit-eastus2-project/agents?api-version=2025-05-15-preview" \
  | python -c "import sys,json; [print(a['name'], (a.get('versions',{}).get('latest',{}).get('metadata',{}) or {}).get('decision_tier_role')) for a in json.load(sys.stdin).get('value',[])]"
```

## Handoff to Next Process

After a successful live apply, proceed with:

- End-to-end demo of the live propose → HITL approve → deterministic recompute
  thread against SIT Cosmos.
- Updating the Sprint 26 design spec §9 status if the golden thread is verified
  live.

## Troubleshooting

If the Cosmos seed fails with `plan already exists` (`CosmosResourceExistsError`,
`409 Conflict`):

1. This is expected once the WS-B seed has been applied — `seed_live` is not
   idempotent. Remove `coordination.seed_live` from the apply chain and run the
   **Foundry-only** re-run variant (Step 2). Do **not** delete the existing
   Cosmos documents to force a re-seed.

If the Cosmos seed fails with a network/timeout error:

1. Confirm the job ran on the agent-host CAE (VNet-integrated) — check the
   `environmentId` on the job resource.
2. Confirm `CSA_COSMOS_ENDPOINT` resolves to the private IP from inside the VNet
   (the private DNS zone `privatelink.documents.azure.com` must be linked).

If the Foundry registration fails with 401/403:

1. Confirm the one-time `Foundry User` grant (Prerequisite 3) landed and has
   propagated. A 401 with an otherwise-valid token almost always means the MI
   holds `Cognitive Services User` (wrong audience) instead of `Foundry User` /
   `Foundry Project Manager`.
2. Confirm the token audience is `https://ai.azure.com/.default` (the Agent
   Service data plane), not `cognitiveservices.azure.com`.
3. Confirm `AZURE_CLIENT_ID` matches `id-ca-agent-host-ihzhhpf-sit`.

If a CLI refuses with an approver error:

1. The handle was empty or bot-like — re-run with a human operator's handle.

## Evidence Checklist

Before closing this runbook execution:

- [ ] Step 1 dry-run execution `Succeeded` with plan output captured.
- [ ] Approver handle (repo-write human) recorded for the live apply.
- [ ] Step 2 live apply execution `Succeeded`.
- [ ] `plans` + `proposed_actions` show the seeded documents.
- [ ] Six Foundry agents carry the `decision_tier_coordination_<role>` tool.
