"""Sprint 31 DQA -- deterministic loader for the trust-score weights/thresholds.

This module is the read side of the versioned ``trustscore-weights.json`` source
of truth ratified by ``docs/adr/0053-dqa-trust-score-model.md``. It is PURE and
stdlib-only: it parses a git-tracked JSON file resolved relative to ``__file__``
(never the CWD), so the same call always returns the same dict regardless of
where the process runs. No randomness, no network, no clock, no LLM estimate --
mirroring the determinism guarantees of ``trust_score.py``.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from quality.trust_score import DIMENSIONS

_CONFIG_PATH = Path(__file__).with_name("trustscore-weights.json")
_DEFAULT = "default"


def _load() -> dict:
    with _CONFIG_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def config_model_version() -> str:
    """Return the ``modelVersion`` recorded in the config (e.g. ``trustscore-v1``)."""
    return str(_load()["modelVersion"])


def load_profile(decision_class: Optional[str] = None) -> Dict[str, float]:
    """Return the weight vector for ``decision_class`` (falls back to ``default``).

    The returned dict covers every dimension in :data:`DIMENSIONS`; values are
    relative weights that :func:`quality.trust_score.trust_score` normalizes.
    """
    profiles = _load()["profiles"]
    raw = profiles.get(decision_class or _DEFAULT, profiles[_DEFAULT])
    profile = {dim: float(raw[dim]) for dim in DIMENSIONS}
    if any(v <= 0 for v in profile.values()):
        raise ValueError(f"profile {decision_class!r} has a non-positive weight")
    return profile


def load_thresholds(decision_class: Optional[str] = None) -> Dict[str, object]:
    """Return ``{"overall": float, "gating": {dim: float}}`` for ``decision_class``.

    Falls back to the ``default`` profile for an unknown or ``None`` class. Used
    by the (separate-slice) grounding-readiness gate; not wired into a gate here.
    """
    thresholds = _load()["thresholds"]
    raw = thresholds.get(decision_class or _DEFAULT, thresholds[_DEFAULT])
    return {
        "overall": float(raw["overall"]),
        "gating": {dim: float(val) for dim, val in raw["gating"].items()},
    }
