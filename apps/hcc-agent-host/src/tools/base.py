"""Sprint 13 T5 — tool adapter contracts.

Each tool adapter wraps a real MCP-server-flavoured SDK behind a small, typed
surface so the orchestrator never improvises tool parameter shapes
(copilot-instructions §3 agentic patterns). Adapters declare their side-effect
ceiling so the host can refuse any call that exceeds an agent's manifest ceiling.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

CEILINGS = ("read", "write", "deploy", "delete")


@runtime_checkable
class ToolAdapter(Protocol):
    """Common shape for every tool adapter."""

    server: str
    ceiling: str

    def invoke(self, tool: str, params: dict[str, Any]) -> Any:
        """Invoke ``tool`` with ``params`` and return the tool result."""
        ...


def ceiling_exceeds(candidate: str, limit: str) -> bool:
    """True when ``candidate`` side-effect ceiling is higher than ``limit``."""
    return CEILINGS.index(candidate) > CEILINGS.index(limit)
