# Sprint 32 — Signal Agent SIT↔PROD agent-host parity evidence

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | 1.0.0 (initial) |

## 1. Summary

The Sprint 32 Signal Agent (SGA) pack (`agents/signal-agent/`) landed on `main`
in [PR #468](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/468)
(`ded7485`) but was **not yet live** in either the SIT or PROD agent-host: both
Container Apps were running image `b796961`, which predates the pack. This
document records the live, read-verified proof that `signal-agent` is now loaded
and dispatchable in **both** environments, at parity.

The agent-host loads any `agents/<name>/manifest.yaml` that declares
`runtime: agent-host` (see `apps/hcc-agent-host/src/manifests/loader.py`), and
the container image bakes in the whole `agents/` folder
(`apps/hcc-agent-host/Dockerfile`, `COPY agents ./agents`). No agent-host code
change is required for a new agent-host pack — the wiring is convention-based.
A repo-manifest regression test
(`tests/unit/test_loader.py::test_loads_real_signal_agent_manifest_from_repo`)
now locks this in so the discovery cannot silently regress.

**Verdict: ✅ Parity proven** — SIT and PROD return the identical 8-agent set,
both including `signal-agent`, both on image `f596cf2`.

## 2. Environment

Subscription `66a9953a-df37-4c51-856c-9971b9bf3e03`, tenant
`1337187a-4c41-4da9-8fca-731bba7a4329` (MngEnvMCAP164444), short name `ihzhhpf`.
Synthetic data only, no PHI ([ADR-0016](../../adr/0016-no-phi-in-mvp-demo-scope.md)).

| Env | Region | Container App | Ingress FQDN |
|-----|--------|---------------|--------------|
| SIT | westus2 ([ADR-0013](../../adr/0013-temporary-us-region-demo-scope.md)) | `ca-agent-host-ihzhhpf-sit` | `ca-agent-host-ihzhhpf-sit.salmonsand-fb86922a.westus2.azurecontainerapps.io` |
| PROD | switzerlandnorth (GA, [ADR-0037](../../adr/0037-prod-region-switzerland-north-greenfield.md)) | `ca-agent-host-ihzhhpf-prod` | `ca-agent-host-ihzhhpf-prod.whiteriver-d854b3bc.switzerlandnorth.azurecontainerapps.io` |

## 3. Approval

`approved-to-apply` granted in-session by repo OWNER **@urruegg** on
**2026-07-28T12:28+02:00** for the SIT + PROD agent-host image roll-forward to
`f596cf2` (`deploy` side-effect ceiling per [AGENTS.md §4](../../../AGENTS.md)).

## 4. Method (least-blast-radius image roll-forward)

Rather than a full `infra/main.bicep` environment redeploy (which resumes Fabric
capacity, re-what-ifs ML/Foundry, and carries a GitHub Environment approval
gate), the change was applied surgically as a single agent-host image swap per
environment, and the IaC param files were reconciled to match:

1. **SIT** — `sit.bicepparam` already declared `f596cf2` (PR #476); the live app
   was lagging at `b796961`. Reconciled live → IaC:
   `az containerapp update -n ca-agent-host-ihzhhpf-sit -g rg-ihzhhpf-sit --image cri75lbu5sj4hza.azurecr.io/hcc-agent-host:f596cf2`.
2. **PROD image promotion** — the PROD ACR held only `b796961`; imported the SIT
   build: `az acr import -n crihzhhpfprod --source cri75lbu5sj4hza.azurecr.io/hcc-agent-host:f596cf2 --image hcc-agent-host:f596cf2`.
3. **PROD** — `az containerapp update -n ca-agent-host-ihzhhpf-prod -g rg-ihzhhpf-prod --image crihzhhpfprod.azurecr.io/hcc-agent-host:f596cf2`,
   and bumped `prod-swn.bicepparam` `agentHostImage` `b796961` → `f596cf2` so the
   next full CD deploy reconciles to the same image (no IaC drift).

`f596cf2` is the newest `main` agent-host build and a superset of `b796961`
(includes signal-agent + all prior agent-host code); both `f596cf2` and the
original landing commit `ded7485` contain `agents/signal-agent/manifest.yaml`.

## 5. Evidence — live `GET /agents`

### 5.1 Before (baseline, both on `b796961`)

Both environments returned the **same 7 host-loaded agents; `signal-agent`
absent**:

```json
[{"name":"bmca-agent"},{"name":"csa-agent"},{"name":"data-quality-agent"},
 {"name":"dca-agent"},{"name":"ooa-agent"},{"name":"orsa-agent"},{"name":"sba-agent"}]
```

### 5.2 After (both on `f596cf2`)

SIT `GET /agents` (revision `ca-agent-host-ihzhhpf-sit--0000008`, `Succeeded`):

```json
[{"name":"bmca-agent","displayName":"BMCA","ceiling":"write"},
 {"name":"csa-agent","displayName":"CSA","ceiling":"write"},
 {"name":"data-quality-agent","displayName":"DATA-QUALITY","ceiling":"write"},
 {"name":"dca-agent","displayName":"DCA","ceiling":"write"},
 {"name":"ooa-agent","displayName":"OOA","ceiling":"write"},
 {"name":"orsa-agent","displayName":"ORSA","ceiling":"write"},
 {"name":"sba-agent","displayName":"SBA","ceiling":"write"},
 {"name":"signal-agent","displayName":"SIGNAL","ceiling":"write"}]
```

PROD `GET /agents` (revision `ca-agent-host-ihzhhpf-prod--0000001`, `Succeeded`):

```json
[{"name":"bmca-agent","displayName":"BMCA","ceiling":"write"},
 {"name":"csa-agent","displayName":"CSA","ceiling":"write"},
 {"name":"data-quality-agent","displayName":"DATA-QUALITY","ceiling":"write"},
 {"name":"dca-agent","displayName":"DCA","ceiling":"write"},
 {"name":"ooa-agent","displayName":"OOA","ceiling":"write"},
 {"name":"orsa-agent","displayName":"ORSA","ceiling":"write"},
 {"name":"sba-agent","displayName":"SBA","ceiling":"write"},
 {"name":"signal-agent","displayName":"SIGNAL","ceiling":"write"}]
```

### 5.3 Parity assertion

```text
SIT  (8): bmca-agent,csa-agent,data-quality-agent,dca-agent,ooa-agent,orsa-agent,sba-agent,signal-agent
PROD (8): bmca-agent,csa-agent,data-quality-agent,dca-agent,ooa-agent,orsa-agent,sba-agent,signal-agent
PARITY (identical agent set): True
signal-agent in SIT:  True
signal-agent in PROD: True
```

## 6. Parity matrix (agent-host / Signal Agent)

| Dimension | SIT (westus2) | PROD (switzerlandnorth) | Verdict |
|---|---|---|---|
| Agent-host image | `cri75lbu5sj4hza.azurecr.io/hcc-agent-host:f596cf2` | `crihzhhpfprod.azurecr.io/hcc-agent-host:f596cf2` | ✅ Parity (same digest, per-env ACR) |
| Host-loaded agent set | 8 agents incl. `signal-agent` | 8 agents incl. `signal-agent` | ✅ Parity |
| `signal-agent` ceiling | `write` | `write` | ✅ Parity |
| `signal-agent` HITL gate | HITL-04 (staff-PII channel activation) | HITL-04 | ✅ Parity |
| MCP tools | `github-mcp` (write) + `fabric-mcp` (read) | same | ✅ Parity |
| IaC param (`agentHostImage`) | `f596cf2` (sit.bicepparam) | `f596cf2` (prod-swn.bicepparam) | ✅ Parity |

The Signal Agent's `write`/HITL-04 posture and MCP tool bindings are read from
the single-source-of-truth manifest `agents/signal-agent/manifest.yaml`, so both
environments enforce the identical contract by construction.

## 7. Non-runtime verification (CI)

* `apps/hcc-agent-host` full pytest suite: **97 passed** (incl. the new
  `test_loads_real_signal_agent_manifest_from_repo` loader regression test).
* Signal modules (`data-platform/signals/`): 11 tests pass (Sprint 32 impl).

## 8. Residual notes

* The image swap was applied imperatively for minimal blast radius; the
  `prod-swn.bicepparam` bump in this PR keeps the next full `cd-infra-deploy-prod`
  reconcile idempotent (no drift). SIT's param was already at `f596cf2`.
* No new environment configuration was required — `signal-agent` grounds via
  `fabric-mcp` (read) and posts via `github-mcp` (write); its tool endpoint stays
  deny-by-default behind the HITL-04 gate (`enforce_gates`).
