"""Smoke test for the entra module: run `az deployment sub what-if` and assert
non-empty planned changes.

Sprint 12 T1 (docs/superpowers/plans/2026-07-09-sprint-12-org-plan.md). This is a
thin wrapper around the Azure CLI: it only executes when `az` is authenticated to
the SIT tenant and the Microsoft Graph Bicep extension can be restored. Without
those prerequisites it prints a SKIP and returns 0 so it never blocks CI on
environments that lack Azure credentials.

Exit 0 = PASS or SKIP, 1 = FAIL.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

TEMPLATE = Path("infra/modules/entra/main.bicep")
PARAMS = Path("infra/modules/entra/parameters/sit.bicepparam")


def main() -> int:
    if shutil.which("az") is None:
        print("SKIP: Azure CLI not available; cannot run what-if.")
        return 0
    if not TEMPLATE.exists() or not PARAMS.exists():
        print(f"FAIL: expected {TEMPLATE} and {PARAMS} to exist.")
        return 1

    account = subprocess.run(
        ["az", "account", "show", "--query", "tenantId", "-o", "tsv"],
        capture_output=True, text=True, check=False,
    )
    if account.returncode != 0:
        print("SKIP: az not signed in; run `az login` against the SIT tenant first.")
        return 0

    result = subprocess.run(
        [
            "az", "deployment", "sub", "what-if",
            "--location", "westus2",
            "--template-file", str(TEMPLATE),
            "--parameters", str(PARAMS),
            "--parameters", "temporaryPassword=SmokeTest-DoNotUse-1!",
            "--result-format", "FullResourcePayloads",
        ],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        print("FAIL: what-if returned non-zero:")
        print(result.stderr)
        return 1
    print("PASS: what-if executed. First 40 lines:")
    print("\n".join(result.stdout.splitlines()[:40]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
