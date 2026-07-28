# Sprint 30 - Closed-loop capture container SIT/PROD parity evidence

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | 1.0.0 (initial) |

## 1. Summary

Sprint 30 shipped the closed-loop **capture middleware** (the agent-host writes a
`DC-AGENT-INTERACTION-v1` record for every turn to the `agent_interactions`
Cosmos container - `apps/hcc-agent-host/src/orchestrator/dispatch.py` ->
`persistence.write("agent_interactions", record)`), but the container itself was
never added to the agent-host Cosmos Bicep module. A live control-plane query of
both environments confirmed `agent_interactions` was **absent in SIT and PROD**,
so the loop had no runtime persistence sink.

This document records the plan-first `what-if`, the gated provisioning, and the
live proof that the capture sink now exists **at parity** in both regions, plus
the deterministic proof that the environment-agnostic loop code passes the
offline evaluation gate.

**Verdict: parity proven** - SIT (`westus2`) and PROD (`switzerlandnorth`) both
expose the identical 4-container `agenthost` set including `agent_interactions`
(PK `/conversationKey`, Hash); the offline gate passes 100%.

## 2. Environment

Subscription `66a9953a-df37-4c51-856c-9971b9bf3e03`, tenant
`1337187a-4c41-4da9-8fca-731bba7a4329` (MngEnvMCAP164444), short name `ihzhhpf`.
Synthetic data only, no PHI ([ADR-0016](../../adr/0016-no-phi-in-mvp-demo-scope.md)).

| Env | Region | Cosmos account | Database |
|-----|--------|----------------|----------|
| SIT | westus2 ([ADR-0013](../../adr/0013-temporary-us-region-demo-scope.md)) | `cosmos-ihzhhpf-sit` | `agenthost` |
| PROD | switzerlandnorth (GA, [ADR-0037](../../adr/0037-prod-region-switzerland-north-greenfield.md)) | `cosmos-ihzhhpf-prod` | `agenthost` |

**Network constraint ([ADR-0029](../../adr/0029-agent-host-cosmos-reachability.md)).**
Both accounts are `publicNetworkAccess: Disabled` + `disableLocalAuth: true`
(private endpoint, Managed Identity only). Container provisioning is a
**control-plane (ARM)** operation and is reachable; **data-plane** capture writes
occur **in-VNet** from the agent-host at runtime. This evidence therefore proves
the sink at parity via the control plane; live traffic is produced by the
agent-host inside the VNet.

## 3. Approval

`approved-to-apply` granted in-session by repo OWNER **@urruegg** on
**2026-07-28T15:03+02:00** for provisioning the `agent_interactions` container in
SIT + PROD (`deploy` side-effect ceiling per
[AGENTS.md section 4](../../../AGENTS.md)).

## 4. Method (least-blast-radius container create)

Rather than a full `infra/main.bicep` environment redeploy (which resumes Fabric
capacity and re-what-ifs ML/Foundry), the container was added surgically per
environment, and the IaC was updated to match (no drift):

1. **IaC** - added `agent_interactions` (PK `/conversationKey`) to the `containers`
   var in `infra/modules/agent-host/cosmos.bicep`; `az bicep build` clean.
2. **SIT** -
   `az cosmosdb sql container create -a cosmos-ihzhhpf-sit -g rg-ihzhhpf-sit -d agenthost -n agent_interactions --partition-key-path /conversationKey`.
3. **PROD** -
   `az cosmosdb sql container create -a cosmos-ihzhhpf-prod -g rg-ihzhhpf-prod -d agenthost -n agent_interactions --partition-key-path /conversationKey`.

The Bicep change keeps the next full `cd-infra-deploy` reconcile idempotent.

## 5. Plan-first evidence - `what-if`

Module-scoped `az deployment group what-if` on
`infra/modules/agent-host/cosmos.bicep`, both resource groups, showed the single
intended create:

```text
SIT : + Microsoft.DocumentDB/.../sqlDatabases/agenthost/containers/agent_interactions
PROD: Resource changes: 1 to create, 4 to modify, 1 no change, 64 to ignore.
      + Microsoft.DocumentDB/.../sqlDatabases/agenthost/containers/agent_interactions
```

The 4 "modify" entries are known `what-if` noise (default indexing policy +
read-only computed properties absent from the minimal template - e.g.
`minimalTlsVersion`, `sqlEndpoint`, `indexingPolicy.automatic`); they are not
changed by this PR and appear on any deploy of this module. **Zero deletes.**

## 6. Evidence - live `agenthost` container set (post-apply)

### 6.1 SIT (`cosmos-ihzhhpf-sit`, westus2)

```text
Name                Pk
------------------  ----------------
agent_interactions  /conversationKey
approval-events     /correlationId
audit               /correlationId
conversations       /conversationId
```

### 6.2 PROD (`cosmos-ihzhhpf-prod`, switzerlandnorth)

```text
Name                Pk
------------------  ----------------
agent_interactions  /conversationKey
approval-events     /correlationId
audit               /correlationId
conversations       /conversationId
```

### 6.3 `agent_interactions` detail (both)

```json
{ "name": "agent_interactions", "pk": ["/conversationKey"], "kind": "Hash" }
```

### 6.4 Parity assertion

```text
SIT  (4): agent_interactions,approval-events,audit,conversations
PROD (4): agent_interactions,approval-events,audit,conversations
PARITY (identical container set + partition keys): True
agent_interactions in SIT:  True  (PK /conversationKey, Hash)
agent_interactions in PROD: True  (PK /conversationKey, Hash)
```

## 7. Parity matrix (capture sink)

| Dimension | SIT (westus2) | PROD (switzerlandnorth) | Verdict |
|---|---|---|---|
| `agenthost` container set | 4 incl. `agent_interactions` | 4 incl. `agent_interactions` | Parity |
| `agent_interactions` partition key | `/conversationKey` (Hash) | `/conversationKey` (Hash) | Parity |
| Capacity mode | serverless | serverless | Parity |
| Data-plane auth | MI/WIF, local auth disabled | MI/WIF, local auth disabled | Parity |
| Network | private endpoint, public disabled | private endpoint, public disabled | Parity |
| IaC declaration | `cosmos.bicep` `agent_interactions` | same module | Parity (single source) |

The container contract is read from the single-source `cosmos.bicep` +
`persistence/cosmos_client.py` (`CONTAINERS` + `PARTITION_KEYS`), so both
environments enforce the identical shape by construction.

## 8. Deterministic loop proof (environment-agnostic code)

The Observe/Evaluate/Curate/Improve code is environment-agnostic (the store is
selected by `COSMOS_*` env via `evals/lib/online_store.build_store_from_env`; the
offline gate uses the versioned golden dataset). Running the gate is deterministic
and identical regardless of environment:

```text
ooa-agent offline gate - 6 interactions
  citation_coverage      pass_rate=100.00% failures=0
  groundedness           pass_rate=100.00% failures=0
  refusal_correctness    pass_rate=100.00% failures=0
  phi_leak               pass_rate=100.00% failures=0
  actionability          pass_rate=100.00% failures=0
  advisory_voice         pass_rate=100.00% failures=0
PASSED: True
```

`evals/` full suite: **167 passed**.

## 9. Non-runtime verification (CI)

* `apps/hcc-agent-host` pytest: full suite green, incl. the new
  `test_cosmos_iac_parity` (asserts every app `CONTAINERS` entry is provisioned
  in `cosmos.bicep` with its matching partition key - locks the drift found here).
* `az bicep build --file infra/modules/agent-host/cosmos.bicep`: clean.

## 10. Residual notes

* The container was applied imperatively for minimal blast radius; the
  `cosmos.bicep` change keeps the next full CD reconcile idempotent (no drift).
* Live data-plane capture is produced by the agent-host **inside the VNet**
  (ADR-0029); it is not seedable from a workstation because public network access
  is disabled. The control-plane parity above proves the sink is present and
  identically shaped in both regions, ready to receive that in-VNet traffic.
* No PHI is captured (NFR-LEARN-001; ADR-0016); PROD residency is satisfied by the
  switzerlandnorth account (NFR-LEARN-002).
