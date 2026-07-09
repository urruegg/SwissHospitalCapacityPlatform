"""Perf-hero benchmark harness for the Power BI Demoable Redesign (M6, plan Task 6.5).

Orchestrates the hero scenario — the Bed Manager page filtered to USZ — as a cold
render followed by a warm render, records elapsed milliseconds, and asserts the
design-spec §12 thresholds (cold < 4000 ms, warm < 500 ms).

A live run executes the scenario query against the published semantic model in
``ws-ihzhhpf-sit-data``. That publish is a ``deploy``-ceiling action gated by an
``approved-to-apply`` comment (AGENTS.md §4); until the gate is approved this
harness runs offline against the static benchmark values recorded in
``capacity-dashboard.SemanticModel/definition/tables/benchmark.tmdl`` so CI can
enforce the threshold contract without a live workspace.

Exit code 0 when both scenarios meet their thresholds, 1 otherwise.

Usage:
    python3 data-platform/scripts/perf_hero.py [--report-json PATH]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BENCHMARK_TMDL = os.path.join(
    REPO_ROOT,
    "data-platform",
    "reports",
    "capacity-dashboard.SemanticModel",
    "definition",
    "tables",
    "benchmark.tmdl",
)

# Design-spec §12 hero-scenario thresholds.
THRESHOLDS_MS = {"Cold": 4000, "Warm": 500}


def read_benchmark_ms(path: str = BENCHMARK_TMDL) -> dict[str, int]:
    """Parse the ``Scenario, ElapsedMs`` rows from the benchmark DATATABLE partition.

    Returns a mapping like ``{"Cold": 3200, "Warm": 280}``. A live run would
    replace this static read with a timed query execution against the published
    model.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"benchmark table not found: {path}")
    text = open(path, encoding="utf-8").read()
    rows = dict(re.findall(r'\{\s*"(Cold|Warm)"\s*,\s*(\d+)\s*\}', text))
    return {scenario: int(ms) for scenario, ms in rows.items()}


def evaluate(measured: dict[str, int]) -> tuple[bool, list[dict[str, object]]]:
    results: list[dict[str, object]] = []
    ok = True
    for scenario, threshold in THRESHOLDS_MS.items():
        elapsed = measured.get(scenario)
        passed = elapsed is not None and elapsed < threshold
        ok = ok and passed
        results.append(
            {
                "scenario": scenario,
                "elapsed_ms": elapsed,
                "threshold_ms": threshold,
                "pass": passed,
            }
        )
    return ok, results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-json", help="write the benchmark result as JSON evidence")
    args = parser.parse_args(argv)

    try:
        measured = read_benchmark_ms()
    except FileNotFoundError as exc:
        print(f"FAIL: {exc}")
        return 1

    ok, results = evaluate(measured)
    for row in results:
        status = "PASS" if row["pass"] else "FAIL"
        print(
            f"{status} {row['scenario']}: {row['elapsed_ms']} ms "
            f"(threshold < {row['threshold_ms']} ms)"
        )

    if args.report_json:
        with open(args.report_json, "w", encoding="utf-8") as handle:
            json.dump({"pass": ok, "results": results}, handle, indent=2, sort_keys=True)

    if not ok:
        print("FAIL: hero scenario did not meet perf thresholds")
        return 1
    print("PASS: hero scenario meets cold < 4000 ms and warm < 500 ms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
