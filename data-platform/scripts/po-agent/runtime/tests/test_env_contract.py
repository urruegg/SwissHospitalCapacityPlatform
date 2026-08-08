import json
import shutil
import subprocess
from pathlib import Path

from env_contract import REQUIRED_ENV_VARS, REQUIRED_REFRESH_JOB_ENV_VARS

_REPO_ROOT = Path(__file__).resolve().parents[5]
_BICEP_MODULE = _REPO_ROOT / "infra" / "modules" / "experience-hosting" / "po-agent-runtime" / "main.bicep"
# Resolve the full path (rather than passing the bare "az" string) so this
# works without shell=True on every platform: on POSIX, shell=True + a list
# of args silently drops all but the first arg; on Windows, "az" is really
# "az.CMD", which CreateProcess can only launch via its fully-qualified path.
_AZ_CLI = shutil.which("az") or "az"


def _build_template() -> dict:
    try:
        result = subprocess.run(
            [_AZ_CLI, "bicep", "build", "--file", str(_BICEP_MODULE), "--stdout"],
            capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError as e:
        raise AssertionError(f"az bicep build failed:\n{e.stderr}") from e
    return json.loads(result.stdout)


def _env_names_by_resource_type(template: dict) -> dict[str, set[str]]:
    """Map ARM resource type -> union of env var names declared on it.

    Kept per-type (not a single flattened union across every resource) so a
    resource missing a var it individually needs can't hide behind a
    different resource that happens to declare the same name - this is
    exactly the gap a first version of this guardrail had: it only checked
    the union across all resources, so the corpus-refresh job silently
    passed while missing AZURE_SEARCH_ENDPOINT/AZURE_SEARCH_INDEX (the
    runtime app's copy satisfied the union), and the job then failed at
    runtime with a real KeyError.
    """
    by_type: dict[str, set[str]] = {}
    for resource in template["resources"]:
        containers = (
            resource.get("properties", {})
            .get("template", {})
            .get("containers", [])
        )
        if not containers:
            continue
        names = by_type.setdefault(resource["type"], set())
        for container in containers:
            for env in container.get("env", []):
                names.add(env["name"])
    return by_type


def test_bicep_declares_every_required_env_var():
    by_type = _env_names_by_resource_type(_build_template())
    declared = by_type.get("Microsoft.App/containerApps", set())
    missing = REQUIRED_ENV_VARS - declared
    assert not missing, f"po-agent-runtime Bicep module is missing env vars: {sorted(missing)}"


def test_bicep_declares_refresh_job_search_env_vars():
    by_type = _env_names_by_resource_type(_build_template())
    declared = by_type.get("Microsoft.App/jobs", set())
    missing = REQUIRED_REFRESH_JOB_ENV_VARS - declared
    assert not missing, f"po-agent-runtime's refresh job is missing env vars: {sorted(missing)}"
