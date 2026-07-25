"""Pytest bootstrap: put the cost module dir on sys.path."""

import sys
from pathlib import Path

COST_DIR = Path(__file__).resolve().parents[1]
if str(COST_DIR) not in sys.path:
    sys.path.insert(0, str(COST_DIR))
