"""Tests for the SIT post-deployment evidence verifier."""

from __future__ import annotations

import importlib.util
from copy import deepcopy
from pathlib import Path
from types import ModuleType


_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_sit_deployment.py"


def _load_verifier() -> ModuleType:
    assert _SCRIPT.is_file(), "SIT deployment evidence verifier is missing"
    spec = importlib.util.spec_from_file_location("verify_sit_deployment", _SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _valid_evidence() -> dict:
    agent_host_url = "https://ca-agent-host-ihzhhpf-sit.example.test"
    return {
        "expected": {
            "agentHostImage": "example.azurecr.io/hcc-agent-host:9daaa64",
            "agentHostUrl": agent_host_url,
            "frontendHostname": "appsit.curavias.ch",
            "oboEnabled": True,
            "oboClientId": "backend-client-id",
            "groupRoleCount": 17,
            "redisEnabled": False,
        },
        "resourceFailures": [],
        "agentHost": {
            "provisioningState": "Succeeded",
            "runningStatus": "Running",
            "latestRevisionName": "revision-1",
            "latestReadyRevisionName": "revision-1",
            "image": "example.azurecr.io/hcc-agent-host:9daaa64",
            "oboEnabled": "true",
            "oboClientId": "backend-client-id",
            "groupRoleMapConfigured": True,
            "groupRoleCount": 17,
            "oboSecretRef": "obo-client-secret",
            "redisConfigured": False,
            "health": {"status": 200, "bodyStatus": "ok"},
            "goldenAnonymous": {"status": 200},
            "invalidBearer": {"status": 401},
            "chat": {"status": 200, "answerPresent": True},
            "worklist": {"status": 200, "recommendationPresent": True},
        },
        "frontend": {
            "provisioningState": "Succeeded",
            "runningStatus": "Running",
            "httpStatus": 200,
            "agentHostUrl": agent_host_url,
            "goldenSourceUrl": f"{agent_host_url}/golden",
        },
        "dependencies": {
            "acrImageDigest": "sha256:abc",
            "cosmosState": "Succeeded",
            "cosmosContainers": [
                "agent_interactions",
                "approval-events",
                "audit",
                "conversations",
            ],
            "fabricState": "Active",
            "foundryState": "Succeeded",
            "keyVaultState": "Succeeded",
            "oboSecretEnabled": True,
            "managedIdentityRoles": [
                "AcrPull",
                "Cognitive Services User",
                "Foundry User",
            ],
            "cosmosDataContributor": True,
        },
    }


def test_expected_release_is_derived_from_compiled_parameters() -> None:
    verifier = _load_verifier()
    document = {
        "parameters": {
            "environmentName": {"value": "sit"},
            "solutionShortName": {"value": "ihzhhpf"},
            "agentHostImage": {
                "value": "example.azurecr.io/hcc-agent-host:9daaa64"
            },
            "agentHostOboEnabled": {"value": True},
            "agentHostOboClientId": {"value": "backend-client-id"},
            "agentHostOboClientSecretName": {"value": "obo-secret"},
            "agentHostOboGroupRoleMap": {
                "value": '{"group-a":"HCC.BedManager","group-b":"HCC.Auditor"}'
            },
            "agentHostEnableRedis": {"value": False},
            "foundryProjectEndpoint": {
                "value": "https://ai-ihzhhpf-sit-eastus2.services.ai.azure.com"
            },
            "appFluentCustomHostname": {"value": "appsit.curavias.ch"},
        }
    }

    expected = verifier.expected_from_parameters(document)

    assert expected["agentHostName"] == "ca-agent-host-ihzhhpf-sit"
    assert expected["frontendName"] == "ca-app-fluent-ihzhhpf-sit"
    assert expected["cosmosName"] == "cosmos-ihzhhpf-sit"
    assert expected["fabricCapacityName"] == "fabricihzhhpfsit"
    assert expected["foundryAccountName"] == "ai-ihzhhpf-sit-eastus2"
    assert expected["groupRoleCount"] == 2


def test_complete_matching_evidence_passes() -> None:
    verifier = _load_verifier()

    assert verifier.validate_evidence(_valid_evidence()) == []


def test_stale_image_and_frontend_wiring_fail() -> None:
    verifier = _load_verifier()
    evidence = _valid_evidence()
    evidence["agentHost"]["image"] = "example.azurecr.io/hcc-agent-host:d97fa11"
    evidence["frontend"]["agentHostUrl"] = "https://old-agent-host.example.test"

    failures = verifier.validate_evidence(evidence)

    assert any("agent-host image" in failure for failure in failures)
    assert any("frontend AGENT_HOST_URL" in failure for failure in failures)


def test_enabled_obo_requires_group_map_secret_and_deny_by_default() -> None:
    verifier = _load_verifier()
    evidence = _valid_evidence()
    evidence["agentHost"]["groupRoleMapConfigured"] = False
    evidence["agentHost"]["groupRoleCount"] = 0
    evidence["agentHost"]["oboSecretRef"] = ""
    evidence["agentHost"]["invalidBearer"]["status"] = 500
    evidence["dependencies"]["oboSecretEnabled"] = False

    failures = verifier.validate_evidence(evidence)

    assert any("group-role map" in failure for failure in failures)
    assert any("client-secret reference" in failure for failure in failures)
    assert any("invalid bearer" in failure for failure in failures)
    assert any("Key Vault OBO secret" in failure for failure in failures)


def test_failed_runtime_dependencies_fail() -> None:
    verifier = _load_verifier()
    evidence = deepcopy(_valid_evidence())
    evidence["resourceFailures"] = [{"name": "broken", "type": "Example"}]
    evidence["dependencies"]["fabricState"] = "Paused"
    evidence["dependencies"]["cosmosContainers"] = ["audit"]
    evidence["dependencies"]["managedIdentityRoles"] = ["AcrPull"]
    evidence["agentHost"]["chat"]["answerPresent"] = False

    failures = verifier.validate_evidence(evidence)

    assert any("failed Azure resources" in failure for failure in failures)
    assert any("Fabric capacity" in failure for failure in failures)
    assert any("Cosmos containers" in failure for failure in failures)
    assert any("managed-identity roles" in failure for failure in failures)
    assert any("chat smoke test" in failure for failure in failures)


def test_http_collector_accepts_html_success(monkeypatch) -> None:
    verifier = _load_verifier()

    class _Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        @staticmethod
        def read() -> bytes:
            return b"<!doctype html><title>Curavias</title>"

    monkeypatch.setattr(verifier, "urlopen", lambda *_args, **_kwargs: _Response())

    result = verifier._http_json("https://appsit.curavias.ch")

    assert result == {"status": 200, "body": None}


def test_wait_for_ready_revision_polls_until_revisions_match() -> None:
    verifier = _load_verifier()
    calls = []

    def fake_show(resource_group: str, name: str) -> dict:
        calls.append(name)
        if len(calls) < 3:
            return {
                "properties": {
                    "latestRevisionName": "rev-2",
                    "latestReadyRevisionName": "rev-1",
                }
            }
        return {
            "properties": {
                "latestRevisionName": "rev-2",
                "latestReadyRevisionName": "rev-2",
            }
        }

    result = verifier.wait_for_ready_revision(
        resource_group="rg",
        agent_host_name="ca-agent-host",
        show=fake_show,
        sleep=lambda _seconds: None,
        max_attempts=5,
    )

    assert len(calls) == 3
    assert result["properties"]["latestRevisionName"] == "rev-2"
    assert result["properties"]["latestReadyRevisionName"] == "rev-2"


def test_wait_for_ready_revision_gives_up_after_max_attempts() -> None:
    verifier = _load_verifier()

    def fake_show(resource_group: str, name: str) -> dict:
        return {
            "properties": {
                "latestRevisionName": "rev-2",
                "latestReadyRevisionName": "rev-1",
            }
        }

    result = verifier.wait_for_ready_revision(
        resource_group="rg",
        agent_host_name="ca-agent-host",
        show=fake_show,
        sleep=lambda _seconds: None,
        max_attempts=3,
    )

    assert result["properties"]["latestRevisionName"] == "rev-2"
    assert result["properties"]["latestReadyRevisionName"] == "rev-1"


def test_http_json_with_retry_recovers_from_transient_5xx() -> None:
    verifier = _load_verifier()
    responses = [{"status": 500}, {"status": 200, "body": {"answer": "ok"}}]
    calls: list[float] = []

    def fake_call(*_args, **_kwargs) -> dict:
        return responses[len(calls)]

    def fake_sleep(seconds: float) -> None:
        calls.append(seconds)

    result = verifier._http_json_with_retry(
        "https://example.test/chat",
        call=fake_call,
        sleep=fake_sleep,
        max_attempts=3,
        retry_delay_seconds=1.0,
    )

    assert calls == [1.0]
    assert result == {"status": 200, "body": {"answer": "ok"}}


def test_http_json_with_retry_does_not_retry_a_definitive_response() -> None:
    verifier = _load_verifier()
    attempts = 0

    def fake_call(*_args, **_kwargs) -> dict:
        nonlocal attempts
        attempts += 1
        return {"status": 404}

    result = verifier._http_json_with_retry(
        "https://example.test/chat",
        call=fake_call,
        sleep=lambda _seconds: None,
        max_attempts=3,
    )

    assert attempts == 1
    assert result == {"status": 404}


def test_http_json_with_retry_gives_up_after_max_attempts() -> None:
    verifier = _load_verifier()
    attempts = 0

    def fake_call(*_args, **_kwargs) -> dict:
        nonlocal attempts
        attempts += 1
        return {"status": 0, "error": "timed out"}

    result = verifier._http_json_with_retry(
        "https://example.test/chat",
        call=fake_call,
        sleep=lambda _seconds: None,
        max_attempts=3,
    )

    assert attempts == 3
    assert result == {"status": 0, "error": "timed out"}