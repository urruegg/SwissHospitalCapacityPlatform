# hcc-agent-host — Sprint 13 T5

Container Apps **agent-host**: loads the Sprint 11 prompt manifests
(`agents/<name>/manifest.yaml`, `runtime: agent-host`) and dispatches to a
Microsoft Foundry chat model (ADR-0008: Foundry = model provider only). Persists
conversations + audit to Cosmos DB and caches grounding in Redis (ADR-0007).
Language choice recorded in [ADR-0022](../../docs/adr/0022-agent-host-language-python-fastapi.md)
(Python + FastAPI).

## What it does

1. **Manifest loader** (`manifests/loader.py`) — validates and loads every
   `runtime: agent-host` manifest at startup; skips Fabric IQ-hosted agents.
2. **Orchestrator** (`orchestrator/dispatch.py`) — composes system prompt +
   Fabric grounding, calls the injected `ChatModel`, redacts the output, and
   persists the conversation + audit record.
3. **HITL gate enforcer** (`hitl/gate_enforcer.py`) — deny-by-default check for
   HITL-01..HITL-05 against the ADR-0007 §6 approval-evidence schema. Positive
   path per-agent enforcement lands in follow-up sprints.
4. **Redaction** (`orchestrator/redaction.py`) — masks secret-like tokens and
   Swiss AHV identifiers before any text is returned or persisted.
5. **HTTP surface** (`api/app.py`) - FastAPI: `GET /healthz`, `GET /agents`,
   `POST /agents/{name}/chat`, `POST /agents/{name}/tools/{tool}`,
   `GET /agents/{role}/worklist`, `POST /agents/{role}/decisions`
   (Sprint 39 P2 operational loop, see below).

The chat model is injected behind a `ChatModel` protocol. Dev/CI use a
deterministic `MockChatModel`; deploy-time uses a live Foundry client. The
Cosmos and Redis clients are in-memory stand-ins with a swap-for-live design, so
unit tests install no cloud SDKs (the live SDKs are the optional `runtime` extra).

> The HTTP package is named `api` (not `http`) to avoid shadowing the Python
> standard-library `http` module that Starlette imports.

## Operational loop (Sprint 39 P2)

Two endpoints host the closed-loop engine **in-process** on real EPIC-sim gold
(seeded snapshot; no deploy, no live write-back):

- **`GET /agents/{role}/worklist`** - the role's live observations + one grounded
  `DC-INSIGHT`-style recommendation. The predicted impact is the deterministic
  `compute_expected_impact` on the seeded occupancy, never an LLM guess.
- **`POST /agents/{role}/decisions`** - a human `accept`/`deny` drives the real
  decision-tier HITL (`plan_runtime.approve_action` -> `ActuationConsumer` ->
  `DC-SIM-OUTCOME-v1`). Accept applies the lever to the in-host `SimState` (the
  worklist shrinks on a re-GET); deny is a no-op that mutates nothing.

The host holds one stateful `SimState` per hospital (`loop/sim_registry.py`),
seeded from a materialized gold snapshot via the Plan 1 `gold_seed`
(`closedloop.gold_seed`). The snapshot path is `GOLD_SNAPSHOT_PATH` (default = the
committed USZ fixture at `apps/sim-capacity/tests/fixtures/gold-snapshot-usz.json`).
This is the **simulated-MVP** seam; the live golden-source read is the follow-on.

**HITL / no-deploy posture (`NFR-UXL-001`):** only a human Entra oid
(`X-User-Oid`) may act - a missing oid is refused `401`, and a bot/self approver
is refused `403` by `approve_action`. This plan changes code only; **enabling it
in SIT is the gated image-tag bump** (`agentHostImage` in
`infra/environments/sit.bicepparam` -> `cd-infra-deploy-sit` ->
`cd-infra-deploy-prod`), which requires the `approved-to-apply` confirmation per
[AGENTS.md Sec 4](../../AGENTS.md#4-confirmation-rule-for-deploy--delete).

## Develop

```bash
cd apps/hcc-agent-host
pip install ".[dev]"      # fastapi + pytest + httpx (no cloud SDKs)
python -m pytest          # 31 unit + integration tests
```

Run the host locally (deterministic mock model, in-memory persistence):

```bash
pip install ".[runtime]"          # only needed for live Azure wiring
uvicorn api.app:app --app-dir src --reload
# GET  http://127.0.0.1:8000/agents
# POST http://127.0.0.1:8000/agents/bmca-agent/chat  {"prompt": "Station B ist fast voll"}
```

## Deploy (gated)

Infra is authored under
[`infra/modules/agent-host/`](../../infra/modules/agent-host/) — Container App +
Redis + Cosmos (ADR-0007). It is **not** deployed by this PR. Deployment is a
`deploy`-ceiling action and requires the `approved-to-apply` gate per
[AGENTS.md §4](../../AGENTS.md#4-confirmation-rule-for-deploy--delete).

```bash
az bicep build --file infra/modules/agent-host/main.bicep
az deployment group what-if -g <rg> -f infra/modules/agent-host/main.bicep
```
