"""Slice 0 — Fabric Data Agent grounding adapter.

Wraps the read-only Fabric Data Agent (agents/fabric-data-agent/AGENT.md) as a
primary grounding source for agent-host copilots. The Data Agent resolves natural
language against the MVO ontology + Direct-Lake semantic model and enforces RLS +
ADR-0016 PHI gate-3, returning concept-level answers with hcp:* citations.

Read ceiling only. When no live client is injected (dev/CI) it returns a
deterministic synthetic grounded answer so the seam can be exercised end-to-end
without a live workspace. Synthetic-only, no PHI (ADR-0016).
"""

from __future__ import annotations

from typing import Any, Callable

# Substrings whose plausible use is cross-hospital re-identification / PHI.
_REFUSAL_TRIGGERS = (
    "patient name",
    "re-identif",
    "reidentif",
    "shared across",
    "date of birth",
)


class FabricDataAgentAdapter:
    server = "fabric-data-agent"
    ceiling = "read"

    def __init__(self, ask_fn: Callable[[str], dict[str, Any]] | None = None):
        # ``ask_fn`` is the live Fabric Data Agent client; absent → synthetic.
        self._ask_fn = ask_fn

    def ask(self, question: str) -> dict[str, Any]:
        """Return {"answer": str, "citations": list[str], "refused": bool}."""
        if self._ask_fn is not None:
            return self._ask_fn(question)
        lowered = question.lower()
        if any(trigger in lowered for trigger in _REFUSAL_TRIGGERS):
            return {
                "answer": "REFUSE: re-identification-risk",
                "citations": [],
                "refused": True,
            }
        return {
            "answer": (
                "Ward B at USZ has 46 of 50 CapacityUnit(Bed) instances occupied "
                "(synthetic grounding)."
            ),
            "citations": ["dim_ward_capacityunit", "hcp:CapacityUnit", "hcp:Bed"],
            "refused": False,
        }
