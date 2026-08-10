# OBO Context-Aware Role-Agent Decision Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make OBO the standard, always-preferred auth pattern end to end: fix the bearer-presence bug that broke Demo mode, mirror real Entra App Roles onto the backend so role/hospital context is server-verified (not just client-claimed), verify CSA's HITL tool-gate approver identity the same way, give `ooa` and `bmca` real catalog-grounded recommendations (not placeholders) alongside `dca`, and make every Accept/Deny decision produce a durably persisted, identity-verified audit record that also serves as this app's durable agent memory.

**Architecture:** Small, independent, dependency-injection-testable changes to `apps/hcc-agent-host/src/auth/obo_context.py`, `api/app.py`, `loop/worklist.py`, `loop/decisions.py`, a new `loop/role_levers.py`, and `persistence/cosmos_client.py`, plus one Entra IAM change (mirror App Roles, gated by `approved-to-apply`) and one one-line Bicep flip. No new infrastructure is required — the Cosmos account, database, all four containers, and managed-identity RBAC already exist live in SIT (confirmed via `az cosmosdb` during the design brainstorm); the `ooa`/`bmca` predicted-impact math already exists too (Sprint 26 WS-B's lever catalog + formula registry) — this plan wires it in, it doesn't invent it. The `product-owner-agent` runtime is explicitly out of scope (deferred to issue #570 per user decision).

**Tech Stack:** Python 3.11, FastAPI, pytest, `azure-cosmos`, `azure-identity`, PyJWT. No frontend changes (the SPA already forwards a bearer to every relevant endpoint).

**Reference:** [`docs/superpowers/specs/2026-08-09-obo-context-aware-role-agent-decision-loop-design.md`](../specs/2026-08-09-obo-context-aware-role-agent-decision-loop-design.md)

---

### Task 1: Fix OBO bearer-presence semantics + propagate roles/hospital through `OboContext`

**Files:**
- Modify: `apps/hcc-agent-host/src/auth/obo_context.py`
- Modify: `apps/hcc-agent-host/tests/unit/test_obo_context.py`

- [ ] **Step 1: Update the existing test that encodes the bug**

In `apps/hcc-agent-host/tests/unit/test_obo_context.py`, replace the test that currently asserts a missing bearer raises (this is the bug being fixed) and add a claims fixture that carries roles:

```python
def test_obo_enabled_missing_bearer_falls_back_to_none(monkeypatch):
    # A missing/absent Authorization header under OBO_ENABLED=true is Demo-mode
    # traffic (no sign-in attempted), not an attempted-and-failed auth. Falls
    # back to the unchanged simulated/native path, exactly like OBO being off.
    _enabled(monkeypatch)
    assert build_obo_context("", decode=lambda t: dict(_CLAIMS), exchange=lambda a, s: "x") is None


def test_obo_enabled_empty_after_scheme_falls_back_to_none(monkeypatch):
    _enabled(monkeypatch)
    assert build_obo_context("Bearer   ", decode=lambda t: dict(_CLAIMS), exchange=lambda a, s: "x") is None
```

Remove `test_obo_enabled_missing_bearer_denies` and `test_obo_enabled_empty_after_scheme_denies` (the two tests these replace).

Add roles to the shared claims fixture and a new test asserting they land on the context:

```python
_CLAIMS = {
    "aud": "api://agent-host",
    "iss": "https://sts.windows.net/tenant-abc/",
    "exp": 9_999_999_999,
    "oid": "user-oid-123",
    "hospital": "hospital-usz",
    "roles": ["HCC.DischargeCoordinator", "HCC.BedManager"],
}


def test_obo_enabled_builds_context_with_roles_and_hospital(monkeypatch):
    _enabled(monkeypatch)
    ctx = build_obo_context(
        "Bearer raw-jwt",
        decode=lambda t: dict(_CLAIMS),
        exchange=lambda a, s: "obo-token-xyz",
    )
    assert ctx.roles == ("HCC.DischargeCoordinator", "HCC.BedManager")
    assert ctx.hospital == "hospital-usz"
```

Note: `test_obo_enabled_builds_context` (the existing test) still passes unchanged — it doesn't assert on `roles`/`hospital`, so adding the fields is additive there.

- [ ] **Step 2: Run tests to verify the expected failures**

Run: `cd apps/hcc-agent-host && python -m pytest tests/unit/test_obo_context.py -v`
Expected: FAIL — `test_obo_enabled_missing_bearer_falls_back_to_none` and `test_obo_enabled_empty_after_scheme_falls_back_to_none` fail because `build_obo_context` still raises; `test_obo_enabled_builds_context_with_roles_and_hospital` fails with `AttributeError: 'OboContext' object has no attribute 'roles'`.

- [ ] **Step 3: Fix `build_obo_context` and `OboContext`**

In `apps/hcc-agent-host/src/auth/obo_context.py`, replace the `OboContext` dataclass and the body of `build_obo_context`:

```python
@dataclass(frozen=True)
class OboContext:
    """A validated per-user identity plus the exchanged downstream token."""

    user_oid: str
    obo_token: str
    roles: tuple[str, ...] = ()
    hospital: str = "aggregated"
```

```python
def build_obo_context(
    authorization: str,
    *,
    decode: Callable[[str], dict[str, Any]] | None = None,
    exchange: Callable[[str, str], str] | None = None,
) -> OboContext | None:
    """Build an :class:`OboContext` from the ``Authorization`` header.

    - OBO disabled -> ``None`` (unchanged simulated/native path).
    - OBO enabled + no bearer presented at all -> ``None``. This is Demo-mode
      traffic (no sign-in was attempted), not a failed auth attempt, and must
      not be refused just because the subsystem is configured.
    - OBO enabled + a bearer WAS presented but is invalid -> raises
      (deny-by-default: anyone who actually attempted auth gets a hard 401).
    - OBO enabled + a valid bearer -> decode, validate claims (aud/iss/exp/oid/
      roles/hospital), exchange on-behalf-of, return the context.
    """
    if not obo_enabled():
        return None

    token = _strip_bearer(authorization)
    if not token:
        # No bearer at all under OBO_ENABLED=true is Demo-mode/anonymous
        # traffic, not an attempted-and-failed auth -- fall back, don't deny.
        return None

    claims = (decode or _default_decode)(token)
    caller = validate_claims(
        claims,
        expected_audience=os.getenv("OBO_AUDIENCE", ""),
        expected_issuer=os.getenv("OBO_ISSUER", ""),
    )
    scope = os.getenv("OBO_FABRIC_SCOPE", _DEFAULT_OBO_SCOPE)
    obo_token = (exchange or acquire_obo_token)(token, scope)
    return OboContext(
        user_oid=caller.oid,
        obo_token=obo_token,
        roles=caller.roles,
        hospital=caller.hospital,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd apps/hcc-agent-host && python -m pytest tests/unit/test_obo_context.py -v`
Expected: PASS (all tests in the file).

- [ ] **Step 5: Update the two integration tests that also encode the old bug**

In `apps/hcc-agent-host/tests/integration/test_golden_obo_endpoint.py`, add a new test confirming Demo-mode parity is preserved when OBO is on:

```python
def test_obo_enabled_no_bearer_falls_back_to_simulated(monkeypatch):
    # Demo mode: OBO_ENABLED=true tenant-wide, but this caller never signed in
    # (no Authorization header at all) -> unchanged simulated behavior, not 401.
    monkeypatch.setenv("OBO_ENABLED", "true")
    monkeypatch.setenv("OBO_AUDIENCE", "api://agent-host")
    monkeypatch.setenv("OBO_ISSUER", "https://sts.windows.net/tenant-abc/")
    resp = _client().get("/golden/network", headers=_SCOPED)
    assert resp.status_code == 200
    assert resp.json()["_rls"]["provider"] == "simulated"
```

In `apps/hcc-agent-host/tests/integration/test_chat_obo.py`, add the same parity test for chat:

```python
def test_chat_obo_enabled_no_bearer_falls_back_to_unchanged(monkeypatch):
    monkeypatch.setenv("OBO_ENABLED", "true")
    monkeypatch.setenv("OBO_AUDIENCE", "api://agent-host")
    monkeypatch.setenv("OBO_ISSUER", "https://sts.windows.net/tenant-abc/")
    monkeypatch.setenv("OBO_JWKS_URL", "https://example.invalid/keys")
    client = TestClient(create_app())
    resp = client.post(
        "/agents/bmca-agent/chat",
        json={"prompt": "Station B ist fast voll", "conversationId": "c1"},
    )
    assert resp.status_code == 200
```

- [ ] **Step 6: Run the full test suite to confirm no regressions**

Run: `cd apps/hcc-agent-host && python -m pytest tests/ -v`
Expected: PASS (all tests, including the new ones).

- [ ] **Step 7: Commit**

```bash
git add apps/hcc-agent-host/src/auth/obo_context.py apps/hcc-agent-host/tests/unit/test_obo_context.py apps/hcc-agent-host/tests/integration/test_golden_obo_endpoint.py apps/hcc-agent-host/tests/integration/test_chat_obo.py
git commit -m "fix(agent-host): OBO bearer-presence semantics + propagate roles/hospital through OboContext"
```

---

### Task 2: Server-side role/hospital validation in `golden()` and `chat()`

**Files:**
- Modify: `apps/hcc-agent-host/src/api/app.py`
- Modify: `apps/hcc-agent-host/tests/integration/test_golden_obo_endpoint.py`
- Modify: `apps/hcc-agent-host/tests/integration/test_chat_obo.py`

- [ ] **Step 1: Write the failing tests**

In `apps/hcc-agent-host/tests/integration/test_golden_obo_endpoint.py`, add:

```python
def test_obo_active_role_not_held_is_refused_403(monkeypatch):
    # A valid OBO context that holds only HCC.Viewer, but the caller asks for
    # HCC.SuperAdmin via the header -- deny-by-default, never silently widen.
    class _Ctx:
        user_oid = "55555555-5555-5555-5555-555555555555"
        obo_token = ""
        roles = ("HCC.Viewer",)
        hospital = "aggregated"

    monkeypatch.setattr(app_module, "build_obo_context", lambda _a: _Ctx())
    resp = _client().get(
        "/golden/network",
        headers={
            "X-Hospital-Scope": "aggregated",
            "X-Active-Role": "HCC.SuperAdmin",
            "Authorization": "Bearer ok",
        },
    )
    assert resp.status_code == 403


def test_obo_active_role_held_is_allowed(monkeypatch):
    class _Ctx:
        user_oid = "66666666-6666-6666-6666-666666666666"
        obo_token = ""
        roles = ("HCC.SuperAdmin", "HCC.Viewer")
        hospital = "aggregated"

    monkeypatch.setattr(app_module, "build_obo_context", lambda _a: _Ctx())
    resp = _client().get(
        "/golden/network",
        headers={
            "X-Hospital-Scope": "aggregated",
            "X-Active-Role": "HCC.SuperAdmin",
            "Authorization": "Bearer ok",
        },
    )
    assert resp.status_code == 200
```

In `apps/hcc-agent-host/tests/integration/test_chat_obo.py`, add the mirrored pair (chat has no `X-Active-Role` header today — this step also introduces reading it there for the check):

```python
def test_chat_obo_active_role_not_held_is_refused_403(monkeypatch):
    import api.app as app_module

    class _Ctx:
        user_oid = "77777777-7777-7777-7777-777777777777"
        obo_token = ""
        roles = ("HCC.Viewer",)
        hospital = "aggregated"

    monkeypatch.setattr(app_module, "build_obo_context", lambda _a: _Ctx())
    client = TestClient(create_app())
    resp = client.post(
        "/agents/bmca-agent/chat",
        json={"prompt": "hi", "conversationId": "c1"},
        headers={"Authorization": "Bearer ok", "X-Active-Role": "HCC.SuperAdmin"},
    )
    assert resp.status_code == 403
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd apps/hcc-agent-host && python -m pytest tests/integration/test_golden_obo_endpoint.py tests/integration/test_chat_obo.py -v`
Expected: FAIL — the new tests fail because no role check exists yet (both currently return 200/other codes, not 403).

- [ ] **Step 3: Add a shared role-check helper and wire it into both endpoints**

In `apps/hcc-agent-host/src/api/app.py`, add this helper near the top-level functions (after `_allowed_origins`):

```python
def _require_active_role_held(obo, active_role: str) -> None:
    """Deny-by-default: when an OBO context is present, the caller's requested
    active role must be one they actually hold on the token. Absent OBO
    (Demo mode), this check does not run -- unchanged legacy behavior."""
    if obo is None or not active_role:
        return
    if active_role not in obo.roles:
        raise HTTPException(
            status_code=403,
            detail=f"active role '{active_role}' is not held by the signed-in user",
        )
```

In `golden()`, right after the `build_obo_context` try/except block, add:

```python
        _require_active_role_held(obo, x_active_role)
```

In `chat()`, add an `x_active_role: str = Header(default="")` parameter and, right after the `build_obo_context` try/except block, add:

```python
        _require_active_role_held(obo, x_active_role)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd apps/hcc-agent-host && python -m pytest tests/integration/test_golden_obo_endpoint.py tests/integration/test_chat_obo.py -v`
Expected: PASS (all tests).

- [ ] **Step 5: Run the full test suite**

Run: `cd apps/hcc-agent-host && python -m pytest tests/ -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add apps/hcc-agent-host/src/api/app.py apps/hcc-agent-host/tests/integration/test_golden_obo_endpoint.py apps/hcc-agent-host/tests/integration/test_chat_obo.py
git commit -m "feat(agent-host): server-side active-role validation against the OBO token's real roles"
```

---

### Task 3: Extend `/worklist` and `/decisions` to derive identity from an OBO bearer

**Files:**
- Modify: `apps/hcc-agent-host/src/api/app.py`
- Modify: `apps/hcc-agent-host/tests/integration/test_worklist_api.py`
- Modify: `apps/hcc-agent-host/tests/integration/test_decisions_api.py`

- [ ] **Step 1: Write the failing tests**

In `apps/hcc-agent-host/tests/integration/test_worklist_api.py`, add:

```python
def test_worklist_obo_oid_overrides_x_user_oid(monkeypatch):
    import api.app as app_module

    class _Ctx:
        user_oid = "obo-oid-999"
        obo_token = ""
        roles = ("HCC.DischargeCoordinator",)
        hospital = "aggregated"

    monkeypatch.setattr(app_module, "build_obo_context", lambda _a: _Ctx())
    resp = _client().get(
        "/agents/dca/worklist",
        headers={"Authorization": "Bearer ok", "X-User-Oid": "header-oid-should-be-ignored"},
    )
    assert resp.status_code == 200
```

In `apps/hcc-agent-host/tests/integration/test_decisions_api.py`, add:

```python
def test_decision_approver_comes_from_obo_oid_not_header():
    import api.app as app_module

    class _Ctx:
        user_oid = "obo-approver-oid"
        obo_token = ""
        roles = ("HCC.DischargeCoordinator",)
        hospital = "aggregated"

    client = _client()
    app_module.build_obo_context = lambda _a: _Ctx()
    try:
        resp = client.post(
            "/agents/dca/decisions",
            json={"decision": "deny", "hospital": "USZ", "params": {}},
            headers={"Authorization": "Bearer ok", "X-User-Oid": "header-oid-should-be-ignored"},
        )
        assert resp.status_code == 200
        assert resp.json()["approver"] == "obo-approver-oid"
    finally:
        import importlib
        importlib.reload(app_module)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd apps/hcc-agent-host && python -m pytest tests/integration/test_worklist_api.py tests/integration/test_decisions_api.py -v`
Expected: FAIL — `worklist()`/`decisions()` don't read `Authorization` yet, so the OBO oid never overrides the header (the second test fails on the `approver` assertion).

- [ ] **Step 3: Wire OBO into both handlers**

In `apps/hcc-agent-host/src/api/app.py`, update the `worklist()` handler signature and body:

```python
    @app.get("/agents/{name}/worklist")
    def worklist(
        name: str,
        hospital: str = "USZ",
        x_user_oid: str = Header(default=""),
        authorization: str = Header(default=""),
    ) -> dict[str, Any]:
        # Sprint 39 P2 — the role's live observations + one grounded recommendation
        # on real seeded gold. Simulated-MVP: gold comes from the Plan 1 fixture via
        # load_gold_snapshot; the live golden-source read is the follow-on.
        # OBO-derived oid (verified token) overrides the client-supplied header
        # when present, mirroring the chat/golden endpoints.
        state = get_state()
        try:
            obo = build_obo_context(authorization)
        except TokenValidationError as exc:
            raise HTTPException(status_code=401, detail=str(exc))
        gold = state.load_gold_snapshot(hospital)
        sim = state.sim_registry.get_or_seed(hospital, gold)
        from loop.worklist import build_worklist

        try:
            return build_worklist(name, sim, provenance=gold.get("provenance", "simulated"))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
```

And `decisions()`:

```python
    @app.post("/agents/{name}/decisions")
    def decisions(
        name: str,
        req: DecisionRequest,
        x_user_oid: str = Header(default=""),
        authorization: str = Header(default=""),
    ) -> dict[str, Any]:
        # Sprint 39 P2 — a human accept/deny drives the REAL HITL apply->outcome on
        # the in-host SimState. NFR-UXL-001: only a human oid may act; the bot/self
        # refusal is enforced by plan_runtime.approve_action (surfaced as 403).
        # OBO-derived oid (verified token) overrides the client-supplied header
        # when present -- the audit trail records a verified identity, not a
        # client-claimed one.
        try:
            obo = build_obo_context(authorization)
        except TokenValidationError as exc:
            raise HTTPException(status_code=401, detail=str(exc))
        approver = (obo.user_oid if obo else x_user_oid)
        if not approver:
            raise HTTPException(status_code=401, detail="human approver (x-user-oid) required")
        state = get_state()
        gold = state.load_gold_snapshot(req.hospital)
        sim = state.sim_registry.get_or_seed(req.hospital, gold)
        from loop.decisions import decide

        try:
            return decide(
                name, req.decision, approver=approver, state=state, sim=sim,
                params=req.params, provenance=gold.get("provenance", "simulated"),
            )
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc))
        except (ValueError, KeyError) as exc:
            raise HTTPException(status_code=400, detail=str(exc))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd apps/hcc-agent-host && python -m pytest tests/integration/test_worklist_api.py tests/integration/test_decisions_api.py -v`
Expected: PASS.

- [ ] **Step 5: Run the full test suite**

Run: `cd apps/hcc-agent-host && python -m pytest tests/ -v`
Expected: PASS. (Note: `test_missing_user_oid_is_refused_401` in `test_decisions_api.py` still passes — with `OBO_ENABLED` unset, `build_obo_context` returns `None`, so `approver` falls back to the still-empty `x_user_oid` header, unchanged.)

- [ ] **Step 6: Commit**

```bash
git add apps/hcc-agent-host/src/api/app.py apps/hcc-agent-host/tests/integration/test_worklist_api.py apps/hcc-agent-host/tests/integration/test_decisions_api.py
git commit -m "feat(agent-host): worklist/decisions derive identity from a verified OBO bearer when present"
```

---

### Task 4: CSA tool-gate endpoint — verified OBO approver identity

**Files:**
- Modify: `apps/hcc-agent-host/src/api/app.py`
- Modify: `apps/hcc-agent-host/tests/integration/test_http.py`

The HITL evidence schema (`hitl/gate_enforcer.py`'s `REQUIRED_EVIDENCE_FIELDS`) already requires `approverObjectId` per gate — but nothing verifies it's real. This closes that gap for `csa-agent`'s HITL-01/HITL-04 gates (and every other agent's `/tools/{tool}` calls), mirroring the pattern Task 3 used for `/worklist`/`/decisions`.

- [ ] **Step 1: Write the failing tests**

In `apps/hcc-agent-host/tests/integration/test_http.py`, add:

```python
def test_tool_invocation_obo_present_approver_mismatch_denied_403(monkeypatch):
    import api.app as app_module

    class _Ctx:
        user_oid = "real-verified-oid"
        obo_token = ""
        roles = ("HCC.PlatformAdmin",)
        hospital = "aggregated"

    monkeypatch.setattr(app_module, "build_obo_context", lambda _a: _Ctx())
    resp = _client().post(
        "/agents/bmca-agent/tools/create-branch",
        json={
            "params": {},
            "hitlEvidence": {
                "HITL-02": {
                    "gateId": "HITL-02",
                    "approverObjectId": "claimed-but-not-verified-oid",
                    "approverRole": "HCC.PlatformAdmin",
                    "decisionTimestampUtc": "2026-08-09T00:00:00Z",
                    "correlationId": "c1",
                    "decisionContextHash": "hash",
                    "decisionOutcome": "approved",
                    "sourceWorkflow": "test",
                }
            },
        },
        headers={"Authorization": "Bearer ok"},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"]["reason"] == "approver_identity_not_verified"


def test_tool_invocation_obo_present_approver_matches_allowed(monkeypatch):
    import api.app as app_module

    class _Ctx:
        user_oid = "real-verified-oid"
        obo_token = ""
        roles = ("HCC.PlatformAdmin",)
        hospital = "aggregated"

    monkeypatch.setattr(app_module, "build_obo_context", lambda _a: _Ctx())
    resp = _client().post(
        "/agents/bmca-agent/tools/create-branch",
        json={
            "params": {},
            "hitlEvidence": {
                "HITL-02": {
                    "gateId": "HITL-02",
                    "approverObjectId": "real-verified-oid",
                    "approverRole": "HCC.PlatformAdmin",
                    "decisionTimestampUtc": "2026-08-09T00:00:00Z",
                    "correlationId": "c1",
                    "decisionContextHash": "hash",
                    "decisionOutcome": "approved",
                    "sourceWorkflow": "test",
                }
            },
        },
        headers={"Authorization": "Bearer ok"},
    )
    assert resp.status_code == 200
    assert resp.json()["decision"] == "allow"


def test_tool_invocation_without_obo_is_unchanged():
    # OBO absent (default) -> unchanged prior behavior, no identity cross-check.
    resp = _client().post(
        "/agents/bmca-agent/tools/create-branch",
        json={"params": {}, "hitlEvidence": {}},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"]["reason"] == "hitl_no_evidence"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd apps/hcc-agent-host && python -m pytest tests/integration/test_http.py -v`
Expected: FAIL — `invoke_tool()` doesn't read `Authorization` or cross-check `approverObjectId` yet, so the mismatch test gets a `200`/wrong-reason response instead of the expected `403`.

- [ ] **Step 3: Wire the identity check into `invoke_tool`**

In `apps/hcc-agent-host/src/api/app.py`, update the `invoke_tool` handler:

```python
    @app.post("/agents/{name}/tools/{tool}")
    def invoke_tool(
        name: str, tool: str, req: ToolRequest, authorization: str = Header(default="")
    ) -> dict[str, Any]:
        state = get_state()
        manifest = state.require(name)
        try:
            obo = build_obo_context(authorization)
        except TokenValidationError as exc:
            raise HTTPException(status_code=401, detail=str(exc))
        if obo is not None:
            # Deny-by-default: when a verified OBO identity is present, every
            # gate's claimed approverObjectId must match it -- the evidence
            # schema already requires this field, but nothing verified it was
            # real until now.
            for gate_id, evidence in req.hitlEvidence.items():
                if evidence.get("approverObjectId") != obo.user_oid:
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "decision": "deny",
                            "gateId": gate_id,
                            "reason": "approver_identity_not_verified",
                        },
                    )
        gate = enforce_gates(manifest.hitl_gates, req.hitlEvidence)
        if not gate.allowed:
            raise HTTPException(
                status_code=403,
                detail={
                    "decision": "deny",
                    "gateId": gate.gate_id,
                    "reason": gate.reason.value if gate.reason else None,
                },
            )
        # Positive-path tool execution wiring lands per agent in follow-up sprints.
        return {"decision": "allow", "gateId": gate.gate_id, "tool": tool}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd apps/hcc-agent-host && python -m pytest tests/integration/test_http.py -v`
Expected: PASS.

- [ ] **Step 5: Run the full test suite**

Run: `cd apps/hcc-agent-host && python -m pytest tests/ -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add apps/hcc-agent-host/src/api/app.py apps/hcc-agent-host/tests/integration/test_http.py
git commit -m "feat(agent-host): verify HITL gate approverObjectId against the OBO token when present (csa-agent alignment)"
```

---

### Task 5: Live grounding citation in `build_worklist`

**Files:**
- Modify: `apps/hcc-agent-host/src/loop/worklist.py`
- Modify: `apps/hcc-agent-host/src/api/app.py`
- Modify: `apps/hcc-agent-host/tests/unit/test_worklist.py`

- [ ] **Step 1: Write the failing tests**

In `apps/hcc-agent-host/tests/unit/test_worklist.py`, add:

```python
def test_dca_worklist_attaches_live_citation_when_fabric_present():
    state = _seeded_state()  # existing helper in this file; reuse it
    fake_rows = [{"patient": "p1", "ward": "B"}]
    fabric = _FakeFabric(rows=fake_rows)
    wl = build_worklist("dca", state, provenance="simulated", fabric=fabric)
    assert wl["recommendation"]["liveGroundingCitations"] == fake_rows


def test_dca_worklist_omits_live_citation_on_fabric_failure():
    state = _seeded_state()
    fabric = _FakeFabric(raise_on_query=True)
    wl = build_worklist("dca", state, provenance="simulated", fabric=fabric)
    assert wl["recommendation"]["liveGroundingCitations"] == []


def test_dca_worklist_no_fabric_means_no_live_citations_key_change():
    state = _seeded_state()
    wl = build_worklist("dca", state, provenance="simulated")
    assert wl["recommendation"]["liveGroundingCitations"] == []
```

Add the two small test fixtures near the top of the file (after imports):

```python
class _FakeFabric:
    def __init__(self, rows=None, raise_on_query=False):
        self._rows = rows or []
        self._raise = raise_on_query

    def query(self, table: str):
        if self._raise:
            raise RuntimeError("simulated fabric outage")
        return self._rows
```

Check the existing file for a shared `_seeded_state()` helper; if it doesn't exist, add one that mirrors what the existing tests build inline (a single-ward `SimState` with open transport barriers) — read the existing `test_dca_worklist_lists_open_barrier_candidates_and_a_recommendation` test body first and factor its setup into `_seeded_state()`, then update that test to call the new helper too (no behavior change, pure refactor).

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd apps/hcc-agent-host && python -m pytest tests/unit/test_worklist.py -v`
Expected: FAIL — `build_worklist` doesn't accept a `fabric` kwarg yet, and `liveGroundingCitations` doesn't exist.

- [ ] **Step 3: Implement the optional `fabric` param**

In `apps/hcc-agent-host/src/loop/worklist.py`, change the signature and add the citation lookup (both branches — `dca` and the non-dca placeholder — get the same treatment; add a small shared helper):

```python
def _live_citations(fabric: Any, table: str) -> list[dict[str, Any]]:
    if fabric is None:
        return []
    try:
        return fabric.query(table)
    except Exception:
        # Honest graceful-miss -- mirrors FabricDeltaClient.query()'s existing
        # behavior. A live-grounding hiccup must never break an otherwise
        # successful worklist read.
        return []


def build_worklist(
    role: str, state: SimState, provenance: str = "simulated", fabric: Any = None
) -> Dict[str, Any]:
    require_single_ward(state)
    ward = ward_of(state)
    if role == "dca":
        barriers = sorted(state.open_barriers(_BARRIER_TYPE), key=lambda b: b.barrier_id)
        observations = [
            {
                "patient": b.patient_id, "ward": ward, "readiness": "BLOCKED",
                "barrier": b.barrier_type, "aged_h": b.aged_h, "provenance": provenance,
            }
            for b in barriers
        ]
        n = len(barriers)
        live_citations = _live_citations(fabric, _CITATIONS[0])
        if n == 0:
            recommendation = {
                "lever_id": "DCA-UNBLOCK-BARRIER",
                "params": {"barrier_type": _BARRIER_TYPE, "n": 0, "ward": ward},
                "predicted_impact": {"metric": "beds", "value": 0},
                "insight_text": f"No open {_BARRIER_TYPE} barriers on {ward}; nothing to unblock",
                "citations": _CITATIONS,
                "liveGroundingCitations": live_citations,
            }
            return {"role": role, "ward": ward, "observations": observations,
                    "recommendation": recommendation, "provenance": provenance}
        gold_impact = {"forecast": [{"wardId": ward, "horizonH": 72,
                                     "bedCapacity": state.ward(ward).staffed_capacity,
                                     "forecastOccupiedBeds": state.occupancy(ward)}]}
        params = {"barrier_type": _BARRIER_TYPE, "n": n, "ward": ward}
        impact = compute_expected_impact("DCA-UNBLOCK-BARRIER", params, gold_impact, catalog=_CATALOG)
        recommendation = {
            "lever_id": "DCA-UNBLOCK-BARRIER", "params": params,
            "predicted_impact": {"metric": "beds", "value": int(impact["delta"])},
            "insight_text": f"Resolve {n} {_BARRIER_TYPE} barriers to free {impact['delta']} beds on {ward}",
            "citations": _CITATIONS,
            "liveGroundingCitations": live_citations,
        }
        return {"role": role, "ward": ward, "observations": observations,
                "recommendation": recommendation, "provenance": provenance}
    # Non-DCA roles: observations + advisory placeholder (full effect is follow-on).
    ready = [p.patient_id for p in state.patients_in_stage(Stage.DISCHARGE_READY)]
    return {
        "role": role, "ward": ward,
        "observations": [
            {"patient": p, "ward": ward, "readiness": "READY", "provenance": provenance}
            for p in sorted(ready)
        ],
        "recommendation": {
            "lever_id": None,
            "insight_text": "role effect pending (S38 multi-agent enrichment)",
            "citations": _CITATIONS,
            "liveGroundingCitations": _live_citations(fabric, _CITATIONS[0]),
        },
        "provenance": provenance,
    }
```

Add `from typing import Any` is already imported (`Dict`/`Any` from `typing` — check the existing import line and extend it to include `Any` if not already present).

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd apps/hcc-agent-host && python -m pytest tests/unit/test_worklist.py -v`
Expected: PASS.

- [ ] **Step 5: Wire `fabric` through from the endpoint**

In `apps/hcc-agent-host/src/api/app.py`, update `worklist()`'s body (from Task 3) to pass `state.fabric_for(obo.obo_token) if obo else None` into `build_worklist`:

```python
        try:
            fabric_override = state.fabric_for(obo.obo_token) if obo else None
            return build_worklist(
                name, sim, provenance=gold.get("provenance", "simulated"), fabric=fabric_override
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
```

- [ ] **Step 6: Run the full test suite**

Run: `cd apps/hcc-agent-host && python -m pytest tests/ -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add apps/hcc-agent-host/src/loop/worklist.py apps/hcc-agent-host/src/api/app.py apps/hcc-agent-host/tests/unit/test_worklist.py
git commit -m "feat(agent-host): worklist attaches a live OBO-grounded citation alongside the simulated recommendation"
```

---

### Task 6: Wire `ooa` and `bmca` into the Sprint 26 WS-B lever/formula registry

**Files:**
- Create: `apps/hcc-agent-host/src/loop/role_levers.py`
- Modify: `apps/hcc-agent-host/src/loop/worklist.py`
- Modify: `apps/hcc-agent-host/src/loop/decisions.py`
- Modify: `apps/hcc-agent-host/tests/unit/test_worklist.py`
- Modify: `apps/hcc-agent-host/tests/unit/test_decisions.py`

`data-platform/decision/levers/{ooa,bmca,orsa,sba}.yaml` and `data-platform/decision/impact/compute_expected_impact.py`'s formula registry already exist (Sprint 26 WS-B) — real, deterministic, gold-grounded predicted-impact math for every role. Only `dca.yaml` has an `effect:` block (real `SimState` actuation); `ooa`/`bmca` get real recommendations here with an honestly-unactuated Accept. `orsa`/`sba` need a domain concept (OR-case, staffing) `SimState` doesn't have — left unchanged.

- [ ] **Step 1: Create the shared role -> lever registry**

Create `apps/hcc-agent-host/src/loop/role_levers.py`:

```python
"""Sprint 43 WS-7 -- shared role -> lever registry, wiring the Sprint 26 WS-B
lever catalog + formula registry (data-platform/decision/impact/
compute_expected_impact.py) into the Sprint 39 P2 worklist/decisions loop.

Only roles listed here get a REAL, catalog-grounded recommendation; roles not
listed keep the existing honest "role effect pending" placeholder
(build_worklist) or today's non-dca decide() behavior -- no regression.

``has_effect`` distinguishes real SimState actuation (only dca today, via
apps/sim-capacity/src/closedloop/effect.py's DischargeBarrier/set_status
branch) from predicted-impact-only roles (ooa, bmca): their Accept is still a
real, tracked HITL decision on a real number, but never mutates SimState (no
`effect:` block exists yet for these two levers in
data-platform/decision/levers/{ooa,bmca}.yaml).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RoleLever:
    lever_id: str
    has_effect: bool


ROLE_LEVERS: dict[str, RoleLever] = {
    "dca": RoleLever(lever_id="DCA-UNBLOCK-BARRIER", has_effect=True),
    "ooa": RoleLever(lever_id="OOA-EXPEDITE-DISCHARGE", has_effect=False),
    "bmca": RoleLever(lever_id="BMCA-REBALANCE-CENSUS", has_effect=False),
}

# BMCA-REBALANCE-CENSUS needs a `to_ward` label; SimState is single-ward MVP
# (see loop/ward_scope), so this is a fixed, documented assumption -- the same
# shape as DCA's own fixed `_BARRIER_TYPE = "transport"` constant.
ASSUMED_SISTER_WARD = "Medicine B"

# OOA-EXPEDITE-DISCHARGE needs a `before` label; no time-of-day concept exists
# in SimState, so this is a fixed, documented assumption.
ASSUMED_EXPEDITE_DEADLINE = "end-of-shift"
```

- [ ] **Step 2: Write the failing worklist tests**

In `apps/hcc-agent-host/tests/unit/test_worklist.py`, add:

```python
def test_ooa_worklist_uses_real_formula_registry():
    state = _seeded_state()
    wl = build_worklist("ooa", state, provenance="simulated")
    assert wl["recommendation"]["lever_id"] == "OOA-EXPEDITE-DISCHARGE"
    assert wl["recommendation"]["predicted_impact"]["value"] >= 0
    assert wl["recommendation"]["params"]["before"] == "end-of-shift"


def test_bmca_worklist_uses_real_formula_registry():
    state = _seeded_state()
    wl = build_worklist("bmca", state, provenance="simulated")
    assert wl["recommendation"]["lever_id"] == "BMCA-REBALANCE-CENSUS"
    assert wl["recommendation"]["params"]["to_ward"] == "Medicine B"


def test_orsa_and_sba_worklist_are_unchanged_placeholder():
    state = _seeded_state()
    for role in ("orsa", "sba"):
        wl = build_worklist(role, state, provenance="simulated")
        assert wl["recommendation"]["lever_id"] is None
        assert "pending" in wl["recommendation"]["insight_text"]
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd apps/hcc-agent-host && python -m pytest tests/unit/test_worklist.py -v`
Expected: FAIL — `build_worklist` has no `ooa`/`bmca` branch yet, so both fall through to the generic placeholder (`lever_id` is `None`, not the expected value).

- [ ] **Step 4: Add the `ooa`/`bmca` branches to `build_worklist`**

In `apps/hcc-agent-host/src/loop/worklist.py`, add the import and insert two new branches between the `dca` branch and the final placeholder fallback (the function ends up with four branches: `dca`, `ooa`, `bmca`, then the placeholder for everything else):

```python
from impact.compute_expected_impact import compute_expected_impact

from .role_levers import ASSUMED_EXPEDITE_DEADLINE, ASSUMED_SISTER_WARD, ROLE_LEVERS
```

(add these alongside the existing imports at the top of the file)

```python
    if role == "ooa":
        ready = sorted(p.patient_id for p in state.patients_in_stage(Stage.DISCHARGE_READY))
        observations = [
            {"patient": p, "ward": ward, "readiness": "READY", "provenance": provenance}
            for p in ready
        ]
        n = len(ready)
        lever_id = ROLE_LEVERS["ooa"].lever_id
        live_citations = _live_citations(fabric, _CITATIONS[0])
        if n == 0:
            recommendation = {
                "lever_id": lever_id,
                "params": {"n": 0, "before": ASSUMED_EXPEDITE_DEADLINE, "ward": ward},
                "predicted_impact": {"metric": "beds", "value": 0},
                "insight_text": f"No discharge-ready patients on {ward} to expedite",
                "citations": _CITATIONS, "liveGroundingCitations": live_citations,
            }
        else:
            gold_impact = {"forecast": [{"wardId": ward, "horizonH": 72,
                                         "bedCapacity": state.ward(ward).staffed_capacity,
                                         "forecastOccupiedBeds": state.occupancy(ward)}]}
            params = {"n": n, "before": ASSUMED_EXPEDITE_DEADLINE, "ward": ward}
            impact = compute_expected_impact(lever_id, params, gold_impact)
            recommendation = {
                "lever_id": lever_id, "params": params,
                "predicted_impact": {"metric": impact["metric"], "value": impact["delta"]},
                "insight_text": (
                    f"Expedite {n} discharge-ready patients on {ward} before "
                    f"{ASSUMED_EXPEDITE_DEADLINE} to free {impact['delta']} beds"
                ),
                "citations": _CITATIONS, "liveGroundingCitations": live_citations,
            }
        return {"role": role, "ward": ward, "observations": observations,
                "recommendation": recommendation, "provenance": provenance}
    if role == "bmca":
        capacity = state.ward(ward).staffed_capacity
        occupied = state.occupancy(ward)
        threshold_beds = round(capacity * 0.90)
        n = max(0, occupied - threshold_beds)
        observations = [{
            "ward": ward, "occupied": occupied, "capacity": capacity,
            "occupancy_pct": round(100 * occupied / capacity) if capacity else 0,
            "provenance": provenance,
        }]
        lever_id = ROLE_LEVERS["bmca"].lever_id
        live_citations = _live_citations(fabric, _CITATIONS[0])
        if n == 0:
            recommendation = {
                "lever_id": lever_id,
                "params": {"n": 0, "to_ward": ASSUMED_SISTER_WARD, "ward": ward},
                "predicted_impact": {"metric": "beds", "value": 0},
                "insight_text": f"{ward} is within its 90% target; no census rebalance needed",
                "citations": _CITATIONS, "liveGroundingCitations": live_citations,
            }
        else:
            gold_impact = {"forecast": [{"wardId": ward, "horizonH": 72,
                                         "bedCapacity": capacity,
                                         "forecastOccupiedBeds": occupied}]}
            params = {"n": n, "to_ward": ASSUMED_SISTER_WARD, "ward": ward}
            impact = compute_expected_impact(lever_id, params, gold_impact)
            recommendation = {
                "lever_id": lever_id, "params": params,
                "predicted_impact": {"metric": impact["metric"], "value": impact["delta"]},
                "insight_text": (
                    f"Transfer {n} patients from {ward} to {ASSUMED_SISTER_WARD} "
                    f"to rebalance census (target 90%)"
                ),
                "citations": _CITATIONS, "liveGroundingCitations": live_citations,
            }
        return {"role": role, "ward": ward, "observations": observations,
                "recommendation": recommendation, "provenance": provenance}
```

Insert both branches immediately after the `dca` branch's `return` statement and before the comment `# Non-DCA roles: observations + advisory placeholder...` — `orsa`/`sba` (and any future unmapped role) fall through to that unchanged placeholder exactly as today.

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd apps/hcc-agent-host && python -m pytest tests/unit/test_worklist.py -v`
Expected: PASS.

- [ ] **Step 6: Write the failing decisions tests**

In `apps/hcc-agent-host/tests/unit/test_decisions.py`, add:

```python
def test_ooa_decide_accept_is_tracked_but_not_applied():
    sim = seed_sim_state_from_gold(_GOLD)
    out = decide("ooa", "accept", approver="clinician@usz.ch", state=None, sim=sim, params={})
    assert out["lever_id"] == "OOA-EXPEDITE-DISCHARGE"
    assert out["applied"] is False
    assert out["decision"] == "accept"
    assert out["approver"] == "clinician@usz.ch"
    assert out["applyReason"] == "actuation_not_modeled_for_lever"


def test_bmca_decide_deny_is_tracked_but_not_applied():
    sim = seed_sim_state_from_gold(_GOLD)
    out = decide("bmca", "deny", approver="clinician@usz.ch", state=None, sim=sim, params={})
    assert out["lever_id"] == "BMCA-REBALANCE-CENSUS"
    assert out["applied"] is False
    assert out["decision"] == "deny"


def test_ooa_decide_bot_approver_still_refused():
    sim = seed_sim_state_from_gold(_GOLD)
    with pytest.raises(PermissionError):
        decide("ooa", "accept", approver="dependabot[bot]", state=None, sim=sim, params={})
```

- [ ] **Step 7: Run tests to verify they fail**

Run: `cd apps/hcc-agent-host && python -m pytest tests/unit/test_decisions.py -v`
Expected: FAIL — `decide()` has no `ROLE_LEVERS`-aware branch yet, so `ooa`/`bmca` fall through to the existing DCA-only logic (which raises or mis-behaves for a role it doesn't recognize).

- [ ] **Step 8: Add the predicted-only branch to `decide()`**

In `apps/hcc-agent-host/src/loop/decisions.py`, add the import and insert a new branch right after the `require_single_ward(sim)` call, before the existing DCA-specific logic:

```python
from .role_levers import ROLE_LEVERS
```

(add alongside the existing `.ward_scope` import)

```python
def decide(
    role: str,
    decision: str,
    approver: str,
    state: Any,
    sim: SimState,
    params: Dict[str, Any],
    provenance: str | None = None,
) -> Dict[str, Any]:
    if decision not in ("accept", "deny"):
        raise ValueError(f"decision must be 'accept' or 'deny', got {decision!r}")

    require_single_ward(sim)

    lever = ROLE_LEVERS.get(role)
    if lever is not None and not lever.has_effect:
        # ooa/bmca: real, catalog-grounded math (Sprint 26 WS-B), but no
        # `effect:` mapping exists yet -- a real, tracked decision on a real
        # number, honestly never applied to SimState.
        if plan_runtime._is_bot_approver(approver):
            raise PermissionError(f"bot approver refused: {approver!r}")
        ward = params.get("ward") or ward_of(sim)
        if ward not in sim.wards:
            raise ValueError(f"unknown ward {ward!r}")
        if provenance is None:
            provenance = _provenance_of(state, sim)
        from .worklist import build_worklist  # reuse the same grounded math

        reco = build_worklist(role, sim, provenance=provenance)["recommendation"]
        plan_id = f"plan-decide-{sim.hospital_id}-{role}"
        return {
            "contract": "DC-SIM-OUTCOME-v1", "cosmos_id": None, "plan_id": plan_id,
            "golden_thread": f"gt-{plan_id}", "lever_id": lever.lever_id, "applied_ts": _NOW,
            "predicted_impact": reco["predicted_impact"],
            "realised_impact": {"metric": reco["predicted_impact"]["metric"], "value": 0},
            "state_delta": {"beds_freed": [], "patients_discharged": [], "patients_promoted": []},
            "divergence": 0.0, "provenance": provenance, "applied": False,
            "applyReason": "actuation_not_modeled_for_lever",
            "branch": decision, "decision": decision, "approver": approver,
        }

    # Single-ward MVP (see loop/ward_scope) + validate any caller-supplied ward so
    # an unknown ward is a 400, never an unhandled KeyError 500 at the mutation.
    barrier_type = params.get("barrier_type", _BARRIER_TYPE)
    ward = params.get("ward") or ward_of(sim)
    if ward not in sim.wards:
        raise ValueError(f"unknown ward {ward!r}")
    if provenance is None:
        provenance = _provenance_of(state, sim)
    plan_id = f"plan-decide-{sim.hospital_id}"
    ... (rest of the existing dca-only body is unchanged)
```

Note: this removes the now-duplicated `require_single_ward(sim)` call from the top of the function body (it moved earlier, before the new branch) — make sure there is exactly one call to it, not two.

- [ ] **Step 9: Run tests to verify they pass**

Run: `cd apps/hcc-agent-host && python -m pytest tests/unit/test_decisions.py -v`
Expected: PASS.

- [ ] **Step 10: Run the full test suite**

Run: `cd apps/hcc-agent-host && python -m pytest tests/ -v`
Expected: PASS.

- [ ] **Step 11: Commit**

```bash
git add apps/hcc-agent-host/src/loop/role_levers.py apps/hcc-agent-host/src/loop/worklist.py apps/hcc-agent-host/src/loop/decisions.py apps/hcc-agent-host/tests/unit/test_worklist.py apps/hcc-agent-host/tests/unit/test_decisions.py
git commit -m "feat(agent-host): wire ooa+bmca into the Sprint 26 WS-B lever/formula registry (real, honestly-unactuated recommendations)"
```

---

### Task 7: Live, config-gated Cosmos persistence for agent memory (conversations, interactions, audit, decisions)

**Files:**
- Modify: `apps/hcc-agent-host/src/persistence/cosmos_client.py`
- Modify: `apps/hcc-agent-host/src/api/app.py`
- Create: `apps/hcc-agent-host/tests/unit/test_live_cosmos_persistence.py`
- Modify: `apps/hcc-agent-host/tests/integration/test_decisions_api.py`

- [ ] **Step 1: Write the failing unit tests for the live class + factory**

Create `apps/hcc-agent-host/tests/unit/test_live_cosmos_persistence.py`:

```python
"""Unit tests for LiveCosmosPersistence + build_cosmos_persistence (config-gated,
mirrors _build_chat_model's guarded-optional pattern). No live Cosmos needed --
the container client is dependency-injected."""
from __future__ import annotations

import pytest

from persistence.cosmos_client import (
    CosmosPersistence,
    LiveCosmosPersistence,
    build_cosmos_persistence,
)


class _FakeContainer:
    def __init__(self):
        self.items: list[dict] = []

    def upsert_item(self, record: dict) -> None:
        self.items = [i for i in self.items if i.get("id") != record.get("id")]
        self.items.append(record)

    def read_all_items(self):
        return list(self.items)

    def query_items(self, query, parameters, enable_cross_partition_query=True):
        # Minimal fake: only supports the two equality queries this module issues.
        field = "correlationId" if "correlationId" in query else "interactionId"
        value = parameters[0]["value"]
        return [i for i in self.items if i.get(field) == value]


def _factory(containers: dict[str, _FakeContainer]):
    return lambda name: containers[name]


def test_build_cosmos_persistence_without_endpoint_is_in_memory(monkeypatch):
    monkeypatch.delenv("COSMOS_ENDPOINT", raising=False)
    persistence = build_cosmos_persistence()
    assert isinstance(persistence, CosmosPersistence)


def test_build_cosmos_persistence_with_endpoint_is_live(monkeypatch):
    monkeypatch.setenv("COSMOS_ENDPOINT", "https://cosmos-ihzhhpf-sit.documents.azure.com:443/")
    containers = {"approval-events": _FakeContainer()}
    persistence = build_cosmos_persistence(container_client_factory=_factory(containers))
    assert isinstance(persistence, LiveCosmosPersistence)


def test_live_persistence_write_and_query_by_correlation():
    containers = {"approval-events": _FakeContainer()}
    persistence = LiveCosmosPersistence(_container_for=_factory(containers))
    record = persistence.write("approval-events", {"correlationId": "gt-1", "decision": "accept"})
    assert record["id"]
    found = persistence.query_by_correlation("approval-events", "gt-1")
    assert found == [record]


def test_live_persistence_write_missing_partition_key_raises():
    containers = {"approval-events": _FakeContainer()}
    persistence = LiveCosmosPersistence(_container_for=_factory(containers))
    with pytest.raises(ValueError):
        persistence.write("approval-events", {"decision": "accept"})


def test_live_persistence_append_user_event():
    containers = {"agent_interactions": _FakeContainer()}
    persistence = LiveCosmosPersistence(_container_for=_factory(containers))
    persistence.write("agent_interactions", {
        "conversationKey": "user1:bmca-agent", "interactionId": "i1",
    })
    updated = persistence.append_user_event("i1", {"type": "click"})
    assert updated["userEvents"] == [{"type": "click"}]


def test_live_persistence_append_user_event_unknown_id_raises():
    containers = {"agent_interactions": _FakeContainer()}
    persistence = LiveCosmosPersistence(_container_for=_factory(containers))
    with pytest.raises(KeyError):
        persistence.append_user_event("nope", {"type": "click"})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd apps/hcc-agent-host && python -m pytest tests/unit/test_live_cosmos_persistence.py -v`
Expected: FAIL — `LiveCosmosPersistence` and `build_cosmos_persistence` don't exist yet (`ImportError`).

- [ ] **Step 3: Implement `LiveCosmosPersistence` and `build_cosmos_persistence`**

In `apps/hcc-agent-host/src/persistence/cosmos_client.py`, add after the existing `CosmosPersistence` class:

```python
@dataclass
class LiveCosmosPersistence:
    """azure-cosmos-backed persistence. Same interface as CosmosPersistence.

    The container-client lookup is injected (``_container_for``) so this class
    is unit-tested without a live account -- mirrors the existing
    ``acquire_obo_token``/``credential_factory`` injection pattern used
    elsewhere in this app.
    """

    _container_for: Callable[[str], Any]

    def write(self, container: str, item: dict[str, Any]) -> dict[str, Any]:
        if container not in CONTAINERS:
            raise ValueError(f"unknown container '{container}'")
        record = dict(item)
        record.setdefault("id", str(uuid.uuid4()))
        pk = PARTITION_KEYS[container]
        if pk not in record:
            raise ValueError(f"item for '{container}' missing partition key '{pk}'")
        self._container_for(container).upsert_item(record)
        return record

    def read_all(self, container: str) -> list[dict[str, Any]]:
        if container not in CONTAINERS:
            raise ValueError(f"unknown container '{container}'")
        return list(self._container_for(container).read_all_items())

    def query_by_correlation(self, container: str, correlation_id: str) -> list[dict[str, Any]]:
        return list(
            self._container_for(container).query_items(
                query="SELECT * FROM c WHERE c.correlationId = @cid",
                parameters=[{"name": "@cid", "value": correlation_id}],
                enable_cross_partition_query=True,
            )
        )

    def append_user_event(self, interaction_id: str, event: dict[str, Any]) -> dict[str, Any]:
        container = self._container_for("agent_interactions")
        matches = list(
            container.query_items(
                query="SELECT * FROM c WHERE c.interactionId = @iid",
                parameters=[{"name": "@iid", "value": interaction_id}],
                enable_cross_partition_query=True,
            )
        )
        if not matches:
            raise KeyError(f"no agent_interactions record with interactionId '{interaction_id}'")
        record = dict(matches[0])
        record.setdefault("userEvents", []).append(dict(event))
        container.upsert_item(record)
        return record


def build_cosmos_persistence(
    *, container_client_factory: Callable[[str], Any] | None = None
) -> "CosmosPersistence | LiveCosmosPersistence":
    """Return a live Cosmos-backed persistence when ``COSMOS_ENDPOINT`` is
    configured, else the in-memory stand-in (unchanged dev/CI default).

    Mirrors ``api/app.py``'s ``_build_chat_model``/``_build_live_data_agent``
    guarded-optional pattern. The Cosmos account, ``agenthost`` database, and
    every container in ``CONTAINERS`` (including ``approval-events``) are
    already deployed live in SIT with ``Cosmos DB Built-in Data Contributor``
    already granted to this app's managed identity -- this function is the
    only missing piece.
    """
    endpoint = os.environ.get("COSMOS_ENDPOINT")
    if not endpoint:
        return CosmosPersistence()
    if container_client_factory is not None:
        return LiveCosmosPersistence(_container_for=container_client_factory)
    from azure.cosmos import CosmosClient
    from azure.identity import DefaultAzureCredential

    client = CosmosClient(endpoint, credential=DefaultAzureCredential())
    database = client.get_database_client("agenthost")
    return LiveCosmosPersistence(_container_for=database.get_container_client)
```

Add the two new imports needed at the top of the file: `import os` and `from typing import Callable` (extend the existing `from typing import Any` line to `from typing import Any, Callable`).

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd apps/hcc-agent-host && python -m pytest tests/unit/test_live_cosmos_persistence.py -v`
Expected: PASS.

- [ ] **Step 5: Wire it into `HostState` and write the decision outcome to Cosmos**

In `apps/hcc-agent-host/src/api/app.py`, in `HostState.__init__`, change the `Orchestrator(...)` construction to pass an explicitly-built persistence:

```python
        from persistence.cosmos_client import build_cosmos_persistence

        self.persistence = build_cosmos_persistence()
        self.orchestrator = Orchestrator(
            chat_model=live_chat_model if live_chat_model is not None else MockChatModel(),
            fabric=self.fabric,
            data_agent=adapter,
            persistence=self.persistence,
        )
```

In the `decisions()` handler, after `decide(...)` returns, persist the outcome before returning it:

```python
        try:
            outcome = decide(
                name, req.decision, approver=approver, state=state, sim=sim,
                params=req.params, provenance=gold.get("provenance", "simulated"),
            )
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc))
        except (ValueError, KeyError) as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        state.persistence.write(
            "approval-events", {**outcome, "correlationId": outcome["golden_thread"]}
        )
        return outcome
```

- [ ] **Step 6: Add an integration test confirming the write happens**

In `apps/hcc-agent-host/tests/integration/test_decisions_api.py`, add:

```python
def test_decision_outcome_is_persisted_to_approval_events():
    client = _client()
    resp = client.post(
        "/agents/dca/decisions",
        json={"decision": "deny", "hospital": "USZ", "params": {}},
        headers=_OID,
    )
    assert resp.status_code == 200
    state = get_state()
    records = state.persistence.query_by_correlation("approval-events", resp.json()["golden_thread"])
    assert len(records) == 1
    assert records[0]["decision"] == "deny"
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `cd apps/hcc-agent-host && python -m pytest tests/integration/test_decisions_api.py tests/unit/test_live_cosmos_persistence.py -v`
Expected: PASS.

- [ ] **Step 8: Run the full test suite**

Run: `cd apps/hcc-agent-host && python -m pytest tests/ -v`
Expected: PASS (all tests; `COSMOS_ENDPOINT` is unset in CI/dev, so `build_cosmos_persistence()` returns the unchanged in-memory `CosmosPersistence`, byte-parity with today).

- [ ] **Step 9: Commit**

```bash
git add apps/hcc-agent-host/src/persistence/cosmos_client.py apps/hcc-agent-host/src/api/app.py apps/hcc-agent-host/tests/unit/test_live_cosmos_persistence.py apps/hcc-agent-host/tests/integration/test_decisions_api.py
git commit -m "feat(agent-host): live Cosmos persistence for the decisions audit trail (config-gated, no new infra)"
```

---

### Task 8: Entra — mirror App Roles + `admin@`'s assignments onto `hcc-agent-host`

**This is an IAM change, not code. Per AGENTS.md §4 it requires an explicit `approved-to-apply` comment before execution — do not run these commands until that approval is given.**

**Files:** none (Entra configuration only).

- [ ] **Step 1: Confirm the current (empty) state**

Run: `az ad app show --id b7608e39-e23a-4576-8489-e092ba5f726b --query appRoles -o json`
Expected: `[]`

- [ ] **Step 2: Build the app-roles manifest from the already-existing master data**

The 17 roles and their `id`/`value`/`displayName`/`description` already exist verbatim on `ihzhhpf-app` (confirmed live, §1.1 of the design doc) and in `data/entra/app-roles.csv`. Export the live `ihzhhpf-app` role definitions (reuse the same GUIDs is not required — new GUIDs are fine and expected for a different app registration) as the manifest for `hcc-agent-host`:

```bash
az ad app show --id 52681a08-c792-44b1-b6b5-01cb560d450f --query appRoles -o json > /tmp/ihzhhpf-app-roles.json
```

Strip the `id` field from each entry so `az ad app update` generates fresh GUIDs for the new app (reusing another app's role GUIDs is not meaningful — role GUIDs are scoped per-application):

```bash
python3 -c "
import json
roles = json.load(open('/tmp/ihzhhpf-app-roles.json'))
for r in roles:
    r.pop('id', None)
json.dump(roles, open('/tmp/hcc-agent-host-app-roles.json', 'w'), indent=2)
"
```

- [ ] **Step 3: Apply the roles to `hcc-agent-host` (requires `approved-to-apply`)**

```bash
az ad app update --id b7608e39-e23a-4576-8489-e092ba5f726b --app-roles @/tmp/hcc-agent-host-app-roles.json
```

- [ ] **Step 4: Verify the roles landed**

```bash
az ad app show --id b7608e39-e23a-4576-8489-e092ba5f726b --query "appRoles[].value" -o tsv
```

Expected: all 17 `HCC.*` values listed.

- [x] **Step 5 (REVISED — resolved via `groupMembershipClaims`, 2026-08-10): assign `admin@` the roles held on `ihzhhpf-app`**

**STATUS: Resolved via a different mechanism, not by completing the original step as written.** The App Role ASSIGNMENT write (`POST /servicePrincipals/{id}/appRoleAssignedTo`) remains genuinely blocked for the reason below (kept for the record — still true, and would matter for a future tenant/identity without the group memberships this pivot relies on):

This specific Graph API requires the caller to hold a qualifying Microsoft Entra directory role (Application Administrator, Cloud Application Administrator, User Administrator, Privileged Role Administrator, Identity Governance Administrator, Hybrid Identity Administrator, Directory Writer, or Directory Synchronization Accounts — see [Microsoft's docs](https://learn.microsoft.com/en-us/graph/api/serviceprincipal-post-approleassignedto)), with no owner-of-the-resource exception. `admin@`'s actual directory roles (`GET /me/memberOf`) confirm Global Reader only.

**The fix:** `groupMembershipClaims` is a *different* Entra mechanism, in the same permission class as App Role *definition* — an owner-level, self-service app-registration property. `admin@` is a real, confirmed member of all 17 `HCC.*` security groups already (`GET /me/memberOf`, 19 total directory memberships, comfortably under the ~150-group JWT overage threshold). Setting `groupMembershipClaims=SecurityGroup` on `hcc-agent-host` puts a `groups` claim on the OBO token driven by those already-existing memberships — zero new IAM writes.

Applied and verified live:

```bash
az ad app update --id b7608e39-e23a-4576-8489-e092ba5f726b --set groupMembershipClaims=SecurityGroup
az ad app show --id b7608e39-e23a-4576-8489-e092ba5f726b --query groupMembershipClaims -o tsv
# -> SecurityGroup
```

Code changes to consume the `groups` claim (see Task 8a below) union group-derived roles onto `ValidatedCaller.roles`, so `OboContext`, `_require_active_role_held`, `worklist.py`, `decisions.py` and every other Task 1-7 consumer needed **zero** changes — they already just check `active_role in obo.roles`.

approved-to-apply by @urruegg (2026-08-10).

- [ ] **Step 6 (superseded): live App Role assignment verification is no longer required** — group-derived roles are verified instead by a live OBO smoke test once Task 9 is attempted (not part of this task; see Task 9's prerequisite note).

- [x] **Step 7: No commit needed for Steps 1-5** (Entra-only changes; no repo files changed by the App Role definition or `groupMembershipClaims` config). Note both changes in the PR description under "Security impact" per the repo's PR Output Contract. (Task 8a below **does** touch repo files — the code + Bicep wiring for the `groups` claim.)

---

### Task 8a: Code + Bicep — consume the `groups` claim (group-derived roles)

**Files:**
- New: `apps/hcc-agent-host/src/auth/group_roles.py` — `group_role_map()` parses `OBO_GROUP_ROLE_MAP` (JSON, group-object-id → HCC.\* role name) from env config. Deny-by-default: unset/malformed → empty map, never raises.
- Modify: `apps/hcc-agent-host/src/auth/token_validator.py` — `validate_claims()` now also parses `claims.get("groups", [])`, maps entries through `group_role_map()`, and unions the result onto the direct `roles` claim (deduped, order-preserving) before constructing `ValidatedCaller`.
- Modify: `apps/hcc-agent-host/tests/unit/test_support_modules.py` — 5 new tests: group→role mapping, union with direct roles, dedup, unmapped group IDs ignored, missing/malformed `OBO_GROUP_ROLE_MAP` tolerated (regression safety).
- Modify: `infra/modules/agent-host/container-app.bicep`, `infra/modules/agent-host/main.bicep`, `infra/main.bicep` — new `oboGroupRoleMap` param threaded through to a new `OBO_GROUP_ROLE_MAP` container env var (same pattern as `oboFabricScope`/`OBO_FABRIC_SCOPE`).
- Modify: `infra/environments/sit.bicepparam` — `agentHostOboGroupRoleMap` set to the live JSON mapping of all 17 `HCC.*` group object IDs (read via `GET /me/memberOf`) to their role names. Non-secret directory metadata, same class as `agentHostOboTenantId`/`agentHostOboClientId` already committed there in plaintext. `agentHostOboEnabled` is left `false` — this task only makes the code/config *ready*, it does not flip the flag (that remains Task 9, separately gated).

**Verification performed:**
- `python -m pytest tests/ -q` — full suite green (293 tests, no regressions).
- `az bicep build --file infra/main.bicep --outfile infra/main.json` — clean compile (verified, then the regenerated `main.json`/`sit.json` were reverted to avoid committing large, unrelated pre-existing drift between those compiled artefacts and their `.bicep`/`.bicepparam` sources — a gap that predates this task).
- `az bicep build-params --file infra/environments/sit.bicepparam` — clean compile against the updated `main.bicep`.

---

### Task 9: Bicep — re-enable `agentHostOboEnabled`

**Files:**
- Modify: `infra/environments/sit.bicepparam`

**Prerequisite:** Tasks 1-8/8a merged and deployed (the image must contain the Task 1-7 code fixes, plus Task 8a's group-claim role mapping, before this flag is safe to flip). **Task 8 Step 5's original blocker (role assignment) is resolved via Task 8a's `groupMembershipClaims` pivot** — no directory-role elevation needed. **Still open, not addressed by this fix:** `sit.bicepparam`'s own history records that `agentHostOboEnabled=true` was reverted same-day (2026-08-09) because `OBO_ENABLED` is a shared, global flag also read by the pre-existing `/golden` board-data endpoint, and a caller with no bearer at all hard-401'd. Task 1's fix (distinguishing "no bearer presented" from "bearer presented but invalid") looks like it should resolve this too, but that has **not been re-verified live** since the revert — do so before flipping this flag again, don't assume it's fixed.

- [ ] **Step 1: Flip the flag**

In `infra/environments/sit.bicepparam`, change:

```bicep
param agentHostOboEnabled = false
```

to:

```bicep
param agentHostOboEnabled = true
```

- [ ] **Step 2: Validate the Bicep build**

Run: `az bicep build --file infra/main.bicep`
Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add infra/environments/sit.bicepparam
git commit -m "feat(infra): re-enable agentHostOboEnabled - safe now the bearer-presence bug is fixed"
```

- [ ] **Step 4: Push, wait for image build (if a new image is needed for Tasks 1-7), approve the SIT deploy, and confirm**

```bash
git push origin main
```

Approve the `ci-build-agent-host.yml` and `cd-infra-deploy-sit.yml` environment gates as usual (see repo memory for the `gh api ... pending_deployments` approval command). After deploy:

```bash
az containerapp show -n ca-agent-host-ihzhhpf-sit -g rg-ihzhhpf-sit --query "properties.template.containers[0].env[?name=='OBO_ENABLED']" -o json
```

Expected: `OBO_ENABLED: true`.

---

### Task 10: Live verification

**No code changes — manual/browser verification.**

- [ ] **Step 1: Confirm Demo mode is unaffected**

In a browser, load `https://appsit.curavias.ch` without signing in (Demo mode). Confirm the bed-manager and occupancy boards load normally with the existing "Grounding degraded" / simulated banners — no 401s.

- [ ] **Step 2: Sign in as `admin@`, switch to User mode**

Confirm the Role dropdown lists (a subset of) the 16 roles now assigned on both `ihzhhpf-app` and `hcc-agent-host`.

- [ ] **Step 3: Narrow to `HCC.DischargeCoordinator` and open the discharge board**

Confirm the worklist loads; inspect the network response for `/agents/dca/worklist` and confirm `recommendation.liveGroundingCitations` is present (either real rows or `[]` if the table doesn't exist yet in the SIT lakehouse — both are honest, expected outcomes per Task 5's graceful-miss design).

- [ ] **Step 4: Accept a recommendation on `dca`**

Click Accept on the discharge board's recommendation. Confirm the worklist observations shrink on refresh (existing behavior, unchanged) and `applied: true` in the response.

- [ ] **Step 5: Narrow to a role that maps to `ooa`, then to `HCC.BedManager` (maps to `bmca`)**

Confirm each worklist shows a real, non-placeholder recommendation (`lever_id` is `OOA-EXPEDITE-DISCHARGE` / `BMCA-REBALANCE-CENSUS`, not `null`) with a real `predicted_impact.value`. Accept one of each. Confirm the response shows `applied: false` and `applyReason: "actuation_not_modeled_for_lever"` — this is the expected, honest outcome (see Task 6), not a bug.

- [ ] **Step 6: Confirm the durable audit records for all three**

```bash
az cosmosdb sql container query --account-name cosmos-ihzhhpf-sit -g rg-ihzhhpf-sit -d agenthost -c approval-events --query-text "SELECT TOP 5 * FROM c ORDER BY c._ts DESC"
```

Expected: the most recent records show `dca`'s (`applied: true`), `ooa`'s and `bmca`'s (`applied: false`, `applyReason` set) decisions, each with `approver` equal to `admin@`'s real object id (not a header-supplied placeholder).

- [ ] **Step 7: Confirm CSA's tool-gate identity check (if a CSA tool call is reachable in this environment)**

Using a raw HTTP client with a valid `admin@` bearer, call `/agents/csa-agent/tools/{a-real-tool}` with `hitlEvidence` whose `approverObjectId` does **not** match `admin@`'s real oid. Confirm `403` with `reason: "approver_identity_not_verified"`. Repeat with the real oid and confirm the existing gate-evaluation behavior (allow/deny per evidence) is otherwise unchanged.

- [ ] **Step 8: Attempt to spoof a role (negative test)**

Using a raw HTTP client with a valid `admin@` bearer but `X-Active-Role: HCC.SomeRoleNotHeld` (or, more realistically, any role string not among the 16 assigned), confirm the request is refused with `403`.

- [ ] **Step 9: Update tracking issues**

Post the live evidence (screenshots/JSON from Steps 1-8) to issue #567. Close issue #569 with a comment linking to this plan's Task 1 as the superseding fix.

```bash
gh issue comment 567 --body "Live-verified: Demo mode unaffected, admin@ context-sensitive worklist + real citation + accept/deny (dca applied, ooa/bmca honestly tracked-not-applied) + durable Cosmos audit records with a verified approver oid + CSA tool-gate identity check. See [design doc] and [this plan]."
gh issue close 569 --comment "Superseded by docs/superpowers/plans/2026-08-09-obo-context-aware-role-agent-decision-loop.md Task 1 (bearer-presence fix) -- a smaller, more correct fix than the flag-split proposed here."
```

---

## Plan Self-Review Notes

- **Spec coverage:** Task 1 covers design §4 item 1+3 (bearer-presence fix, roles/hospital propagation). Task 2 covers item 3's validation half. Task 3 covers §7 item 3 (worklist/decisions bearer + verified approver). Task 4 covers §8.1's CSA tool-gate approver-identity gap. Task 5 covers §7 item 5 (live citation). Task 6 covers §7 item 6 (`ooa`/`bmca` wired into the Sprint 26 WS-B catalog). Task 7 covers §7 item 7 / §2's Cosmos-as-agent-memory framing (corrected to reflect already-deployed infra). Task 8 covers §7 item 8 (Entra role mirroring). Task 9 covers §7 item 9 (flag re-enable). Task 10 covers §7 items 10-11 (live verification across `dca`/`ooa`/`bmca`/CSA + issue updates). `product-owner-agent` (§8.2) is explicitly out of scope, tracked as issue #570.
- **Type consistency:** `OboContext.roles`/`.hospital` (Task 1) are consumed identically in Tasks 2-4 (`obo.roles`, `_require_active_role_held(obo, ...)`) — no signature drift across tasks. `ROLE_LEVERS` (Task 6) is consumed identically by `build_worklist` (`loop/worklist.py`) and `decide()` (`loop/decisions.py`) — same `RoleLever.lever_id`/`.has_effect` fields, no drift.
- **No new infra:** confirmed live (design doc §1.1) that the Cosmos account, database, all four containers, and RBAC already exist — Task 7 has zero Bicep changes, only Task 9 touches Bicep (one boolean flip). The `ooa`/`bmca` predicted-impact formulas (Task 6) are also pre-existing (Sprint 26 WS-B) — no new lever YAML, no new formula code, only the wiring in `loop/`.
- **Honesty preserved:** Task 6's `ooa`/`bmca` Accept path never claims a state mutation that didn't happen — `applied: false` + `applyReason: "actuation_not_modeled_for_lever"` is explicit in both the code and every relevant test, matching this repo's provenance discipline.

