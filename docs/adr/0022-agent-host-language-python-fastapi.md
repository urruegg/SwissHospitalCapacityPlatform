# ADR-0022 — Agent-host implementation language (Python + FastAPI vs Node + Fastify)

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-07-09 |
| **Deciders** | @urruegg |
| **Superseded by** | — |

> Sprint 13 T5 kickoff mini-ADR. Records the implementation-language choice for
> the Container Apps **agent-host** that loads the Sprint 11 prompt manifests and
> dispatches to a Microsoft Foundry chat model (design spec
> [`2026-07-09-sprint-13-app-design.md`](../superpowers/specs/2026-07-09-sprint-13-app-design.md) §7,
> plan [`2026-07-09-sprint-13-app-plan.md`](../superpowers/plans/2026-07-09-sprint-13-app-plan.md) T5).

## Context

T5 delivers a small HTTP control plane (ADR-0008: application-hosted agents,
Foundry = model provider only) that:

1. loads every `agents/<name>/manifest.yaml` with `runtime: agent-host`,
2. composes a system prompt + Fabric grounding per manifest,
3. calls a Foundry chat-completion deployment,
4. enforces deny-by-default HITL gates (ADR-0007) before any side effect,
5. persists conversations + audit to Cosmos DB and caches grounding in Redis.

Two candidate stacks were considered, both first-class on Azure Container Apps:

1. **Python + FastAPI** — the plan's default. Mature Foundry / Azure OpenAI
   chat-completion SDK (`openai`, `azure-identity`, `azure-cosmos`), Pydantic
   request models, `pytest` + `httpx` TestClient for TDD.
2. **Node + Fastify** — shares TypeScript with the Fluent app (T1–T6); one
   language across the repo's app tier.

## Decision

Use **Python + FastAPI** for the agent-host.

Rationale:

- **SDK maturity** — the Azure OpenAI / Foundry chat-completion and
  `azure-identity` OBO surfaces are most mature in Python; this is the core of
  the host's job.
- **Testability** — FastAPI's `TestClient` (Starlette) plus `pytest` let every
  T5 module start from a failing test (TDD skill) with no live Azure
  dependency; the in-memory Cosmos/Redis stand-ins keep unit tests hermetic.
- **Data-tier alignment** — the Fabric notebooks and semantic-model tests are
  already Python (`infra/modules/data-platform/fabric/notebooks`), so the grounding
  and data-contract code shares a language with the agent-host.
- **Boundary is HTTP + JSON** — the Fluent app talks to the host only over
  `POST /agents/<name>/chat` and `GET /agents`, so a language split across the
  frontend/backend seam costs nothing.

## Consequences

- `apps/hcc-agent-host/` is a `setuptools` Python 3.11 package
  (`pyproject.toml`), tested with `pytest` (`pythonpath = ["src"]`).
- The HTTP package is named `api` (not `http`) to avoid shadowing the Python
  standard-library `http` module that Starlette imports.
- Live Azure SDKs (`azure-identity`, `azure-cosmos`, `redis`, `openai`) are an
  optional `runtime` extra so unit tests install no cloud dependencies.
- The chat model is injected behind a `ChatModel` protocol; dev/CI use a
  deterministic `MockChatModel`, deploy-time uses a live Foundry client.
- Sprints 14+ inherit Python for agent-host extensions; a future move to Node
  would require re-authoring this ADR.

## Alternatives considered

- **Node + Fastify** — rejected for Sprint 13: it would unify the app-tier
  language but trade away the more mature Python Foundry/Cosmos SDKs and the
  Python data-tier alignment for a benefit (single language) that the clean
  HTTP/JSON boundary already neutralises.
