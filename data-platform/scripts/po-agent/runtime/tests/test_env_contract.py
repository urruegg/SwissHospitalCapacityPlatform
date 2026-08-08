import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from env_contract import REQUIRED_ENV_VARS

_REPO_ROOT = Path(__file__).resolve().parents[5]
_BICEP_MODULE = _REPO_ROOT / "infra" / "modules" / "experience-hosting" / "po-agent-runtime" / "main.bicep"


def _declared_env_names() -> set[str]:
    result = subprocess.run(
        ["az", "bicep", "build", "--file", str(_BICEP_MODULE), "--stdout"],
        capture_output=True, text=True, check=True, shell=True,
    )
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
