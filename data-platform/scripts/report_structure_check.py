"""Structure contract check for the capacity-dashboard v2 report (Power BI redesign M2–M6).

Asserts the design-spec §12 / plan Task-6 structure that `powerbi-report-author
validate` does not enforce on its own:

  - every required visible page and hidden helper page exists,
  - no page has an empty `visuals/` folder (design-spec §12 "no empty
    visualContainers"),
  - the RLS-proof pill (`dim_persona[Effective Viewing Label]`) is present on
    every visible page,
  - the field-parameter / grounding / benchmark tables are registered in the
    semantic model.

Exit code 0 when the contract holds, 1 otherwise.
"""
from __future__ import annotations

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORT = os.path.join(
    REPO_ROOT, "data-platform", "reports", "capacity-dashboard.Report", "definition"
)
PAGES = os.path.join(REPORT, "pages")
MODEL = os.path.join(
    REPO_ROOT,
    "data-platform",
    "reports",
    "capacity-dashboard.SemanticModel",
    "definition",
    "model.tmdl",
)

VISIBLE_PAGES = [
    "page-landing",
    "page-bed-manager",
    "page-or-coordinator",
    "page-ops-lead",
    "page-grounding",
]
HIDDEN_PAGES = [
    "tooltip-kpi-delta",
    "tooltip-contributor",
    "drill-ward",
    "drill-theatre",
    "drill-discharge",
    "page-perf-benchmark",
]
PILL_MEASURE = "Effective Viewing Label"
# Fully-qualified queryRef used by the RLS-proof pill visual. Narrower than
# the raw measure name — avoids false positives if another visual coincidentally
# contains the string "Effective Viewing Label" (title, comment, unrelated field).
PILL_QUERY_REF = "dim_persona.Effective Viewing Label"
REQUIRED_MODEL_TABLES = [
    "param_capacity_measure",
    "param_or_measure",
    "grounding",
    "benchmark",
]


def page_visual_files(page: str) -> list[str]:
    vdir = os.path.join(PAGES, page, "visuals")
    if not os.path.isdir(vdir):
        return []
    out = []
    for name in os.listdir(vdir):
        vjson = os.path.join(vdir, name, "visual.json")
        if os.path.isfile(vjson):
            out.append(vjson)
    return out


def page_has_pill(page: str) -> bool:
    """Return True iff any visual on `page` binds the `dim_persona[Effective Viewing Label]` measure.

    Uses a fully-qualified queryRef match (``dim_persona.Effective Viewing Label``)
    so a stray occurrence of the measure name in unrelated text — a title, a
    comment, another field's caption — does not falsely satisfy the RLS-proof
    contract.
    """
    for vjson in page_visual_files(page):
        try:
            with open(vjson, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if PILL_QUERY_REF in json.dumps(data):
            return True
    return False


def main() -> int:
    failures: list[str] = []

    for page in VISIBLE_PAGES + HIDDEN_PAGES:
        pdir = os.path.join(PAGES, page)
        if not os.path.isdir(pdir):
            failures.append(f"missing page: {page}")
            continue
        if not page_visual_files(page):
            failures.append(f"empty page (no visuals): {page}")

    for page in VISIBLE_PAGES:
        if os.path.isdir(os.path.join(PAGES, page)) and not page_has_pill(page):
            failures.append(f"RLS-proof pill missing on visible page: {page}")

    model_text = open(MODEL, encoding="utf-8").read() if os.path.isfile(MODEL) else ""
    for table in REQUIRED_MODEL_TABLES:
        if f"ref table {table}" not in model_text:
            failures.append(f"model.tmdl missing 'ref table {table}'")

    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        return 1

    print(
        f"PASS: {len(VISIBLE_PAGES)} visible + {len(HIDDEN_PAGES)} hidden pages, "
        f"all populated; RLS pill on every visible page; "
        f"{len(REQUIRED_MODEL_TABLES)} v2 tables registered."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
