# Sprint 43 WS-2 Implementation Plan — Real Fabric Grounding (FabricDeltaClient)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `FabricAdapter`'s hardcoded 3-row dict with a real
`FabricDeltaClient` that reads Gold Delta tables directly from OneLake,
covering all 12 tables used by `bmca-agent`, `dca-agent`, `ooa-agent`,
`orsa-agent`, and `sba-agent` — not just the 3 tables the mock happened to
hardcode.

**Architecture:** A single `FabricDeltaClient` instance (workspace-scoped,
not per-table) is constructed once in `HostState.__init__` when
`FABRIC_WORKSPACE_ID`/`FABRIC_LAKEHOUSE_ID` env vars are set, and injected
as `FabricAdapter`'s `query_fn`. `query_fn(table)` splits `"gold.foo"` into
schema `gold` + name `foo`, builds the OneLake `abfss://` URI, and reads the
Delta table via the `deltalake` package. Missing tables (6 of the 12 don't
exist yet — see the design doc §2 WS-2 inventory) degrade to `[]`,
matching `FabricAdapter`'s existing behavior for unrecognized tables — no
new error paths, no crashes.

**Tech Stack:** Python 3.11, `deltalake` (new dependency), `azure-identity`
(already optional `runtime` dependency), Bicep, pytest.

**Confirmed live technical contract (WS-2 spike, 2026-08-08):**

- URI: `abfss://{workspace_id}@onelake.dfs.fabric.microsoft.com/{lakehouse_id}/Tables/{schema}/{name}`
- Auth: Bearer token, scope `https://storage.azure.com/.default`.
- Read: `DeltaTable(uri, storage_options={"bearer_token": token, "use_fabric_endpoint": "true"})`,
  then transpose `.to_pyarrow_table().to_pydict()` into row dicts.
- RBAC: **already granted** — `id-ca-agent-host-ihzhhpf-sit` already holds
  the Fabric workspace **Viewer** role on `ws-ihzhhpf-sit-data`
  (`f3af9733-9503-4e92-98f9-a901d96f1c87`), confirmed live via
  `GET /v1/workspaces/{id}/roleAssignments`. No new grant needed.
- Missing-table handling: `DeltaTable(...)` raises (deltalake's
  `TableNotFoundError`, surfaces as a generic exception in older bindings)
  when the table doesn't exist. `FabricDeltaClient.query()` must catch any
  exception from the read and return `[]`, matching
  `FabricAdapter`'s current `samples.get(table, [])` behavior for unknown
  tables — a missing table is a data gap, not a system failure.
- Live-verified table existence (SIT, 2026-08-08): `gold.bed_assignment`,
  `gold.fact_capacity_baseline`, `gold.discharge_score`,
  `gold.discharge_recommendation`, `gold.encounter`, `gold.or_schedule`,
  `gold.forecast_output` exist. `gold.seasonality`, `gold.anaesthesia_status`,
  `gold.staff_availability`, `gold.shift_roster`, `gold.shift_plan` do
  **not** exist yet (upstream data gap, not a WS-2 blocker).

---

## File Structure

| File | Responsibility |
| ---- | -------------- |
| `apps/hcc-agent-host/src/tools/fabric_delta_client.py` (create) | `FabricDeltaClient` — the real OneLake Delta reader |
| `apps/hcc-agent-host/src/api/app.py` (modify) | `_build_fabric_query_fn()` factory + `HostState.__init__` wiring |
| `apps/hcc-agent-host/pyproject.toml` (modify) | Add `deltalake` to the `runtime` optional-dependency group |
| `apps/hcc-agent-host/tests/unit/test_fabric_delta_client.py` (create) | Unit tests, no cloud calls |
| `apps/hcc-agent-host/tests/unit/test_build_fabric_query_fn.py` (create) | Unit tests for the env-gated factory |
| `infra/modules/agent-host/container-app.bicep` (modify) | New param `fabricLakehouseId` → env var `FABRIC_LAKEHOUSE_ID` |
| `infra/modules/agent-host/main.bicep` (modify) | Pass-through param |
| `infra/main.bicep` (modify) | Top-level param → pass-through |
| `infra/environments/sit.bicepparam` (modify) | Set the real SIT lakehouse ID (`30594c20-46ba-40ea-91fa-4701b105e0b9`, reuses the existing `fabricWorkspaceId` value already set for the Data Agent) |

---

### Task 1: Create `FabricDeltaClient`

**Files:**
- Create: `apps/hcc-agent-host/src/tools/fabric_delta_client.py`
- Test: `apps/hcc-agent-host/tests/unit/test_fabric_delta_client.py` (create)

- [ ] **Step 1: Write the failing tests**

Create `apps/hcc-agent-host/tests/unit/test_fabric_delta_client.py`:

```python
"""Unit tests for FabricDeltaClient (Sprint 43 WS-2).

No cloud calls -- token_provider and table_reader are injected fakes.
"""

from __future__ import annotations

import pytest

from tools.fabric_delta_client import FabricDeltaClient


def _client(fake_reader):
    return FabricDeltaClient(
        workspace_id="ws-1",
        lakehouse_id="lh-1",
        token_provider=lambda: "fake-token",
        table_reader=fake_reader,
    )


def test_query_builds_correct_onelake_uri_and_passes_token():
    captured = {}

    def fake_reader(uri, token):
        captured["uri"] = uri
        captured["token"] = token
        return [{"ward": "B", "occupied": 46, "capacity": 50}]

    rows = _client(fake_reader).query("gold.bed_assignment")

    assert rows == [{"ward": "B", "occupied": 46, "capacity": 50}]
    assert captured["uri"] == (
        "abfss://ws-1@onelake.dfs.fabric.microsoft.com/lh-1/Tables/gold/bed_assignment"
    )
    assert captured["token"] == "fake-token"


def test_query_handles_schema_other_than_gold():
    captured = {}

    def fake_reader(uri, token):
        captured["uri"] = uri
        return []

    _client(fake_reader).query("ops.data_quality_runs")

    assert captured["uri"] == (
        "abfss://ws-1@onelake.dfs.fabric.microsoft.com/lh-1/Tables/ops/data_quality_runs"
    )


def test_query_raises_on_malformed_table_name():
    def fake_reader(uri, token):
        return []

    with pytest.raises(ValueError):
        _client(fake_reader).query("no_dot_in_this_name")


def test_query_returns_empty_list_when_table_missing():
    def fake_reader(uri, token):
        raise RuntimeError("Generic delta kernel error: No files in log segment")

    rows = _client(fake_reader).query("gold.seasonality")

    assert rows == []


def test_query_returns_empty_list_on_any_reader_exception():
    def fake_reader(uri, token):
        raise ValueError("boom -- some other unexpected error")

    rows = _client(fake_reader).query("gold.anaesthesia_status")

    assert rows == []
```

- [ ] **Step 2: Run the tests to verify they fail**

Run (from `apps/hcc-agent-host/`): `python -m pytest tests/unit/test_fabric_delta_client.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'tools.fabric_delta_client'`

- [ ] **Step 3: Write the implementation**

Create `apps/hcc-agent-host/src/tools/fabric_delta_client.py`:

```python
"""Sprint 43 WS-2 -- live Fabric Gold table reads via direct OneLake access.

Reads Gold Delta tables directly from OneLake (bypasses the Fabric SQL
analytics endpoint, which lags and is not authoritative -- see
``data-platform/scripts/fabric/read_gold_evidence.py``, the proven pattern
this class mirrors).

Confirmed live contract (Sprint 43 WS-2 spike, 2026-08-08):
  URI: abfss://{workspace_id}@onelake.dfs.fabric.microsoft.com/{lakehouse_id}/Tables/{schema}/{name}
  Auth: Bearer token, scope https://storage.azure.com/.default
  Read: DeltaTable(uri, storage_options={"bearer_token": token,
        "use_fabric_endpoint": "true"}), then transpose
        .to_pyarrow_table().to_pydict() into row dicts.

Missing tables are a genuine upstream data gap (6 of the 12 tables this
platform's manifests reference do not exist yet in the SIT lakehouse) --
``query()`` catches any read failure and returns ``[]``, matching
``FabricAdapter``'s existing graceful-miss behavior for unrecognized
tables. This is not error suppression for its own sake: a missing Gold
table should read as "no grounding available", the same as it does today.

Token provider and table reader are injected (mirrors
``tools/fabric_data_agent_client.py`` and
``orchestrator/foundry_chat_model.py``) so this class is unit-testable
without cloud access.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

_STORAGE_SCOPE = "https://storage.azure.com/.default"
_ONELAKE_HOST = "onelake.dfs.fabric.microsoft.com"

logger = logging.getLogger(__name__)


def _default_token_provider() -> str:
    from azure.identity import DefaultAzureCredential

    cred = DefaultAzureCredential()
    return cred.get_token(_STORAGE_SCOPE).token


def _default_table_reader(uri: str, token: str) -> list[dict[str, Any]]:
    from deltalake import DeltaTable

    dt = DeltaTable(uri, storage_options={"bearer_token": token, "use_fabric_endpoint": "true"})
    pydict = dt.to_pyarrow_table().to_pydict()
    if not pydict:
        return []
    columns = list(pydict.keys())
    row_count = len(next(iter(pydict.values())))
    return [{col: pydict[col][i] for col in columns} for i in range(row_count)]


class FabricDeltaClient:
    """Reads Gold (or any schema) Delta tables directly from OneLake."""

    def __init__(
        self,
        workspace_id: str,
        lakehouse_id: str,
        token_provider: Callable[[], str] = _default_token_provider,
        table_reader: Callable[[str, str], list[dict[str, Any]]] = _default_table_reader,
    ):
        self._workspace_id = workspace_id
        self._lakehouse_id = lakehouse_id
        self._token_provider = token_provider
        self._table_reader = table_reader

    def query(self, table: str) -> list[dict[str, Any]]:
        schema, sep, name = table.partition(".")
        if not sep or not name:
            raise ValueError(f"expected 'schema.table', got {table!r}")
        uri = (
            f"abfss://{self._workspace_id}@{_ONELAKE_HOST}/"
            f"{self._lakehouse_id}/Tables/{schema}/{name}"
        )
        token = self._token_provider()
        try:
            return self._table_reader(uri, token)
        except Exception:
            logger.warning("Fabric Gold table '%s' unavailable; returning no grounding", table)
            return []
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/unit/test_fabric_delta_client.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add apps/hcc-agent-host/src/tools/fabric_delta_client.py apps/hcc-agent-host/tests/unit/test_fabric_delta_client.py
git commit -m "feat(agent-host): add FabricDeltaClient (Sprint 43 WS-2)"
```

---

### Task 2: Wire the env-gated factory into `HostState`

**Files:**
- Modify: `apps/hcc-agent-host/src/api/app.py`
- Modify: `apps/hcc-agent-host/pyproject.toml`
- Test: `apps/hcc-agent-host/tests/unit/test_build_fabric_query_fn.py` (create)

- [ ] **Step 1: Add `deltalake` to the runtime dependency group**

In `apps/hcc-agent-host/pyproject.toml`, replace:

```toml
runtime = [
  "azure-identity>=1.19,<2",
  "azure-cosmos>=4.7,<5",
  "redis>=5.1,<6",
  "openai>=1.55,<2",
  "azure-monitor-opentelemetry>=1.6,<2",
]
```

with:

```toml
runtime = [
  "azure-identity>=1.19,<2",
  "azure-cosmos>=4.7,<5",
  "redis>=5.1,<6",
  "openai>=1.55,<2",
  "azure-monitor-opentelemetry>=1.6,<2",
  "deltalake>=0.20,<2",
]
```

- [ ] **Step 2: Write the failing tests**

Create `apps/hcc-agent-host/tests/unit/test_build_fabric_query_fn.py`:

```python
"""Unit tests for the env-gated live Fabric Delta query factory (Sprint 43 WS-2)."""

from __future__ import annotations

import api.app as appmod


def _clear_env(monkeypatch):
    for k in ("FABRIC_WORKSPACE_ID", "FABRIC_LAKEHOUSE_ID"):
        monkeypatch.delenv(k, raising=False)


def test_returns_none_when_no_env(monkeypatch):
    _clear_env(monkeypatch)
    assert appmod._build_fabric_query_fn() is None


def test_returns_none_on_partial_env(monkeypatch, caplog):
    _clear_env(monkeypatch)
    monkeypatch.setenv("FABRIC_WORKSPACE_ID", "ws-1")
    assert appmod._build_fabric_query_fn() is None
    assert "FABRIC_LAKEHOUSE_ID" in caplog.text or "partially configured" in caplog.text


def test_returns_callable_when_all_env_set(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("FABRIC_WORKSPACE_ID", "ws-1")
    monkeypatch.setenv("FABRIC_LAKEHOUSE_ID", "lh-1")
    query_fn = appmod._build_fabric_query_fn()
    assert query_fn is not None
    assert callable(query_fn)
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python -m pytest tests/unit/test_build_fabric_query_fn.py -v`
Expected: FAIL with `AttributeError: module 'api.app' has no attribute '_build_fabric_query_fn'`

- [ ] **Step 4: Add the factory function**

In `apps/hcc-agent-host/src/api/app.py`, immediately after `_build_chat_model()`, add:

```python
def _build_fabric_query_fn():
    """Return a live FabricDeltaClient.query callable when env is configured, else None.

    Sprint 43 WS-2 -- reuses FABRIC_WORKSPACE_ID (already set for the Fabric
    Data Agent binding, same workspace) plus the new FABRIC_LAKEHOUSE_ID.
    """
    workspace = os.environ.get("FABRIC_WORKSPACE_ID")
    lakehouse = os.environ.get("FABRIC_LAKEHOUSE_ID")
    provided = [bool(workspace), bool(lakehouse)]
    if not all(provided):
        if any(provided):
            logger.warning(
                "FABRIC_WORKSPACE_ID/FABRIC_LAKEHOUSE_ID partially configured "
                "(%d/2 set); FabricAdapter stays on synthetic fallback",
                sum(provided),
            )
        return None
    from tools.fabric_delta_client import FabricDeltaClient

    return FabricDeltaClient(workspace_id=workspace, lakehouse_id=lakehouse).query
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest tests/unit/test_build_fabric_query_fn.py -v`
Expected: PASS (3 passed)

- [ ] **Step 6: Wire it into `HostState.__init__`**

In `apps/hcc-agent-host/src/api/app.py`, find:

```python
class HostState:
    def __init__(self, agents_root: Path):
        self.agents_root = agents_root
        self.manifests: dict[str, AgentManifest] = load_agent_host_manifests(agents_root)
```

and the block a few lines below it that builds `adapter`:

```python
        live = _build_live_data_agent()
        self._live_data_agent = live
        adapter = FabricDataAgentAdapter(ask_fn=(live.ask if live is not None else None))
```

Immediately before that block, add the fabric query_fn build, and pass it
into `FabricAdapter`. Replace:

```python
        live = _build_live_data_agent()
        self._live_data_agent = live
        adapter = FabricDataAgentAdapter(ask_fn=(live.ask if live is not None else None))
```

with:

```python
        # Sprint 43 WS-2 -- live Fabric Gold table reads (replaces
        # FabricAdapter's hardcoded 3-row dict). Unset env keeps the
        # synthetic fallback (dev/CI default).
        fabric_query_fn = _build_fabric_query_fn()
        self.fabric = FabricAdapter(query_fn=fabric_query_fn)

        live = _build_live_data_agent()
        self._live_data_agent = live
        adapter = FabricDataAgentAdapter(ask_fn=(live.ask if live is not None else None))
```

Then find where `Orchestrator(...)` is constructed:

```python
        self.orchestrator = Orchestrator(
            chat_model=live_chat_model if live_chat_model is not None else MockChatModel(),
            data_agent=adapter,
        )
```

and add the `fabric` field so the orchestrator uses the same adapter
instance:

```python
        self.orchestrator = Orchestrator(
            chat_model=live_chat_model if live_chat_model is not None else MockChatModel(),
            fabric=self.fabric,
            data_agent=adapter,
        )
```

Finally, add the import at the top of the file, next to the existing
`from tools.fabric_data_agent_adapter import FabricDataAgentAdapter` line:

```python
from tools.fabric_adapter import FabricAdapter
```

- [ ] **Step 7: Run the full test suite**

Run: `python -m pytest -v`
Expected: PASS (all tests, including the 3 new build-factory tests and
the 5 new `FabricDeltaClient` tests)

- [ ] **Step 8: Commit**

```bash
git add apps/hcc-agent-host/src/api/app.py apps/hcc-agent-host/pyproject.toml apps/hcc-agent-host/tests/unit/test_build_fabric_query_fn.py
git commit -m "feat(agent-host): wire FabricDeltaClient behind FABRIC_WORKSPACE_ID/FABRIC_LAKEHOUSE_ID"
```

---

### Task 3: Thread the Bicep param through to SIT

**Files:**
- Modify: `infra/modules/agent-host/container-app.bicep`
- Modify: `infra/modules/agent-host/main.bicep`
- Modify: `infra/main.bicep`
- Modify: `infra/environments/sit.bicepparam`

- [ ] **Step 1: Add the param + env var in `container-app.bicep`**

In `infra/modules/agent-host/container-app.bicep`, after the existing
`foundryProjectName` param, add:

```bicep
@description('Sprint 43 WS-2 -- Fabric lakehouse ID for direct OneLake Gold table reads (reuses fabricWorkspaceId for the workspace half). Empty string keeps FabricAdapter on its synthetic 3-row fallback.')
param fabricLakehouseId string = ''
```

Then, inside the `baseEnv` array, after the `FOUNDRY_PROJECT_NAME` entry,
add:

```bicep
  {
    name: 'FABRIC_LAKEHOUSE_ID'
    value: fabricLakehouseId
  }
```

- [ ] **Step 2: Validate the module builds**

Run: `az bicep build --file infra/modules/agent-host/container-app.bicep --stdout > $null`
Expected: exit code 0.

- [ ] **Step 3: Pass the param through `agent-host/main.bicep`**

In `infra/modules/agent-host/main.bicep`, after the existing
`foundryProjectName` param, add:

```bicep
@description('Sprint 43 WS-2 -- Fabric lakehouse ID for direct OneLake Gold table reads. Empty string keeps FabricAdapter on its synthetic fallback.')
param fabricLakehouseId string = ''
```

Then, inside the `containerApp` module's `params` block, after the
existing `foundryProjectName: foundryProjectName` line, add:

```bicep
    fabricLakehouseId: fabricLakehouseId
```

- [ ] **Step 4: Validate the module builds**

Run: `az bicep build --file infra/modules/agent-host/main.bicep --stdout > $null`
Expected: exit code 0.

- [ ] **Step 5: Add the top-level param in `infra/main.bicep`**

In `infra/main.bicep`, after the existing `foundryProjectName` param, add:

```bicep
@description('Sprint 43 WS-2 -- Fabric lakehouse ID for direct OneLake Gold table reads. Empty string keeps FabricAdapter on its synthetic fallback.')
param fabricLakehouseId string = ''
```

Then, inside the `agentHost` module's `params` block, after the existing
`foundryProjectName: foundryProjectName` line, add:

```bicep
    fabricLakehouseId: fabricLakehouseId
```

- [ ] **Step 6: Validate the top-level template builds**

Run: `az bicep build --file infra/main.bicep --stdout > $null`
Expected: exit code 0.

- [ ] **Step 7: Set the real SIT value in `sit.bicepparam`**

In `infra/environments/sit.bicepparam`, immediately after the existing
`param foundryProjectName = '...'` line, add:

```bicep
// Sprint 43 WS-2 -- real Fabric Gold table reads (replaces FabricAdapter's
// hardcoded 3-row dict). Same lakehouse already referenced in
// data-platform/fabric/environments.yml (SIT). The agent-host MI already
// holds Fabric workspace Viewer on ws-ihzhhpf-sit-data (confirmed live via
// GET /v1/workspaces/{id}/roleAssignments 2026-08-08) -- no new grant needed.
param fabricLakehouseId = '30594c20-46ba-40ea-91fa-4701b105e0b9'
```

- [ ] **Step 8: Validate the bicepparam file**

Run: `az bicep build-params --file infra/environments/sit.bicepparam --stdout > $null`
Expected: exit code 0.

- [ ] **Step 9: Run a `what-if` against the real SIT resource group**

Run:

```bash
az deployment group what-if --resource-group rg-ihzhhpf-sit --template-file infra/main.bicep --parameters infra/environments/sit.bicepparam
```

Expected: the only change is the new `FABRIC_LAKEHOUSE_ID` env var being
added to `ca-agent-host-ihzhhpf-sit` (a `Modify` on that one resource).

- [ ] **Step 10: Commit**

```bash
git add infra/modules/agent-host/container-app.bicep infra/modules/agent-host/main.bicep infra/main.bicep infra/environments/sit.bicepparam
git commit -m "feat(infra): thread FABRIC_LAKEHOUSE_ID to agent-host (Sprint 43 WS-2)"
```

---

### Task 4: Rebuild the image, redeploy, and live-verify

**Files:** none (operational task)

> **Lesson from WS-1** (see `docs/superpowers/plans/2026-08-08-sprint-43-ws1-foundry-chat-model.md`
> and the repo-memory note `image-build-vs-infra-deploy-decoupling.md`):
> `ci-build-agent-host.yml` builds a new image on push but does **not**
> auto-bump `agentHostImage` in `sit.bicepparam`. After Task 1-3's push,
> check for the new image tag and bump `agentHostImage` explicitly
> **before** relying on any `cd-infra-deploy-sit.yml` run to actually ship
> this code — otherwise the env var lands but the old code (without
> `FabricDeltaClient`) keeps running.

- [ ] **Step 1: Push and find the new image tag**

```bash
git push
gh run list --workflow=ci-build-agent-host.yml --limit 1 --json databaseId,status,conclusion,headSha
```

Wait for `status: completed`, `conclusion: success`. The image tag is the
7-char short SHA of `headSha`.

- [ ] **Step 2: Bump `agentHostImage` in `sit.bicepparam` to the new tag**

Follow the existing inline-comment convention (see the WS-1 hotfix entries
immediately above the `param agentHostImage = ...` line) — add a dated
note explaining this bump ships `FabricDeltaClient`, then commit and push.

- [ ] **Step 3: Wait for `cd-infra-deploy-sit.yml`, approve if needed, confirm success**

```bash
gh run list --workflow=cd-infra-deploy-sit.yml --limit 1 --json databaseId,status,conclusion
```

If `status: waiting`, this needs the "sit" GitHub Environment approval —
tell the user and wait; do not attempt to bypass it.

- [ ] **Step 4: Confirm the new env var and image landed**

```bash
az containerapp show --name ca-agent-host-ihzhhpf-sit --resource-group rg-ihzhhpf-sit --query "{image: properties.template.containers[0].image, fabricLakehouse: properties.template.containers[0].env[?name=='FABRIC_LAKEHOUSE_ID'].value | [0]}"
```

- [ ] **Step 5: Re-test `bmca-agent` live via raw HTTP**

```bash
curl -s -X POST "https://ca-agent-host-ihzhhpf-sit.<domain>/agents/bmca-agent/chat" \
  -H "content-type: application/json" \
  -d '{"prompt": "Wie ist die aktuelle Belegung auf Station B?", "conversationId": "sprint43-ws2-verify", "callerObjectId": "verify.user"}'
```

Expected: `refused: false`, and the grounding row values are now the
**real** live table contents (from `gold.bed_assignment` etc.), not the
hardcoded `{"ward": "B", "occupied": 46, "capacity": 50}` triple. Compare
against the raw table read from Task 1's spike to confirm the numbers
match the live data, not the old mock.

- [ ] **Step 6: Re-test `orsa-agent` and `sba-agent` (the partial-coverage cases)**

Confirm these agents' answers now incorporate whatever real grounding is
available (`gold.or_schedule` for orsa; `gold.forecast_output` for sba)
without erroring, even though 2 of their 3 tables are still missing
upstream.

- [ ] **Step 7: Record verification evidence in the design doc**

Append to `docs/superpowers/specs/2026-08-08-sprint-43-real-iq-layer-grounding-design.md`
§2 (WS-2 section) with the live curl output, deployed image tag, and
commit SHA. Bump the doc's version (MINOR, per `document-authoring`).

- [ ] **Step 8: Re-run the full local test suite**

```bash
cd apps/hcc-agent-host
python -m pytest -v
```

Expected: PASS, unchanged count from Task 2 plus this session's runs.

- [ ] **Step 9: Post completion comment + check off WS-2 on issue #567**

Summarize the live evidence, commits, and the 6-table upstream gap (not a
WS-2 blocker) on the issue thread; check off WS-2's 3 checklist items.

---

## Notes for the next plan (WS-3)

WS-3 (replace `SimulatedRlsProvider` with a live Fabric-backed RLS
provider for `/golden/{resource}`) reuses the exact same
`FabricDeltaClient`/OneLake connection this plan establishes — no new
Fabric client needed, just a new provider class in `golden/rls.py` that
calls it. Write a fresh plan via `writing-plans` once WS-2 is verified
live, following this same TDD/Bicep/deploy/verify shape.
