# Sprint 43 WS-1 — Real Foundry Chat Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `MockChatModel` with a real `FoundryResponsesChatModel` that
invokes the 8 registered Microsoft Foundry Agent Service agents
(`bmca-agent`, `ooa-agent`, `dca-agent`, `orsa-agent`, `sba-agent`,
`csa-agent`, `data-quality-agent`, `onboarding-agent`) via the Responses API,
wire it into `hcc-agent-host` behind an env-gated factory (mirroring the
existing `FabricDataAgentClient` pattern), thread it through Bicep, deploy to
SIT, and verify live that every agent now returns a real, non-mock,
non-hardcoded answer.

**Architecture:** A single `FoundryResponsesChatModel` instance (not one per
agent) is constructed once in `HostState.__init__` when
`FOUNDRY_PROJECT_ENDPOINT`/`FOUNDRY_PROJECT_NAME` env vars are set (else
`MockChatModel`, unchanged dev/CI default). The `ChatModel` protocol gains one
keyword-only parameter — `agent_name` — so `Orchestrator.dispatch()` can pass
`manifest.agent` (which is already, by AGENTS.md naming convention, identical
to the registered Foundry Agent name) at call time, letting one client route
to any of the 8 agents without per-agent construction. Token acquisition and
HTTP transport are injected callables (mirrors
`tools/fabric_data_agent_client.py`) so the new class is fully unit-testable
without cloud access.

**Tech Stack:** Python 3.11, FastAPI, `requests` (lazy-imported, already used
transitively in this image), `azure-identity` (already an optional `runtime`
dependency), Bicep (Container Apps env vars), pytest.

**Confirmed live technical contract (Sprint 43 WS-1 Task 0 spike,
2026-08-08):**

- Endpoint: `POST {project_endpoint}/api/projects/{project_name}/openai/v1/responses`
  — **no `api-version` query parameter** on `/v1` paths (returns
  `400 api-version query parameter is not allowed when using /v1 path` if
  present).
- Body: `{"agent_reference": {"name": "<agent-name>", "type": "agent_reference"}, "input": "<text>"}`.
- Auth: `Authorization: Bearer <token>` where the token's scope is
  `https://ai.azure.com/.default` (the `Foundry User` role — already granted
  to `id-ca-agent-host-ihzhhpf-sit`'s MI since 2026-07-26, confirmed via an
  idempotent `az role assignment create` check — **no new RBAC grant needed**).
- Synchronous — the response body has `"status": "completed"` immediately; no
  thread/run/poll loop (unlike the classic Assistants API used by
  `FabricDataAgentClient`).
- Real evidence: a bare `input` with **no grounding context** produced a
  genuine, reasoned GPT-5 response from `bmca-agent` (asked for missing
  bed-state figures, proposed a projection formula, defined pressure bands) —
  categorically different from `MockChatModel`'s hardcoded template
  matching, and the response echoed the agent's own registered
  `decision_tier_coordination_bmca` function tool in its `tools` array,
  confirming the actual registered Agent object (not a bare model deployment)
  was invoked.

---

## File Structure

| File | Responsibility |
| ---- | -------------- |
| `apps/hcc-agent-host/src/orchestrator/dispatch.py` (modify) | `ChatModel` protocol gains `agent_name` kwarg; `dispatch()` passes `manifest.agent` |
| `apps/hcc-agent-host/src/orchestrator/mock_model.py` (modify) | `MockChatModel.complete()` accepts (and ignores) `agent_name` |
| `apps/hcc-agent-host/src/orchestrator/foundry_chat_model.py` (create) | `FoundryResponsesChatModel` — the real client |
| `apps/hcc-agent-host/src/api/app.py` (modify) | `_build_chat_model()` factory + `HostState.__init__` wiring |
| `apps/hcc-agent-host/tests/unit/test_foundry_chat_model.py` (create) | Unit tests for the new client, no cloud calls |
| `apps/hcc-agent-host/tests/unit/test_build_chat_model.py` (create) | Unit tests for the env-gated factory |
| `apps/hcc-agent-host/tests/unit/test_dispatch_grounding_agent.py` (modify) | `_EchoModel.complete()` accepts `agent_name` |
| `apps/hcc-agent-host/tests/unit/test_dispatch_tracing.py` (modify) | `_StubModel.complete()` accepts `agent_name` |
| `apps/hcc-agent-host/tests/unit/test_interaction_capture.py` (modify) | `_StubModel.complete()` accepts `agent_name` |
| `infra/modules/agent-host/container-app.bicep` (modify) | New params `foundryProjectEndpoint`/`foundryProjectName` → env vars |
| `infra/modules/agent-host/main.bicep` (modify) | Pass-through params to `container-app.bicep` |
| `infra/main.bicep` (modify) | Top-level params → pass-through to the `agentHost` module |
| `infra/environments/sit.bicepparam` (modify) | Set the real SIT values |

**Do not touch:** `infra/main.json`, `infra/modules/agent-host/*.json` — these
are stale compiled-ARM companions; `cd-infra-deploy-sit.yml` deploys directly
from `infra/main.bicep` (`--template-file infra/main.bicep`), so the `.json`
files are not read by CI and editing them is unrelated scope.

---

### Task 1: Extend the `ChatModel` protocol with `agent_name`

**Files:**
- Modify: `apps/hcc-agent-host/src/orchestrator/dispatch.py`
- Modify: `apps/hcc-agent-host/src/orchestrator/mock_model.py`
- Modify: `apps/hcc-agent-host/tests/unit/test_dispatch_grounding_agent.py`
- Modify: `apps/hcc-agent-host/tests/unit/test_dispatch_tracing.py`
- Modify: `apps/hcc-agent-host/tests/unit/test_interaction_capture.py`
- Test: `apps/hcc-agent-host/tests/unit/test_mock_model.py` (create)

- [ ] **Step 1: Write the failing test for `MockChatModel` accepting `agent_name`**

Create `apps/hcc-agent-host/tests/unit/test_mock_model.py`:

```python
"""Unit tests for MockChatModel's agent_name kwarg (Sprint 43 WS-1 prep)."""

from __future__ import annotations

from orchestrator.mock_model import MockChatModel


def test_complete_accepts_agent_name_kwarg():
    model = MockChatModel()
    answer = model.complete(
        "sys", "Wie ist die Auslastung?", [{"ward": "B", "occupied": 46, "capacity": 50}],
        agent_name="bmca-agent",
    )
    assert "92%" in answer


def test_complete_agent_name_is_optional():
    model = MockChatModel()
    # Existing call sites that omit agent_name must keep working (default "").
    answer = model.complete("sys", "q", [])
    assert "Keine Auslastungsdaten" in answer
```

- [ ] **Step 2: Run the test to verify it fails**

Run (from `apps/hcc-agent-host/`): `python -m pytest tests/unit/test_mock_model.py -v`
Expected: FAIL with `TypeError: complete() got an unexpected keyword argument 'agent_name'`

- [ ] **Step 3: Update the `ChatModel` protocol and `dispatch()` call site**

In `apps/hcc-agent-host/src/orchestrator/dispatch.py`, replace:

```python
class ChatModel(Protocol):
    """Foundry chat-completion surface (ADR-0008)."""

    def complete(self, system_prompt: str, user_prompt: str, grounding: list[dict[str, Any]]) -> str:
        ...
```

with:

```python
class ChatModel(Protocol):
    """Foundry chat-completion surface (ADR-0008).

    ``agent_name`` (Sprint 43 WS-1) identifies which registered Foundry Agent
    to invoke — always ``manifest.agent`` (AGENTS.md naming convention: the
    manifest's ``agent`` field is identical to the registered Foundry Agent
    name). A single ``ChatModel`` instance serves every agent-host manifest;
    routing happens per-call, not per-instance.
    """

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        grounding: list[dict[str, Any]],
        *,
        agent_name: str = "",
    ) -> str:
        ...
```

Then, in the same file, update the call site inside `dispatch()`:

```python
            with self.tracer.span(
                "agent.model", agent=manifest.agent, model=type(self.chat_model).__name__
            ):
                raw_answer = self.chat_model.complete(system_prompt, user_prompt, grounding)
```

to:

```python
            with self.tracer.span(
                "agent.model", agent=manifest.agent, model=type(self.chat_model).__name__
            ):
                raw_answer = self.chat_model.complete(
                    system_prompt, user_prompt, grounding, agent_name=manifest.agent
                )
```

- [ ] **Step 4: Update `MockChatModel.complete()`'s signature**

In `apps/hcc-agent-host/src/orchestrator/mock_model.py`, replace:

```python
class MockChatModel:
    def complete(
        self, system_prompt: str, user_prompt: str, grounding: list[dict[str, Any]]
    ) -> str:
```

with:

```python
class MockChatModel:
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        grounding: list[dict[str, Any]],
        *,
        agent_name: str = "",
    ) -> str:
```

(the body is unchanged — the mock never used `agent_name`, it stays
ignored.)

- [ ] **Step 5: Run the test to verify it passes**

Run: `python -m pytest tests/unit/test_mock_model.py -v`
Expected: PASS (2 passed)

- [ ] **Step 6: Update the three test fakes that implement `ChatModel`**

In `apps/hcc-agent-host/tests/unit/test_dispatch_grounding_agent.py`, replace:

```python
class _EchoModel:
    def complete(self, system_prompt, user_prompt, grounding):
        return f"answer using {len(grounding)} grounding item(s)"
```

with:

```python
class _EchoModel:
    def complete(self, system_prompt, user_prompt, grounding, *, agent_name=""):
        return f"answer using {len(grounding)} grounding item(s)"
```

In `apps/hcc-agent-host/tests/unit/test_dispatch_tracing.py`, replace:

```python
class _StubModel:
    def complete(self, system_prompt, user_prompt, grounding):
        return "Auslastung Station B: 92%."
```

with:

```python
class _StubModel:
    def complete(self, system_prompt, user_prompt, grounding, *, agent_name=""):
        return "Auslastung Station B: 92%."
```

In `apps/hcc-agent-host/tests/unit/test_interaction_capture.py`, replace:

```python
class _StubModel:
    def complete(self, system_prompt, user_prompt, grounding):
        return "Auslastung Station B: 92%."
```

with:

```python
class _StubModel:
    def complete(self, system_prompt, user_prompt, grounding, *, agent_name=""):
        return "Auslastung Station B: 92%."
```

- [ ] **Step 7: Run the full test suite to verify nothing else broke**

Run: `python -m pytest -v`
Expected: PASS (all previously-passing tests still pass; the two new tests
from Step 1 also pass)

- [ ] **Step 8: Commit**

```bash
git add apps/hcc-agent-host/src/orchestrator/dispatch.py apps/hcc-agent-host/src/orchestrator/mock_model.py apps/hcc-agent-host/tests/unit/test_mock_model.py apps/hcc-agent-host/tests/unit/test_dispatch_grounding_agent.py apps/hcc-agent-host/tests/unit/test_dispatch_tracing.py apps/hcc-agent-host/tests/unit/test_interaction_capture.py
git commit -m "feat(agent-host): add agent_name to ChatModel protocol (Sprint 43 WS-1 prep)"
```

---

### Task 2: Create `FoundryResponsesChatModel`

**Files:**
- Create: `apps/hcc-agent-host/src/orchestrator/foundry_chat_model.py`
- Test: `apps/hcc-agent-host/tests/unit/test_foundry_chat_model.py` (create)

- [ ] **Step 1: Write the failing tests**

Create `apps/hcc-agent-host/tests/unit/test_foundry_chat_model.py`:

```python
"""Unit tests for FoundryResponsesChatModel (Sprint 43 WS-1).

No cloud calls — token_provider and http_request are injected fakes, mirroring
tools/fabric_data_agent_client.py's test style.
"""

from __future__ import annotations

from orchestrator.foundry_chat_model import FoundryResponsesChatModel


class _FakeResponse:
    def __init__(self, json_body: dict, status_code: int = 200):
        self._json = json_body
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._json


def _ok_response(text: str) -> _FakeResponse:
    return _FakeResponse({
        "status": "completed",
        "output": [
            {"type": "reasoning", "content": []},
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": text}],
            },
        ],
    })


def _model(fake_http):
    return FoundryResponsesChatModel(
        project_endpoint="https://ai-example.services.ai.azure.com",
        project_name="proj-1",
        token_provider=lambda: "fake-token",
        http_request=fake_http,
    )


def test_complete_posts_agent_reference_and_returns_text():
    captured = {}

    def fake_http(method, url, headers=None, json=None, timeout=None):
        captured["method"] = method
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return _ok_response("The occupancy is 92%.")

    answer = _model(fake_http).complete(
        "You are bmca-agent.",
        "Wie ist die Auslastung?",
        [{"ward": "B", "occupied": 46, "capacity": 50}],
        agent_name="bmca-agent",
    )

    assert answer == "The occupancy is 92%."
    assert captured["method"] == "POST"
    assert captured["url"] == (
        "https://ai-example.services.ai.azure.com/api/projects/proj-1/openai/v1/responses"
    )
    assert "api-version" not in captured["url"]
    assert captured["headers"]["Authorization"] == "Bearer fake-token"
    assert captured["headers"]["Content-Type"] == "application/json"
    assert captured["json"]["agent_reference"] == {
        "name": "bmca-agent",
        "type": "agent_reference",
    }
    assert captured["json"]["instructions"] == "You are bmca-agent."
    assert "Wie ist die Auslastung?" in captured["json"]["input"]
    assert "occupied" in captured["json"]["input"]


def test_complete_with_no_grounding_says_so_in_input():
    captured = {}

    def fake_http(method, url, headers=None, json=None, timeout=None):
        captured["json"] = json
        return _ok_response("Please share bed-state figures.")

    answer = _model(fake_http).complete(
        "sys", "What's tonight's outlook?", [], agent_name="bmca-agent"
    )

    assert answer == "Please share bed-state figures."
    assert "No grounding data" in captured["json"]["input"]


def test_complete_extracts_first_message_text_skipping_reasoning():
    def fake_http(method, url, headers=None, json=None, timeout=None):
        return _ok_response("final text")

    answer = _model(fake_http).complete("sys", "q", [], agent_name="bmca-agent")
    assert answer == "final text"


def test_complete_returns_empty_string_when_no_message_output():
    def fake_http(method, url, headers=None, json=None, timeout=None):
        return _FakeResponse({"status": "completed", "output": [{"type": "reasoning", "content": []}]})

    answer = _model(fake_http).complete("sys", "q", [], agent_name="bmca-agent")
    assert answer == ""


def test_complete_raises_on_http_error():
    import pytest

    def fake_http(method, url, headers=None, json=None, timeout=None):
        return _FakeResponse({"error": {"message": "boom"}}, status_code=500)

    with pytest.raises(RuntimeError):
        _model(fake_http).complete("sys", "q", [], agent_name="bmca-agent")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/unit/test_foundry_chat_model.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'orchestrator.foundry_chat_model'`

- [ ] **Step 3: Write the implementation**

Create `apps/hcc-agent-host/src/orchestrator/foundry_chat_model.py`:

```python
"""Sprint 43 WS-1 — live Foundry Agent Service chat model (Option A).

Invokes a registered Foundry Agent (Agent Service "prompt" kind, e.g.
``bmca-agent``) via the Responses API and normalises the reply into the plain
string the ``ChatModel`` protocol expects (see ``orchestrator/dispatch.py``).

Confirmed live contract (Sprint 43 WS-1 Task 0 spike, 2026-08-08):
  POST {project_endpoint}/api/projects/{project_name}/openai/v1/responses
  Body: {"agent_reference": {"name": "<agent>", "type": "agent_reference"},
         "instructions": "<system prompt>", "input": "<grounded question>"}
  Auth: Bearer token, scope https://ai.azure.com/.default (Foundry User role)
  No api-version query param on /v1 paths (returns 400 if present).
  Synchronous -- "status": "completed" in the same response, no polling.

One instance serves every agent-host manifest: the Foundry Agent name is
passed per-call (``agent_name``), not bound at construction, because
``manifest.agent`` is already identical to the registered Foundry Agent name
(AGENTS.md naming convention) for all 8 agent-host agents.

Token provider and HTTP transport are injected (mirrors
``tools/fabric_data_agent_client.py``) so this class is unit-testable without
cloud access.
"""

from __future__ import annotations

from typing import Any, Callable

_FOUNDRY_SCOPE = "https://ai.azure.com/.default"


def _default_token_provider() -> str:
    from azure.identity import DefaultAzureCredential

    cred = DefaultAzureCredential()
    return cred.get_token(_FOUNDRY_SCOPE).token


def _default_http_request(method: str, url: str, headers=None, json=None, timeout=None):
    import requests

    return requests.request(method, url, headers=headers, json=json, timeout=timeout)


def _format_grounding(grounding: list[dict[str, Any]]) -> str:
    if not grounding:
        return "No grounding data was retrieved for this question."
    lines = ["Grounding data (Fabric gold tables, one JSON row per line):"]
    lines.extend(f"- {row}" for row in grounding)
    return "\n".join(lines)


class FoundryResponsesChatModel:
    """``ChatModel`` that invokes a registered Foundry Agent via the Responses API."""

    def __init__(
        self,
        project_endpoint: str,
        project_name: str,
        token_provider: Callable[[], str] = _default_token_provider,
        http_request: Callable[..., Any] = _default_http_request,
        timeout: int = 60,
    ):
        self._url = (
            f"{project_endpoint.rstrip('/')}/api/projects/{project_name}/openai/v1/responses"
        )
        self._token_provider = token_provider
        self._http_request = http_request
        self._timeout = timeout

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        grounding: list[dict[str, Any]],
        *,
        agent_name: str = "",
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self._token_provider()}",
            "Content-Type": "application/json",
        }
        body = {
            "agent_reference": {"name": agent_name, "type": "agent_reference"},
            "instructions": system_prompt,
            "input": f"{_format_grounding(grounding)}\n\nQuestion: {user_prompt}",
        }
        resp = self._http_request(
            "POST", self._url, headers=headers, json=body, timeout=self._timeout
        )
        resp.raise_for_status()
        return self._first_message_text(resp.json())

    @staticmethod
    def _first_message_text(payload: dict[str, Any]) -> str:
        for item in payload.get("output") or []:
            if item.get("type") != "message":
                continue
            for part in item.get("content") or []:
                if part.get("type") == "output_text":
                    text = part.get("text", "")
                    if text:
                        return text
        return ""
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/unit/test_foundry_chat_model.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add apps/hcc-agent-host/src/orchestrator/foundry_chat_model.py apps/hcc-agent-host/tests/unit/test_foundry_chat_model.py
git commit -m "feat(agent-host): add FoundryResponsesChatModel (Sprint 43 WS-1 Option A)"
```

---

### Task 3: Wire the env-gated factory into `HostState`

**Files:**
- Modify: `apps/hcc-agent-host/src/api/app.py`
- Test: `apps/hcc-agent-host/tests/unit/test_build_chat_model.py` (create)

- [ ] **Step 1: Write the failing tests**

Create `apps/hcc-agent-host/tests/unit/test_build_chat_model.py`:

```python
"""Unit tests for the env-gated live chat-model factory (Sprint 43 WS-1)."""

from __future__ import annotations

import api.app as appmod


def _clear_env(monkeypatch):
    for k in ("FOUNDRY_PROJECT_ENDPOINT", "FOUNDRY_PROJECT_NAME"):
        monkeypatch.delenv(k, raising=False)


def test_returns_none_when_no_env(monkeypatch):
    _clear_env(monkeypatch)
    assert appmod._build_chat_model() is None


def test_returns_none_on_partial_env(monkeypatch, caplog):
    _clear_env(monkeypatch)
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://ai-example.services.ai.azure.com")
    assert appmod._build_chat_model() is None
    assert "FOUNDRY_PROJECT_* partially configured" in caplog.text


def test_returns_client_when_all_env_set(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://ai-example.services.ai.azure.com")
    monkeypatch.setenv("FOUNDRY_PROJECT_NAME", "proj-1")
    model = appmod._build_chat_model()
    assert model is not None
    assert model.complete.__self__ is model
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/unit/test_build_chat_model.py -v`
Expected: FAIL with `AttributeError: module 'api.app' has no attribute '_build_chat_model'`

- [ ] **Step 3: Add the factory function**

In `apps/hcc-agent-host/src/api/app.py`, immediately after the existing
`_build_live_data_agent()` function, add:

```python
def _build_chat_model():
    """Return a live FoundryResponsesChatModel when env is configured, else None.

    A single instance serves every agent-host manifest — the Foundry Agent
    name is supplied per-call as ``agent_name`` (manifest.agent), not bound at
    construction (Sprint 43 WS-1).
    """
    endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT")
    project = os.environ.get("FOUNDRY_PROJECT_NAME")
    provided = [bool(endpoint), bool(project)]
    if not all(provided):
        if any(provided):
            logger.warning(
                "FOUNDRY_PROJECT_* partially configured (%d/2 set); using MockChatModel",
                sum(provided),
            )
        return None
    from orchestrator.foundry_chat_model import FoundryResponsesChatModel

    return FoundryResponsesChatModel(project_endpoint=endpoint, project_name=project)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/unit/test_build_chat_model.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Wire it into `HostState.__init__`**

In `apps/hcc-agent-host/src/api/app.py`, replace:

```python
        live = _build_live_data_agent()
        self._live_data_agent = live
        adapter = FabricDataAgentAdapter(ask_fn=(live.ask if live is not None else None))
        self.orchestrator = Orchestrator(
            chat_model=MockChatModel(),
            data_agent=adapter,
        )
```

with:

```python
        live = _build_live_data_agent()
        self._live_data_agent = live
        adapter = FabricDataAgentAdapter(ask_fn=(live.ask if live is not None else None))
        # Sprint 43 WS-1 — live Foundry Agent Service chat model (Option A).
        # FOUNDRY_PROJECT_ENDPOINT/FOUNDRY_PROJECT_NAME unset (dev/CI default)
        # keeps the deterministic MockChatModel; both set (SIT/PROD) invokes
        # the real registered agents via FoundryResponsesChatModel.
        live_chat_model = _build_chat_model()
        self.orchestrator = Orchestrator(
            chat_model=live_chat_model if live_chat_model is not None else MockChatModel(),
            data_agent=adapter,
        )
```

- [ ] **Step 6: Run the full test suite**

Run: `python -m pytest -v`
Expected: PASS (all tests, including the 3 new ones)

- [ ] **Step 7: Commit**

```bash
git add apps/hcc-agent-host/src/api/app.py apps/hcc-agent-host/tests/unit/test_build_chat_model.py
git commit -m "feat(agent-host): wire FoundryResponsesChatModel behind FOUNDRY_PROJECT_* env gate"
```

---

### Task 4: Thread the Bicep params through to SIT

**Files:**
- Modify: `infra/modules/agent-host/container-app.bicep`
- Modify: `infra/modules/agent-host/main.bicep`
- Modify: `infra/main.bicep`
- Modify: `infra/environments/sit.bicepparam`

- [ ] **Step 1: Add the params + env vars in `container-app.bicep`**

In `infra/modules/agent-host/container-app.bicep`, after the existing
`fabricDataAgentId` param, add:

```bicep
@description('Sprint 43 WS-1 — Foundry Agent Service project account root (e.g. https://ai-ihzhhpf-sit-eastus2.services.ai.azure.com). Empty string keeps the agent-host on the deterministic MockChatModel.')
param foundryProjectEndpoint string = ''

@description('Sprint 43 WS-1 — Foundry Agent Service project name (e.g. ai-ihzhhpf-sit-eastus2-project). Empty string keeps the agent-host on the deterministic MockChatModel.')
param foundryProjectName string = ''
```

Then, in the same file, inside the `baseEnv` array, after the
`FABRIC_DATA_AGENT_ID` entry, add:

```bicep
  {
    name: 'FOUNDRY_PROJECT_ENDPOINT'
    value: foundryProjectEndpoint
  }
  {
    name: 'FOUNDRY_PROJECT_NAME'
    value: foundryProjectName
  }
```

- [ ] **Step 2: Validate the module builds**

Run: `az bicep build --file infra/modules/agent-host/container-app.bicep --stdout`
Expected: Compiles with no errors (warnings about unused params are fine if
none appear; this file has no such precedent).

- [ ] **Step 3: Pass the params through `agent-host/main.bicep`**

In `infra/modules/agent-host/main.bicep`, after the existing
`fabricDataAgentId` param, add:

```bicep
@description('Sprint 43 WS-1 — Foundry Agent Service project account root. Empty string keeps the agent-host on the deterministic MockChatModel.')
param foundryProjectEndpoint string = ''

@description('Sprint 43 WS-1 — Foundry Agent Service project name. Empty string keeps the agent-host on the deterministic MockChatModel.')
param foundryProjectName string = ''
```

Then, inside the `containerApp` module's `params` block, after the existing
`fabricDataAgentId: fabricDataAgentId` line, add:

```bicep
    foundryProjectEndpoint: foundryProjectEndpoint
    foundryProjectName: foundryProjectName
```

- [ ] **Step 4: Validate the module builds**

Run: `az bicep build --file infra/modules/agent-host/main.bicep --stdout`
Expected: Compiles with no errors.

- [ ] **Step 5: Add top-level params in `infra/main.bicep` and pass through**

In `infra/main.bicep`, after the existing `fabricDataAgentId` param (near
line 297), add:

```bicep
@description('Sprint 43 WS-1 — Foundry Agent Service project account root (e.g. https://ai-ihzhhpf-sit-eastus2.services.ai.azure.com). Empty string keeps the agent-host on the deterministic MockChatModel.')
param foundryProjectEndpoint string = ''

@description('Sprint 43 WS-1 — Foundry Agent Service project name (e.g. ai-ihzhhpf-sit-eastus2-project). Empty string keeps the agent-host on the deterministic MockChatModel.')
param foundryProjectName string = ''
```

Then, inside the `agentHost` module's `params` block (near line 708), after
the existing `fabricDataAgentId: fabricDataAgentId` line, add:

```bicep
    foundryProjectEndpoint: foundryProjectEndpoint
    foundryProjectName: foundryProjectName
```

- [ ] **Step 6: Validate the top-level template builds**

Run: `az bicep build --file infra/main.bicep --stdout`
Expected: Compiles with no errors.

- [ ] **Step 7: Set the real SIT values in `sit.bicepparam`**

In `infra/environments/sit.bicepparam`, immediately after the existing
`param fabricDataAgentId = '...'` line (near line 234), add:

```bicep
// Sprint 43 WS-1 — real Foundry Agent Service chat model (Option A). Same
// eastus2 project already used by the decision-tier apply job and the
// Foundry-hosted runtime agents (ADR-0032); the agent-host MI already holds
// `Foundry User` on this account (granted 2026-07-26, confirmed idempotent).
param foundryProjectEndpoint = 'https://ai-ihzhhpf-sit-eastus2.services.ai.azure.com'
param foundryProjectName = 'ai-ihzhhpf-sit-eastus2-project'
```

- [ ] **Step 8: Validate the bicepparam file against the built template**

Run: `az bicep build-params --file infra/environments/sit.bicepparam --stdout`
Expected: Compiles with no errors.

- [ ] **Step 9: Run a `what-if` against the real SIT resource group (dry-run, no apply)**

Run:

```bash
az deployment group what-if \
  --resource-group rg-ihzhhpf-sit \
  --template-file infra/main.bicep \
  --parameters infra/environments/sit.bicepparam
```

Expected: The only changes shown are the two new container-app env vars
(`FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_PROJECT_NAME`) being added to
`ca-agent-host-ihzhhpf-sit` (a `Modify` on that one resource). No other
resource should show a diff. **Do not apply yet** — this is the plan artefact
for the human confirmation step in Task 5.

- [ ] **Step 10: Commit**

```bash
git add infra/modules/agent-host/container-app.bicep infra/modules/agent-host/main.bicep infra/main.bicep infra/environments/sit.bicepparam
git commit -m "feat(infra): thread FOUNDRY_PROJECT_ENDPOINT/NAME to agent-host (Sprint 43 WS-1)"
```

---


### Task 5: Deploy to SIT and verify live

**Files:** none (operational task — CI workflow + manual verification)

- [ ] **Step 1: Push and trigger the SIT infra deploy**

```bash
git push
gh workflow run cd-infra-deploy-sit.yml
```

Wait for the run to reach the manual-approval gate (the "sit" GitHub
Environment reviewer step), then approve it (user reviewer role — this is
the standing `approved-to-apply` authorization already given for this
workstream).

- [ ] **Step 2: Confirm the workflow succeeded**

```bash
gh run list --workflow=cd-infra-deploy-sit.yml --limit 1
```

Expected: `completed` / `success`.

- [ ] **Step 3: Confirm the new env vars landed on the running container**

```bash
az containerapp show --name ca-agent-host-ihzhhpf-sit --resource-group rg-ihzhhpf-sit --query "properties.template.containers[0].env[?name=='FOUNDRY_PROJECT_ENDPOINT' || name=='FOUNDRY_PROJECT_NAME']" -o table
```

Expected: both env vars present with the values set in Step 7 of Task 4.

- [ ] **Step 4: Re-test `bmca-agent` live via raw HTTP (mirrors Sprint 42's evidence style)**

```bash
curl -s -X POST "https://ca-agent-host-ihzhhpf-sit.<domain>/agents/bmca-agent/chat" \
  -H "content-type: application/json" \
  -d '{"prompt": "Station B ist fast voll -- was sollen wir tun?", "conversationId": "sprint43-verify", "callerObjectId": "verify.user"}'
```

Expected: `refused: false`, an `answer` that reflects the real grounding row
(`ward B, 46/50`) **and** is phrased differently from `MockChatModel`'s fixed
template (`"Auslastung Station B liegt bei 92%..."` verbatim) — a real model
response paraphrases, may add reasoning, and will not be byte-identical
across repeated calls.

- [ ] **Step 5: Re-test at least 2 more of the 8 agents live via raw HTTP**

Repeat Step 4's pattern for `ooa-agent` and one of `dca-agent`/`orsa-agent`/
`sba-agent`/`csa-agent` — these previously returned `MockChatModel`'s
"Keine Auslastungsdaten..." fallback (no grounding row matched). Expected:
each now returns a real, reasoned answer (possibly asking for missing data,
per the Task 0 spike's own evidence) instead of the fixed German fallback
string.

- [ ] **Step 6: Re-test via the real UI**

Open `https://appsit.curavias.ch` in a browser, navigate to at least 2 of the
specialized-agent panes tested in the original UI sweep, and send the same
canonical prompt used earlier this session. Confirm the answer is no longer
the hardcoded/templated text previously observed.

- [ ] **Step 7: Record the verification evidence**

Append a dated entry to
`docs/superpowers/specs/2026-08-08-sprint-43-real-iq-layer-grounding-design.md`
§2 (or a new §2.1 "WS-1 live verification") capturing: the exact
`curl`/UI outputs for the agents tested, confirmation they differ from the
`MockChatModel` fixtures, and the deployed commit SHA. Bump the doc's
`Version` (PATCH if purely evidentiary, MINOR if new sections are added) per
the `document-authoring` skill.

---

### Task 6: Re-run eval golden-task suites and close out the issue

**Files:**
- Check: `evals/` and any `agents/<name>/golden-tasks.md` fixtures touched by
  this change (none are expected to need edits — the contract
  `{answer, citations[], refused}` is unchanged — but re-running proves it).

- [ ] **Step 1: Re-run the full `hcc-agent-host` test suite one more time post-deploy**

```bash
cd apps/hcc-agent-host
python -m pytest -v
```

Expected: PASS (unchanged from Task 3's run — this is a regression check
after the Bicep/deploy work, confirming no local code drifted).

- [ ] **Step 2: Post a completion comment on issue #567**

Summarize: WS-1 implemented and deployed; live verification evidence (Task 5
Steps 4-6) linked; commits listed; remaining workstreams (WS-2, WS-3, WS-4)
still open with their own plans to follow.

```bash
gh issue comment 567 --body "WS-1 complete: FoundryResponsesChatModel deployed to SIT, live-verified against bmca-agent + 2 other agents (raw HTTP + UI) -- real, non-mock GPT-5 answers confirmed, MockChatModel fallback no longer observed. Commits: <list>. Next: WS-2 (Fabric grounding for FabricAdapter)."
```

- [ ] **Step 3: Update the todo list / close WS-1's tracking checklist items on the issue**

Check off WS-1's items in issue #567's task list (via the GitHub UI or
`gh issue edit`), leaving WS-2/WS-3/WS-4 open.

---

## Notes for the next plan (WS-2)

WS-2 (replace `FabricAdapter`'s hardcoded 3-row dict with a real Fabric
query) is a separate, independently deployable workstream per the Sprint 43
design doc §5 sequencing. Do not start it inside this plan — write a fresh
plan via `writing-plans` once WS-1 is verified live, using the same
TDD/Bicep/deploy/verify shape as this plan.
