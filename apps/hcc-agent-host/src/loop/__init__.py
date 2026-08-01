"""Sprint 39 P2 — in-host operational closed loop (worklist + decisions).

Path bootstrap: the operational loop reuses the sim-capacity ``closedloop``
package and the decision-tier ``impact``/``coordination`` packages, which live
in sibling source roots. Add them to ``sys.path`` here so BOTH the runtime
(``api.app`` importing ``loop.*``) and the test suite resolve ``closedloop.*`` /
``impact.*`` / ``coordination.*`` without per-module bootstrapping.
"""
from __future__ import annotations

import sys
from pathlib import Path

# apps/hcc-agent-host/src/loop/__init__.py -> repo root is parents[4].
_ROOT = Path(__file__).resolve().parents[4]
for _p in (_ROOT / "apps" / "sim-capacity" / "src", _ROOT / "data-platform" / "decision"):
    _s = str(_p)
    if _s not in sys.path:
        sys.path.insert(0, _s)
