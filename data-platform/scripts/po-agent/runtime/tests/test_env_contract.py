import json
import shutil
import subprocess
from pathlib import Path

from env_contract import REQUIRED_ENV_VARS

_REPO_ROOT = Path(__file__).resolve().parents[5]
_BICEP_MODULE = _REPO_ROOT / "infra" / "modules" / "experience-hosting" / "po-agent-runtime" / "main.bicep"
# Resolve the full path (rather than passing the bare "az" string) so this
# works without shell=True on every platform: on POSIX, shell=True + a list
# of args silently drops all but the first arg; on Windows, "az" is really
# "az.CMD", which CreateProcess can only launch via its fully-qualified path.
_AZ_CLI = shutil.which("az") or "az"


def _declared_env_names() -> set[str]:
    try:
        result = subprocess.run(
            [_AZ_CLI, "bicep", "build", "--file", str(_BICEP_MODULE), "--stdout"],
            capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError as e:
        raise AssertionError(f"az bicep build failed:\n{e.stderr}") from e
    template = json.loads(result.stdout)
    names: set[str] = set()
    for resource in template["resources"]:
        containers = (
            resource.get("properties", {})
            .get("template", {})
            .get("containers", [])
        )
        for container in containers:
            for env in container.get("env", []):
                names.add(env["name"])
    return names


def test_bicep_declares_every_required_env_var():
    declared = _declared_env_names()
    missing = REQUIRED_ENV_VARS - declared
    assert not missing, f"po-agent-runtime Bicep module is missing env vars: {sorted(missing)}"
