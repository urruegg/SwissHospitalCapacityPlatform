"""Sprint 13 T5 — deterministic mock Foundry chat model for dev/CI.

Returns a grounded, PHI-free answer derived from the injected grounding rows so
the host and the Copilot Drawer can be demonstrated end-to-end without a live
Foundry deployment (ADR-0013 westus2 demo scope; synthetic-only, ADR-0016).
"""

from __future__ import annotations

from typing import Any


class MockChatModel:
    def complete(
        self, system_prompt: str, user_prompt: str, grounding: list[dict[str, Any]]
    ) -> str:
        # Summarise ward occupancy from the grounding rows if present.
        occupied = next(
            (r for r in grounding if "occupied" in r and "capacity" in r), None
        )
        if occupied:
            pct = round(100 * occupied["occupied"] / max(occupied["capacity"], 1))
            return (
                f"Auslastung Station {occupied.get('ward', '?')} liegt bei {pct}%. "
                "Empfehlung: 2 Betten Richtung Notaufnahme umschichten. "
                "Aktion erfordert HITL-02-Freigabe."
            )
        return (
            "Keine Auslastungsdaten in der Grundierung gefunden. "
            "Bitte Fabric-Gold-Tabellen prüfen."
        )
