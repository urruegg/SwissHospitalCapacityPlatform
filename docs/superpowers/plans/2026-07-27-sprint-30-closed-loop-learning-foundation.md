# Closed-Loop Learning — Capture Foundation Implementation Plan (Sprint 30, Plan 1)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persist every agent turn as a governed, PHI-free `DC-AGENT-INTERACTION-v1` record in the agent-host, and expose an endpoint to append user-interaction events — the capture prerequisite the rest of the closed loop (evaluate → curate → improve) and hybrid testing run on.

**Architecture:** Extend the existing agent-host `Orchestrator.dispatch()` (which already redacts and writes `conversations` + `audit` to the in-memory-abstracted Cosmos) with a new agent-agnostic interaction-record builder + a new `agent_interactions` container, and add a user-events append endpoint. All new logic is pure/TDD-able against the in-memory Cosmos; no live Azure needed for the tests.

**Tech Stack:** Python 3.11, FastAPI, Pydantic, pytest (`pythonpath=src`), the existing `orchestrator/redaction.py`, `persistence/cosmos_client.py`.

**Scope note:** Sprint 30 is one large loop (M0–M9 in the [design spec](../specs/2026-07-27-sprint-30-closed-loop-learning-foundation-design.md)). This plan delivers the **capture foundation** only — M0, the Cosmos-write half of M1, and the M2 append endpoint. It produces working, testable software on its own. **Follow-on plans** (each its own file when we reach it): OTel → App Insights tracing (M1-observe); app-side `userEvent` emission in `hcc-app-fluent` (M2-app); evaluator library + offline gate (M3); online continuous eval (M4); curator + advisory backlog (M5); Improve — prompt/knowledge optimize + fine-tune (M7–M9).

**Working directory for all commands:** `apps/hcc-agent-host` (run `cd apps/hcc-agent-host` first). Full test suite command: `python -m pytest`.

---

## File structure

| File | Responsibility |
|------|----------------|
| `data/synthetic/schema/agent-interaction-v1.schema.json` *(create)* | The `DC-AGENT-INTERACTION-v1` JSON Schema contract (mirrors design §6). |
| `apps/hcc-agent-host/src/orchestrator/interaction_record.py` *(create)* | Pure builder: `prompt_hash()` + `build_interaction_record()`; reuses `redact()`. One responsibility: turn turn-data into a contract-shaped, redacted record. |
| `apps/hcc-agent-host/src/persistence/cosmos_client.py` *(modify)* | Add the `agent_interactions` container + partition key + an `append_user_event()` method. |
| `apps/hcc-agent-host/src/orchestrator/dispatch.py` *(modify)* | Build + persist the interaction record inside `dispatch()`; add `interaction_id` to `GroundedReply`. |
| `apps/hcc-agent-host/src/api/app.py` *(modify)* | Return `interactionId` from `POST /chat`; add `POST /agents/{name}/interactions/{interactionId}/events`. |
| `apps/hcc-agent-host/tests/unit/test_interaction_record.py` *(create)* | Builder unit tests. |
| `apps/hcc-agent-host/tests/unit/test_interaction_capture.py` *(create)* | Container + dispatch-capture + append-event tests. |
| `apps/hcc-agent-host/tests/integration/test_capture_api.py` *(create)* | API-level tests (chat returns interactionId; events endpoint appends). |
| `docs/DATA.md` *(modify)* | Register the `DC-AGENT-INTERACTION-v1` contract + `agent_interactions` container. |

---

## Task 1: `DC-AGENT-INTERACTION-v1` JSON Schema contract

**Files:**
- Create: `data/synthetic/schema/agent-interaction-v1.schema.json`

- [ ] **Step 1: Write the schema file**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://curavias/schema/agent-interaction-v1.schema.json",
  "title": "DC-AGENT-INTERACTION-v1",
  "type": "object",
  "required": ["contractId", "interactionId", "conversationKey", "agent", "ts", "request", "response", "userEvents", "eval"],
  "additionalProperties": true,
  "properties": {
    "contractId": { "const": "DC-AGENT-INTERACTION-v1" },
    "interactionId": { "type": "string", "pattern": "^AIX-[0-9a-f]+$" },
    "conversationKey": { "type": "string" },
    "agent": { "type": "string" },
    "ts": { "type": "string", "format": "date-time" },
    "env": { "type": "string" },
    "region": { "type": "string" },
    "scope": { "type": "object" },
    "request": {
      "type": "object",
      "required": ["promptHash"],
      "properties": {
        "promptHash": { "type": "string", "pattern": "^sha256:[0-9a-f]{64}$" },
        "promptRedacted": { "type": "string" },
        "lang": { "type": "string" }
      }
    },
    "response": {
      "type": "object",
      "required": ["refused"],
      "properties": {
        "answerRedacted": { "type": "string" },
        "citations": { "type": "array", "items": { "type": "string" } },
        "refused": { "type": "boolean" },
        "reco": { "type": ["object", "null"] }
      }
    },
    "model": { "type": "object" },
    "tools": { "type": "array" },
    "timing": { "type": "object" },
    "provenance": { "type": "string", "enum": ["live", "simulated"] },
    "userEvents": { "type": "array", "items": { "type": "object" } },
    "eval": { "type": "object", "required": ["scored"], "properties": { "scored": { "type": "boolean" } } }
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add data/synthetic/schema/agent-interaction-v1.schema.json
git commit -m "feat(learn): add DC-AGENT-INTERACTION-v1 JSON Schema contract"
```

---

## Task 2: Interaction-record builder (`interaction_record.py`)

**Files:**
- Create: `apps/hcc-agent-host/src/orchestrator/interaction_record.py`
- Test: `apps/hcc-agent-host/tests/unit/test_interaction_record.py`

- [ ] **Step 1: Write the failing test**

```python
"""Sprint 30 M0 — DC-AGENT-INTERACTION-v1 record builder tests."""

from __future__ import annotations

from orchestrator.interaction_record import prompt_hash, build_interaction_record


def test_prompt_hash_is_sha256_prefixed():
    h = prompt_hash("Wie ist die Auslastung auf Station B?")
    assert h.startswith("sha256:")
    assert len(h) == len("sha256:") + 64


def test_build_record_shape_and_redaction():
    rec = build_interaction_record(
        agent="ooa-agent",
        conversation_key="user-oid:ooa-agent",
        prompt="patient 756.1234.5678.90 fragt nach Station B",
        answer="Auslastung 92%. token ghp_abcdefghijklmnopqrstuvwxyz0123",
        citations=["hcp:Ward", "gold.occupancy"],
        refused=False,
        reco=None,
        env="sit",
        region="eastus2",
        provenance="simulated",
        total_ms=1234,
    )
    assert rec["contractId"] == "DC-AGENT-INTERACTION-v1"
    assert rec["interactionId"].startswith("AIX-")
    assert rec["conversationKey"] == "user-oid:ooa-agent"
    assert rec["agent"] == "ooa-agent"
    # redaction applied to prompt + answer
    assert "756.1234.5678.90" not in rec["request"]["promptRedacted"]
    assert "ghp_" not in rec["response"]["answerRedacted"]
    # raw prompt never stored, only a hash
    assert "prompt" not in rec["request"]
    assert rec["request"]["promptHash"].startswith("sha256:")
    # capture is cheap: eval unscored, no user events yet
    assert rec["eval"] == {"scored": False}
    assert rec["userEvents"] == []
    assert rec["response"]["citations"] == ["hcp:Ward", "gold.occupancy"]
    assert rec["timing"]["totalMs"] == 1234
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/hcc-agent-host; python -m pytest tests/unit/test_interaction_record.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'orchestrator.interaction_record'`.

- [ ] **Step 3: Write the implementation**

```python
"""Sprint 30 M0 — build a DC-AGENT-INTERACTION-v1 record for one agent turn.

Pure + deterministic (apart from id/timestamp). PHI-free by construction: the raw
prompt is hashed (never stored) and prompt/answer text pass through the existing
redaction gate before persistence (design §6; ADR-0016).
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any

from orchestrator.redaction import redact

CONTRACT_ID = "DC-AGENT-INTERACTION-v1"


def prompt_hash(prompt: str) -> str:
    """Return ``sha256:<hex>`` for dedup / regression matching without retaining text."""
    return "sha256:" + hashlib.sha256((prompt or "").encode("utf-8")).hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_interaction_record(
    *,
    agent: str,
    conversation_key: str,
    prompt: str,
    answer: str,
    citations: list[str],
    refused: bool,
    reco: dict[str, Any] | None = None,
    lang: str | None = None,
    scope: dict[str, Any] | None = None,
    model: dict[str, Any] | None = None,
    tools: list[dict[str, Any]] | None = None,
    total_ms: int = 0,
    provenance: str = "simulated",
    env: str = "sit",
    region: str = "eastus2",
    ts: str | None = None,
) -> dict[str, Any]:
    """Assemble one contract-shaped, redacted interaction record."""
    return {
        "contractId": CONTRACT_ID,
        "interactionId": f"AIX-{uuid.uuid4().hex}",
        "conversationKey": conversation_key,
        "agent": agent,
        "ts": ts or _now_iso(),
        "env": env,
        "region": region,
        "scope": scope or {},
        "request": {
            "promptHash": prompt_hash(prompt),
            "promptRedacted": redact(prompt),
            "lang": lang,
        },
        "response": {
            "answerRedacted": redact(answer),
            "citations": list(citations),
            "refused": refused,
            "reco": reco,
        },
        "model": model or {},
        "tools": tools or [],
        "timing": {"totalMs": total_ms},
        "provenance": provenance,
        "userEvents": [],
        "eval": {"scored": False},
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/hcc-agent-host; python -m pytest tests/unit/test_interaction_record.py -q`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add apps/hcc-agent-host/src/orchestrator/interaction_record.py apps/hcc-agent-host/tests/unit/test_interaction_record.py
git commit -m "feat(learn): DC-AGENT-INTERACTION-v1 record builder + prompt hash"
```

---

## Task 3: Add the `agent_interactions` container + `append_user_event`

**Files:**
- Modify: `apps/hcc-agent-host/src/persistence/cosmos_client.py`
- Test: `apps/hcc-agent-host/tests/unit/test_interaction_capture.py`

- [ ] **Step 1: Write the failing test**

```python
"""Sprint 30 M0/M2 — agent_interactions container + user-event append."""

from __future__ import annotations

import pytest

from persistence.cosmos_client import CosmosPersistence


def test_agent_interactions_container_writes_by_conversation_key():
    p = CosmosPersistence()
    rec = p.write("agent_interactions", {
        "interactionId": "AIX-abc",
        "conversationKey": "user-oid:ooa-agent",
        "agent": "ooa-agent",
    })
    assert rec["conversationKey"] == "user-oid:ooa-agent"
    assert p.read_all("agent_interactions")[0]["interactionId"] == "AIX-abc"


def test_agent_interactions_requires_partition_key():
    p = CosmosPersistence()
    with pytest.raises(ValueError):
        p.write("agent_interactions", {"interactionId": "AIX-x"})  # no conversationKey


def test_append_user_event_adds_to_record():
    p = CosmosPersistence()
    p.write("agent_interactions", {
        "interactionId": "AIX-abc",
        "conversationKey": "user-oid:ooa-agent",
        "userEvents": [],
    })
    updated = p.append_user_event("AIX-abc", {"type": "thumbs", "value": "up", "ts": "2026-07-27T09:00:00Z"})
    assert updated["userEvents"][-1]["type"] == "thumbs"
    assert p.read_all("agent_interactions")[0]["userEvents"][-1]["value"] == "up"


def test_append_user_event_unknown_id_raises():
    p = CosmosPersistence()
    with pytest.raises(KeyError):
        p.append_user_event("AIX-missing", {"type": "thumbs", "value": "up"})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/hcc-agent-host; python -m pytest tests/unit/test_interaction_capture.py -q`
Expected: FAIL — `agent_interactions` not in `CONTAINERS` (`ValueError: unknown container`) / no `append_user_event`.

- [ ] **Step 3: Write the implementation** (edit `cosmos_client.py`)

Change the `CONTAINERS` + `PARTITION_KEYS` constants:

```python
CONTAINERS = ("conversations", "audit", "approval-events", "agent_interactions")

# Partition key per container (ADR-0007 §Implementation Notes: correlationId
# indexing; conversations partition by conversationId; Sprint 30 agent_interactions
# partition by conversationKey = <userOid>:<agent>).
PARTITION_KEYS = {
    "conversations": "conversationId",
    "audit": "correlationId",
    "approval-events": "correlationId",
    "agent_interactions": "conversationKey",
}
```

Add this method to `CosmosPersistence` (after `query_by_correlation`):

```python
    def append_user_event(self, interaction_id: str, event: dict[str, Any]) -> dict[str, Any]:
        """Append a user-interaction event to a stored agent_interactions record."""
        for record in self._store["agent_interactions"]:
            if record.get("interactionId") == interaction_id:
                record.setdefault("userEvents", []).append(dict(event))
                return record
        raise KeyError(f"no agent_interactions record with interactionId '{interaction_id}'")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/hcc-agent-host; python -m pytest tests/unit/test_interaction_capture.py -q`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add apps/hcc-agent-host/src/persistence/cosmos_client.py apps/hcc-agent-host/tests/unit/test_interaction_capture.py
git commit -m "feat(learn): agent_interactions container + append_user_event"
```

---

## Task 4: Capture the record inside `Orchestrator.dispatch()`

**Files:**
- Modify: `apps/hcc-agent-host/src/orchestrator/dispatch.py`
- Test: `apps/hcc-agent-host/tests/unit/test_interaction_capture.py` (append)

- [ ] **Step 1: Add the failing test** (append to `test_interaction_capture.py`)

```python
from manifests.loader import AgentManifest
from orchestrator.dispatch import Orchestrator


class _StubModel:
    def complete(self, system_prompt, user_prompt, grounding):
        return "Auslastung Station B: 92%."


def _manifest() -> AgentManifest:
    return AgentManifest(
        agent="ooa-agent",
        version="1.0.0",
        runtime="agent-host",
        model_deployment_ref="gpt-5",
        system_prompt_ref="AGENT.md",
        grounding_tables=("gold.occupancy",),
        grounding_agent=None,
        hitl_gates=(),
    )


def test_dispatch_writes_agent_interaction_record():
    orch = Orchestrator(chat_model=_StubModel())
    reply = orch.dispatch(
        _manifest(), "You are ooa-agent.", "Wie ist die Auslastung?",
        conversation_id="conv-1", caller_oid="user-oid",
    )
    records = orch.persistence.read_all("agent_interactions")
    assert len(records) == 1
    rec = records[0]
    assert rec["contractId"] == "DC-AGENT-INTERACTION-v1"
    assert rec["agent"] == "ooa-agent"
    assert rec["conversationKey"] == "user-oid:ooa-agent"
    assert rec["response"]["refused"] is False
    assert rec["interactionId"] == reply.interaction_id
```

> **Note:** `AgentManifest` (from `manifests/loader.py`) requires `agent`, `version`, `runtime`, `model_deployment_ref`, `system_prompt_ref`; `tools` / `hitl_gates` / `grounding_tables` / `grounding_agent` have defaults, and `max_ceiling` is a computed property (not a constructor arg).

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/hcc-agent-host; python -m pytest tests/unit/test_interaction_capture.py::test_dispatch_writes_agent_interaction_record -q`
Expected: FAIL — `GroundedReply` has no `interaction_id`; no `agent_interactions` record written.

- [ ] **Step 3: Implement** (edit `dispatch.py`)

Add the import near the top:

```python
from orchestrator.interaction_record import build_interaction_record
```

Add `interaction_id` to the reply dataclass:

```python
@dataclass(frozen=True)
class GroundedReply:
    answer: str
    citations: tuple[str, ...]
    refused: bool
    correlation_id: str
    interaction_id: str = ""
```

At the **start** of `dispatch()` capture the wall-clock start:

```python
        started = time.perf_counter()
```

Replace **both** `return GroundedReply(...)` blocks so they build + persist the record and pass `interaction_id`. Extract this helper method on `Orchestrator` and call it from each return path:

```python
    def _capture(
        self,
        *,
        agent: str,
        caller_oid: str,
        prompt: str,
        answer: str,
        citations: list[str],
        refused: bool,
        degraded: bool,
        started: float,
    ) -> str:
        record = build_interaction_record(
            agent=agent,
            conversation_key=f"{caller_oid}:{agent}",
            prompt=prompt,
            answer=answer,
            citations=citations,
            refused=refused,
            reco=None,
            model={"name": type(self.chat_model).__name__},
            provenance="live" if not degraded else "simulated",
            total_ms=int((time.perf_counter() - started) * 1000),
        )
        self.persistence.write("agent_interactions", record)
        return record["interactionId"]
```

Then in the refusal path:

```python
            interaction_id = self._capture(
                agent=manifest.agent, caller_oid=caller_oid, prompt=user_prompt,
                answer=refusal_answer, citations=citations, refused=True,
                degraded=False, started=started,
            )
            return GroundedReply(
                answer=refusal_answer,
                citations=tuple(citations),
                refused=True,
                correlation_id=correlation_id,
                interaction_id=interaction_id,
            )
```

And in the normal path:

```python
        interaction_id = self._capture(
            agent=manifest.agent, caller_oid=caller_oid, prompt=user_prompt,
            answer=answer, citations=citations, refused=refused,
            degraded=degraded, started=started,
        )
        return GroundedReply(
            answer=answer,
            citations=tuple(citations),
            refused=refused,
            correlation_id=correlation_id,
            interaction_id=interaction_id,
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd apps/hcc-agent-host; python -m pytest tests/unit/test_interaction_capture.py -q`
Expected: PASS (5 passed). Then run the full suite to confirm no regression: `python -m pytest -q`.

- [ ] **Step 5: Commit**

```bash
git add apps/hcc-agent-host/src/orchestrator/dispatch.py apps/hcc-agent-host/tests/unit/test_interaction_capture.py
git commit -m "feat(learn): capture DC-AGENT-INTERACTION-v1 in orchestrator dispatch"
```

---

## Task 5: Surface `interactionId` in the chat endpoint

**Files:**
- Modify: `apps/hcc-agent-host/src/api/app.py`
- Test: `apps/hcc-agent-host/tests/integration/test_capture_api.py`

- [ ] **Step 1: Write the failing test**

```python
"""Sprint 30 — capture API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.app import create_app


def test_chat_returns_interaction_id():
    client = TestClient(create_app())
    res = client.post("/agents/ooa-agent/chat", json={"prompt": "Wie ist die Auslastung?"})
    assert res.status_code == 200
    body = res.json()
    assert body["interactionId"].startswith("AIX-")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/hcc-agent-host; python -m pytest tests/integration/test_capture_api.py -q`
Expected: FAIL — response has no `interactionId` key.

- [ ] **Step 3: Implement** — in `app.py`, extend the `chat()` return dict:

```python
        return {
            "answer": reply.answer,
            "citations": list(reply.citations),
            "refused": reply.refused,
            "correlationId": reply.correlation_id,
            "interactionId": reply.interaction_id,
        }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/hcc-agent-host; python -m pytest tests/integration/test_capture_api.py -q`
Expected: PASS (1 passed).

- [ ] **Step 5: Commit**

```bash
git add apps/hcc-agent-host/src/api/app.py apps/hcc-agent-host/tests/integration/test_capture_api.py
git commit -m "feat(learn): return interactionId from POST /chat"
```

---

## Task 6: User-events append endpoint

**Files:**
- Modify: `apps/hcc-agent-host/src/api/app.py`
- Test: `apps/hcc-agent-host/tests/integration/test_capture_api.py` (append)

- [ ] **Step 1: Add the failing test** (append to `test_capture_api.py`)

```python
def test_append_user_event_endpoint():
    client = TestClient(create_app())
    chat = client.post("/agents/ooa-agent/chat", json={"prompt": "Wie ist die Auslastung?"}).json()
    iid = chat["interactionId"]
    res = client.post(
        f"/agents/ooa-agent/interactions/{iid}/events",
        json={"type": "thumbs", "value": "up"},
    )
    assert res.status_code == 200
    assert res.json()["ok"] is True


def test_append_user_event_unknown_id_is_404():
    client = TestClient(create_app())
    res = client.post(
        "/agents/ooa-agent/interactions/AIX-missing/events",
        json={"type": "thumbs", "value": "up"},
    )
    assert res.status_code == 404
```

> **Note:** `TestClient` uses the module-level `app` state via `create_app()`; each `create_app()` shares the `@lru_cache`d `get_state()` singleton, so the chat in step 1 and the append use the same in-memory store within a test process.

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/hcc-agent-host; python -m pytest tests/integration/test_capture_api.py -q`
Expected: FAIL — 404 route not found for the events path.

- [ ] **Step 3: Implement** — add a request model + route in `app.py`.

Add near `ToolRequest`:

```python
class UserEventRequest(BaseModel):
    type: str
    value: str | None = None
    ts: str | None = None
```

Add inside `create_app()` after the `invoke_tool` route:

```python
    @app.post("/agents/{name}/interactions/{interaction_id}/events")
    def append_event(name: str, interaction_id: str, req: UserEventRequest) -> dict[str, Any]:
        state = get_state()
        state.require(name)  # 404 on unknown agent
        event = {k: v for k, v in req.model_dump().items() if v is not None}
        try:
            state.orchestrator.persistence.append_user_event(interaction_id, event)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"unknown interactionId '{interaction_id}'")
        return {"ok": True, "interactionId": interaction_id}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd apps/hcc-agent-host; python -m pytest tests/integration/test_capture_api.py -q`
Expected: PASS (3 passed). Then `python -m pytest -q` for the full suite.

- [ ] **Step 5: Commit**

```bash
git add apps/hcc-agent-host/src/api/app.py apps/hcc-agent-host/tests/integration/test_capture_api.py
git commit -m "feat(learn): user-events append endpoint for agent interactions"
```

---

## Task 7: Register the contract in `docs/DATA.md`

**Files:**
- Modify: `docs/DATA.md`

- [ ] **Step 1: Add a row to the "Suggested Contract Groups (MVP)" table**

Add this row after the `DC-EXT-SIGNAL-v1` row:

```markdown
| Agent-interaction contract | DC-AGENT-INTERACTION-v1 | Closed-loop-learning capture: one PHI-free record per agent turn + user events (Sprint 30) |
```

- [ ] **Step 2: Bump the doc version header** (per copilot-instructions §9 — MINOR, additive)

Change `Version` to the next MINOR and update `Previous Version` with the hint `added DC-AGENT-INTERACTION-v1 capture contract`. Update `Date` to today.

- [ ] **Step 3: Run the doc gates**

Run (from repo root): `python scripts/lint/check_mojibake.py docs/DATA.md` then `npx --yes markdownlint-cli2 "docs/DATA.md"`
Expected: no mojibake; 0 lint issues.

- [ ] **Step 4: Commit**

```bash
git add docs/DATA.md
git commit -m "docs(data): register DC-AGENT-INTERACTION-v1 capture contract"
```

---

## Final verification

- [ ] Run the full agent-host suite: `cd apps/hcc-agent-host; python -m pytest -q` — all green, no regressions in the existing dispatch/redaction/loader tests.
- [ ] Confirm a captured record is PHI-free: the record stores `promptHash` + `promptRedacted` only (no raw `prompt` key), and `answerRedacted` masks AHV/secret tokens.

---

## Follow-on plans (not this plan)

Each becomes its own `docs/superpowers/plans/` file when its prerequisites are met:

1. **M1-observe** — OpenTelemetry spans (retrieve → model → assemble) → Application Insights `customEvents`; wire the OTel SDK + exporter in the agent-host (runtime-config, gated on the App Insights connection string).
2. **M2-app** — emit `userEvent`s from `hcc-app-fluent` (a thumbs / accept control on the reco/reply) → `POST /agents/{name}/interactions/{id}/events` via a new `postInteractionEvent()` in `iq-client.ts`.
3. **M3** — evaluator library (citation coverage, groundedness, refusal correctness, PHI-leak, actionability, advisory-voice) + offline regression gate, extending `evals/product-owner-agent`.
4. **M4** — online continuous eval (scheduled ACA job sampling `agent_interactions`).
5. **M5** — curator (trace → versioned golden dataset with lineage) + advisory GitHub-issue backlog.
6. **M7–M9 (Improve)** — `prompt_optimize` / Agent Optimizer, knowledge refresh, and fine-tune (SFT/DPO/RFT) on the curated dataset, human-gated.
