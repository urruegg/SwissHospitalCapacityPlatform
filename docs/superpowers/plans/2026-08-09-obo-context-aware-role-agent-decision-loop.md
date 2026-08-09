# OBO Context-Aware Role-Agent Decision Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make OBO the standard, always-preferred auth pattern end to end: fix the bearer-presence bug that broke Demo mode, mirror real Entra App Roles onto the backend so role/hospital context is server-verified (not just client-claimed), let a role agent's worklist recommendation carry a real Fabric citation when OBO is present, and make an Accept/Deny decision produce a durably persisted, identity-verified audit record.

**Architecture:** Small, independent, dependency-injection-testable changes to `apps/hcc-agent-host/src/auth/obo_context.py`, `api/app.py`, `loop/worklist.py`, and `persistence/cosmos_client.py`, plus one Entra IAM change (mirror App Roles, gated by `approved-to-apply`) and one one-line Bicep flip. No new infrastructure is required — the Cosmos account, database, `approval-events` container, and managed-identity RBAC already exist live in SIT (confirmed via `az cosmosdb` during the design brainstorm).

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

### Task 4: Live grounding citation in `build_worklist`

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

### Task 5: Live, config-gated Cosmos persistence for the decisions audit trail

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

### Task 6: Entra — mirror App Roles + `admin@`'s assignments onto `hcc-agent-host`

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

- [ ] **Step 5: Assign `admin@` the same roles already held on `ihzhhpf-app` (requires `approved-to-apply`)**

```bash
$spId = az ad sp show --id b7608e39-e23a-4576-8489-e092ba5f726b --query id -o tsv
$userId = az ad user show --id admin@mngenvmcap164444.onmicrosoft.com --query id -o tsv
$roleIds = az ad app show --id b7608e39-e23a-4576-8489-e092ba5f726b --query "appRoles[].id" -o tsv
foreach ($roleId in $roleIds) {
  az rest --method POST `
    --uri "https://graph.microsoft.com/v1.0/servicePrincipals/$spId/appRoleAssignedTo" `
    --body "{`"principalId`":`"$userId`",`"resourceId`":`"$spId`",`"appRoleId`":`"$roleId`"}"
}
```

- [ ] **Step 6: Verify the assignments landed**

```bash
az rest --method GET --uri "https://graph.microsoft.com/v1.0/users/admin@mngenvmcap164444.onmicrosoft.com/appRoleAssignments" -o json |
  ConvertFrom-Json | Select-Object -ExpandProperty value |
  Where-Object { $_.resourceDisplayName -eq "hcc-agent-host" } |
  Select-Object principalDisplayName, appRoleId
```

Expected: one row per assigned role (matching the 16-ish held on `ihzhhpf-app`, excluding whichever single role was never assigned there).

- [ ] **Step 7: No commit needed** (Entra-only change; no repo files changed). Note the change in the PR description under "Security impact" per the repo's PR Output Contract.

---

### Task 7: Bicep — re-enable `agentHostOboEnabled`

**Files:**
- Modify: `infra/environments/sit.bicepparam`

**Prerequisite:** Tasks 1-6 merged and deployed (the image must contain the Task 1-5 code fixes before this flag is safe to flip — re-enabling it before Task 1's fix is what caused the earlier incident).

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

- [ ] **Step 4: Push, wait for image build (if a new image is needed for Tasks 1-5), approve the SIT deploy, and confirm**

```bash
git push origin main
```

Approve the `ci-build-agent-host.yml` and `cd-infra-deploy-sit.yml` environment gates as usual (see repo memory for the `gh api ... pending_deployments` approval command). After deploy:

```bash
az containerapp show -n ca-agent-host-ihzhhpf-sit -g rg-ihzhhpf-sit --query "properties.template.containers[0].env[?name=='OBO_ENABLED']" -o json
```

Expected: `OBO_ENABLED: true`.

---

### Task 8: Live verification

**No code changes — manual/browser verification.**

- [ ] **Step 1: Confirm Demo mode is unaffected**

In a browser, load `https://appsit.curavias.ch` without signing in (Demo mode). Confirm the bed-manager and occupancy boards load normally with the existing "Grounding degraded" / simulated banners — no 401s.

- [ ] **Step 2: Sign in as `admin@`, switch to User mode**

Confirm the Role dropdown lists (a subset of) the 16 roles now assigned on both `ihzhhpf-app` and `hcc-agent-host`.

- [ ] **Step 3: Narrow to `HCC.DischargeCoordinator` and open the discharge board**

Confirm the worklist loads; inspect the network response for `/agents/dca/worklist` and confirm `recommendation.liveGroundingCitations` is present (either real rows or `[]` if the table doesn't exist yet in the SIT lakehouse — both are honest, expected outcomes per Task 4's graceful-miss design).

- [ ] **Step 4: Accept a recommendation**

Click Accept on the discharge board's recommendation. Confirm the worklist observations shrink on refresh (existing behavior, unchanged).

- [ ] **Step 5: Confirm the durable audit record**

```bash
az cosmosdb sql container query --account-name cosmos-ihzhhpf-sit -g rg-ihzhhpf-sit -d agenthost -c approval-events --query-text "SELECT TOP 1 * FROM c ORDER BY c._ts DESC"
```

Expected: the most recent record shows `decision: "accept"`, `approver` equal to `admin@`'s real object id (not a header-supplied placeholder), and `applied: true`.

- [ ] **Step 6: Attempt to spoof a role (negative test)**

Using a raw HTTP client with a valid `admin@` bearer but `X-Active-Role: HCC.SomeRoleNotHeld` (or, more realistically, any role string not among the 16 assigned), confirm the request is refused with `403`.

- [ ] **Step 7: Update tracking issues**

Post the live evidence (screenshots/JSON from Steps 1-6) to issue #567. Close issue #569 with a comment linking to this plan's Task 1 as the superseding fix.

```bash
gh issue comment 567 --body "Live-verified: Demo mode unaffected, admin@ context-sensitive worklist + real citation + accept/deny + durable Cosmos audit record with a verified approver oid. See [design doc] and [this plan]."
gh issue close 569 --comment "Superseded by docs/superpowers/plans/2026-08-09-obo-context-aware-role-agent-decision-loop.md Task 1 (bearer-presence fix) -- a smaller, more correct fix than the flag-split proposed here."
```

---

## Plan Self-Review Notes

- **Spec coverage:** Task 1 covers design §4 item 1+3 (bearer-presence fix, roles/hospital propagation). Task 2 covers item 3's validation half. Task 3 covers item 4 (worklist/decisions bearer + verified approver). Task 4 covers item 5 (live citation). Task 5 covers item 6 (Cosmos persistence — corrected to reflect already-deployed infra). Task 6 covers item 2 (Entra role mirroring). Task 7 covers item 7 (flag re-enable). Task 8 covers design §7 step 8-9 (live verification + issue updates).
- **Type consistency:** `OboContext.roles`/`.hospital` (Task 1) are consumed identically in Tasks 2-4 (`obo.roles`, `_require_active_role_held(obo, ...)`) — no signature drift across tasks.
- **No new infra:** confirmed live (design doc §1.1) that the Cosmos account, database, `approval-events` container, and RBAC already exist — Task 5 has zero Bicep changes, only Task 7 touches Bicep (one boolean flip).
