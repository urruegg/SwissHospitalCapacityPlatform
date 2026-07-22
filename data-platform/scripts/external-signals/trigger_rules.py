"""Evaluate TriggerRule gates + arbitrate overlapping hazard events."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_RULES_PATH = Path(__file__).resolve().parent / "trigger_rules.yaml"
_DEFAULTS = {
    "gate": {"min_severity": "Severe", "min_danger_level": 3,
             "required_status": "Actual", "required_trust_tier": "A"},
    "severity_rank": {"Minor": 1, "Moderate": 2, "Severe": 3, "Extreme": 4},
    "arbitration": {"order": ["lage_tier", "severity", "certainty"]},
}
_CERTAINTY_RANK = {"Unlikely": 1, "Possible": 2, "Likely": 3, "Observed": 4}


@dataclass
class Result:
    fired: bool
    outcome: str


def load_rules() -> dict:
    try:
        import yaml
        return yaml.safe_load(_RULES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return _DEFAULTS


def evaluate(event: dict, rules: dict) -> Result:
    g = rules["gate"]
    rank = rules["severity_rank"]
    if event.get("status") != g["required_status"]:
        return Result(False, "quarantined-status")
    if event.get("trustTier", "A") != g["required_trust_tier"]:
        return Result(False, "trust-tier-not-a")
    if rank.get(event.get("severity"), 0) < rank.get(g["min_severity"], 3):
        return Result(False, "evaluated-no-trigger")
    dl = event.get("dangerLevel")
    if dl is not None and dl < g["min_danger_level"]:
        return Result(False, "evaluated-no-trigger")
    return Result(True, "trigger-fired")


def arbitrate(events: list[dict]) -> tuple[dict, list[dict]]:
    def key(e):
        return (e.get("defaultLageTier") or 0,
                _DEFAULTS["severity_rank"].get(e.get("severity"), 0),
                _CERTAINTY_RANK.get(e.get("certainty"), 0))
    ordered = sorted(events, key=key, reverse=True)
    return ordered[0], ordered[1:]
