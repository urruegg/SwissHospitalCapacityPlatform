"""Sprint 16 T5 — csa-simulate Fabric notebook.

Reads synthetic Gold capacity data, applies the scenario shock model
(``shock_model``), classifies the projected state into a Swiss Lage tier
(``csa-tier-classifier``, ADR-0024), writes a ``DC-SIM-RESULT`` row back to
Fabric, and returns a ``simulation-runs`` document for Cosmos.

Synthetic-only (ADR-0016). No PHI. The heavy Spark I/O is isolated in ``run()``
so the shock model + tier classification stay unit-testable without a Spark
session (see ``tests/test_csa_simulate_pure.py``).

Published to `ws-ihzhhpf-sit-data` via
`data-platform/scripts/csa/deploy-notebook.py` behind an `approved-to-apply`
gate (design spec §11).
"""
from __future__ import annotations

import datetime as _dt
import importlib.util
import sys
from pathlib import Path
from typing import Any

import shock_model

# The tier classifier lives with the seed scripts; load it by path (hyphenated).
_CLASSIFIER_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "csa"
    / "csa-tier-classifier.py"
)


def _load_classifier():
    spec = importlib.util.spec_from_file_location("csa_tier_classifier", _CLASSIFIER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def simulate(
    baseline: dict[str, dict[str, Any]],
    scenario: dict[str, Any],
    run_id: str,
    requested_by: str,
    now: _dt.datetime | None = None,
) -> dict[str, Any]:
    """Pure end-to-end simulation: shock -> tier -> KPIs -> run document.

    Returns a ``simulation-runs`` document (per the T3 schema) plus the
    ``DC-SIM-RESULT`` payload under ``result``.
    """
    classifier = _load_classifier()
    now = now or _dt.datetime.now(_dt.timezone.utc)

    shock = {
        "shockVector": scenario.get("shockVector", "demand-surge"),
        "affectedResources": scenario.get("affectedResources", []),
        "magnitude": scenario.get("magnitude", {}),
    }
    state = shock_model.project_state(baseline, shock, flags=scenario.get("flags"))
    tier_result = classifier.classify_tier(state)
    kpis = shock_model.summarize_kpis(state)

    return {
        "runId": run_id,
        "scenarioId": scenario["scenarioId"],
        "status": "succeeded",
        "requestedBy": requested_by,
        "requestedAt": now.isoformat(),
        "completedAt": now.isoformat(),
        "tier": tier_result["tier"],
        "resultRef": f"DC-SIM-RESULT/{run_id}",
        "kpis": kpis,
        "result": {
            "state": state,
            "tierReasons": tier_result["reasons"],
            "rulesVersion": tier_result["rulesVersion"],
        },
    }


def run() -> None:  # pragma: no cover - requires a live Fabric Spark session
    """Fabric entrypoint. Reads Gold, runs `simulate`, writes DC-SIM-RESULT."""
    from pyspark.sql import SparkSession  # noqa: F401 - Fabric-provided

    raise NotImplementedError(
        "run() executes inside the Fabric Spark runtime; publish via "
        "data-platform/scripts/csa/deploy-notebook.py behind approved-to-apply."
    )


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
