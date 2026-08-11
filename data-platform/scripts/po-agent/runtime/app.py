"""Sprint 41 WS-SVC/WS-RET: thin HTTP wrapper around the existing orchestrator.

No business logic lives here. This module only (1) parses the frozen
request shape, (2) calls the already-tested `orchestrator.answer()`, and
(3) maps its output onto the frontend's frozen `GroundedReco` TypeScript
shape. Real Class A-D tool wiring is injected via `get_tools()` (WS-RET):
each class's real client lives in its own sibling module
(corpus/liveproof/cost/ontology) and is wired in independently, so a
missing/misconfigured class degrades to a grounded refusal for that class
only, never a crashed request.
"""
from __future__ import annotations

import datetime as _dt
import os
import sys
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI
from pydantic import BaseModel

import orchestrator
from authz import CallerContext
from env_contract import REQUIRED_ENV_VARS  # noqa: F401 - proves env_contract is a real sibling module of app.py

app = FastAPI(title="po-agent-service", version="1.0.0")

_APP_DIR = Path(__file__).resolve().parent
_PO_AGENT_ROOT = _APP_DIR.parent
_CLASS_MODULE_DIRS = ("corpus", "liveproof", "cost", "ontology")


def _ensure_class_module_paths() -> None:
    """Put the Class A-D sibling modules on sys.path.

    The Dockerfile copies corpus/liveproof/cost/ontology flat next to
    app.py in the container image, but in the repo tree they live one
    level up (siblings of runtime/, not of app.py) - support both
    layouts so this works identically in dev/test and in the built image.
    """
    for base in (_APP_DIR, _PO_AGENT_ROOT):
        for name in _CLASS_MODULE_DIRS:
            candidate = base / name
            if candidate.is_dir():
                path_str = str(candidate)
                if path_str not in sys.path:
                    sys.path.insert(0, path_str)


def _resolve_repo_root() -> Path:
    """Resolve the repo root Class C needs for docs/BVA.md + master data.

    Dev tree: data-platform/scripts/po-agent/runtime/app.py -> repo root is
    three parents above po-agent/ (``_PO_AGENT_ROOT.parents[2]``).

    Container: docs/ and data/ are NOT part of the runtime image's normal
    Python source layout, so runtime/Dockerfile copies just the subset Class
    C needs (docs/BVA.md, data/master-data/bva/, data-platform/bva/) into
    ``/app/repo/`` -- detect and prefer that if present. Without this, the
    dev-tree formula resolves to ``Path("/").parents[2]`` in the container,
    which raises IndexError and silently disables Class C entirely (caught
    by the outer ``except Exception: pass`` in ``get_tools()``).
    """
    container_repo_root = _APP_DIR / "repo"
    if (container_repo_root / "docs" / "BVA.md").is_file():
        return container_repo_root
    return _PO_AGENT_ROOT.parents[2]


class Caller(BaseModel):
    persona: str
    tier: str = "internal"


class HospitalDelta(BaseModel):
    """New-hospital what-if inputs for `bva.simulate` (Sprint 44 follow-up)."""

    hospitalName: str
    archetype: str
    beds: int
    occupancyTarget: float
    onboardingScope: str


class PoVerdictInput(BaseModel):
    """A PO Agent verdict supplied by the caller -- never invented here.

    Per docs/data-platform/bva-po-fanout.md: "Verdict is an input, never
    invented." No caller (control-plane agent, human reviewer, or a future
    Opportunity lookup) means the composer degrades to an honest partial.
    """

    verdict: str
    rationale: str = ""
    citations: list[str] = []
    chunks: list[dict[str, Any]] = []


class AnswerRequest(BaseModel):
    question: str
    caller: Caller
    language: str = "en"
    hospitalDelta: Optional[HospitalDelta] = None
    poVerdict: Optional[PoVerdictInput] = None


def get_tools() -> dict[str, Any]:
    """Real Class A-D tools (WS-RET). Each class is wired independently
    and degrades on its own if unconfigured/unreachable: a missing key
    just means `orchestrator.answer()` skips that class (never crashes
    the whole request), matching the pre-WS-RET "empty means refusal,
    never fabrication" doctrine this function used to implement wholesale.
    """
    _ensure_class_module_paths()
    tools: dict[str, Any] = {}

    try:
        from search_client import build_production_client as build_search_client, query_corpus

        search_client = build_search_client()
        tools["A"] = lambda q: query_corpus(q, client=search_client)
    except Exception:
        pass

    try:
        from data_agent import build_production_client as build_data_agent_client, ontologyQuery

        data_agent_client = build_data_agent_client()
        tools["D"] = lambda q: ontologyQuery(q, data_agent_client=data_agent_client)
    except Exception:
        pass

    try:
        from azure_clients import build_production_clients
        from probes import liveProof

        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        live_clients = build_production_clients(subscription_id=subscription_id)
        tools["B"] = lambda q: liveProof(q, subscription_id, clients=live_clients)
    except Exception:
        pass

    try:
        from azure_cost import build_production_client as build_cost_client, get_effective_prod_cost
        from copilot_cost import build_production_client as build_copilot_client, get_copilot_cost
        from reconcile_bva import (
            CostObservation,
            build_cost_evidence_chunk,
            combined_run_rate,
            reconcile_bva,
        )

        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        cost_client = build_cost_client(subscription_id=subscription_id)
        copilot_client = build_copilot_client()
        repo_root = _resolve_repo_root()

        def _class_c(q: str) -> list[dict[str, Any]]:
            window_end = _dt.date.today()
            window_start = window_end - _dt.timedelta(days=30)
            start, end = window_start.isoformat(), window_end.isoformat()
            try:
                azure_amount = get_effective_prod_cost(
                    cost_client, cost_client.default_scope, start, end
                ).amount
                copilot_amount = get_copilot_cost(copilot_client, start, end).amount
                # docs/BVA.md's documented USD->CHF rate (figures are all CHF).
                observation = combined_run_rate(
                    azure_amount, copilot_amount * 0.88, "CHF", start, end, end
                )
            except Exception:  # any live feed failure degrades to snapshot, never raises
                observation = CostObservation(
                    amount=0.0,
                    currency="CHF",
                    window_start=start,
                    window_end=end,
                    feed="Azure Cost Management + GitHub Copilot usage",
                    as_of=end,
                    ok=False,
                )
            chunks = [reconcile_bva(observation, repo_root=repo_root)]
            try:
                # BVA evidence & narrative master data (Sprint 44 task b): the
                # measured showcase build-cost total, additive to the live
                # run-rate reconciliation above. Its own try/except so a
                # missing/stale evidence file degrades this one chunk only.
                chunks.append(build_cost_evidence_chunk(repo_root))
            except Exception:
                pass
            return chunks

        tools["C"] = _class_c
    except Exception:
        pass

    return tools


def _bva_simulate_module():
    """Import `bva.simulate`/`bva.models` relative to `_resolve_repo_root()`.

    Unlike `evidence_grounding.py` (stdlib-only, loaded by file path in
    `reconcile_bva.py`), `simulate.py` relies on sibling-relative imports
    (`.archetypes`, `.models`) -- it needs its package context, so this adds
    `data-platform` to sys.path rather than loading by bare file path. Works
    in both dev tree and container because runtime/Dockerfile copies the
    *whole* `data-platform/bva/` package into `/app/repo/data-platform/bva/`.
    """
    import sys

    data_platform_dir = str(_resolve_repo_root() / "data-platform")
    if data_platform_dir not in sys.path:
        sys.path.insert(0, data_platform_dir)
    from bva.models import BvaBaseline, HospitalDelta as BvaHospitalDelta  # noqa: PLC0415
    from bva.simulate import simulate  # noqa: PLC0415

    return simulate, BvaBaseline, BvaHospitalDelta


def _bva_what_if_answer(req: AnswerRequest, caller: CallerContext) -> dict[str, Any]:
    """Hospital-delta what-if path (Sprint 44 bva_fanout follow-up).

    Only engaged when the caller supplies `hospitalDelta` - existing callers
    (no hospitalDelta) are entirely unaffected, still routed through
    `orchestrator.answer()`'s Class A-D grounding below. `financial` and
    `strategic` questions cite the live `bva.simulate()` numbers through the
    standard grounded-answer contract (citation gate, threshold, DE/EN,
    audit); `onboarding` questions compose verdict-first via `bva_fanout`,
    which degrades to an honest partial when no `poVerdict` is supplied
    (never fabricates one - see `PoVerdictInput`'s docstring).
    """
    import bva_fanout  # noqa: PLC0415

    delta = req.hospitalDelta
    assert delta is not None  # only called when hospitalDelta is present

    try:
        simulate, BvaBaseline, BvaHospitalDelta = _bva_simulate_module()
        bva_result = simulate(
            BvaBaseline.rom_default(),
            BvaHospitalDelta(
                hospital_name=delta.hospitalName,
                archetype=delta.archetype,
                beds=delta.beds,
                occupancy_target=delta.occupancyTarget,
                onboarding_scope=delta.onboardingScope,
            ),
            language=req.language,
        )
    except Exception:  # invalid delta or missing module degrades, never crashes
        bva_result = {"chunks": []}

    intent = bva_fanout.classify_intent(req.question)

    if intent == "onboarding":
        po_verdict = req.poVerdict.model_dump() if req.poVerdict is not None else None
        composed = bva_fanout.compose_onboarding_answer(
            req.question, bva_result, po_verdict, caller, audit_store=None
        )
        return {
            "agentLabel": "product-owner-agent",
            "contextChip": {"subject": req.caller.persona, "tone": "signal"},
            "read": composed["answer"],
            "levers": [],
            "citations": composed.get("citations", []),
            "provenance": "live",
            "refused": not composed.get("chunks"),
        }

    # financial / strategic: cite the BVA chunks as Class C through the
    # standard grounded-answer contract, alongside whatever A/B/D tools are
    # otherwise available.
    tools = get_tools()
    tools["C"] = lambda q: bva_fanout.bva_chunks_from_result(bva_result)
    result = orchestrator.answer(req.question, caller, tools=tools)
    citations = [
        c["citation"]["sourceRef"]
        for c in result.get("chunks", [])
        if c.get("citation", {}).get("sourceRef")
    ]
    return {
        "agentLabel": "product-owner-agent",
        "contextChip": {"subject": req.caller.persona, "tone": "signal"},
        "read": result["answer"],
        "levers": [],
        "citations": citations,
        "provenance": "live",
        "refused": not result.get("chunks"),
    }


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/answer")
def answer(req: AnswerRequest) -> dict[str, Any]:
    # HTTP contract calls the caller field "persona"; authz/orchestrator
    # call the same concept "identity" - map it at this boundary only.
    caller = CallerContext(
        identity=req.caller.persona, tier=req.caller.tier, language=req.language
    )

    if req.hospitalDelta is not None:
        return _bva_what_if_answer(req, caller)

    result = orchestrator.answer(req.question, caller, tools=get_tools())
    citations = [
        c["citation"]["sourceRef"]
        for c in result.get("chunks", [])
        if c.get("citation", {}).get("sourceRef")
    ]
    return {
        "agentLabel": "product-owner-agent",
        "contextChip": {"subject": req.caller.persona, "tone": "signal"},
        "read": result["answer"],
        "levers": [],
        "citations": citations,
        "provenance": "live",
        # orchestrator's `status` field is overloaded (also "partial" for a
        # synthesised-but-mixed-status answer), so refusal is derived from
        # the grounded-answer contract directly: no usable chunks means the
        # grounded-refusal path was taken (orchestrator's min_chunks default
        # is 1, unmodified by this wrapper).
        "refused": not result.get("chunks"),
    }
