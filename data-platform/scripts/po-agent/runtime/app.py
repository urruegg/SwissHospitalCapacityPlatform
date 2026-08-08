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
    answer degrades to a transparent refusal - never a fabricated one."""
    return {}


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
