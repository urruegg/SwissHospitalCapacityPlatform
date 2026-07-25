"""Pytest bootstrap: put the liveproof module dir on sys.path.

Mirrors the WS-A corpus convention (and external-signals) so that
``import probes`` / ``import reconcile`` resolve without an installed
package.
"""

import sys
from pathlib import Path

LIVEPROOF_DIR = Path(__file__).resolve().parents[1]
if str(LIVEPROOF_DIR) not in sys.path:
    sys.path.insert(0, str(LIVEPROOF_DIR))
