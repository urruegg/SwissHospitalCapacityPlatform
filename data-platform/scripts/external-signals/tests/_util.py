"""Shared helpers for the external-signals test-suite (dependency-free)."""
from __future__ import annotations

import json
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def load_fixture(name: str) -> dict:
    """Load a raw source payload fixture by filename."""
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))
