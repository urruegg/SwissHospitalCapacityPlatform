"""Build secret-free parameters for the scoped SIT agent-host release."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


_PARAMETER_MAP = {
    "environmentName": "environmentName",
    "solutionShortName": "solutionShortName",
    "location": "location",
    "owner": "owner",
    "costCenter": "costCenter",
    "workload": "workload",
    "agentHostImage": "agentHostImage",
    "fabricDataAgentEndpoint": "fabricDataAgentEndpoint",
    "fabricWorkspaceId": "fabricWorkspaceId",
    "fabricDataAgentId": "fabricDataAgentId",
    "foundryProjectEndpoint": "foundryProjectEndpoint",
    "foundryProjectName": "foundryProjectName",
    "fabricLakehouseId": "fabricLakehouseId",
    "agentHostOboEnabled": "oboEnabled",
    "agentHostOboTenantId": "oboTenantId",
    "agentHostOboClientId": "oboClientId",
    "agentHostOboClientSecretName": "oboClientSecretName",
    "agentHostOboJwksUrl": "oboJwksUrl",
    "agentHostOboAudience": "oboAudience",
    "agentHostOboIssuer": "oboIssuer",
    "agentHostOboFabricScope": "oboFabricScope",
    "agentHostOboGroupRoleMap": "oboGroupRoleMap",
    "simCapacityContainerRegistryLoginServer": "containerRegistryLoginServer",
    "agentHostEnableRedis": "enableRedis",
}

# Not declared in every environment's .bicepparam file; main.bicep defaults it
# to 'simulated'. Treated as optional so a valid compiled document that omits
# it still produces a correct release.
_RLS_PROVIDER_SOURCE = "agentHostRlsProvider"
_RLS_PROVIDER_DEFAULT = "simulated"


def build_release_parameters(
    compiled_root: dict[str, Any], *, key_vault_name: str
) -> dict[str, Any]:
    """Map compiled root parameters to the scoped release contract."""
    if not key_vault_name.strip():
        raise ValueError("Key Vault name is required")

    source = compiled_root.get("parameters", {})
    missing = [name for name in _PARAMETER_MAP if name not in source]
    if missing:
        raise ValueError(f"compiled parameters are missing: {', '.join(missing)}")

    parameters = {
        target: {"value": source[source_name].get("value")}
        for source_name, target in _PARAMETER_MAP.items()
    }
    parameters["rlsProvider"] = {
        "value": source.get(_RLS_PROVIDER_SOURCE, {}).get("value", _RLS_PROVIDER_DEFAULT)
    }
    parameters["keyVaultName"] = {"value": key_vault_name.strip()}
    return {
        "$schema": (
            "https://schema.management.azure.com/schemas/"
            "2019-04-01/deploymentParameters.json#"
        ),
        "contentVersion": "1.0.0.0",
        "parameters": parameters,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiled-root", required=True, type=Path)
    parser.add_argument("--key-vault-name", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    source = json.loads(args.compiled_root.read_text(encoding="utf-8-sig"))
    result = build_release_parameters(source, key_vault_name=args.key_vault_name)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())