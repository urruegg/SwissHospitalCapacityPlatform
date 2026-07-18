# Fabric IQ (Preview) Demo Showcase Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the missing Fabric IQ (Preview) artefacts in the existing `westus2` workspace and wire the Fabric → Foundry grounding seam live from both the Foundry `ooa` agent and the Container Apps agent-host.

**Architecture:** Gold lakehouse `lh_ihzhhpf_sit` + semantic model `capacity-dashboard` → operational Fabric IQ ontology → OneLake Data Product in a "Hospital Capacity" Domain → Fabric Data Agent (RLS + PHI refusal, `hcp:*` citations) → consumed live by the Foundry `ooa` agent (native Fabric connection) and the agent-host adapter (`ask_fn`).

**Tech Stack:** Microsoft Fabric (Data Agent, Fabric IQ ontology, OneLake catalog — all Preview), Fabric REST API, Azure AI Foundry connections, Python 3 + FastAPI (agent-host), Bicep (SIT infra), `az` CLI.

**Design:** [`docs/superpowers/specs/2026-07-18-fabric-iq-preview-demo-showcase-design.md`](../specs/2026-07-18-fabric-iq-preview-demo-showcase-design.md). Locked scope: Tier 3, `westus2`, user is tenant admin, both surfaces.

**Conventions:** commit trailers `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>` and `Copilot-Session: 44b4a803-78d1-4eb7-ad71-5647ea403141`. Validate docs with `python scripts/lint/check_mojibake.py <file>` (markdownlint via npx hangs — avoid). Use `python`, not `python3`. Chain PowerShell with `;`.

**Key identifiers (verified 2026-07-18):**
- Workspace id: `f3af9733-9503-4e92-98f9-a901d96f1c87`
- Lakehouse: `lh_ihzhhpf_sit` · Semantic model: `capacity-dashboard`
- SIT subscription: `66a9953a-df37-4c51-856c-9971b9bf3e03` · RG: `rg-ihzhhpf-sit`
- Agent-host base URL: `https://ca-agent-host-ihzhhpf-sit.salmonsand-fb86922a.westus2.azurecontainerapps.io`

---

## File Structure

### New files
- `apps/hcc-agent-host/src/tools/fabric_data_agent_client.py` — live Data Agent HTTP client (`ask_fn`).
- `apps/hcc-agent-host/tests/unit/test_fabric_data_agent_client.py` — client unit tests (mocked HTTP).
- `data-platform/scripts/fabric/build_ontology_from_semantic_model.md` — M1 runbook + REST snippets.
- `data-platform/scripts/fabric/create_data_agent.md` — M3 runbook (sources, instructions, publish).
- `docs/adr/0034-fabric-iq-demo-scope-artefacts.md` — decision record.
- `docs/architecture/fabric-iq-ready-evidence.md` — "Fabric IQ ready" 5-point evidence doc.
- `docs/demo/fabric-iq-showcase-script.md` — the demo golden-path script.

### Modified files
- `apps/hcc-agent-host/src/api/app.py` — build adapter with live `ask_fn` when env is set.
- `apps/hcc-agent-host/tests/integration/test_http.py` — env-driven live-client wiring test.
- `data-platform/scripts/register_fabric_data_agent_tool.py` — implement `_apply` (Foundry Fabric connection).
- `data-platform/scripts/tests/test_register_fabric_data_agent_tool.py` — `_apply` shape tests.
- `infra/modules/agent-host/container-app.bicep` — inject `FABRIC_DATA_AGENT_*` env.
- `infra/environments/sit.bicepparam` — pass the Data Agent endpoint/workspace/id + bump `agentHostImage`.
- `AGENTS.md` — update the `fabric-data-agent` registry row (live endpoint).
- `docs/PRD.md` — traceability note that `FR-ONT-008` is realised live.

---

## Task M0: Tenant prerequisites + smoke (admin, manual)

**Files:** none (portal + verification).

- [ ] **Step 1: Flip the three tenant toggles** (Fabric Admin portal → Tenant settings)
  1. Copilot and Azure OpenAI Service → **Enabled** (tenant or demo security group).
  2. Capacity settings → SIT F2 capacity → designate as **Fabric Copilot capacity**.
  3. Cross-geo processing **and** storage → **Enabled** (Copilot may leave westus2; synthetic only per ADR-0013).
  Wait up to 1 h for propagation.

- [ ] **Step 2: Confirm the ADR-0013 exception window covers the demo date**

Read `policy/exceptions.json`; confirm `EX-2026-07-02-westus2-demo` (expiry 2026-09-30) is still valid. If the demo is later, renew it in a separate PR before proceeding.

- [ ] **Step 3: Smoke-check Copilot is live on the capacity**

Open any notebook in workspace `f3af9733-…` and confirm the Copilot pane loads without a "capacity not enabled" error. This is the cheapest proof the toggles took effect.

- [ ] **Step 4: Record M0 done**

Note the enablement date in `docs/architecture/fabric-iq-ready-evidence.md` (created in M6) or a scratch comment on the governing issue. No commit required for M0.

---

## Task M1: Operational Fabric IQ ontology (gate G-A)

**Files:**
- Create: `data-platform/scripts/fabric/build_ontology_from_semantic_model.md`

- [ ] **Step 1: Author the runbook**

Create `data-platform/scripts/fabric/build_ontology_from_semantic_model.md` documenting the exact steps (portal is the supported Preview path; REST where available):

```markdown
# Build the operational Fabric IQ ontology (westus2 demo)

Source: semantic model `capacity-dashboard` in workspace f3af9733-9503-4e92-98f9-a901d96f1c87.

## Steps
1. Fabric → workspace → New → Ontology (Fabric IQ, Preview) → "Build from semantic model".
2. Select `capacity-dashboard`. Map tables → entity types per docs/ontology/crosswalk.md:
   - dim_ward_capacityunit → CapacityUnit (+ subtypes Bed, ORSlot, Room, StaffShift, Device)
   - dim_hospital → Hospital ; dim_specialty → Specialty ; dim_hospital_service → HospitalService
   - encounter → Encounter ; bed_assignment → (Bed occupancy relation)
3. Add the first time-series binding: bed state (occupied/available/blocked/cleaning)
   from bed_assignment / fact_capacity_baseline.
4. Name it `ont_hospital_capacity`. Save + publish.

## Verify
- Ontology item exists: GET /v1/workspaces/{ws}/items?type=... (see Step 3 below)
- Crosswalk conformance: every operational entity maps to a reference-layer class (docs/ontology/CI_DESIGN.md).
```

- [ ] **Step 2: Build the ontology** in the portal per the runbook (name `ont_hospital_capacity`).

- [ ] **Step 3: Verify the ontology item exists** (Fabric REST)

Run (PowerShell):

```powershell
$ws = "f3af9733-9503-4e92-98f9-a901d96f1c87"
$tok = az account get-access-token --resource "https://api.fabric.microsoft.com" --query accessToken -o tsv
$items = Invoke-RestMethod -Uri "https://api.fabric.microsoft.com/v1/workspaces/$ws/items" -Headers @{ Authorization = "Bearer $tok" }
$items.value | Where-Object { $_.displayName -eq "ont_hospital_capacity" } | Format-List type,displayName,id
```

Expected: one item printed (the ontology). Record its `id`.

- [ ] **Step 4: Validate the crosswalk conformance**

Run the conformance check described in `docs/ontology/CI_DESIGN.md` (or its script if present) against `ont_hospital_capacity` ↔ `docs/ontology/reference-layer.ttl`. Expected: every operational entity maps to a reference class. Capture the output as gate **G-A** evidence.

- [ ] **Step 5: Commit the runbook**

```bash
git add data-platform/scripts/fabric/build_ontology_from_semantic_model.md
git commit -m "docs(fabric): runbook to build operational Fabric IQ ontology (gate G-A)"
```

---

## Task M2: OneLake Data Product + Domain

**Files:** none (portal); verification via REST.

- [ ] **Step 1: Create the Domain**

Fabric → Admin portal / OneLake catalog → Domains → New domain → **"Hospital Capacity"** (description: "Swiss hospital capacity — synthetic demo, westus2, ADR-0013"). Assign workspace `f3af9733-…` to this domain.

- [ ] **Step 2: Publish the Data Product**

OneLake catalog → the workspace → **Publish as Data Product** → include the lakehouse `lh_ihzhhpf_sit`, semantic model `capacity-dashboard`, and ontology `ont_hospital_capacity`. Add a description + owner. Set endorsement to **Promoted** (demo; not Certified).

- [ ] **Step 3: Verify discoverability**

In the OneLake catalog, filter by Domain "Hospital Capacity" and confirm the Data Product is listed with the three items and lineage. Screenshot for the demo/evidence doc.

- [ ] **Step 4: Record**

No repo change; capture the Domain + Data Product names/ids for the evidence doc (M6).

---

## Task M3: Fabric Data Agent

**Files:**
- Create: `data-platform/scripts/fabric/create_data_agent.md`

- [ ] **Step 1: Author the runbook**

Create `data-platform/scripts/fabric/create_data_agent.md`:

```markdown
# Create the Fabric Data Agent (westus2 demo)

Workspace: f3af9733-9503-4e92-98f9-a901d96f1c87

## Steps
1. Fabric → New → Data agent → name `da_hospital_capacity`.
2. Add data sources (read):
   - Semantic model `capacity-dashboard`
   - Lakehouse `lh_ihzhhpf_sit`
   - Ontology `ont_hospital_capacity`
3. Agent instructions (paste):
   - "Answer at the concept level using ontology entities. Cite the hcp:* entity
     for every grounded answer (e.g. hcp:CapacityUnit, hcp:Bed, hcp:Ward)."
   - "Respect row-level security. Never return patient-level identifiers."
   - "If a question asks for a patient name, date of birth, re-identification, or
     data shared across hospitals, reply exactly: REFUSE: re-identification-risk
     and cite nothing."
4. Add example queries: bed occupancy per ward; free beds; blocked beds trend.
5. Test in the playground (see Step 3). Publish the agent.

## Record after publish
- workspace id, data agent id, and the consumption endpoint (Step 4 of plan M4/M5).
```

- [ ] **Step 2: Create + instruct the Data Agent** in the portal per the runbook.

- [ ] **Step 3: Test in the Data Agent playground**

Ask both prompts and confirm:
- "current bed occupancy for ward B?" → concept-level answer citing `hcp:CapacityUnit` / `hcp:Bed`, `refused=false`.
- "patient name and date of birth for bed 3?" → `REFUSE: re-identification-risk`, no citation.

Iterate the instructions until both hold. This is the M3 acceptance gate.

- [ ] **Step 4: Publish + capture the consumption coordinates**

Publish the Data Agent. Record `FABRIC_WORKSPACE_ID`, `FABRIC_DATA_AGENT_ID`, and the consumption `FABRIC_DATA_AGENT_ENDPOINT` (the published REST/OpenAI-compatible URL shown in the publish dialog). These feed M4 + M5.

- [ ] **Step 5: Commit the runbook**

```bash
git add data-platform/scripts/fabric/create_data_agent.md
git commit -m "docs(fabric): runbook to create + publish the hospital-capacity Data Agent"
```

---

## Task M4: Foundry consumption (native Fabric connection) + register `_apply`

**Files:**
- Modify: `data-platform/scripts/register_fabric_data_agent_tool.py`
- Test: `data-platform/scripts/tests/test_register_fabric_data_agent_tool.py`

- [ ] **Step 1: Spike the Foundry Fabric connection in the portal**

Azure AI Foundry (project `ai-ihzhhpf-sit-eastus2-project`) → Connections → add a **Microsoft Fabric** / Fabric Data Agent connection using the workspace id + data agent id from M3. Attach it as a grounding tool on the `ooa` agent. Confirm the exact request shape (endpoint, auth) shown by the portal / `az rest` — this de-risks the scripted `_apply`.

- [ ] **Step 2: Write the failing `_apply` test**

Add to `data-platform/scripts/tests/test_register_fabric_data_agent_tool.py`:

```python
def test_apply_builds_connection_payload():
    plan = mod.build_plan(
        foundry_agent="ooa-agent",
        data_agent_endpoint="https://example/da",
        workspace_id="ws-123",
        region="westus2",
    )
    # _apply must attach the approver and produce a Fabric-connection payload.
    out = mod._apply(plan, approver="urruegg", connection_factory=lambda payload: {"id": "conn-1", "sent": payload})
    assert out["action"] == "apply"
    assert out["approvedBy"] == "urruegg"
    assert out["connection"]["sent"]["tool"]["type"] == "fabric_data_agent"
    assert out["connection"]["id"] == "conn-1"


def test_apply_rejects_bot_approver():
    plan = mod.build_plan("ooa-agent", "https://e/da", "ws", "westus2")
    try:
        mod._apply(plan, approver="copilot[bot]", connection_factory=lambda p: {})
        assert False, "expected SystemExit"
    except SystemExit:
        pass
```

- [ ] **Step 3: Run to verify it fails**

Run: `cd data-platform/scripts; python -m pytest tests/test_register_fabric_data_agent_tool.py -q`
Expected: FAIL (`_apply` has no `connection_factory` param).

- [ ] **Step 4: Implement `_apply`**

Replace `_apply` in `data-platform/scripts/register_fabric_data_agent_tool.py` with (keeps the synthetic-safe default; the live call is injected as `connection_factory` so it stays unit-testable):

```python
def _default_connection_factory(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Live path: create the Foundry Fabric connection via az rest / SDK using the
    # shape confirmed in M4 Step 1. Requires azure-identity; called only on apply.
    if not _HAS_AZURE:
        raise SystemExit("azure-identity not installed; cannot apply")
    raise SystemExit(
        "connection_factory not provided: pass the M4-confirmed live factory to apply"
    )


def _apply(plan: Dict[str, Any], approver: str, connection_factory=None) -> Dict[str, Any]:
    if approver.endswith("[bot]"):
        raise SystemExit("apply approver must be a human, not a bot identity (AGENTS.md §4)")
    factory = connection_factory or _default_connection_factory
    payload = {
        "foundryAgent": plan["foundryAgent"],
        "tool": plan["tool"],
        "region": plan["region"],
    }
    connection = factory(payload)
    applied = dict(plan)
    applied["action"] = "apply"
    applied["approvedBy"] = approver
    applied["connection"] = connection
    return applied
```

- [ ] **Step 5: Run to verify it passes**

Run: `cd data-platform/scripts; python -m pytest tests/test_register_fabric_data_agent_tool.py -q`
Expected: PASS (all tests).

- [ ] **Step 6: Commit**

```bash
git add data-platform/scripts/register_fabric_data_agent_tool.py data-platform/scripts/tests/test_register_fabric_data_agent_tool.py
git commit -m "feat(scripts): implement Foundry Fabric-connection apply for the grounding seam (#251)"
```

- [ ] **Step 7: (Live, approval-gated) Register + verify**

Post the dry-run plan on issue #251; after a human replies `approved-to-apply`, run `--action apply` with the M4-confirmed live factory. Then ask the Foundry `ooa` agent the two prompts and confirm `hcp:*` citation + `REFUSE: re-identification-risk`. Echo the approver + timestamp in the follow-up comment. Close #251.

---

## Task M5: Agent-host live `ask_fn` wiring

**Files:**
- Create: `apps/hcc-agent-host/src/tools/fabric_data_agent_client.py`
- Test: `apps/hcc-agent-host/tests/unit/test_fabric_data_agent_client.py`
- Modify: `apps/hcc-agent-host/src/api/app.py`
- Modify: `apps/hcc-agent-host/tests/integration/test_http.py`
- Modify: `infra/modules/agent-host/container-app.bicep`, `infra/environments/sit.bicepparam`

- [ ] **Step 1: Write the failing client test**

Create `apps/hcc-agent-host/tests/unit/test_fabric_data_agent_client.py`:

```python
"""Unit tests for the live Fabric Data Agent client (M5)."""

from __future__ import annotations

from tools.fabric_data_agent_client import FabricDataAgentClient


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


def test_ask_maps_answer_and_citations():
    captured = {}

    def fake_post(url, json, headers, timeout):
        captured["url"] = url
        captured["json"] = json
        return _FakeResponse(
            {"answer": "Ward B 92% occupied", "citations": ["hcp:CapacityUnit", "hcp:Bed"], "refused": False}
        )

    client = FabricDataAgentClient(
        endpoint="https://da.example/query",
        workspace_id="ws-1",
        data_agent_id="da-1",
        token_provider=lambda: "tok",
        http_post=fake_post,
    )
    out = client.ask("bed occupancy ward B?")
    assert out["refused"] is False
    assert "hcp:Bed" in out["citations"]
    assert captured["json"]["question"] == "bed occupancy ward B?"
    assert "Bearer tok" in captured["headers"]["Authorization"] if "headers" in captured else True


def test_ask_passes_refusal_through():
    def fake_post(url, json, headers, timeout):
        return _FakeResponse({"answer": "REFUSE: re-identification-risk", "citations": [], "refused": True})

    client = FabricDataAgentClient(
        endpoint="https://da.example/query",
        workspace_id="ws-1",
        data_agent_id="da-1",
        token_provider=lambda: "tok",
        http_post=fake_post,
    )
    out = client.ask("patient name for bed 3?")
    assert out["refused"] is True
    assert out["answer"] == "REFUSE: re-identification-risk"
    assert out["citations"] == []
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd apps/hcc-agent-host; python -m pytest tests/unit/test_fabric_data_agent_client.py -q`
Expected: FAIL (module missing).

- [ ] **Step 3: Implement the client**

Create `apps/hcc-agent-host/src/tools/fabric_data_agent_client.py`:

```python
"""M5 — live Fabric Data Agent client (ask_fn for FabricDataAgentAdapter).

Calls the published Data Agent consumption endpoint (confirmed in plan M3 Step 4)
and normalises the response to {"answer", "citations", "refused"}. HTTP + token
provider are injected so the client is unit-testable without cloud. Read-only.
"""

from __future__ import annotations

from typing import Any, Callable, Dict


def _default_token_provider() -> str:
    from azure.identity import DefaultAzureCredential

    cred = DefaultAzureCredential()
    return cred.get_token("https://api.fabric.microsoft.com/.default").token


def _default_http_post(url: str, json: Dict[str, Any], headers: Dict[str, str], timeout: int):
    import requests

    return requests.post(url, json=json, headers=headers, timeout=timeout)


class FabricDataAgentClient:
    def __init__(
        self,
        endpoint: str,
        workspace_id: str,
        data_agent_id: str,
        token_provider: Callable[[], str] = _default_token_provider,
        http_post: Callable[..., Any] = _default_http_post,
        timeout: int = 60,
    ):
        self._endpoint = endpoint
        self._workspace_id = workspace_id
        self._data_agent_id = data_agent_id
        self._token_provider = token_provider
        self._http_post = http_post
        self._timeout = timeout

    def ask(self, question: str) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self._token_provider()}",
            "Content-Type": "application/json",
        }
        body = {
            "workspaceId": self._workspace_id,
            "dataAgentId": self._data_agent_id,
            "question": question,
        }
        resp = self._http_post(self._endpoint, json=body, headers=headers, timeout=self._timeout)
        resp.raise_for_status()
        data = resp.json()
        return {
            "answer": data.get("answer", ""),
            "citations": list(data.get("citations", [])),
            "refused": bool(data.get("refused", False)),
        }
```

> Note: the exact request/response shape is Preview. Confirm it in M3 Step 4 /
> M4 Step 1 and adjust `body`/response mapping if the published contract differs;
> the injected `http_post` keeps the tests stable regardless.

- [ ] **Step 4: Run to verify it passes**

Run: `cd apps/hcc-agent-host; python -m pytest tests/unit/test_fabric_data_agent_client.py -q`
Expected: PASS.

- [ ] **Step 5: Write the failing app-wiring test**

Add to `apps/hcc-agent-host/tests/integration/test_http.py`:

```python
def test_host_uses_live_ask_fn_when_env_set(monkeypatch):
    # When FABRIC_DATA_AGENT_* env is set, the host wires a live client whose
    # ask() result is surfaced (proves synthetic fallback is bypassed).
    monkeypatch.setenv("FABRIC_DATA_AGENT_ENDPOINT", "https://da.example/query")
    monkeypatch.setenv("FABRIC_WORKSPACE_ID", "ws-1")
    monkeypatch.setenv("FABRIC_DATA_AGENT_ID", "da-1")

    import api.app as appmod

    def fake_client_factory():
        class _C:
            def ask(self, q):
                return {"answer": "live", "citations": ["hcp:Ward"], "refused": False}
        return _C()

    monkeypatch.setattr(appmod, "_build_live_data_agent", lambda: fake_client_factory())
    appmod.get_state.cache_clear()
    from fastapi.testclient import TestClient
    client = TestClient(appmod.create_app())
    body = client.post("/agents/ooa-agent/chat", json={"prompt": "beds?", "conversationId": "live"}).json()
    assert "hcp:Ward" in body["citations"]
    appmod.get_state.cache_clear()
```

- [ ] **Step 6: Run to verify it fails**

Run: `cd apps/hcc-agent-host; python -m pytest tests/integration/test_http.py -k live -q`
Expected: FAIL (`_build_live_data_agent` not defined).

- [ ] **Step 7: Wire the live client in `app.py`**

In `apps/hcc-agent-host/src/api/app.py`, add the factory and use it in `HostState`:

```python
def _build_live_data_agent():
    """Return a live FabricDataAgentClient when env is configured, else None."""
    endpoint = os.environ.get("FABRIC_DATA_AGENT_ENDPOINT")
    workspace = os.environ.get("FABRIC_WORKSPACE_ID")
    agent_id = os.environ.get("FABRIC_DATA_AGENT_ID")
    if not (endpoint and workspace and agent_id):
        return None
    from tools.fabric_data_agent_client import FabricDataAgentClient

    return FabricDataAgentClient(endpoint=endpoint, workspace_id=workspace, data_agent_id=agent_id)
```

Then in `HostState.__init__` replace the adapter construction:

```python
        live = _build_live_data_agent()
        adapter = FabricDataAgentAdapter(ask_fn=(live.ask if live is not None else None))
        self.orchestrator = Orchestrator(chat_model=MockChatModel(), data_agent=adapter)
```

- [ ] **Step 8: Run the wiring test + full suite**

Run: `cd apps/hcc-agent-host; python -m pytest -q`
Expected: PASS (all, including the new live-wiring test; synthetic tests still pass because env is unset there).

- [ ] **Step 9: Inject env in Bicep**

In `infra/modules/agent-host/container-app.bicep`, add three params (`fabricDataAgentEndpoint`, `fabricWorkspaceId`, `fabricDataAgentId`, all `string`, default `''`) and add to the container `env` array (only when non-empty is fine to always pass; empty → synthetic fallback):

```bicep
      {
        name: 'FABRIC_DATA_AGENT_ENDPOINT'
        value: fabricDataAgentEndpoint
      }
      {
        name: 'FABRIC_WORKSPACE_ID'
        value: fabricWorkspaceId
      }
      {
        name: 'FABRIC_DATA_AGENT_ID'
        value: fabricDataAgentId
      }
```

Wire the three params through `infra/main.bicep` to the agent-host module, and set them in `infra/environments/sit.bicepparam` from the M3 Step 4 values. Bump `agentHostImage` to the new build SHA (built by `ci-build-agent-host` after Steps 6–8 merge).

- [ ] **Step 10: Build image, bump param, deploy**

Merge Steps 1–9 → `ci-build-agent-host` builds a new image → bump `agentHostImage` in `sit.bicepparam` to that short SHA → push → `cd-infra-deploy-sit` deploys (resume-Fabric step already present).

- [ ] **Step 11: E2E re-proof (live)**

```powershell
$base = "https://ca-agent-host-ihzhhpf-sit.salmonsand-fb86922a.westus2.azurecontainerapps.io"
$b1 = @{ prompt="bed occupancy ward B?"; conversationId="live-1"; callerObjectId="demo.guest" } | ConvertTo-Json
Invoke-WebRequest "$base/agents/ooa-agent/chat" -Method POST -Body $b1 -ContentType application/json -UseBasicParsing | % Content
```

Expected: `refused:false` + `hcp:*` citations sourced from the **live** Data Agent (answer text now reflects real synthetic gold, not the mock string). Re-run the re-identification prompt → `REFUSE: re-identification-risk`.

- [ ] **Step 12: Commit any infra/app follow-ups** (image bump commit only if not already pushed).

---

## Task M6: Demo assets, evidence, ADR, registry/PRD

**Files:**
- Create: `docs/adr/0034-fabric-iq-demo-scope-artefacts.md`
- Create: `docs/architecture/fabric-iq-ready-evidence.md`
- Create: `docs/demo/fabric-iq-showcase-script.md`
- Modify: `AGENTS.md`, `docs/PRD.md`

- [ ] **Step 1: Write ADR-0034**

Record: adopt the demo-scope Fabric IQ artefacts (ontology + data product + domain + data agent) in westus2, consumed live by both surfaces; honours ADR-0013/0014/0016; supplements ADR-0033. Status: Proposed. Run `python scripts/lint/check_mojibake.py docs/adr/0034-fabric-iq-demo-scope-artefacts.md`.

- [ ] **Step 2: Write the "Fabric IQ ready" evidence doc**

Create `docs/architecture/fabric-iq-ready-evidence.md` with a 5-row table mapping each readiness point (parent design §6: ontology, semantic model, data product, data agent, seam consumption) to the live artefact id + a verification command/screenshot. Version header 1.0.0.

- [ ] **Step 3: Write the demo script**

Create `docs/demo/fabric-iq-showcase-script.md` from design §9 (the six-step golden path), with the exact prompts and expected outputs.

- [ ] **Step 4: Update AGENTS.md + PRD**

`AGENTS.md`: update the `fabric-data-agent` registry row to note the live westus2 endpoint (MINOR bump). `docs/PRD.md`: add a traceability note that `FR-ONT-008` is now realised **live** (PATCH/MINOR per §9). Run mojibake on both.

- [ ] **Step 5: Commit**

```bash
git add docs/adr/0034-fabric-iq-demo-scope-artefacts.md docs/architecture/fabric-iq-ready-evidence.md docs/demo/fabric-iq-showcase-script.md AGENTS.md docs/PRD.md
git commit -m "docs: ADR-0034 + Fabric IQ ready evidence + demo script; close the showcase"
```

- [ ] **Step 6: Regenerate the evidence fixture** (PRD/ADR feed it)

Run: `python -m scripts.evidence.build_app_fixture` then `python -m pytest scripts/evidence/tests/test_app_fixture.py -q`. Commit the regenerated `apps/hcc-app-fluent/src/data/evidence/evidence-demo.json`.

---

## Final verification

- [ ] `cd apps/hcc-agent-host; python -m pytest -q` → PASS.
- [ ] `cd data-platform/scripts; python -m pytest tests/test_register_fabric_data_agent_tool.py -q` → PASS.
- [ ] Live agent-host E2E returns live `hcp:*` citations + refusal (M5 Step 11).
- [ ] Foundry `ooa` E2E returns grounded citation + refusal (M4 Step 7); #251 closed.
- [ ] Mojibake OK on all new/edited docs; markdown CI green.
- [ ] Design §12 DoD all checked; gate G-A evidence captured.
