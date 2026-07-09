#!/usr/bin/env python3
"""Sprint 16 T6 — seed the CSA `scenarios` Cosmos container.

Loads the 8 seeded scenarios from `data/csa/scenarios/*.yaml`, validates them
against `schema/scenarios.schema.json`, and — when Cosmos is configured — upserts
them into the `scenarios` container. The YAML files are the round-trip source of
truth; the `csa-scenario-sync.yml` workflow (T8) upserts on merge.

Dry run (no creds): validate + summary, exit 0.

    python3 data-platform/scripts/csa/csa-seed-scenarios.py --dry-run

Synthetic-only (ADR-0016). No PHI.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _cosmos import cosmos_configured, upsert_all
from _schema_util import load_schema, validate

REPO_ROOT = Path(__file__).resolve().parents[3]
SCENARIO_DIR = REPO_ROOT / "data" / "csa" / "scenarios"


def _require_yaml():
    try:
        import yaml  # type: ignore

        return yaml
    except ImportError as exc:  # pragma: no cover - exercised only without pyyaml
        raise RuntimeError(
            "PyYAML is required to load scenario YAML. `pip install pyyaml`."
        ) from exc


def build_scenarios() -> list[dict]:
    """Load and return the seeded scenario documents from YAML."""
    yaml = _require_yaml()
    scenarios: list[dict] = []
    for path in sorted(SCENARIO_DIR.glob("*.yaml")):
        with path.open(encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)
        if doc is None:
            raise ValueError(f"empty scenario file: {path.name}")
        scenarios.append(doc)
    return scenarios


def validate_all(scenarios: list[dict]) -> list[str]:
    schema = load_schema("scenarios")
    errors: list[str] = []
    for scenario in scenarios:
        sid = scenario.get("scenarioId", "<missing>")
        errors.extend(validate(scenario, schema, f"$[{sid}]"))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seed the CSA scenario catalogue.")
    parser.add_argument("--dry-run", action="store_true", help="Validate only; never upsert.")
    args = parser.parse_args(argv)

    scenarios = build_scenarios()
    if not scenarios:
        print(f"FAIL: no scenario YAML found under {SCENARIO_DIR}")
        return 1

    errors = validate_all(scenarios)
    if errors:
        print("FAIL: scenario validation errors:")
        for err in errors[:20]:
            print(f"  - {err}")
        return 1
    print(f"OK: loaded and validated {len(scenarios)} scenarios.")

    if args.dry_run or not cosmos_configured():
        print("Dry run — skipping Cosmos upsert (set CSA_COSMOS_ENDPOINT to seed).")
        return 0

    count = upsert_all("scenarios", scenarios)
    print(f"Upserted {count} scenarios into Cosmos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
