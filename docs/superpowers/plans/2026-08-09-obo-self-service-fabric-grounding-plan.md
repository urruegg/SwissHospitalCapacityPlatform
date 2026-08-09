# Self-Service OBO for Real Fabric Grounding — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Get real, per-user-delegated Fabric Gold table reads flowing into
the chat-grounding path for bmca/dca/ooa/orsa/sba-agent, using On-Behalf-Of
(OBO) auth — which this tenant's own policies allow any signed-in user to
self-consent to, with zero Fabric/Power BI/Global Administrator involvement.

**Architecture:** Extend the already-built-but-unwired OBO seam
(`auth/obo_context.py`, `auth/token_validator.py`, #424 M5) into the
chat-grounding path only (board-data RLS stays out of scope, per
`docs/superpowers/specs/2026-08-09-obo-self-service-fabric-grounding-design.md`
§3). A per-request `FabricAdapter` built from the caller's OBO'd token
replaces the startup managed-identity instance whenever a valid bearer is
presented; the Redis grounding cache gets a per-user key prefix to prevent
cross-user leakage. New Entra resources (app registration, scope, delegated
permission) are self-service per the design doc's verified tenant policies,
but still require an `approved-to-apply` comment before creation (AGENTS.md
§4 — any new IAM grant needs explicit sign-off, even when no special role is
needed to create it).

**Tech Stack:** Python (FastAPI, `azure-identity`), TypeScript/React (MSAL v2),
Bicep.

---

## Task 1: Per-request Fabric adapter from an OBO token

**Files:**
- Modify: `apps/hcc-agent-host/src/api/app.py`
- Test: `apps/hcc-agent-host/tests/unit/test_fabric_for_obo.py`

- [ ] **Step 1: Write the failing tests**

Create `apps/hcc-agent-host/tests/unit/test_fabric_for_obo.py`:

```python
"""Sprint 43 WS-6 -- HostState.fabric_for builds a per-request Fabric
adapter from an OBO token instead of reusing the startup managed-identity
instance, mirroring the existing rls_provider_for(obo_token) pattern.
"""

from __future__ import annotations

from pathlib import Path

import api.app as appmod


def _agents_root() -> Path:
    return Path(__file__).resolve().parents[4] / "agents"


def _clear_env(monkeypatch):
    for k in ("FABRIC_WORKSPACE_ID", "FABRIC_LAKEHOUSE_ID"):
        monkeypatch.delenv(k, raising=False)


def test_fabric_for_returns_startup_instance_when_no_token(monkeypatch):
    _clear_env(monkeypatch)
    state = appmod.HostState(_agents_root())
    assert state.fabric_for(None) is state.fabric


def test_fabric_for_returns_startup_instance_when_env_unconfigured(monkeypatch):
    _clear_env(monkeypatch)
    state = appmod.HostState(_agents_root())
    # A token is present, but FABRIC_WORKSPACE_ID/LAKEHOUSE_ID aren't --
    # nothing to build a per-request client from, fall back unchanged.
    assert state.fabric_for("some-obo-token") is state.fabric


def test_fabric_for_builds_a_fresh_adapter_when_token_and_env_present(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("FABRIC_WORKSPACE_ID", "ws-1")
    monkeypatch.setenv("FABRIC_LAKEHOUSE_ID", "lh-1")
    state = appmod.HostState(_agents_root())
    adapter = state.fabric_for("some-obo-token")
    assert adapter is not state.fabric


def test_fabric_for_uses_the_obo_token_not_the_managed_identity(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("FABRIC_WORKSPACE_ID", "ws-1")
    monkeypatch.setenv("FABRIC_LAKEHOUSE_ID", "lh-1")
    state = appmod.HostState(_agents_root())
    adapter = state.fabric_for("some-obo-token")

    captured_tokens: list[str] = []

    def fake_reader(uri: str, token: str):
        captured_tokens.append(token)
        return [{"ward": "B"}]

    # Reach into the client the adapter wraps to prove it used our token,
    # not DefaultAzureCredential -- swap the table_reader after construction
    # via the same private attribute FabricDeltaClient exposes for this.
    adapter._query_fn.__self__._table_reader = fake_reader  # type: ignore[attr-defined]
    rows = adapter.query("gold.bed_assignment")
    assert rows == [{"ward": "B"}]
    assert captured_tokens == ["some-obo-token"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run (from `apps/hcc-agent-host/`): `python -m pytest tests/unit/test_fabric_for_obo.py -v`
Expected: FAIL with `AttributeError: 'HostState' object has no attribute 'fabric_for'`

- [ ] **Step 3: Implement `HostState.fabric_for`**

In `apps/hcc-agent-host/src/api/app.py`, find the `rls_provider_for` method
inside `class HostState` and add a new method immediately after it:

```python
    def rls_provider_for(self, obo_token: str | None):
        """#424 M5 — the per-request RLS provider.

        When an OBO context is present (``OBO_ENABLED`` + a valid bearer), build a
        provider carrying the user's token so the read runs on-behalf-of the user
        (config-selected via ``RLS_PROVIDER``). Otherwise reuse the startup
        provider (SIT default: simulated). Config, not code (ADR-0057).
        """
        if not obo_token:
            return self.rls_provider
        return build_rls_provider(
            data_agent_client=self._live_data_agent, obo_token=obo_token
        )

    def fabric_for(self, obo_token: str | None) -> FabricAdapter:
        """Sprint 43 WS-6 -- the per-request chat-grounding Fabric adapter.

        Mirrors ``rls_provider_for``: an OBO token builds a fresh
        ``FabricDeltaClient`` scoped to the signed-in user's own delegated
        Fabric permissions, bypassing the service-principal restriction the
        startup ``self.fabric`` (managed identity) hits (see
        docs/superpowers/specs/2026-08-09-obo-self-service-fabric-grounding-design.md).
        No token, or the Fabric env unconfigured, reuses the startup instance
        unchanged (byte-parity with today when OBO is off).
        """
        if not obo_token:
            return self.fabric
        workspace = os.environ.get("FABRIC_WORKSPACE_ID")
        lakehouse = os.environ.get("FABRIC_LAKEHOUSE_ID")
        if not (workspace and lakehouse):
            return self.fabric
        from tools.fabric_delta_client import FabricDeltaClient

        client = FabricDeltaClient(
            workspace_id=workspace,
            lakehouse_id=lakehouse,
            token_provider=lambda: obo_token,
        )
        return FabricAdapter(query_fn=client.query)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/unit/test_fabric_for_obo.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add apps/hcc-agent-host/src/api/app.py apps/hcc-agent-host/tests/unit/test_fabric_for_obo.py
git commit -m "feat(agent-host): add HostState.fabric_for per-request OBO grounding adapter"
```

---

## Task 2: Orchestrator accepts a per-request grounding override + per-user cache key

**Files:**
- Modify: `apps/hcc-agent-host/src/orchestrator/dispatch.py`
- Test: `apps/hcc-agent-host/tests/unit/test_dispatch_fabric_override.py`

- [ ] **Step 1: Write the failing tests**

Create `apps/hcc-agent-host/tests/unit/test_dispatch_fabric_override.py`:

```python
"""Sprint 43 WS-6 -- Orchestrator.dispatch accepts a per-request
`fabric_override`, used instead of the startup `self.fabric` for grounding.
Also verifies the grounding cache is namespaced per-user when an override is
supplied, so one user's OBO-scoped rows never leak into another's reply."""

from __future__ import annotations

from manifests.loader import AgentManifest
from orchestrator.dispatch import Orchestrator
from tools.fabric_adapter import FabricAdapter


class _StubModel:
    def complete(self, system_prompt, user_prompt, grounding, *, agent_name=""):
        return f"answer using {len(grounding)} grounding item(s)"


def _manifest() -> AgentManifest:
    return AgentManifest(
        agent="bmca-agent",
        version="1.0.0",
        runtime="agent-host",
        model_deployment_ref="gpt-5",
        system_prompt_ref="AGENT.md",
        grounding_tables=("gold.bed_assignment",),
    )


def test_dispatch_uses_fabric_override_when_supplied():
    default_fabric = FabricAdapter(query_fn=lambda table: [])
    override_fabric = FabricAdapter(query_fn=lambda table: [{"ward": "B", "occupied": 46}])
    orch = Orchestrator(chat_model=_StubModel(), fabric=default_fabric)

    reply = orch.dispatch(
        _manifest(), "sys", "question",
        conversation_id="c1", caller_oid="user-a",
        fabric_override=override_fabric,
    )

    assert "gold.bed_assignment" in reply.citations
    assert "1 grounding item" in reply.answer


def test_dispatch_falls_back_to_startup_fabric_when_no_override():
    default_fabric = FabricAdapter(query_fn=lambda table: [{"ward": "B"}])
    orch = Orchestrator(chat_model=_StubModel(), fabric=default_fabric)

    reply = orch.dispatch(
        _manifest(), "sys", "question",
        conversation_id="c1", caller_oid="user-a",
    )

    assert "gold.bed_assignment" in reply.citations


def test_two_users_with_different_obo_overrides_do_not_share_cached_rows():
    orch = Orchestrator(chat_model=_StubModel())
    fabric_a = FabricAdapter(query_fn=lambda table: [{"ward": "A-only"}])
    fabric_b = FabricAdapter(query_fn=lambda table: [{"ward": "B-only"}])

    reply_a = orch.dispatch(
        _manifest(), "sys", "q1", conversation_id="c1", caller_oid="user-a",
        fabric_override=fabric_a,
    )
    reply_b = orch.dispatch(
        _manifest(), "sys", "q2", conversation_id="c2", caller_oid="user-b",
        fabric_override=fabric_b,
    )

    assert "1 grounding item" in reply_a.answer
    assert "1 grounding item" in reply_b.answer
    # If the cache key collided across users, user B's second call would
    # silently reuse user A's cached rows instead of querying fabric_b.
    assert orch.cache.get_grounding("user-a:gold.bed_assignment") == [{"ward": "A-only"}]
    assert orch.cache.get_grounding("user-b:gold.bed_assignment") == [{"ward": "B-only"}]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/unit/test_dispatch_fabric_override.py -v`
Expected: FAIL with `TypeError: dispatch() got an unexpected keyword argument 'fabric_override'`

- [ ] **Step 3: Implement the override + per-user cache key**

In `apps/hcc-agent-host/src/orchestrator/dispatch.py`, replace the
`_grounding` method:

```python
    def _grounding(self, manifest: AgentManifest) -> tuple[list[dict[str, Any]], list[str]]:
        rows: list[dict[str, Any]] = []
        citations: list[str] = []
        for table in manifest.grounding_tables:
            cached = self.cache.get_grounding(table)
            if cached is None:
                cached = self.fabric.query(table)
                self.cache.cache_grounding(table, cached)
            rows.extend(cached)
            # Sprint 43 WS-5 -- a citation asserts "this answer used this
            # source". A table that returned zero rows (e.g. WS-2's Fabric
            # read blocked upstream) contributed nothing, so citing it would
            # mislead the reader into believing the answer is grounded when
            # it is not (found via live UI verification, 2026-08-09).
            if cached:
                citations.append(table)
        return rows, citations
```

with:

```python
    def _grounding(
        self,
        manifest: AgentManifest,
        *,
        fabric: FabricAdapter | None = None,
        cache_key_prefix: str = "",
    ) -> tuple[list[dict[str, Any]], list[str]]:
        fabric = fabric or self.fabric
        rows: list[dict[str, Any]] = []
        citations: list[str] = []
        for table in manifest.grounding_tables:
            # Sprint 43 WS-6 -- namespaced per-user when an OBO-scoped fabric
            # override is in play, so one user's delegated read is never
            # served from another user's cached rows. Empty prefix (OBO off)
            # keeps today's cache key byte-identical.
            cache_key = f"{cache_key_prefix}{table}" if cache_key_prefix else table
            cached = self.cache.get_grounding(cache_key)
            if cached is None:
                cached = fabric.query(table)
                self.cache.cache_grounding(cache_key, cached)
            rows.extend(cached)
            # Sprint 43 WS-5 -- a citation asserts "this answer used this
            # source". A table that returned zero rows (e.g. WS-2's Fabric
            # read blocked upstream) contributed nothing, so citing it would
            # mislead the reader into believing the answer is grounded when
            # it is not (found via live UI verification, 2026-08-09).
            if cached:
                citations.append(table)
        return rows, citations
```

Then update `_primary_grounding` to accept and forward the same two
parameters — replace:

```python
    def _primary_grounding(
        self, manifest: AgentManifest, user_prompt: str
    ) -> tuple[list[dict[str, Any]], list[str], str | None, bool, str]:
        """Return (grounding_rows, citations, refusal_answer, degraded, mode).

        ``mode`` is the grounding source actually used (``"agent"`` or
        ``"table"``). Uses the Fabric Data Agent when the manifest binds one and
        an adapter is available. On adapter failure, degrades LOUDLY to table
        grounding.
        """
        binding = manifest.grounding_agent
        if binding is None or self.data_agent is None or binding.precedence != "primary":
            rows, citations = self._grounding(manifest)
            return rows, citations, None, False, "table"
        try:
            result = self.data_agent.ask(user_prompt)
        except Exception:
            logger.exception(
                "Fabric Data Agent grounding failed; degrading to table grounding"
            )
            rows, citations = self._grounding(manifest)
            return rows, citations, None, True, "table"
        if result.get("refused"):
            return [], list(result.get("citations", [])), result["answer"], False, "agent"
        rows = [{"dataAgentAnswer": result["answer"]}]
        return rows, list(result.get("citations", [])), None, False, "agent"
```

with:

```python
    def _primary_grounding(
        self,
        manifest: AgentManifest,
        user_prompt: str,
        *,
        fabric: FabricAdapter | None = None,
        cache_key_prefix: str = "",
    ) -> tuple[list[dict[str, Any]], list[str], str | None, bool, str]:
        """Return (grounding_rows, citations, refusal_answer, degraded, mode).

        ``mode`` is the grounding source actually used (``"agent"`` or
        ``"table"``). Uses the Fabric Data Agent when the manifest binds one and
        an adapter is available. On adapter failure, degrades LOUDLY to table
        grounding.
        """
        binding = manifest.grounding_agent
        if binding is None or self.data_agent is None or binding.precedence != "primary":
            rows, citations = self._grounding(manifest, fabric=fabric, cache_key_prefix=cache_key_prefix)
            return rows, citations, None, False, "table"
        try:
            result = self.data_agent.ask(user_prompt)
        except Exception:
            logger.exception(
                "Fabric Data Agent grounding failed; degrading to table grounding"
            )
            rows, citations = self._grounding(manifest, fabric=fabric, cache_key_prefix=cache_key_prefix)
            return rows, citations, None, True, "table"
        if result.get("refused"):
            return [], list(result.get("citations", [])), result["answer"], False, "agent"
        rows = [{"dataAgentAnswer": result["answer"]}]
        return rows, list(result.get("citations", [])), None, False, "agent"
```

Finally, update `dispatch`'s signature and its one call to
`_primary_grounding` — replace:

```python
    def dispatch(
        self,
        manifest: AgentManifest,
        system_prompt: str,
        user_prompt: str,
        *,
        conversation_id: str,
        caller_oid: str,
    ) -> GroundedReply:
        started = time.perf_counter()
        correlation_id = hashlib.sha256(
            f"{manifest.agent}:{conversation_id}:{time.time_ns()}".encode()
        ).hexdigest()[:16]

        with self.tracer.span("agent.turn", agent=manifest.agent) as root:
            with self.tracer.span("agent.retrieve", agent=manifest.agent) as rspan:
                grounding, citations, refusal_answer, degraded, mode = self._primary_grounding(
                    manifest, user_prompt
                )
```

with:

```python
    def dispatch(
        self,
        manifest: AgentManifest,
        system_prompt: str,
        user_prompt: str,
        *,
        conversation_id: str,
        caller_oid: str,
        fabric_override: FabricAdapter | None = None,
    ) -> GroundedReply:
        started = time.perf_counter()
        correlation_id = hashlib.sha256(
            f"{manifest.agent}:{conversation_id}:{time.time_ns()}".encode()
        ).hexdigest()[:16]
        # Sprint 43 WS-6 -- an OBO-scoped fabric_override means this turn's
        # grounding is per-user; namespace the cache so it never mixes rows
        # across users. No override (OBO off) keeps today's plain table key.
        cache_key_prefix = f"{caller_oid}:" if fabric_override is not None else ""

        with self.tracer.span("agent.turn", agent=manifest.agent) as root:
            with self.tracer.span("agent.retrieve", agent=manifest.agent) as rspan:
                grounding, citations, refusal_answer, degraded, mode = self._primary_grounding(
                    manifest, user_prompt, fabric=fabric_override, cache_key_prefix=cache_key_prefix
                )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/unit/test_dispatch_fabric_override.py -v`
Expected: 3 passed

- [ ] **Step 5: Run the full backend suite to confirm no regressions**

Run (from `apps/hcc-agent-host/`): `python -m pytest -q`
Expected: all tests pass (185 + 4 new from Task 1 + 3 new here = 192)

- [ ] **Step 6: Commit**

```bash
git add apps/hcc-agent-host/src/orchestrator/dispatch.py apps/hcc-agent-host/tests/unit/test_dispatch_fabric_override.py
git commit -m "feat(agent-host): accept a per-request fabric_override + per-user grounding cache key"
```

---

## Task 3: Wire the chat endpoint to build and pass the OBO context

**Files:**
- Modify: `apps/hcc-agent-host/src/api/app.py`
- Test: `apps/hcc-agent-host/tests/integration/test_chat_obo.py`

- [ ] **Step 1: Write the failing tests**

Create `apps/hcc-agent-host/tests/integration/test_chat_obo.py`:

```python
"""Sprint 43 WS-6 -- /agents/{name}/chat honors an OBO bearer when
OBO_ENABLED is on, mirroring tests/integration/test_golden_obo_endpoint.py's
parity/deny-by-default shape for the golden read."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.app import create_app


def _client(monkeypatch) -> TestClient:
    monkeypatch.delenv("OBO_ENABLED", raising=False)
    return TestClient(create_app())


def test_chat_without_obo_is_unchanged(monkeypatch):
    client = _client(monkeypatch)
    resp = client.post(
        "/agents/bmca-agent/chat",
        json={"prompt": "Station B ist fast voll", "conversationId": "c1"},
    )
    assert resp.status_code == 200
    assert "citations" in resp.json()


def test_chat_with_obo_enabled_and_invalid_bearer_denies(monkeypatch):
    monkeypatch.setenv("OBO_ENABLED", "true")
    monkeypatch.setenv("OBO_AUDIENCE", "api://agent-host")
    monkeypatch.setenv("OBO_ISSUER", "https://sts.windows.net/tenant-abc/")
    monkeypatch.setenv("OBO_JWKS_URL", "https://example.invalid/keys")
    client = TestClient(create_app())
    resp = client.post(
        "/agents/bmca-agent/chat",
        json={"prompt": "Station B ist fast voll", "conversationId": "c1"},
        headers={"Authorization": "Bearer not-a-real-jwt"},
    )
    assert resp.status_code == 401
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/integration/test_chat_obo.py -v`
Expected: `test_chat_without_obo_is_unchanged` passes already (no behavior
change needed for that path); `test_chat_with_obo_enabled_and_invalid_bearer_denies`
FAILS with 200 instead of 401 (the endpoint doesn't check `authorization` yet).

- [ ] **Step 3: Wire `build_obo_context` into the chat endpoint**

In `apps/hcc-agent-host/src/api/app.py`, replace the `chat` endpoint:

```python
    @app.post("/agents/{name}/chat")
    def chat(name: str, req: ChatRequest, x_user_oid: str = Header(default="")) -> dict[str, Any]:
        state = get_state()
        manifest = state.require(name)
        system_prompt = _system_prompt_for(manifest, state.agents_root)
        # #424 M3 — thread-scoped when a threadId is supplied; identity header
        # (OBO oid) overrides the demo caller default when present.
        conversation_id = req.threadId or req.conversationId
        caller_oid = x_user_oid or req.callerObjectId
        reply = state.orchestrator.dispatch(
            manifest,
            system_prompt,
            req.prompt,
            conversation_id=conversation_id,
            caller_oid=caller_oid,
        )
        return {
            "answer": reply.answer,
            "citations": list(reply.citations),
            "refused": reply.refused,
            "correlationId": reply.correlation_id,
            "interactionId": reply.interaction_id,
        }
```

with:

```python
    @app.post("/agents/{name}/chat")
    def chat(
        name: str,
        req: ChatRequest,
        authorization: str = Header(default=""),
        x_user_oid: str = Header(default=""),
    ) -> dict[str, Any]:
        state = get_state()
        manifest = state.require(name)
        system_prompt = _system_prompt_for(manifest, state.agents_root)
        # #424 M3 — thread-scoped when a threadId is supplied; identity header
        # (OBO oid) overrides the demo caller default when present.
        conversation_id = req.threadId or req.conversationId
        # Sprint 43 WS-6 — when OBO is enabled and a valid bearer is presented,
        # grounding runs on-behalf-of the signed-in user (real Fabric reads,
        # bypassing the service-principal restriction the startup managed
        # identity hits); otherwise unchanged (OBO off is the SIT default).
        # Deny-by-default: an invalid bearer under OBO is a 401, mirrored
        # from the /golden read path.
        try:
            obo = build_obo_context(authorization)
        except TokenValidationError as exc:
            raise HTTPException(status_code=401, detail=str(exc))
        caller_oid = (obo.user_oid if obo else x_user_oid) or req.callerObjectId
        fabric_override = state.fabric_for(obo.obo_token) if obo else None
        reply = state.orchestrator.dispatch(
            manifest,
            system_prompt,
            req.prompt,
            conversation_id=conversation_id,
            caller_oid=caller_oid,
            fabric_override=fabric_override,
        )
        return {
            "answer": reply.answer,
            "citations": list(reply.citations),
            "refused": reply.refused,
            "correlationId": reply.correlation_id,
            "interactionId": reply.interaction_id,
        }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/integration/test_chat_obo.py -v`
Expected: 2 passed

- [ ] **Step 5: Run the full backend suite**

Run: `python -m pytest -q`
Expected: all tests pass (192 + 2 new = 194)

- [ ] **Step 6: Commit**

```bash
git add apps/hcc-agent-host/src/api/app.py apps/hcc-agent-host/tests/integration/test_chat_obo.py
git commit -m "feat(agent-host): wire OBO context into the chat endpoint for real per-user grounding"
```

---

## Task 4: Provision the Entra resources (self-service — still needs `approved-to-apply`)

**Files:** none (Entra/Azure resources, not repo files — the *config* that
references them lands in Task 5)

> **Gate:** per AGENTS.md §4, creating a new Entra app registration + a
> delegated permission is a new IAM grant. Even though this design confirms
> no Fabric/Power BI/Global Administrator is required (§1.2 of the design
> doc), do not run these steps until a human posts `approved-to-apply` on the
> tracking issue.

- [ ] **Step 1: Create the agent-host app registration**

```powershell
$app = az ad app create --display-name "hcc-agent-host" --sign-in-audience AzureADMyOrg | ConvertFrom-Json
$app.appId
```

- [ ] **Step 2: Expose the `access_as_user` API scope**

```powershell
$scopeId = [guid]::NewGuid().ToString()
az ad app update --id $app.appId --identifier-uris "api://$($app.appId)"
az rest --method PATCH --uri "https://graph.microsoft.com/v1.0/applications/$($app.id)" --body (@{
  api = @{
    oauth2PermissionScopes = @(@{
      id = $scopeId
      adminConsentDescription = "Allow the app to access hcc-agent-host on behalf of the signed-in user"
      adminConsentDisplayName = "Access hcc-agent-host"
      userConsentDescription = "Allow this app to access hcc-agent-host on your behalf"
      userConsentDisplayName = "Access hcc-agent-host"
      value = "access_as_user"
      type = "User"
      isEnabled = $true
    })
  }
} | ConvertTo-Json -Depth 5)
```

- [ ] **Step 3: Add the delegated `OneLake.Read.All` permission**

```powershell
$powerBiServiceAppId = "00000009-0000-0000-c000-000000000000"
$oneLakeScopeId = (az ad sp show --id $powerBiServiceAppId --query "oauth2PermissionScopes[?value=='OneLake.Read.All'].id" -o tsv)
az ad app permission add --id $app.appId --api $powerBiServiceAppId --api-permissions "$($oneLakeScopeId)=Scope"
```

- [ ] **Step 4: Create a client secret and store it in Key Vault**

```powershell
$secret = az ad app credential reset --id $app.appId --display-name "obo-exchange" --years 1 | ConvertFrom-Json
az keyvault secret set --vault-name <existing-sit-keyvault-name> --name "agent-host-obo-client-secret" --value $secret.password
```

- [ ] **Step 5: Add the exposed scope to the SPA's API permissions**

```powershell
$spaAppId = "52681a08-c792-44b1-b6b5-01cb560d450f"  # ihzhhpf-app (sit)
az ad app permission add --id $spaAppId --api $app.appId --api-permissions "$($scopeId)=Scope"
```

- [ ] **Step 6: Record the new identifiers for Task 5**

Note `$app.appId` (→ `OBO_CLIENT_ID`), the tenant ID (→ `OBO_TENANT_ID`,
already known: `1337187a-4c41-4da9-8fca-731bba7a4329`), and
`api://$($app.appId)/access_as_user` (→ `VITE_AGENT_HOST_SCOPE`) for the next task.

---

## Task 5: Wire Bicep config for the new OBO env vars + flip the flag

**Files:**
- Modify: `infra/modules/agent-host/container-app.bicep`
- Modify: `infra/modules/agent-host/main.bicep`
- Modify: `infra/main.bicep`
- Modify: `infra/environments/sit.bicepparam`
- Modify: `infra/modules/apps/hcc-app-fluent/main.bicep` (for `VITE_AGENT_HOST_SCOPE`)

- [ ] **Step 1: Add OBO params to `container-app.bicep`**

In `infra/modules/agent-host/container-app.bicep`, find the existing
`oboEnabled` param block and add new params + env vars immediately after it:

```bicep
@description('#424 M5 — enable the OBO ingress seam (`false` default = simulated/native parity with M4). `true` requires a valid caller bearer on the golden read and exchanges it downstream. See ADR-0057. Config, not code.')
param oboEnabled bool = false

@description('Sprint 43 WS-6 — tenant ID for the OBO On-Behalf-Of exchange (agent-host confidential client).')
param oboTenantId string = ''

@description('Sprint 43 WS-6 — client ID of the hcc-agent-host app registration used for the OBO exchange.')
param oboClientId string = ''

@description('Sprint 43 WS-6 — Key Vault secret URI for the agent-host app registration client secret.')
@secure()
param oboClientSecret string = ''

@description('Sprint 43 WS-6 — JWKS URL used to validate the caller bearer (tenant discovery keys endpoint).')
param oboJwksUrl string = ''

@description('Sprint 43 WS-6 — expected audience on the caller bearer token (api://<agent-host-app-id>).')
param oboAudience string = ''

@description('Sprint 43 WS-6 — expected issuer on the caller bearer token.')
param oboIssuer string = ''
```

Then find where `OBO_ENABLED` is set as a container env var and add the new
ones alongside it:

```bicep
  {
    name: 'OBO_ENABLED'
    value: oboEnabled ? 'true' : 'false'
  }
```

becomes:

```bicep
  {
    name: 'OBO_ENABLED'
    value: oboEnabled ? 'true' : 'false'
  }
  {
    name: 'OBO_TENANT_ID'
    value: oboTenantId
  }
  {
    name: 'OBO_CLIENT_ID'
    value: oboClientId
  }
  {
    name: 'OBO_CLIENT_SECRET'
    secretRef: 'obo-client-secret'
  }
  {
    name: 'OBO_JWKS_URL'
    value: oboJwksUrl
  }
  {
    name: 'OBO_AUDIENCE'
    value: oboAudience
  }
  {
    name: 'OBO_ISSUER'
    value: oboIssuer
  }
```

Add the matching `secrets` entry (find the container app's `secrets` array
and add one entry, following the existing pattern for other `secretRef`-based
env vars in this file):

```bicep
      {
        name: 'obo-client-secret'
        value: oboClientSecret
      }
```

- [ ] **Step 2: Thread the new params through `main.bicep` (module) and top-level `infra/main.bicep`**

In `infra/modules/agent-host/main.bicep`, add the same 6 params and pass them
through to the `container-app.bicep` module call (follow the exact pattern
`oboEnabled` already uses in this file — find `oboEnabled: oboEnabled` in the
module's parameter object and add the 6 new ones alongside it).

In `infra/main.bicep`, add the same 6 top-level params (following the
existing `agentHostOboEnabled` param's doc-comment style) and pass them
through to the `agent-host` module invocation the same way
`oboEnabled: agentHostOboEnabled` already does.

- [ ] **Step 3: Set the new params in `sit.bicepparam`**

In `infra/environments/sit.bicepparam`, find `param agentHostOboEnabled = false`
and change it, adding the new params directly below with values from Task 4's
output (the client secret must be a Key Vault reference, not a literal —
follow whatever existing pattern this file uses for other secrets, e.g.
check how `FOUNDRY_PROJECT_ENDPOINT` or similar secrets are referenced):

```bicep
// Sprint 43 WS-6 (approved-to-apply by @urruegg, <date>): flips on the OBO
// seam for chat-grounding only (board-data RLS stays simulated per WS-3's
// re-scoping). Self-service Entra provisioning per
// docs/superpowers/specs/2026-08-09-obo-self-service-fabric-grounding-design.md
// — no Fabric/Power BI/Global Administrator involved.
param agentHostOboEnabled = true
param agentHostOboTenantId = '1337187a-4c41-4da9-8fca-731bba7a4329'
param agentHostOboClientId = '<app.appId from Task 4>'
param agentHostOboClientSecret = '<Key Vault reference — match this file's existing secret-reference pattern>'
param agentHostOboJwksUrl = 'https://login.microsoftonline.com/1337187a-4c41-4da9-8fca-731bba7a4329/discovery/v2.0/keys'
param agentHostOboAudience = 'api://<app.appId from Task 4>'
param agentHostOboIssuer = 'https://login.microsoftonline.com/1337187a-4c41-4da9-8fca-731bba7a4329/v2.0'
```

- [ ] **Step 4: Add `VITE_AGENT_HOST_SCOPE` to the SPA's Container App**

In `infra/modules/apps/hcc-app-fluent/main.bicep`, add a new param:

```bicep
@description('Sprint 43 WS-6 — the agent-host API scope the SPA requests via MSAL for OBO-forwarded chat grounding. Empty (default) keeps the app on OIDC-only sign-in (no Authorization header forwarded).')
param agentHostScope string = ''
```

Add it to the app's runtime env-config injection (find where
`FOUNDRY_THREADS_ENABLED` or similar `window.__ENV__.*` values are injected
in this file, per the file's own comment about "the app-shell can request
tokens for downstream MSAL OBO flows" and follow that exact pattern) as
`window.__ENV__.AGENT_HOST_SCOPE`.

Thread `agentHostScope` through `infra/main.bicep` → this module the same
way other per-app params already do, and set it in `sit.bicepparam`:

```bicep
param appFluentAgentHostScope = 'api://<app.appId from Task 4>/access_as_user'
```

- [ ] **Step 5: Validate the Bicep builds cleanly**

Run: `az bicep build --file infra/main.bicep --stdout > $null`
Expected: exits 0, no errors.

- [ ] **Step 6: Commit**

```bash
git add infra/modules/agent-host/container-app.bicep infra/modules/agent-host/main.bicep infra/main.bicep infra/environments/sit.bicepparam infra/modules/apps/hcc-app-fluent/main.bicep
git commit -m "feat(infra): wire OBO client config + VITE_AGENT_HOST_SCOPE for real per-user Fabric grounding"
```

---

## Task 6: Frontend — request the new scope and forward the bearer token

**Files:**
- Modify: `apps/hcc-app-fluent/src/auth/msal-provider.ts`
- Modify: `apps/hcc-app-fluent/src/copilot-drawer/agent-manifest.ts`
- Test: `apps/hcc-app-fluent/src/copilot-drawer/agent-manifest.test.ts` (create if it doesn't exist, else extend it)

- [ ] **Step 1: Read the current `invokeAgent` implementation first**

Run: read `apps/hcc-app-fluent/src/copilot-drawer/agent-manifest.ts` around
its `invokeAgent` function (the one that calls `POST /agents/{name}/chat`)
before editing, to match its exact current fetch/header-building shape —
this plan's diff below assumes it builds a plain `fetch(url, { method:
'POST', headers: {...}, body: JSON.stringify(...) })` call; adjust the exact
`headers` object literal to match what's actually there if it differs.

- [ ] **Step 2: Write the failing test**

In the existing test file for `agent-manifest.ts` (find it via
`apps/hcc-app-fluent/tests/` or a co-located `*.test.ts` — check which
convention this file already uses), add:

```typescript
it('forwards an Authorization bearer header when a token provider is configured', async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ answer: 'ok', citations: [], refused: false, correlationId: 'x', interactionId: 'y' }),
  });
  vi.stubGlobal('fetch', fetchMock);

  await invokeAgent('bmca-agent', 'a question', { getBearerToken: async () => 'test-token' });

  const [, options] = fetchMock.mock.calls[0];
  expect(options.headers.Authorization).toBe('Bearer test-token');
});
```

- [ ] **Step 3: Run the test to verify it fails**

Run (from `apps/hcc-app-fluent/`): `npm test -- agent-manifest`
Expected: FAIL — `invokeAgent` doesn't accept a third argument yet, or the
header isn't set.

- [ ] **Step 4: Add an optional bearer-token parameter to `invokeAgent`**

Add a new exported type and extend `invokeAgent`'s signature to accept an
optional `{ getBearerToken?: () => Promise<string> }` options object; when
present, `await` it and set `headers.Authorization = \`Bearer ${token}\`` on
the existing fetch call, leaving every other line unchanged. Keep the
parameter optional and default-absent so every existing caller compiles
unchanged (config-gated, matches the design doc's "absent = unchanged OIDC-
only behavior").

- [ ] **Step 5: Run the test to verify it passes**

Run: `npm test -- agent-manifest`
Expected: passes, plus the full existing suite for this file still passes
(no regressions to callers that don't pass the new option).

- [ ] **Step 6: Wire MSAL token acquisition as the real `getBearerToken`**

In `apps/hcc-app-fluent/src/auth/msal-provider.ts`, add a helper that reads
`window.__ENV__.AGENT_HOST_SCOPE` (or the existing `runtime-config.ts`
accessor pattern this file already uses for other `window.__ENV__.*` values —
follow that, don't invent a new config-reading convention) and, when
non-empty, calls `msalInstance.acquireTokenSilent({ scopes: [scope],
account })` to get a bearer token; when empty, returns `undefined` (today's
unchanged behavior). Wire this helper as the `getBearerToken` passed into
`invokeAgent` at its call site in the Agent Plane (`AgentPlane.tsx`'s
`useConversation`/`send` path — check `useConversation.ts` for where
`invokeAgent`/`invokeInsight` is actually called and pass it through there).

- [ ] **Step 7: Run the full frontend test suite**

Run: `npm test`
Expected: all existing tests still pass.

- [ ] **Step 8: Commit**

```bash
git add apps/hcc-app-fluent/src/auth/msal-provider.ts apps/hcc-app-fluent/src/copilot-drawer/agent-manifest.ts
git commit -m "feat(app-fluent): forward an OBO bearer token to agent-host chat when configured"
```

---

## Task 7: Live verification

**Files:**
- Modify: `apps/hcc-app-fluent/tests/e2e-live/all-boards-iq.spec.ts` (or a new spec, whichever keeps the file focused)

- [ ] **Step 1: Deploy Tasks 1-6 to SIT**

Follow this repo's established image-build → bump `sit.bicepparam` image tag
→ approve `cd-infra-deploy-sit.yml` sequence (see repo memory
`image-build-vs-infra-deploy-decoupling.md`). Confirm the running container's
image tag matches before testing (`az containerapp show ... --query
properties.template.containers[0].image`).

- [ ] **Step 2: Sign in as a fresh demo user and confirm the one-time consent screen**

Manually, once: sign in to `https://appsit.curavias.ch`, confirm a new
consent screen appears listing "Access hcc-agent-host" and the OneLake
permission, and accept it. Screenshot this for the demo-run notes (§6 of the
design doc flags this as expected, not an error).

- [ ] **Step 3: Extend the live suite to assert real citations, not just honesty**

Add a case to `all-boards-iq.spec.ts` (or a new
`tests/e2e-live/obo-grounding.spec.ts`) that asks a bed-manager question and
asserts `rail.getByTestId('citations')` contains an actual `gold.` table
name **and** the conversation text does not match the existing
`DEGRADED_PATTERN` — i.e., this is the one place the suite now expects a
genuinely grounded answer, not just an honest degraded one.

- [ ] **Step 4: Run the live suite**

Run: `cd apps/hcc-app-fluent; npx playwright test --project=live tests/e2e-live/all-boards-iq.spec.ts --reporter=list`
Expected: all pass, including the new grounded-citation assertion.

- [ ] **Step 5: Update the design doc + issue #567 with the live evidence**

Bump `docs/superpowers/specs/2026-08-09-obo-self-service-fabric-grounding-design.md`
to record the live verification result (real citations, screenshot
reference), and post a summary comment on issue #567 closing the loop on
WS-2/WS-5's Fabric-grounding blocker.

- [ ] **Step 6: Commit**

```bash
git add apps/hcc-app-fluent/tests/e2e-live/ docs/superpowers/specs/2026-08-09-obo-self-service-fabric-grounding-design.md
git commit -m "test(app-fluent): verify real OBO-grounded citations live; close out Fabric-grounding blocker"
```
