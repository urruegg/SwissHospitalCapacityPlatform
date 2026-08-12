"""Sprint 44 live path (Slice 1) — gold.ext_fact_signal -> BoardSignal mapping.

Pure translation from Fabric Gold external-signal rows to the app's
``BoardSignal`` shape (``occupancy-data.ts``), so the golden surface can serve
live Event-Hub-fed signals to the OOA/CSA panels. Kept dependency-free and
offline-testable; the caller supplies rows from ``FabricDeltaClient.query``.
"""

from __future__ import annotations

import json
from typing import Any

# ext_source_id (or a substring) -> app SIGNAL_ICONS key. External sources default
# to the globe (web/authority) icon.
_SOURCE_ICONS: tuple[tuple[str, str], ...] = (
    ("webiq", "globe"),
    ("microsoft", "globe"),
    ("meteo", "weather"),
    ("bag", "pulse"),
    ("foph", "pulse"),
    ("sed", "seismic"),
    ("alert", "alert"),
)

# Severity (lower-cased) -> RAG status tone used by the signal panel.
_TONE_BY_SEVERITY: dict[str, str] = {
    "severe": "over", "high": "over", "extreme": "over", "critical": "over",
    "moderate": "watch", "elevated": "watch", "watch": "watch",
    "minor": "ok", "low": "ok", "nominal": "ok", "ok": "ok",
}


def _icon_for(source_id: str) -> str:
    sid = (source_id or "").lower()
    for needle, icon in _SOURCE_ICONS:
        if needle in sid:
            return icon
    return "globe"


def _tone_for(severity: str | None) -> str:
    return _TONE_BY_SEVERITY.get((severity or "").strip().lower(), "signal")


def _detail_for(fact: dict[str, Any]) -> str:
    parts = [fact.get("ext_hazard_type"), fact.get("ext_severity")]
    return " \u00b7 ".join(p for p in parts if p)


def _web_citations(value: Any) -> list[dict[str, Any]]:
    """Normalise ext_web_citations to a list of dicts (accepts a JSON string)."""
    if not value:
        return []
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (ValueError, TypeError):
            return []
    if not isinstance(value, list):
        return []
    return [c for c in value if isinstance(c, dict)]


def gold_rows_to_board_signals(
    fact_rows: list[dict[str, Any]],
    source_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Map ``gold.ext_fact_signal`` rows (+ ``gold.ext_dim_source``) to BoardSignals.

    ``source_rows`` supplies the trust tier + data mode (Live/Simulated) per
    ``ext_source_id``; a fact row with no matching source degrades to a
    simulated, trust-classless signal rather than being dropped.
    """
    sources = {r.get("ext_source_id"): r for r in source_rows}
    signals: list[dict[str, Any]] = []
    for fact in fact_rows:
        source_id = fact.get("ext_source_id")
        src = sources.get(source_id, {})
        signal: dict[str, Any] = {
            "id": fact.get("ext_signal_id") or source_id,
            "label": src.get("ext_source_authority") or source_id,
            "detail": _detail_for(fact),
            "iconKey": _icon_for(source_id),
            "scope": "external",
            "provenance": "live" if src.get("ext_data_mode") == "Live" else "simulated",
            "statusLabel": fact.get("ext_status") or (fact.get("ext_severity") or "").title(),
            "statusTone": _tone_for(fact.get("ext_severity")),
        }
        trust_tier = src.get("ext_trust_tier")
        if trust_tier:
            signal["trustClass"] = f"Trust-{trust_tier}"
        if fact.get("ext_hazard_type"):
            signal["hazardType"] = fact["ext_hazard_type"]
        cantons = list(fact.get("ext_cantons") or [])
        if cantons:
            signal["cantons"] = cantons
        citations = _web_citations(fact.get("ext_web_citations"))
        if citations:
            signal["webCitations"] = citations
        signals.append(signal)
    return signals
