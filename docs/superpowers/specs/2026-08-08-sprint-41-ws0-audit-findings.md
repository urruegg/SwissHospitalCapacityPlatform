---
Version: 1.0.0
Date: 2026-08-08
Author: Copilot coding agent (autopilot, delegated)
Status: Partial - blocked on live Azure access
Previous Version: n/a
---

# Sprint 41 WS-0 audit findings

> Task 0.1 of [the implementation plan](../plans/2026-08-08-sprint-41-po-agent-e2e-grounding.md).
> **Blocker:** this session has no live Azure CLI / MCP access to the
> Curavias tenant (`MngEnvMCAP164444`, subscription
> `66a9953a-df37-4c51-856c-9971b9bf3e03`) - both the Azure MCP tools and the
> terminal's `az` CLI are authenticated to an unrelated identity (confirmed:
> `az account show` returns tenant `b829e4ef-...`, and an Azure Resource
> Graph query for `rg-ihzhhpf-sit` returned zero resources). The three real
> queries below could not be run. WS-RET and WS-INF must treat their
> production-client wiring as **implemented and unit-tested against the
> frozen contract, not yet verified against real SIT data**, until someone
> with tenant access runs the commands in this doc and updates the verdict.

## Finding 1 — Corpus-landing job run history

**Not run.** Command to execute once access is available:

```bash
az containerapp job execution list -g rg-ihzhhpf-sit -n <corpus-landing-job-name> -o table
```

**Verdict: unknown.** Until this is run, Task RET.1 must not assume the
Azure AI Search index already has real content — the task's implementation
covers both cases (query an existing index, or note a first-ingest run is
needed) but the actual index document count is unverified.

## Finding 2 — Azure AI Search index document count

**Not run.** Command to execute once access is available:

```bash
az rest --method get --uri "https://<search-service>.search.windows.net/indexes/<po-agent-index>/docs/$count?api-version=2024-07-01" --headers "api-key=<key>"
```

**Verdict: unknown.**

## Finding 3 — Runtime container managed-identity role assignments

**Not run.** Command to execute once access is available:

```bash
az role assignment list --assignee <po-agent-runtime-mi-object-id> -o table
```

**Verdict: unknown.** WS-RET's real client builders (`build_production_client`
functions across Class A/B/C/D) assume Workload Identity Federation with
Cost Management Reader / Reader (Resource Graph) / Search Index Data Reader
/ Fabric workspace read. If any role is missing, the client builders will
fail at runtime with an auth error (fail loud, per the app's existing
`degraded` doctrine) rather than silently fabricating an answer — but the
gap should be closed via a Bicep role-assignment fix, not worked around in
code.

## Per-class verdict

| Class | Verdict |
| ----- | ------- |
| A (corpus) | Unverified — needs Finding 1 + 2 |
| B (live-proof) | Unverified — needs Finding 3 |
| C (cost) | Unverified — needs Finding 3; logic reuses the same Azure Cost Management + Copilot-telemetry sources already proven this session for `docs/BVA.md` v2.0.0, so the *data source* is known-good even though this specific MI's access to it is not yet confirmed |
| D (ontology) | Unverified — needs confirmation that `agent-host`'s existing `da_hospital_capacity` connection permits a second caller identity (the PO service) without a quota/throttle conflict |

## Follow-up required before WS-INF's deploy step and before any PROD claim

1. Someone with `az login` access to the Curavias tenant runs the three
   commands above and updates this doc's verdicts.
2. If Finding 1/2 show an empty index, run a first real corpus ingest
   (`publish.py`) before treating Class A as "wired," not just "coded."
3. If Finding 3 shows missing roles, file an infra fix (Bicep role
   assignment) before WS-INF's deploy step, not as a manual `az role
   assignment create` workaround.
