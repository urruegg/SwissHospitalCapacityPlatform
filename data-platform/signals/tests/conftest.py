"""Pytest path wiring for signal package tests."""
from __future__ import annotations

import sys
from pathlib import Path

DATA_PLATFORM_DIR = Path(__file__).resolve().parents[2]
if str(DATA_PLATFORM_DIR) not in sys.path:
    sys.path.insert(0, str(DATA_PLATFORM_DIR))
