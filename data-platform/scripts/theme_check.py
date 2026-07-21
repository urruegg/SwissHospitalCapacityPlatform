"""Ensure the Curavias theme JSON contains the required Brandkit tokens.

Regression test for the Power BI Demoable Redesign (M1). Asserts the Curavias
Power BI theme carries every brand data colour from the design spec §8 mapping.

Exit 0 = PASS, 1 = FAIL (missing token or absent file).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

THEME_PATH = Path(
    "data-platform/reports/capacity-dashboard.Report/themes/curavias.json"
)

REQUIRED_DATA_COLORS = [
    "#E30613",  # Curavias Red
    "#365B7D",  # Curavias Blue
    "#FF9A2E",  # Rainbow warm tip
    "#FF5A4E",
    "#F0398F",
    "#9A4FF0",
    "#3E7BF6",
    "#23C57E",  # Rainbow cool base
]


def main() -> int:
    if not THEME_PATH.exists():
        print(f"FAIL: {THEME_PATH} not found")
        return 1
    theme = json.loads(THEME_PATH.read_text(encoding="utf-8"))
    data_colors = theme.get("dataColors", [])
    missing = [c for c in REQUIRED_DATA_COLORS if c not in data_colors]
    if missing:
        print(f"FAIL: missing dataColors {missing}")
        return 1
    if theme.get("name") != "Curavias":
        print(f"FAIL: theme name is {theme.get('name')!r}, expected 'Curavias'")
        return 1
    print("PASS: Curavias theme contains all required dataColors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
