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
5. **HTTP surface** (`api/app.py`) — FastAPI: `GET /healthz`, `GET /agents`,
   `POST /agents/{name}/chat`, `POST /agents/{name}/tools/{tool}`.

The chat model is injected behind a `ChatModel` protocol. Dev/CI use a
deterministic `MockChatModel`; deploy-time uses a live Foundry client. The
Cosmos and Redis clients are in-memory stand-ins with a swap-for-live design, so
unit tests install no cloud SDKs (the live SDKs are the optional `runtime` extra).

> The HTTP package is named `api` (not `http`) to avoid shadowing the Python
> standard-library `http` module that Starlette imports.

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
