#!/usr/bin/env python3
"""Sprint 16 T5 — CSA tier classifier (Swiss Lage doctrine).

Rules layer over ontology capacity states. Classifies a projected capacity state
into the Swiss Lage tiers:

- Tier 1 — Normallage — within normal operating capacity.
- Tier 2 — Besondere Lage — one+ resource dimension breaches its threshold;
  internal reallocation required; single-site.
- Tier 3 — Ausserordentliche Lage — demand exceeds site capacity even after
  internal levers, OR a special capability is overwhelmed (burn ICU, ventilators,
  decontamination), OR the event is multi-canton / severe-consequence per
  VKSD Art. 2.

Rules are VERSION-PINNED. Any change requires an ADR reference
(see docs/adr/0024-csa-tier-classifier-rules.md). Do not edit thresholds without
bumping RULES_VERSION and citing a superseding ADR.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

# Version-pinned per ADR-0024. Bump only with a superseding ADR.
RULES_VERSION = "1.0.0"
RULES_ADR = "docs/adr/0024-csa-tier-classifier-rules.md"

# Utilization at/above which a resource dimension "breaches threshold" (Tier 2).
TIER2_UTILIZATION_THRESHOLD = 0.90

# Special capabilities whose exhaustion escalates straight to Tier 3.
SPECIAL_CAPABILITIES = frozenset(
    {"burn-beds", "ventilators", "decontamination", "isolation-beds"}
)


def classify_tier(state: dict[str, Any]) -> dict[str, Any]:
    """Classify a projected capacity state into a Lage tier.

    ``state`` shape::

        {
          "resources": {
            "<name>": {"utilization": float, "shortfall": int}
          },
          "flags": {
            "multiCanton": bool,
            "severeConsequence": bool,
            "capacityExceededAfterLevers": bool
          }
        }

    Returns ``{"tier": 1|2|3, "reasons": [...], "rulesVersion": ...}``.
    """
    resources = state.get("resources", {}) or {}
    flags = state.get("flags", {}) or {}
    reasons: list[str] = []

    # --- Tier 3 triggers (Ausserordentliche Lage) ---
    if flags.get("capacityExceededAfterLevers"):
        reasons.append("demand exceeds site capacity even after internal levers")
    if flags.get("multiCanton"):
        reasons.append("multi-canton event (VKSD Art. 2)")
    if flags.get("severeConsequence"):
        reasons.append("severe-consequence event (VKSD Art. 2)")
    for name, dim in resources.items():
        util = float(dim.get("utilization", 0.0))
        shortfall = int(dim.get("shortfall", 0))
        if name in SPECIAL_CAPABILITIES and (util > 1.0 or shortfall > 0):
            reasons.append(f"special capability overwhelmed: {name}")

    if reasons:
        return {"tier": 3, "reasons": reasons, "rulesVersion": RULES_VERSION}

    # --- Tier 2 triggers (Besondere Lage) ---
    for name, dim in resources.items():
        util = float(dim.get("utilization", 0.0))
        if util >= TIER2_UTILIZATION_THRESHOLD:
            reasons.append(
                f"{name} utilization {util:.0%} breaches threshold "
                f"{TIER2_UTILIZATION_THRESHOLD:.0%} — internal reallocation required"
            )

    if reasons:
        return {"tier": 2, "reasons": reasons, "rulesVersion": RULES_VERSION}

    # --- Tier 1 (Normallage) ---
    return {
        "tier": 1,
        "reasons": ["all resource dimensions within normal operating capacity"],
        "rulesVersion": RULES_VERSION,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classify a capacity state into a Lage tier.")
    parser.add_argument("--state", help="Path to a JSON state file. Reads stdin when omitted.")
    args = parser.parse_args(argv)

    if args.state:
        with open(args.state, encoding="utf-8") as fh:
            state = json.load(fh)
    else:
        state = json.load(sys.stdin)

    result = classify_tier(state)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
