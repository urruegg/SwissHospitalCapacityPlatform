"""Sprint 39 P2 - in-host operational closed loop (worklist + decisions).

Path bootstrap for LOCAL dev + tests: the operational loop reuses the
sim-capacity ``closedloop`` package and the decision-tier ``impact`` /
``coordination`` packages, which live in sibling source roots. Walk up to the
repo root (the ancestor that contains ``apps/sim-capacity/src``) and add the
reused roots to ``sys.path`` so ``closedloop.*`` / ``impact.*`` /
``coordination.*`` resolve without per-module bootstrapping.

In the container these packages are vendored onto the path by the Dockerfile
(``closedloop`` under ``src/``; ``data-platform/decision`` via ``PYTHONPATH``),
so the sibling repo roots are absent and this walk is a safe no-op. Robust to
path depth - it iterates ancestors and never indexes a fixed depth, so it cannot
IndexError in the shallower container layout (``/app/src/loop``).
"""
from __future__ import annotations

import sys
from pathlib import Path

for _anc in Path(__file__).resolve().parents:
    _sim_src = _anc / "apps" / "sim-capacity" / "src"
    if _sim_src.is_dir():
        for _p in (_sim_src, _anc / "data-platform" / "decision"):
            _s = str(_p)
            if _p.is_dir() and _s not in sys.path:
                sys.path.insert(0, _s)
        break
