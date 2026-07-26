"""WS-RT audit bundle: question -> chunks -> citations -> confidence -> caller.

Every answer is logged as one immutable bundle to the Cosmos audit store
(EAA-style, NFR-POA-002). The Cosmos client is injected so CI uses the
in-memory store and no external call is made. Bundles carry citations and
caller identity only - never secrets or PHI.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from typing import Any, Protocol


class AuditStore(Protocol):
    """Minimal write-only surface the audit bundle needs (Cosmos-shaped)."""

    def write(self, item: dict[str, Any]) -> None: ...


@dataclass
class InMemoryAuditStore:
    """Test/dev audit store; mirrors the Cosmos ``write`` surface."""

    items: list[dict[str, Any]] = field(default_factory=list)

    def write(self, item: dict[str, Any]) -> None:
        self.items.append(item)


def build_bundle(
    *,
    question: str,
    caller_identity: str,
    caller_tier: str,
    chunks: list[dict[str, Any]],
    confidence: float,
    status: str,
    language: str,
) -> dict[str, Any]:
    """Assemble the audit bundle. Records citations, not full chunk text-only."""

    citations = [
        {
            "classId": c.get("classId"),
            "sourceRef": c.get("citation", {}).get("sourceRef"),
            "anchor": c.get("citation", {}).get("anchor"),
            "conceptRef": c.get("citation", {}).get("conceptRef"),
            "goldBinding": c.get("citation", {}).get("goldBinding"),
            "confidence": c.get("confidence"),
            "status": c.get("status"),
        }
        for c in chunks
    ]
    return {
        "ts": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "question": question,
        "caller": {"identity": caller_identity, "tier": caller_tier},
        "citations": citations,
        "chunkCount": len(chunks),
        "confidence": confidence,
        "status": status,
        "language": language,
    }


def audit_log(store: AuditStore | None, bundle: dict[str, Any]) -> dict[str, Any]:
    """Write the bundle to the store (no-op if no store injected)."""

    if store is not None:
        store.write(bundle)
    return bundle
