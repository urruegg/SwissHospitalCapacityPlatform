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
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

import orchestrator
from authz import CallerContext
from env_contract import REQUIRED_ENV_VARS

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


class Caller(BaseModel):
    persona: str
    tier: str = "internal"


class AnswerRequest(BaseModel):
    question: str
    caller: Caller
    language: str = "en"


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
        from reconcile_bva import CostObservation, combined_run_rate, reconcile_bva

        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        cost_client = build_cost_client(subscription_id=subscription_id)
        copilot_client = build_copilot_client()
        repo_root = _PO_AGENT_ROOT.parents[2]

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
            return [reconcile_bva(observation, repo_root=repo_root)]

        tools["C"] = _class_c
    except Exception:
        pass

    return tools


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
