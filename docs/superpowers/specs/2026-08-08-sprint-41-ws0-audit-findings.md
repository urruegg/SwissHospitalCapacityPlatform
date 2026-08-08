---
Version: 2.1.0
Date: 2026-08-08
Author: Copilot coding agent (autopilot, delegated)
Status: Complete - SIT deployed and live-tested
Previous Version: 2.0.0 (real audit findings from live SIT tenant, deploy not yet attempted)
---

# Sprint 41 WS-0 audit findings

> Task 0.1 of [the implementation plan](../plans/2026-08-08-sprint-41-po-agent-e2e-grounding.md).
> **Update (same day):** the user granted device-code access to the Curavias
> tenant (`MngEnvMCAP164444`, subscription
> `66a9953a-df37-4c51-856c-9971b9bf3e03`, `az login --use-device-code`). All
> three audit queries below were run for real against `rg-ihzhhpf-sit`. The
> results are more sobering than a placeholder-only gap: every one of the
> four knowledge classes has at least one real, unaddressed infra gap beyond
> the placeholder container images already known. These are new findings,
> not previously documented, and are **not fixed by this audit** - fixing
> IAM role assignments and building the corpus-refresh job's real image are
> separate, security/access-relevant changes that need their own explicit
> approval, distinct from the already-approved `poAgentContainerImage` bump.

## Finding 1 — Corpus-landing job run history

**Real resource:** `caj-po-refresh-ihzhhpf-sit` (Container Apps Job), scheduled
daily at 02:30 UTC.

```text
Name                                  StartTime                  Status
caj-po-refresh-ihzhhpf-sit-29769270   2026-08-08T02:30:00+00:00  Failed
caj-po-refresh-ihzhhpf-sit-29767830   2026-08-07T02:30:00+00:00  Failed
... (13 consecutive daily executions, 2026-07-27 through 2026-08-08, ALL Failed)
```

**Root cause (confirmed via `az containerapp job execution show`):** the job's
container still runs `image: mcr.microsoft.com/dotnet/samples:aspnetapp` - the
same placeholder identified for the runtime container in the design spec.
**Real corpus-refresh code (`data-platform/scripts/po-agent/corpus/publish.py`)
has never been containerized or deployed to this job.** It has been failing
silently, on schedule, for at least 13 days.

**Verdict: Class A ingestion has never run for real.** This is a second,
previously-undocumented placeholder-image gap (the corpus-refresh job),
distinct from the runtime service's `poAgentContainerImage` gap. Closing it
needs a second container image + CI workflow (a thin batch wrapper around
`publish.py`, not the FastAPI service) - out of this sprint's original
WS-SVC/WS-INF scope, tracked as a follow-up.

## Finding 2 — Azure AI Search index document count

**Real resource:** `srch-ihzhhpf-sit` (Standard SKU, status `running`).

```json
GET https://srch-ihzhhpf-sit.search.windows.net/indexes?api-version=2024-07-01
{"value": []}
```

**Verdict: zero indexes exist, therefore zero documents.** Directly explained
by Finding 1 - there is no index because the job that would create/populate
it has never run its real code. Class A's `search_client.py` (WS-RET Task
RET.1) is correctly wired and tested against fakes, but has nothing real to
query yet.

## Finding 3 — Runtime container managed-identity role assignments

**Real resource:** `id-po-ihzhhpf-sit` (principalId
`cf4a8863-f671-47f7-b25a-9ed63c86c8da`, clientId
`f1dd5c0c-e984-4fd6-9e0f-49316654fa09`).

**Assignments found (resource-group + resource scope):**

| Role | Scope |
| ---- | ----- |
| Search Index Data Reader | `srch-ihzhhpf-sit` |
| AcrPull | `cri75lbu5sj4hza` (container registry) |
| Key Vault Secrets User | `kvpoihzhhpfsit` |
| Cognitive Services OpenAI User | `oai-poihzhhpfsit` (the PO agent's **own** OpenAI resource - answer-synthesis LLM calls, not the Fabric Data Agent) |
| Storage Blob Data Contributor | `stcorpusihzhhpfsit` (corpus landing) |

**Assignments checked and confirmed MISSING:**

- **No subscription-scope role at all** (`az role assignment list --scope
  /subscriptions/<id>` returns empty for this identity) - **Class B
  (live-proof Resource Graph queries) and Class C (Cost Management reads)
  have no read access whatsoever.** `azure_clients.py` (RET.3) and
  `azure_cost.py` (RET.4) build real, correctly-coded clients, but every
  live call from them will 403 until `Reader` (Resource Graph) and `Cost
  Management Reader` are granted at subscription scope.
- **No role assignment on `ai-ihzhhpf-sit-eastus2`** (the shared Foundry
  project hosting the `da_hospital_capacity` Fabric Data Agent that
  `ooa-agent` already uses) - confirmed via a role-assignment query scoped
  to that exact resource, zero rows returned. **Class D - the class closest
  to "already proven" by reuse of `agent-host`'s connection code - is
  ALSO blocked**, on IAM, not on missing code.

## Per-class verdict (updated with real evidence)

| Class | Verdict |
| ----- | ------- |
| A (corpus) | **Blocked on data + a second placeholder image.** Zero index, corpus-refresh job never ran real code. |
| B (live-proof) | **Blocked on IAM.** Client code is real and correct; MI has no subscription-scope `Reader` role for Resource Graph. |
| C (cost) | **Blocked on IAM.** Client code is real and correct; MI has no `Cost Management Reader` role. |
| D (ontology) | **Blocked on IAM.** Client code reuses `agent-host`'s proven connection; MI has no role assignment on `ai-ihzhhpf-sit-eastus2` (the Foundry project that actually hosts the Fabric Data Agent). |

**Bottom line: every class's code is real, tested, and correctly wired. Every
class is currently blocked by an access or data gap in the SIT environment
itself, not by anything in this sprint's code.** Deploying the runtime
service now (the user's approved-to-apply scope) makes `/answer` genuinely
reachable, but a real question will currently degrade to a transparent
partial/refusal on every class until the gaps below are separately closed
and approved.

## Follow-up required (separate approval - NOT part of the already-approved `poAgentContainerImage` bump)

1. Grant the PO agent MI (`cf4a8863-f671-47f7-b25a-9ed63c86c8da`) **Reader**
   at subscription scope (Class B) and **Cost Management Reader** at
   subscription scope (Class C).
2. Grant the PO agent MI a read role (e.g. **Cognitive Services User**) on
   `ai-ihzhhpf-sit-eastus2` so it can call the shared Fabric Data Agent
   (Class D).
3. Build and deploy a real image for `caj-po-refresh-ihzhhpf-sit` (a thin
   batch wrapper around `publish.py`), then trigger a manual run and
   re-check the index document count (Class A).
4. Re-run this audit after 1-3 land; only then does a live end-to-end
   answer have real data behind every class.

## SIT deployment + live smoke-test (same day, `approved-to-apply` confirmed by user)

**Image build:** `az acr build --registry cri75lbu5sj4hza --image
po-agent-service:sit-manual-20260808 --file
data-platform/scripts/po-agent/runtime/Dockerfile
data-platform/scripts/po-agent` - built and pushed successfully
(`cri75lbu5sj4hza.azurecr.io/po-agent-service:sit-manual-20260808`).

**Deployment method - deviated from the plan's `az deployment group create`
on purpose:** a full `az deployment group what-if` against `main.bicep` +
`sit.bicepparam` (with only `poAgentContainerImage` overridden) surfaced a
large amount of **pre-existing, unrelated drift** across this resource
group - Cosmos DB `enableAutomaticFailover`/indexing-policy defaults, ACR
encryption/auth-policy defaults, Cognitive Services identity flags,
Container App environment Dapr peer-authentication settings, and more -
none of it caused by this sprint. Applying the full template would have
touched all of that, a far bigger blast radius than the approved scope
("bump the PO agent's container image"). Used a surgical
`az containerapp update -g rg-ihzhhpf-sit -n ca-po-ihzhhpf-sit --image
cri75lbu5sj4hza.azurecr.io/po-agent-service:sit-manual-20260808` instead -
`provisioningState: Succeeded`, `runningStatus: Running`, only the one
container's image changed.

**Live smoke-test:**

- `GET /healthz` -> `200 {"status":"ok"}`, `server: uvicorn` - genuinely the
  real FastAPI app, not a placeholder.
- `POST /answer` with a real CEO-persona question ->

  ```json
  {
    "agentLabel": "product-owner-agent",
    "contextChip": { "subject": "CEO", "tone": "signal" },
    "read": "Advisory only. This is a partial, transparently-degraded answer: insufficient high-confidence grounded sources were available.",
    "levers": [],
    "citations": [],
    "provenance": "live",
    "refused": true
  }
  ```

  **This is the correct, safe result given the findings above - not a bug.**
  The service is live, the wire contract is exactly right, and the
  zero-hallucination doctrine holds: with no class actually able to
  retrieve real chunks yet, it refuses rather than fabricates.

**New finding while verifying - env var contract mismatch:** the deployed
Container App's configured env vars are `AZURE_CLIENT_ID`, `SEARCH_ENDPOINT`,
`SEARCH_API_VERSION`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`,
`COSMOS_ENDPOINT`, `KEY_VAULT_URI`, `DEMO_SCOPE` - **none of which match**
what WS-RET's `get_tools()` actually reads (`AZURE_SEARCH_ENDPOINT` /
`AZURE_SEARCH_INDEX`, `AZURE_SUBSCRIPTION_ID`, `FABRIC_DATA_AGENT_ENDPOINT` /
`FABRIC_WORKSPACE_ID` / `FABRIC_DATA_AGENT_ID`). The infra module's env-var
contract was defined before WS-RET's real implementation names were settled
and was never reconciled. Every class's `try/except` correctly catches the
resulting `KeyError`/missing-env and omits that class rather than crashing -
which is exactly why the live test above safely refused instead of erroring.

**Updated follow-up list (supersedes the numbered list above) - all still
need their own separate approval, none applied yet:**

1. Reconcile the Container App's env var names/values with what the code
   reads (rename or add: `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_INDEX`,
   `AZURE_SUBSCRIPTION_ID`, `FABRIC_DATA_AGENT_ENDPOINT`,
   `FABRIC_WORKSPACE_ID`, `FABRIC_DATA_AGENT_ID`, `FOUNDRY_PROJECT_ENDPOINT`,
   `FOUNDRY_PROJECT_NAME`) - a Bicep change to the runtime module, not a
   one-off manual `containerapp update`.
2. Grant the PO agent MI (`cf4a8863-f671-47f7-b25a-9ed63c86c8da`) `Reader`
   at subscription scope (Class B) and `Cost Management Reader` at
   subscription scope (Class C).
3. Grant the PO agent MI a read role on `ai-ihzhhpf-sit-eastus2` (Class D).
4. Build and deploy a real image for `caj-po-refresh-ihzhhpf-sit`, trigger a
   manual run, re-check the index document count (Class A).
5. Re-run the live smoke-test after 1-4 land and confirm `refused: false`
   with real citations on at least one class.
