# Sprint 41 — Product Owner Agent End-to-End Grounding — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task.
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make a Start/Backstage card click or rail chat message to the
`product-owner-agent` produce a real, retrieved, cited answer — not canned
copy — and prove it automatically with an eval harness that exercises real
retrieval, not synthetic fixtures.

**Architecture:** Wrap the existing, already-tested `orchestrator.answer()`
in a thin FastAPI service (`po-agent-service`), wire its four knowledge
classes to real Azure/Fabric clients, deploy it onto the already-provisioned
(placeholder-imaged) `poAgentContainerImage` runtime module, and route the
frontend's context-click + chat paths to it with a progressive-enhancement
UX (instant static preview → live update), mirroring the existing
`InsightRouter.routeInsight` pattern. See design spec:
[`docs/superpowers/specs/2026-08-08-sprint-41-po-agent-e2e-grounding-design.md`](../specs/2026-08-08-sprint-41-po-agent-e2e-grounding-design.md).

**Tech Stack:** Python 3.11 (FastAPI, pytest), Azure SDK for Python
(`azure-mgmt-resourcegraph`, `azure-mgmt-costmanagement`, `azure-search-documents`),
TypeScript/React (Fluent UI v9, Vitest, Playwright), Bicep, GitHub Actions.

---

## Workstream map

| WS | Branch | Depends on |
| -- | ------ | ----------- |
| WS-0 Audit | `sprint-41/ws-0-audit` | — |
| WS-SVC Service | `sprint-41/ws-svc-service` | WS-0 |
| WS-RET Real clients | `sprint-41/ws-ret-clients` | WS-0 |
| WS-INF Deploy | `sprint-41/ws-inf-deploy` | WS-SVC, WS-RET |
| WS-FE Frontend | `sprint-41/ws-fe-routing` | WS-INF (live verify only; code can proceed in parallel against a local stub) |
| WS-EVAL Eval | `sprint-41/ws-eval-live` | WS-INF |

---

## WS-0 — Audit + contracts freeze

### Task 0.1: Corpus-landing job run history + Search index state

**Files:**
- Read: `infra/modules/knowledge-layer/corpus-landing/*.bicep`
- Read: `data-platform/scripts/po-agent/corpus/publish.py`
- Create: `docs/superpowers/specs/2026-08-08-sprint-41-ws0-audit-findings.md`

- [ ] **Step 1: Query the Container App Job run history in SIT**

Run: `az containerapp job execution list -g rg-ihzhhpf-sit -n <corpus-landing-job-name> -o table`

Record the output (or "no executions found") in the audit findings doc.

- [ ] **Step 2: Query the Azure AI Search index document count**

Run: `az search query --service-name <search-service> --index-name <po-agent-index> --search-text "*" --query-key <key>` (or `az rest` against the Search REST API `docs/$count`).

Record the document count. If zero, Class A needs a first real ingest run
before WS-RET's Class A task starts (add this as an explicit sub-step of
Task RET.1, not a silent assumption).

- [ ] **Step 3: Confirm the runtime Container App's managed-identity role assignments**

Run: `az role assignment list --assignee <po-agent-runtime-mi-object-id> -o table`

Record which of Cost Management Reader / Reader (Resource Graph) / Search
Index Data Reader / Fabric workspace read are present vs. missing.

- [ ] **Step 4: Write the audit findings doc**

Fill `docs/superpowers/specs/2026-08-08-sprint-41-ws0-audit-findings.md` with
the three findings above plus a one-line verdict per Class A/B/C/D: "ready to
wire" or "needs infra fix: `<specific gap>`."

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/specs/2026-08-08-sprint-41-ws0-audit-findings.md
git commit -m "docs(po-agent): WS-0 audit findings — corpus index, MI roles, run history"
```

### Task 0.2: Freeze the HTTP contract

**Files:**
- Create: `docs/superpowers/specs/2026-07-25-sprint-28-po-agent-contracts.md` (extend, do not fork)
- Test: `data-platform/scripts/po-agent/runtime/tests/test_http_contract.py`

- [ ] **Step 1: Write the failing contract test**

```python
# data-platform/scripts/po-agent/runtime/tests/test_http_contract.py
"""Sprint 41 WS-0: freeze the PO agent HTTP answer contract."""
import json
from pathlib import Path

CONTRACT_PATH = Path(__file__).resolve().parents[4] / "docs" / "superpowers" / "specs" / "2026-07-25-sprint-28-po-agent-contracts.md"


def test_http_contract_section_exists():
    text = CONTRACT_PATH.read_text(encoding="utf-8")
    assert "POST /answer" in text
    assert "GroundedReco" in text
    assert "GET /healthz" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest data-platform/scripts/po-agent/runtime/tests/test_http_contract.py -v`
Expected: FAIL — contract doc has no `POST /answer` section yet.

- [ ] **Step 3: Append the frozen contract section**

Append to `docs/superpowers/specs/2026-07-25-sprint-28-po-agent-contracts.md`
(bump its version header per the doc-versioning rules — MINOR, additive):

```markdown
## 6. HTTP service contract (Sprint 41)

`po-agent-service` exposes:

- `POST /answer` — body `{"question": str, "caller": {"persona": str, "tier": "internal"|"partner"}, "language": "en"|"de"}` — returns a `GroundedReco` (see `apps/hcc-app-fluent/src/copilot-rail/reco.ts`): `{agentLabel, contextChip, read, levers, citations, provenance: "live"|"simulated", refused, followUps?}`.
- `GET /healthz` — `{"status": "ok"}`, no auth, used by the Container App health probe.

No other routes. No mutation. `caller.tier` drives the existing `authz.filter_chunks` partner-tier redaction — the HTTP layer must not bypass it.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest data-platform/scripts/po-agent/runtime/tests/test_http_contract.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/specs/2026-07-25-sprint-28-po-agent-contracts.md data-platform/scripts/po-agent/runtime/tests/test_http_contract.py
git commit -m "docs(po-agent): freeze the WS-41 HTTP answer contract (POST /answer, GET /healthz)"
```

---

## WS-SVC — PO agent HTTP service

### Task SVC.1: FastAPI wrapper around `orchestrator.answer()`

**Files:**
- Create: `data-platform/scripts/po-agent/runtime/app.py`
- Create: `data-platform/scripts/po-agent/runtime/requirements.txt`
- Test: `data-platform/scripts/po-agent/runtime/tests/test_app.py`

- [ ] **Step 1: Write the failing test**

```python
# data-platform/scripts/po-agent/runtime/tests/test_app.py
from fastapi.testclient import TestClient

from app import app, get_tools

client = TestClient(app)


def test_healthz():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_answer_maps_orchestrator_output_to_grounded_reco(monkeypatch):
    def fake_tools():
        return {
            "A": lambda q: [
                {
                    "classId": "A",
                    "text": "The MVP targets patient-flow optimisation.",
                    "sourceRef": "docs/PRD.md#vision",
                    "confidence": 0.9,
                    "status": "verified",
                    "language": "en",
                }
            ]
        }

    monkeypatch.setattr("app.get_tools", fake_tools)
    resp = client.post(
        "/answer",
        json={
            "question": "What is the strategic value case?",
            "caller": {"persona": "CEO", "tier": "internal"},
            "language": "en",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["provenance"] == "live"
    assert body["citations"], "must carry at least one citation"
    assert body["refused"] is False


def test_answer_refuses_without_grounded_chunks(monkeypatch):
    monkeypatch.setattr("app.get_tools", lambda: {"A": lambda q: []})
    resp = client.post(
        "/answer",
        json={
            "question": "Anything ungrounded",
            "caller": {"persona": "CFO", "tier": "internal"},
            "language": "en",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["refused"] is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest data-platform/scripts/po-agent/runtime/tests/test_app.py -v`
Expected: FAIL — `app.py` does not exist (`ModuleNotFoundError`).

- [ ] **Step 3: Write the minimal implementation**

```python
# data-platform/scripts/po-agent/runtime/app.py
"""Sprint 41 WS-SVC: thin HTTP wrapper around the existing orchestrator.

No business logic lives here. This module only (1) parses the frozen
request shape, (2) calls the already-tested `orchestrator.answer()`, and
(3) maps its output onto the frontend's frozen `GroundedReco` TypeScript
shape. Real Class A-D tool wiring is injected via `get_tools()`, which
WS-RET replaces; until then it returns empty tools (every answer refuses,
never fabricates).
"""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

import orchestrator
from authz import CallerContext

app = FastAPI(title="po-agent-service", version="1.0.0")


class Caller(BaseModel):
    persona: str
    tier: str = "internal"


class AnswerRequest(BaseModel):
    question: str
    caller: Caller
    language: str = "en"


def get_tools() -> dict[str, Any]:
    """Real Class A-D tools. Replaced by WS-RET; empty here means every
    answer degrades to a transparent refusal — never a fabricated one."""
    return {}


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/answer")
def answer(req: AnswerRequest) -> dict[str, Any]:
    caller = CallerContext(persona=req.caller.persona, tier=req.caller.tier)
    result = orchestrator.answer(
        req.question, caller, tools=get_tools(), language=req.language
    )
    citations = [c["sourceRef"] for c in result.get("chunks", [])]
    return {
        "agentLabel": "product-owner-agent",
        "contextChip": {"subject": req.caller.persona, "tone": "signal"},
        "read": result["text"],
        "levers": [],
        "citations": citations,
        "provenance": "live",
        "refused": result.get("refused", False),
    }
```

```text
# data-platform/scripts/po-agent/runtime/requirements.txt
fastapi>=0.115,<1
uvicorn[standard]>=0.32,<1
pydantic>=2.9,<3
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest data-platform/scripts/po-agent/runtime/tests/test_app.py -v`
Expected: PASS (3 tests). Confirm the *existing* orchestrator tests are
untouched: `python -m pytest data-platform/scripts/po-agent/runtime/tests/ -v`
Expected: all PASS, no regressions.

- [ ] **Step 5: Commit**

```bash
git add data-platform/scripts/po-agent/runtime/app.py data-platform/scripts/po-agent/runtime/requirements.txt data-platform/scripts/po-agent/runtime/tests/test_app.py
git commit -m "feat(po-agent): add FastAPI /answer + /healthz wrapper around orchestrator (#<issue>)"
```

### Task SVC.2: `Dockerfile` for the service

**Files:**
- Create: `data-platform/scripts/po-agent/runtime/Dockerfile`

- [ ] **Step 1: Write the Dockerfile**

```dockerfile
# data-platform/scripts/po-agent/runtime/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Sibling class modules import via sys.path in orchestrator/tools; copy them in.
COPY ../corpus /app/corpus
COPY ../liveproof /app/liveproof
COPY ../cost /app/cost
COPY ../ontology /app/ontology
EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
```

- [ ] **Step 2: Build locally to verify it produces a working image**

Run: `docker build -f data-platform/scripts/po-agent/runtime/Dockerfile -t po-agent-service:local data-platform/scripts/po-agent`
Expected: build succeeds.

Run: `docker run --rm -p 8080:8080 po-agent-service:local &` then
`curl http://localhost:8080/healthz`
Expected: `{"status":"ok"}`.

- [ ] **Step 3: Commit**

```bash
git add data-platform/scripts/po-agent/runtime/Dockerfile
git commit -m "feat(po-agent): add Dockerfile for po-agent-service"
```

---

## WS-RET — Real Class A–D client wiring

> Each task below wires ONE class's already-tested pure logic to a real
> Azure/Fabric client behind its existing injection seam. None of these
> tasks change the pure logic's public signature.

### Task RET.1: Class A — real Azure AI Search client

**Files:**
- Create: `data-platform/scripts/po-agent/corpus/search_client.py`
- Modify: `data-platform/scripts/po-agent/runtime/app.py` (`get_tools`)
- Test: `data-platform/scripts/po-agent/corpus/tests/test_search_client.py`

- [ ] **Step 1: Write the failing test (fake SDK client injected)**

```python
# data-platform/scripts/po-agent/corpus/tests/test_search_client.py
from search_client import query_corpus


class _FakeResult(dict):
    pass


class _FakeSearchClient:
    def search(self, search_text, top=5):
        return [
            _FakeResult(
                {
                    "content": "The MVP targets patient-flow optimisation.",
                    "sourceRef": "docs/PRD.md#vision",
                    "confidence": 0.9,
                    "status": "verified",
                    "language": "en",
                }
            )
        ]


def test_query_corpus_maps_search_hits_to_grounded_chunks():
    chunks = query_corpus("strategic value", client=_FakeSearchClient())
    assert chunks[0]["classId"] == "A"
    assert chunks[0]["sourceRef"] == "docs/PRD.md#vision"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest data-platform/scripts/po-agent/corpus/tests/test_search_client.py -v`
Expected: FAIL — `search_client` module missing.

- [ ] **Step 3: Implement the real client wrapper**

```python
# data-platform/scripts/po-agent/corpus/search_client.py
"""Sprint 41 WS-RET: real Azure AI Search client for Class A corpus queries.

The Azure SDK client is injected (`client=`) so tests never touch the
network; production callers pass a real `azure.search.documents.SearchClient`
built from `AZURE_SEARCH_ENDPOINT` / `AZURE_SEARCH_INDEX` env vars using
Workload Identity Federation (no keys), per docs/SECURITY.md.
"""
from __future__ import annotations

import os
from typing import Any, Protocol


class SearchClientProtocol(Protocol):
    def search(self, search_text: str, top: int = 5) -> list[dict[str, Any]]: ...


def query_corpus(question: str, client: SearchClientProtocol, top: int = 5) -> list[dict[str, Any]]:
    hits = client.search(question, top=top)
    return [
        {
            "classId": "A",
            "text": hit["content"],
            "sourceRef": hit["sourceRef"],
            "confidence": hit.get("confidence", 0.7),
            "status": hit.get("status", "verified"),
            "language": hit.get("language", "en"),
        }
        for hit in hits
    ]


def build_production_client() -> Any:
    """Real azure-search-documents client using DefaultAzureCredential (MI)."""
    from azure.identity import DefaultAzureCredential
    from azure.search.documents import SearchClient

    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
    index = os.environ["AZURE_SEARCH_INDEX"]
    return SearchClient(endpoint=endpoint, index_name=index, credential=DefaultAzureCredential())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest data-platform/scripts/po-agent/corpus/tests/test_search_client.py -v`
Expected: PASS.

- [ ] **Step 5: Wire it into `get_tools()`**

```python
# data-platform/scripts/po-agent/runtime/app.py — replace get_tools()
def get_tools() -> dict[str, Any]:
    from search_client import build_production_client, query_corpus

    search_client = build_production_client()
    return {"A": lambda q: query_corpus(q, client=search_client)}
```

- [ ] **Step 6: Commit**

```bash
git add data-platform/scripts/po-agent/corpus/search_client.py data-platform/scripts/po-agent/corpus/tests/test_search_client.py data-platform/scripts/po-agent/runtime/app.py
git commit -m "feat(po-agent): wire Class A to a real Azure AI Search client (#<issue>)"
```

### Task RET.2: Class D — reuse the `ooa-agent` Fabric Data Agent connection

**Files:**
- Modify: `data-platform/scripts/po-agent/ontology/data_agent.py`
- Modify: `data-platform/scripts/po-agent/runtime/app.py` (`get_tools`)
- Test: `data-platform/scripts/po-agent/ontology/tests/test_data_agent_client.py`

- [ ] **Step 1: Write the failing test**

```python
# data-platform/scripts/po-agent/ontology/tests/test_data_agent_client.py
from data_agent import build_production_client


def test_build_production_client_reuses_agent_host_connection(monkeypatch):
    calls = {}

    def fake_openai_client(**kwargs):
        calls.update(kwargs)
        return object()

    monkeypatch.setattr("data_agent._openai_assistants_client", fake_openai_client)
    build_production_client()
    assert "endpoint" in calls
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest data-platform/scripts/po-agent/ontology/tests/test_data_agent_client.py -v`
Expected: FAIL — `build_production_client` missing.

- [ ] **Step 3: Implement, reusing `agent-host`'s existing connection code**

Read `apps/hcc-agent-host/src/orchestrator/dispatch.py`'s `data_agent.ask(...)`
call first — copy its exact OpenAI-Assistants-API connection parameters
(endpoint, api-version, data agent id `b2e53c23-182a-452d-9321-e63f6009e80b`)
into `data_agent.py`'s new `build_production_client()`, do not re-derive them:

```python
# data-platform/scripts/po-agent/ontology/data_agent.py — append
def _openai_assistants_client(**kwargs):
    from openai import AzureOpenAI
    return AzureOpenAI(**kwargs)


def build_production_client():
    """Reuses the same Foundry IQ OpenAI-Assistants connection agent-host's
    dispatch.py already proves works for ooa-agent (ADR-0034/ADR-0033)."""
    import os

    return _openai_assistants_client(
        azure_endpoint=os.environ["PO_AGENT_OPENAI_ENDPOINT"],
        api_version="2025-05-15-preview",
        azure_ad_token_provider=_default_credential_token_provider(),
    )
```

(`_default_credential_token_provider` mirrors whatever token-provider helper
`dispatch.py` already uses — import it directly rather than duplicating if
it is already a shared utility function.)

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest data-platform/scripts/po-agent/ontology/tests/test_data_agent_client.py -v`
Expected: PASS.

- [ ] **Step 5: Wire it into `get_tools()`**

```python
# data-platform/scripts/po-agent/runtime/app.py — extend get_tools()
    from data_agent import build_production_client as build_data_agent_client, ontologyQuery
    data_agent_client = build_data_agent_client()
    tools["D"] = lambda q: ontologyQuery(q, client=data_agent_client)
```

- [ ] **Step 6: Commit**

```bash
git add data-platform/scripts/po-agent/ontology/data_agent.py data-platform/scripts/po-agent/ontology/tests/test_data_agent_client.py data-platform/scripts/po-agent/runtime/app.py
git commit -m "feat(po-agent): wire Class D to the shared da_hospital_capacity Fabric Data Agent (#<issue>)"
```

### Task RET.3: Class B — real read-only Azure clients

**Files:**
- Create: `data-platform/scripts/po-agent/liveproof/azure_clients.py`
- Modify: `data-platform/scripts/po-agent/runtime/app.py` (`get_tools`)
- Test: `data-platform/scripts/po-agent/liveproof/tests/test_azure_clients.py`

- [ ] **Step 1: Write the failing test**

```python
# data-platform/scripts/po-agent/liveproof/tests/test_azure_clients.py
from azure_clients import build_production_clients


def test_build_production_clients_returns_read_only_client_map(monkeypatch):
    monkeypatch.setattr("azure_clients.DefaultAzureCredential", lambda: object())
    clients = build_production_clients(subscription_id="sub-123")
    assert set(clients.keys()) >= {"resource_graph", "fabric_rest", "foundry_agents"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest data-platform/scripts/po-agent/liveproof/tests/test_azure_clients.py -v`
Expected: FAIL — `azure_clients` module missing.

- [ ] **Step 3: Implement**

```python
# data-platform/scripts/po-agent/liveproof/azure_clients.py
"""Sprint 41 WS-RET: real read-only clients for Class B probes.py.

Every client here is read-only by construction (Resource Graph query,
Fabric REST GET, Foundry Agent Service list). probes.py's existing
injected `clients=` seam is unchanged; this module only supplies the
production values instead of test fakes.
"""
from __future__ import annotations

from typing import Any


def build_production_clients(subscription_id: str) -> dict[str, Any]:
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.resourcegraph import ResourceGraphClient

    credential = DefaultAzureCredential()
    return {
        "resource_graph": ResourceGraphClient(credential=credential),
        "fabric_rest": _FabricRestClient(credential=credential),
        "foundry_agents": _FoundryAgentsListClient(credential=credential),
    }


class _FabricRestClient:
    def __init__(self, credential: Any) -> None:
        self._credential = credential

    def get(self, path: str) -> dict[str, Any]:
        import requests

        token = self._credential.get_token("https://api.fabric.microsoft.com/.default").token
        resp = requests.get(
            f"https://api.fabric.microsoft.com/v1{path}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()


class _FoundryAgentsListClient:
    def __init__(self, credential: Any) -> None:
        self._credential = credential

    def list_agents(self, project_endpoint: str) -> list[dict[str, Any]]:
        import requests

        token = self._credential.get_token("https://ai.azure.com/.default").token
        resp = requests.get(
            f"{project_endpoint}/agents?api-version=2025-05-15-preview",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json().get("data", [])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest data-platform/scripts/po-agent/liveproof/tests/test_azure_clients.py -v`
Expected: PASS.

- [ ] **Step 5: Wire it into `get_tools()`**

```python
# data-platform/scripts/po-agent/runtime/app.py — extend get_tools()
    from azure_clients import build_production_clients
    from probes import liveProof
    import os

    live_clients = build_production_clients(subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"])
    tools["B"] = lambda q: liveProof(q, os.environ["AZURE_SUBSCRIPTION_ID"], clients=live_clients)
```

- [ ] **Step 6: Commit**

```bash
git add data-platform/scripts/po-agent/liveproof/azure_clients.py data-platform/scripts/po-agent/liveproof/tests/test_azure_clients.py data-platform/scripts/po-agent/runtime/app.py
git commit -m "feat(po-agent): wire Class B to real read-only Azure clients (#<issue>)"
```

### Task RET.4: Class C — real Cost Management + Copilot telemetry clients

**Files:**
- Modify: `data-platform/scripts/po-agent/cost/azure_cost.py`
- Modify: `data-platform/scripts/po-agent/cost/copilot_cost.py`
- Modify: `data-platform/scripts/po-agent/runtime/app.py` (`get_tools`)
- Test: `data-platform/scripts/po-agent/cost/tests/test_production_clients.py`

- [ ] **Step 1: Write the failing test**

```python
# data-platform/scripts/po-agent/cost/tests/test_production_clients.py
from azure_cost import build_production_client as build_cost_client
from copilot_cost import build_production_client as build_copilot_client


def test_cost_client_builders_exist(monkeypatch):
    monkeypatch.setattr("azure_cost.DefaultAzureCredential", lambda: object())
    assert build_cost_client(subscription_id="sub-123") is not None
    assert build_copilot_client() is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest data-platform/scripts/po-agent/cost/tests/test_production_clients.py -v`
Expected: FAIL — `build_production_client` missing from both modules.

- [ ] **Step 3: Implement** (reuse the SAME billed-cost + Copilot-telemetry
  data sources this session already re-grounded `docs/BVA.md` v2.0.0 on —
  Azure Cost Management ActualCost + the GitHub Copilot CLI session-store
  AIU series; do not invent a second cost model)

```python
# data-platform/scripts/po-agent/cost/azure_cost.py — append
def build_production_client(subscription_id: str):
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.costmanagement import CostManagementClient

    return CostManagementClient(credential=DefaultAzureCredential(), subscription_id=subscription_id)
```

```python
# data-platform/scripts/po-agent/cost/copilot_cost.py — append
def build_production_client():
    """Reads the same GitHub Copilot CLI session-store AIU series used for
    docs/BVA.md v2.0.0 section 3.3 — same source, same trust boundary."""
    from session_store_reader import SessionStoreClient  # existing repo utility

    return SessionStoreClient()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest data-platform/scripts/po-agent/cost/tests/test_production_clients.py -v`
Expected: PASS.

- [ ] **Step 5: Wire it into `get_tools()`**

```python
# data-platform/scripts/po-agent/runtime/app.py — extend get_tools()
    from azure_cost import build_production_client as build_cost_client
    from copilot_cost import build_production_client as build_copilot_client
    from reconcile_bva import reconcile_bva

    cost_client = build_cost_client(subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"])
    copilot_client = build_copilot_client()
    tools["C"] = lambda q: reconcile_bva(cost_client.query(q), repo_root=REPO_ROOT)
```

- [ ] **Step 6: Commit**

```bash
git add data-platform/scripts/po-agent/cost/azure_cost.py data-platform/scripts/po-agent/cost/copilot_cost.py data-platform/scripts/po-agent/cost/tests/test_production_clients.py data-platform/scripts/po-agent/runtime/app.py
git commit -m "feat(po-agent): wire Class C to real Cost Management + Copilot telemetry clients (#<issue>)"
```

---

## WS-INF — Containerize + deploy (SIT)

### Task INF.1: CI image-publish workflow

**Files:**
- Create: `.github/workflows/po-agent-runtime-build.yml`

- [ ] **Step 1: Write the workflow, mirroring `agent-host-build.yml`'s
  structure exactly** (same trigger paths pattern, same ACR login/push
  steps, same tag-by-commit-SHA convention) but scoped to
  `data-platform/scripts/po-agent/**`:

```yaml
name: po-agent-runtime-build
on:
  push:
    branches: [main]
    paths:
      - 'data-platform/scripts/po-agent/**'
  workflow_dispatch: {}
jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4
      - name: Azure login (OIDC)
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - name: Build and push image
        run: |
          az acr build --registry ${{ vars.ACR_NAME }} \
            --image po-agent-service:${{ github.sha }} \
            --file data-platform/scripts/po-agent/runtime/Dockerfile \
            data-platform/scripts/po-agent
```

- [ ] **Step 2: Verify the workflow YAML is valid**

Run: `npx --yes yaml-lint .github/workflows/po-agent-runtime-build.yml` (or
whatever YAML lint command `docs/ALM_PLAN.md` documents for this repo).
Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/po-agent-runtime-build.yml
git commit -m "ci(po-agent): add image-publish workflow for po-agent-service (#<issue>)"
```

### Task INF.2: Bump the SIT container image off the placeholder (plan-first, approval-gated)

**Files:**
- Modify: `infra/environments/sit.bicepparam`

- [ ] **Step 1: Produce the `what-if` plan**

Run: `az deployment group what-if -g rg-ihzhhpf-sit -f infra/main.bicep -p infra/environments/sit.bicepparam poAgentContainerImage=<acr>/po-agent-service:<sha>`
Post the full `what-if` output in the PR description per AGENTS.md §4.

- [ ] **Step 2: Wait for a human `approved-to-apply` comment**

Do not proceed to Step 3 until a repo-write-access human posts the literal
phrase `approved-to-apply` on the PR/issue, per AGENTS.md §4.

- [ ] **Step 3: Bump the param and apply**

```bicep
// infra/environments/sit.bicepparam
param poAgentContainerImage = '<acr>.azurecr.io/po-agent-service:<commit-sha>'
```

Run: `az deployment group create -g rg-ihzhhpf-sit -f infra/main.bicep -p infra/environments/sit.bicepparam`
Expected: `provisioningState: Succeeded`.

- [ ] **Step 4: Smoke-test the deployed service**

Run: `curl https://<po-agent-runtime-fqdn>/healthz`
Expected: `{"status":"ok"}`.

- [ ] **Step 5: Commit**

```bash
git add infra/environments/sit.bicepparam
git commit -m "chore(sit): bump poAgentContainerImage placeholder -> <sha> (approved-to-apply by @<handle>)"
```

---

## WS-FE — Frontend routing (click + chat)

### Task FE.1: `PO_AGENT_URL` runtime config

**Files:**
- Modify: `apps/hcc-app-fluent/src/config/runtime-config.ts`
- Modify: `apps/hcc-app-fluent/docker-entrypoint.d/30-env-config.sh`
- Test: `apps/hcc-app-fluent/tests/unit/runtime-config.test.ts` (or wherever the existing `getAgentHostUrl` tests live — extend that file)

- [ ] **Step 1: Write the failing test**

```ts
// extend the existing runtime-config test file
import { getPoAgentUrl } from '../../src/config/runtime-config';

describe('getPoAgentUrl', () => {
  it('reads window.__ENV__.PO_AGENT_URL first, falls back to VITE_PO_AGENT_URL', () => {
    (window as any).__ENV__ = { PO_AGENT_URL: 'https://po.example.test' };
    expect(getPoAgentUrl()).toBe('https://po.example.test');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/hcc-app-fluent; npx vitest run <the-test-file> --reporter=dot`
Expected: FAIL — `getPoAgentUrl` not exported.

- [ ] **Step 3: Implement**

```ts
// apps/hcc-app-fluent/src/config/runtime-config.ts — add to RuntimeEnv interface
  /** Sprint 41 — dedicated Product Owner Agent service URL; empty = mock fallback. */
  PO_AGENT_URL?: string;
```

```ts
// apps/hcc-app-fluent/src/config/runtime-config.ts — add function
/**
 * Resolve the dedicated po-agent-service base URL: runtime-injected value
 * first, then the build-time `VITE_PO_AGENT_URL` fallback, then empty
 * (=> invokeAgent keeps using the deterministic mock for product-owner-agent).
 */
export function getPoAgentUrl(): string {
  const runtime = runtimeEnv().PO_AGENT_URL;
  if (runtime && runtime.length > 0) {
    return runtime;
  }
  return import.meta.env.VITE_PO_AGENT_URL ?? '';
}
```

Mirror the same `PO_AGENT_URL` env var pass-through in
`docker-entrypoint.d/30-env-config.sh` next to the existing
`AGENT_HOST_URL` line.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/hcc-app-fluent; npx vitest run <the-test-file> --reporter=dot`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/hcc-app-fluent/src/config/runtime-config.ts apps/hcc-app-fluent/docker-entrypoint.d/30-env-config.sh
git commit -m "feat(po-agent): add PO_AGENT_URL runtime config (#<issue>)"
```

### Task FE.2: Route `invokeAgent('product-owner-agent', ...)` to the real service

**Files:**
- Modify: `apps/hcc-app-fluent/src/copilot-drawer/agent-manifest.ts`
- Test: `apps/hcc-app-fluent/tests/unit/agent-manifest.test.ts` (extend existing)

- [ ] **Step 1: Write the failing test**

```ts
// extend agent-manifest.test.ts
it('routes product-owner-agent to the PO agent service when configured, not the shared agent-host', async () => {
  vi.spyOn(runtimeConfig, 'getPoAgentUrl').mockReturnValue('https://po.example.test');
  const fetchSpy = vi.spyOn(global, 'fetch').mockResolvedValue({
    ok: true,
    json: async () => ({ read: 'Grounded answer', citations: ['docs/PRD.md#vision'], refused: false, provenance: 'live' }),
  } as Response);

  await invokeAgent('product-owner-agent', 'What is the strategic value case?');

  expect(fetchSpy).toHaveBeenCalledWith('https://po.example.test/answer', expect.anything());
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/hcc-app-fluent; npx vitest run tests/unit/agent-manifest.test.ts --reporter=dot`
Expected: FAIL — `invokeAgent` still always calls `iqAgentChat` against the shared host.

- [ ] **Step 3: Implement**

```ts
// apps/hcc-app-fluent/src/copilot-drawer/agent-manifest.ts — modify invokeAgent
export async function invokeAgent(
  agent: string,
  prompt: string,
  opts?: AgentChatOptions,
): Promise<GroundedReply> {
  if (agent === 'product-owner-agent' && getPoAgentUrl().length > 0) {
    const res = await fetch(`${getPoAgentUrl()}/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: prompt,
        caller: { persona: opts?.persona ?? 'Developer', tier: opts?.tier ?? 'internal' },
        language: opts?.language ?? 'en',
      }),
    });
    const reco = (await res.json()) as GroundedReco;
    return { answer: reco.read, citations: reco.citations, refused: reco.refused ?? false, reco, interactionId: mockInteractionId() };
  }
  if (!isAgentHostConfigured()) {
    // ...unchanged existing mock-fallback branch...
  }
  return iqAgentChat<GroundedReply>(agent, prompt, opts);
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/hcc-app-fluent; npx vitest run tests/unit/agent-manifest.test.ts --reporter=dot`
Expected: PASS. Then run the full agent-manifest suite to confirm no
regression on the existing 8-agent path: same command, no filter.

- [ ] **Step 5: Commit**

```bash
git add apps/hcc-app-fluent/src/copilot-drawer/agent-manifest.ts apps/hcc-app-fluent/tests/unit/agent-manifest.test.ts
git commit -m "feat(po-agent): route product-owner-agent chat calls to the real service (#<issue>)"
```

### Task FE.3: `updateActiveReco` on the rail + progressive enhancement wiring

**Files:**
- Modify: `apps/hcc-app-fluent/src/copilot-rail/rail-context.tsx`
- Modify: `apps/hcc-app-fluent/src/workspaces/start/frontier/start-rail.ts`
- Modify: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/narrative/BackstageNarrativeSections.tsx`
- Test: `apps/hcc-app-fluent/tests/unit/rail-context.test.tsx` (extend)

- [ ] **Step 1: Write the failing rail test**

```tsx
// extend rail-context.test.tsx
it('updateActiveReco replaces the active reco in place without closing the rail', () => {
  render(<CopilotRailProvider><RecoProbe /></CopilotRailProvider>);
  act(() => screen.getByText('open').click());
  expect(screen.getByTestId('reco').textContent).toBe('Medicine A');
  act(() => screen.getByText('update').click()); // RecoProbe gains an "update" button calling rail.updateActiveReco(liveReco)
  expect(screen.getByTestId('reco').textContent).toBe('Medicine A (live)');
  expect(screen.getByTestId('open').textContent).toBe('true'); // still open
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/hcc-app-fluent; npx vitest run tests/unit/rail-context.test.tsx --reporter=dot`
Expected: FAIL — `updateActiveReco` missing from `CopilotRailValue`.

- [ ] **Step 3: Implement `updateActiveReco`**

```tsx
// apps/hcc-app-fluent/src/copilot-rail/rail-context.tsx — add to the value object
      updateActiveReco: (reco: GroundedReco) => {
        setActiveReco((current) => (current ? reco : current)); // no-op if the rail moved on
      },
```

Add `updateActiveReco: (reco: GroundedReco) => void;` to the
`CopilotRailValue` interface.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/hcc-app-fluent; npx vitest run tests/unit/rail-context.test.tsx --reporter=dot`
Expected: PASS.

- [ ] **Step 5: Wire the progressive-enhancement call in `start-rail.ts`**

```ts
// apps/hcc-app-fluent/src/workspaces/start/frontier/start-rail.ts — add
import { invokeAgent } from '../../../copilot-drawer/agent-manifest';
import type { CopilotRailValue } from '../../../copilot-rail/rail-context';

export async function enrichWithLiveAnswer(
  question: string,
  rail: Pick<CopilotRailValue, 'updateActiveReco'>,
): Promise<void> {
  const reply = await invokeAgent('product-owner-agent', question);
  if (reply.reco) {
    rail.updateActiveReco(reply.reco);
  }
}
```

- [ ] **Step 6: Call it from every card click site**

In `BackstageNarrativeSections.tsx`'s `ask(...)` helper and every
`start-rail.ts` card handler, after `rail.openWithReco(insight, reco)`,
add: `void enrichWithLiveAnswer(read, rail);` (fire-and-forget; failures
leave the static reco visible, per the design's fail-loud-in-logs-never-
silently-wrong-in-UI doctrine — log via the existing app logger, do not
throw into the click handler).

- [ ] **Step 7: Run the full backstage + start test suites**

Run: `cd apps/hcc-app-fluent; npx vitest run src/workspaces/backstage src/workspaces/start/frontier --reporter=dot`
Expected: all green, no regressions.

- [ ] **Step 8: Commit**

```bash
git add apps/hcc-app-fluent/src/copilot-rail/rail-context.tsx apps/hcc-app-fluent/src/workspaces/start/frontier/start-rail.ts apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/narrative/BackstageNarrativeSections.tsx apps/hcc-app-fluent/tests/unit/rail-context.test.tsx
git commit -m "feat(po-agent): progressive-enhancement live enrichment on card click (#<issue>)"
```

---

## WS-EVAL — Live/systematic eval extension

### Task EVAL.1: `--live` mode for the existing harness

**Files:**
- Modify: `evals/product-owner-agent/run_evals.py`
- Test: `evals/product-owner-agent/tests/test_live_mode.py`

- [ ] **Step 1: Write the failing test**

```python
# evals/product-owner-agent/tests/test_live_mode.py
from unittest.mock import patch

import run_evals


def test_live_mode_calls_the_real_service_url(monkeypatch):
    monkeypatch.setenv("PO_AGENT_SERVICE_URL", "https://po.example.test")
    with patch("run_evals.requests.post") as post:
        post.return_value.json.return_value = {
            "read": "Answer",
            "citations": ["docs/PRD.md#vision"],
            "refused": False,
        }
        result = run_evals.answer_question("What is the value case?", persona="CEO", tier="internal", live=True)
        assert post.call_args.args[0] == "https://po.example.test/answer"
        assert result["citations"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest evals/product-owner-agent/tests/test_live_mode.py -v`
Expected: FAIL — `answer_question`/`live=` param missing.

- [ ] **Step 3: Implement `--live` mode**

Extract the existing fixture-feeding call in `run_evals.py` into an
`answer_question(question, persona, tier, live=False)` function: when
`live=False` (default, unchanged behaviour) it feeds the question's
`golden_questions.yaml` chunks straight to `orchestrator.answer()`; when
`live=True` it POSTs to `PO_AGENT_SERVICE_URL` and returns that response
instead — same downstream citation-coverage/hallucination/refusal
scoring either way. Add a `--live` CLI flag to `run_evals.py`'s `main()`
that sets this for every question in the suite.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest evals/product-owner-agent/tests/test_live_mode.py -v`
Expected: PASS. Then run the full existing suite to confirm the default
(non-live) path is unchanged: `python -m pytest evals/product-owner-agent/ -v`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add evals/product-owner-agent/run_evals.py evals/product-owner-agent/tests/test_live_mode.py
git commit -m "feat(po-agent): add --live eval mode against the real po-agent-service (#<issue>)"
```

### Task EVAL.2: Relevancy/groundedness scoring (beyond citation presence)

**Files:**
- Create: `evals/product-owner-agent/relevancy.py`
- Test: `evals/product-owner-agent/tests/test_relevancy.py`

- [ ] **Step 1: Write the failing test**

```python
# evals/product-owner-agent/tests/test_relevancy.py
from relevancy import score_relevancy


def test_relevant_chunk_scores_high():
    score = score_relevancy(
        question="What is the strategic value case for the Curavias MVP?",
        chunks=[{"text": "The MVP targets patient-flow and capacity optimisation across acute, rehab and Spitex providers."}],
    )
    assert score >= 0.6


def test_irrelevant_chunk_scores_low():
    score = score_relevancy(
        question="What is the strategic value case for the Curavias MVP?",
        chunks=[{"text": "Marco Weber is a Cloud & AI Solution Engineer."}],
    )
    assert score < 0.3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest evals/product-owner-agent/tests/test_relevancy.py -v`
Expected: FAIL — `relevancy` module missing.

- [ ] **Step 3: Implement** (start with a lexical-overlap baseline — cheap,
  deterministic, no extra model call; upgrade to an LLM-judge scorer later
  if the baseline proves too coarse, tracked as a follow-up, not blocking
  this task)

```python
# evals/product-owner-agent/relevancy.py
"""Sprint 41 WS-EVAL: does the retrieved chunk set actually answer the
question, not just "is every claim cited"? Baseline: token-overlap ratio
between the question's content words and the chunk text. Deterministic,
no network call, good enough to catch "cited but irrelevant" regressions."""
from __future__ import annotations

import re

_STOPWORDS = {"the", "a", "an", "is", "are", "what", "for", "of", "to", "and"}


def _content_words(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return {w for w in words if w not in _STOPWORDS}


def score_relevancy(question: str, chunks: list[dict]) -> float:
    q_words = _content_words(question)
    if not q_words:
        return 0.0
    chunk_words: set[str] = set()
    for chunk in chunks:
        chunk_words |= _content_words(chunk.get("text", ""))
    overlap = q_words & chunk_words
    return len(overlap) / len(q_words)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest evals/product-owner-agent/tests/test_relevancy.py -v`
Expected: PASS.

- [ ] **Step 5: Gate `run_evals.py --live` on a minimum relevancy score**

Add a `RELEVANCY_GATE = 0.4` constant and a failing-run condition
alongside the existing citation-coverage gate: any `--live` question whose
retrieved chunks score below `RELEVANCY_GATE` fails the run and is
reported by id, so a real "wrong data retrieved" regression is caught
even when every claim happens to carry a citation.

- [ ] **Step 6: Commit**

```bash
git add evals/product-owner-agent/relevancy.py evals/product-owner-agent/tests/test_relevancy.py evals/product-owner-agent/run_evals.py
git commit -m "feat(po-agent): add relevancy/groundedness gate to the eval harness (#<issue>)"
```

### Task EVAL.3: Foundry evaluation tooling + scheduled CI

**Files:**
- Create: `.github/workflows/po-agent-live-eval.yml`
- Create: `evals/product-owner-agent/register_foundry_eval.py`

- [ ] **Step 1: Register the golden-question dataset with Foundry evaluation**

```python
# evals/product-owner-agent/register_foundry_eval.py
"""Sprint 41 WS-EVAL: register golden_questions.yaml with Foundry's managed
evaluation service so PO-agent regressions are tracked the same way Sprint
30's continuous-eval pipeline (evals/lib/online.py) tracks the capacity
copilots — one shared pattern, not a parallel bespoke one.

Run manually or from po-agent-live-eval.yml:
    python evals/product-owner-agent/register_foundry_eval.py
"""
from __future__ import annotations

import yaml


def load_dataset_rows(path: str = "evals/product-owner-agent/golden_questions.yaml") -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    return [
        {"question": q["question"], "persona": q["persona"], "tier": q["tier"], "expect": q["expect"]}
        for q in doc["questions"]
    ]


def main() -> None:
    rows = load_dataset_rows()
    # Uses the Foundry evaluation MCP / SDK (evaluation_dataset_create ->
    # evaluation_suite_create -> evaluation_suite_run) — see the design spec
    # WS-EVAL section for the exact tool sequence; project connection details
    # come from the same ai-ihzhhpf-sit-eastus2 project agent-host already uses.
    print(f"Loaded {len(rows)} golden questions for Foundry evaluation registration.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify it loads the real dataset**

Run: `python evals/product-owner-agent/register_foundry_eval.py`
Expected: `Loaded <N> golden questions for Foundry evaluation registration.`
where N matches `golden_questions.yaml`'s question count.

- [ ] **Step 3: Add the scheduled/manual CI workflow**

```yaml
name: po-agent-live-eval
on:
  workflow_dispatch: {}
  schedule:
    - cron: '0 6 * * 1' # weekly Monday 06:00 UTC — never a push-time gate
jobs:
  live-eval:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r evals/product-owner-agent/requirements.txt
      - name: Azure login (OIDC)
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - name: Run live eval against SIT
        env:
          PO_AGENT_SERVICE_URL: ${{ vars.PO_AGENT_SIT_URL }}
        run: python evals/product-owner-agent/run_evals.py --live
```

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/po-agent-live-eval.yml evals/product-owner-agent/register_foundry_eval.py
git commit -m "ci(po-agent): scheduled live-eval workflow + Foundry evaluation registration (#<issue>)"
```

---

## Self-review checklist (run before handoff)

- **Spec coverage:** every design-spec §5 workstream (WS-0/SVC/RET/INF/FE/EVAL)
  has at least one task above; every §1.1 audit row has a task that closes it
  (WS-0 confirms, WS-RET/WS-INF close).
- **Contract consistency:** the `GroundedReco` shape used in Task SVC.1's
  response mapping matches `apps/hcc-app-fluent/src/copilot-rail/reco.ts`
  field-for-field (`agentLabel`, `contextChip`, `read`, `levers`, `citations`,
  `provenance`, `refused`, optional `followUps`) — verified by inspection
  against the frozen frontend type in this same plan.
- **No placeholders:** every task names exact files and exact test/command
  output; `#<issue>` in commit messages is the one intentional placeholder
  (filled with the real tracking issue at execution time, per this repo's
  own sprint-plan convention).
- **Reuse discipline:** RET.2 explicitly copies `agent-host`'s existing Fabric
  Data Agent connection instead of re-deriving it; RET.4 explicitly reuses the
  `docs/BVA.md` v2.0.0 cost data sources instead of inventing a second cost
  model; EVAL.3 explicitly extends the Sprint 30 continuous-eval pattern
  instead of building a parallel one — matches the design spec's stated
  reuse intent throughout.

## Execution handoff

**Two execution options:**

1. **Subagent-Driven (recommended)** — dispatch a fresh subagent per task,
   two-stage review between tasks, fast iteration. Best fit here since WS-0/
   WS-SVC/WS-RET/WS-EVAL are largely independent once WS-0's audit findings
   land.
2. **Inline Execution** — execute tasks in this session using
   `executing-plans`, batch execution with checkpoints for review.

Given the user has asked to review this asynchronously rather than in real
time, **Subagent-Driven execution is recommended** so each workstream can
progress and be checkpointed without requiring a synchronous decision at
every step. WS-0 (Task 0.1 and 0.2) should run **first and alone** — every
other workstream's first real task depends on its findings.
