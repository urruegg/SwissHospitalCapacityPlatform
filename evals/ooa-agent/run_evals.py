"""Sprint 30 M3 — ooa-agent offline regression gate.

Thin entrypoint over the shared harness (`evals/lib/harness.py`): runs the six
seed evaluators over the v1 golden dataset and prints a per-evaluator report.
Exit 0 iff the regression gates pass. Run:

    python evals/ooa-agent/run_evals.py
"""

from __future__ import annotations

import sys
from pathlib import Path

EVALS_ROOT = Path(__file__).resolve().parents[1]
if str(EVALS_ROOT) not in sys.path:
    sys.path.insert(0, str(EVALS_ROOT))

from lib import harness  # noqa: E402

DATASET = Path(__file__).resolve().parent / "datasets" / "v1" / "interactions.jsonl"


def main() -> int:
    report = harness.run_dataset(DATASET)
    print(f"ooa-agent offline gate - {report['n']} interactions")
    for name, bucket in report["by_evaluator"].items():
        fails = len(bucket["failures"])
        print(f"  {name:22s} pass_rate={bucket['pass_rate']:.2%} failures={fails}")
    print(f"PASSED: {report['passed']}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
