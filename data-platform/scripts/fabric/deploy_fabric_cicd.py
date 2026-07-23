#!/usr/bin/env python
"""Fabric IQ release train — parameterized fabric-cicd deploy.

Deploys the ``capacity-dashboard`` semantic model (+ report) into the Fabric
workspace of a chosen environment (SIT / PROD), rewriting the Direct Lake
OneLake path via ``data-platform/reports/parameter.yml`` so the same source
tree targets a different region/workspace by changing ``--environment`` only
(readiness design D5/D7; ADR-0035).

Two modes:

* ``--mode validate`` (default) — **network-free** static checks: the variable
  library and the fabric-cicd parameter file agree, every ``find_value`` is
  present in the semantic-model TMDL, and the deployable items exist on disk.
  Safe for a CI PR gate; needs only PyYAML.
* ``--mode publish`` — live deploy via ``fabric-cicd`` (needs an Azure token
  with access to the target Fabric workspace). Excludes the unrelated
  ``evidence`` / ``bva-boardroom`` items from this workspace.

Usage::

    python deploy_fabric_cicd.py --environment PROD --mode validate
    python deploy_fabric_cicd.py --environment PROD --mode publish
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

# Repo layout anchors (this file lives in data-platform/scripts/fabric/).
REPO_ROOT = Path(__file__).resolve().parents[3]
REPORTS_DIR = REPO_ROOT / "data-platform" / "reports"
ENVIRONMENTS_FILE = REPO_ROOT / "data-platform" / "fabric" / "environments.yml"
PARAMETER_FILE = REPORTS_DIR / "parameter.yml"
SEMANTIC_MODEL = "capacity-dashboard.SemanticModel"
EXPRESSIONS_TMDL = REPORTS_DIR / SEMANTIC_MODEL / "definition" / "expressions.tmdl"

# Item types the release train owns in this workspace.
ITEM_TYPE_IN_SCOPE = ["SemanticModel", "Report"]
# Items in data-platform/reports/ that belong to OTHER products, excluded here.
EXCLUDE_ITEM_NAME_REGEX = r"^(evidence|bva-boardroom)$"
# Items this train deploys (used for the validate-mode disk check + plan output).
DEPLOYABLE_ITEMS = [
    "capacity-dashboard.SemanticModel",
    "capacity-dashboard.Report",
    "external-signals.SemanticModel",
]


def _load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _environments() -> dict:
    data = _load_yaml(ENVIRONMENTS_FILE)
    envs = data.get("environments") or {}
    if not envs:
        raise SystemExit(f"No environments defined in {ENVIRONMENTS_FILE}")
    return envs


def validate(environment: str) -> None:
    """Network-free consistency + presence checks. Raises SystemExit on failure."""
    problems: list[str] = []
    envs = _environments()

    if environment not in envs:
        raise SystemExit(f"Unknown environment '{environment}'. Known: {sorted(envs)}")

    env = envs[environment]
    for key in ("workspace_id", "lakehouse_id", "workspace_name", "region"):
        if not env.get(key):
            problems.append(f"environments.yml[{environment}] missing '{key}'")

    # fabric-cicd parameter file must agree with the variable library.
    params = _load_yaml(PARAMETER_FILE)
    find_replace = params.get("find_replace") or []
    if not find_replace:
        problems.append(f"{PARAMETER_FILE} has no find_replace entries")

    # Map each parameter to the env id it should resolve to, for cross-checking.
    sit_ws = envs.get("SIT", {}).get("workspace_id")
    sit_lh = envs.get("SIT", {}).get("lakehouse_id")
    target_ws = env.get("workspace_id")
    target_lh = env.get("lakehouse_id")
    expected = {sit_ws: target_ws, sit_lh: target_lh}

    for entry in find_replace:
        find_value = entry.get("find_value")
        replace = entry.get("replace_value") or {}
        item_name = entry.get("item_name")
        tmdl_path = REPORTS_DIR / f"{item_name}.SemanticModel" / "definition" / "expressions.tmdl"

        # The find_value is the SIT-pinned coordinate; it must exist in the TMDL.
        if not tmdl_path.exists():
            problems.append(f"Missing Direct Lake TMDL for item '{item_name}': {tmdl_path}")
        else:
            tmdl_text = tmdl_path.read_text(encoding="utf-8")
            if find_value not in tmdl_text:
                problems.append(f"find_value '{find_value}' not present in {tmdl_path}")
        # SIT replacement must be identity (repo is SIT-pinned).
        if replace.get("SIT") != find_value:
            problems.append(
                f"parameter '{find_value}': replace_value.SIT must equal find_value (repo is SIT-pinned)"
            )
        # The target-environment replacement must match the variable library.
        if find_value in expected and expected[find_value] is not None:
            if replace.get(environment) != expected[find_value]:
                problems.append(
                    f"parameter '{find_value}': replace_value.{environment} "
                    f"'{replace.get(environment)}' != environments.yml id '{expected[find_value]}'"
                )

    # Deployable item folders must exist with a .platform marker.
    for item in DEPLOYABLE_ITEMS:
        marker = REPORTS_DIR / item / ".platform"
        if not marker.exists():
            problems.append(f"Deployable item missing .platform: {marker}")

    if problems:
        print("VALIDATION FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        raise SystemExit(1)

    print(f"VALIDATION OK for environment '{environment}'")
    print(f"  workspace : {env['workspace_name']} ({target_ws})")
    print(f"  lakehouse : {env.get('lakehouse_name')} ({target_lh})")
    print(f"  region    : {env['region']}")
    print(f"  items     : {', '.join(DEPLOYABLE_ITEMS)}")
    print(f"  excluded  : {EXCLUDE_ITEM_NAME_REGEX}")


def publish(environment: str) -> None:
    """Live fabric-cicd deploy into the target workspace."""
    validate(environment)  # fail closed before touching the workspace
    env = _environments()[environment]

    # Lazy imports so validate-mode needs only PyYAML.
    from azure.identity import AzureCliCredential
    from fabric_cicd import FabricWorkspace, publish_all_items

    workspace = FabricWorkspace(
        workspace_id=env["workspace_id"],
        environment=environment,
        repository_directory=str(REPORTS_DIR),
        item_type_in_scope=ITEM_TYPE_IN_SCOPE,
        token_credential=AzureCliCredential(),
    )
    print(f"Publishing capacity-dashboard into {env['workspace_name']} ({env['workspace_id']})...")
    publish_all_items(workspace, item_name_exclude_regex=EXCLUDE_ITEM_NAME_REGEX)
    print("Publish complete.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", required=True, choices=["SIT", "PROD"])
    parser.add_argument("--mode", default="validate", choices=["validate", "publish"])
    args = parser.parse_args(argv)

    if args.mode == "validate":
        validate(args.environment)
    else:
        publish(args.environment)
    return 0


if __name__ == "__main__":
    sys.exit(main())
