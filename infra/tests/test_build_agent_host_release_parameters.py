"""Tests for scoped agent-host release parameter generation."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


_SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "build_agent_host_release_parameters.py"
)


def _load_generator() -> ModuleType:
    assert _SCRIPT.is_file(), "agent-host release parameter generator is missing"
    spec = importlib.util.spec_from_file_location(
        "build_agent_host_release_parameters", _SCRIPT
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _compiled_root_parameters() -> dict:
    values = {
        "environmentName": "sit",
        "solutionShortName": "ihzhhpf",
        "location": "westus2",
        "owner": "platform-team",
        "costCenter": "ihzhhpf-sit",
        "workload": "hospital-capacity",
        "agentHostImage": "example.azurecr.io/hcc-agent-host:9daaa64",
        "fabricDataAgentEndpoint": "https://api.fabric.microsoft.com/example",
        "fabricWorkspaceId": "workspace-id",
        "fabricDataAgentId": "data-agent-id",
        "foundryProjectEndpoint": "https://foundry.example.test",
        "foundryProjectName": "foundry-project",
        "fabricLakehouseId": "lakehouse-id",
        "agentHostRlsProvider": "simulated",
        "agentHostOboEnabled": True,
        "agentHostOboTenantId": "tenant-id",
        "agentHostOboClientId": "client-id",
        "agentHostOboClientSecretName": "obo-secret-name",
        "agentHostOboJwksUrl": "https://login.example.test/keys",
        "agentHostOboAudience": "api://client-id",
        "agentHostOboIssuer": "https://login.example.test/v2.0",
        "agentHostOboFabricScope": "https://storage.azure.com/.default",
        "agentHostOboGroupRoleMap": '{"group-id":"HCC.BedManager"}',
        "simCapacityContainerRegistryLoginServer": "example.azurecr.io",
        "agentHostEnableRedis": False,
    }
    return {"parameters": {name: {"value": value} for name, value in values.items()}}


def test_maps_canonical_parameters_without_secret_values() -> None:
    generator = _load_generator()

    result = generator.build_release_parameters(
        _compiled_root_parameters(), key_vault_name="kv-ihzhhpf-sit-abc1"
    )

    values = result["parameters"]
    assert values["agentHostImage"]["value"].endswith(":9daaa64")
    assert values["oboEnabled"]["value"] is True
    assert values["oboClientSecretName"]["value"] == "obo-secret-name"
    assert values["keyVaultName"]["value"] == "kv-ihzhhpf-sit-abc1"
    assert values["containerRegistryLoginServer"]["value"] == "example.azurecr.io"
    assert values["enableRedis"]["value"] is False
    assert "oboClientSecret" not in values
    assert "logAnalyticsSharedKey" not in values


def test_missing_required_source_parameter_is_rejected() -> None:
    generator = _load_generator()
    source = _compiled_root_parameters()
    del source["parameters"]["agentHostImage"]

    with pytest.raises(ValueError, match="agentHostImage"):
        generator.build_release_parameters(source, key_vault_name="kv-name")


def test_empty_key_vault_name_is_rejected() -> None:
    generator = _load_generator()

    with pytest.raises(ValueError, match="Key Vault"):
        generator.build_release_parameters(
            _compiled_root_parameters(), key_vault_name=""
        )


def test_rls_provider_defaults_when_not_declared_in_environment() -> None:
    generator = _load_generator()
    source = _compiled_root_parameters()
    del source["parameters"]["agentHostRlsProvider"]

    result = generator.build_release_parameters(source, key_vault_name="kv-name")

    assert result["parameters"]["rlsProvider"]["value"] == "simulated"