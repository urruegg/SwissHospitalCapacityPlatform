"""Sprint 13 T5 — GitHub tool adapter (write ceiling).

Wraps the ``github-mcp`` tools an agent may call (issues, comments, branches,
files). Write ceiling. A live callable is injected at runtime; without one the
adapter records calls in-memory so tests can assert intent without side effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class RecordedCall:
    tool: str
    params: dict[str, Any]


class GithubAdapter:
    server = "github-mcp"
    ceiling = "write"

    _ALLOWED_TOOLS = {
        "get-issue",
        "add-issue-comment",
        "create-branch",
        "create-or-update-file",
    }

    def __init__(self, call_fn: Callable[[str, dict[str, Any]], Any] | None = None):
        self._call_fn = call_fn
        self.calls: list[RecordedCall] = []

    def invoke(self, tool: str, params: dict[str, Any]) -> Any:
        if tool not in self._ALLOWED_TOOLS:
            raise ValueError(f"github-mcp adapter does not expose tool '{tool}'")
        self.calls.append(RecordedCall(tool, params))
        if self._call_fn is not None:
            return self._call_fn(tool, params)
        return {"ok": True, "tool": tool}
