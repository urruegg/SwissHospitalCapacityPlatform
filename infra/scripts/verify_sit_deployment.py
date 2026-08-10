"""Collect and validate sanitized evidence for a Curavias SIT deployment."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


_REQUIRED_COSMOS_CONTAINERS = {
    "agent_interactions",
    "approval-events",
    "audit",
    "conversations",
}
_REQUIRED_MANAGED_IDENTITY_ROLES = {
    "AcrPull",
    "Cognitive Services User",
    "Foundry User",
}
_COSMOS_DATA_CONTRIBUTOR_ID = "00000000-0000-0000-0000-000000000002"
_AZ_EXECUTABLE = shutil.which("az") or "az"


def _parameter_values(document: dict[str, Any]) -> dict[str, Any]:
    parameters = document.get("parameters", {})
    return {name: definition.get("value") for name, definition in parameters.items()}


def expected_from_parameters(document: dict[str, Any]) -> dict[str, Any]:
    """Derive deployment expectations from compiled Bicep parameters."""
    values = _parameter_values(document)
    required = (
        "environmentName",
        "solutionShortName",
        "agentHostImage",
        "agentHostOboEnabled",
        "agentHostOboClientId",
        "agentHostOboClientSecretName",
        "agentHostOboGroupRoleMap",
        "agentHostEnableRedis",
        "foundryProjectEndpoint",
        "appFluentCustomHostname",
    )
    missing = [name for name in required if values.get(name) is None]
    if missing:
        raise ValueError(f"compiled parameters are missing: {', '.join(missing)}")

    environment = str(values["environmentName"])
    solution = str(values["solutionShortName"])
    suffix = f"{solution}-{environment}"
    group_role_map = json.loads(str(values["agentHostOboGroupRoleMap"] or "{}"))
    if not isinstance(group_role_map, dict):
        raise ValueError("agentHostOboGroupRoleMap must compile to a JSON object")

    foundry_host = urlparse(str(values["foundryProjectEndpoint"])).hostname or ""
    if not foundry_host:
        raise ValueError("foundryProjectEndpoint must contain a hostname")

    return {
        "environmentName": environment,
        "solutionShortName": solution,
        "agentHostName": f"ca-agent-host-{suffix}",
        "frontendName": f"ca-app-fluent-{suffix}",
        "cosmosName": f"cosmos-{suffix}",
        "fabricCapacityName": f"fabric{solution.replace('-', '')}{environment}",
        "foundryAccountName": foundry_host.split(".", maxsplit=1)[0],
        "agentHostImage": str(values["agentHostImage"]),
        "oboEnabled": bool(values["agentHostOboEnabled"]),
        "oboClientId": str(values["agentHostOboClientId"]),
        "oboSecretName": str(values["agentHostOboClientSecretName"]),
        "groupRoleCount": len(group_role_map),
        "redisEnabled": bool(values["agentHostEnableRedis"]),
        "frontendHostname": str(values["appFluentCustomHostname"]),
    }


def _value(mapping: dict[str, Any], key: str, default: Any = None) -> Any:
    value = mapping.get(key, default)
    return default if value is None else value


def validate_evidence(evidence: dict[str, Any]) -> list[str]:
    """Return every deployment-evidence failure; an empty list is a pass."""
    failures: list[str] = []
    expected = evidence.get("expected", {})
    agent = evidence.get("agentHost", {})
    frontend = evidence.get("frontend", {})
    dependencies = evidence.get("dependencies", {})

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(
        not evidence.get("resourceFailures"),
        "SIT contains failed Azure resources",
    )
    require(
        agent.get("provisioningState") == "Succeeded",
        "agent-host provisioning state is not Succeeded",
    )
    require(
        agent.get("runningStatus") == "Running",
        "agent-host running status is not Running",
    )
    require(
        agent.get("latestRevisionName") == agent.get("latestReadyRevisionName"),
        "agent-host latest revision is not the latest ready revision",
    )
    require(
        agent.get("image") == expected.get("agentHostImage"),
        "live agent-host image does not match compiled parameters",
    )
    require(
        agent.get("health", {}).get("status") == 200
        and agent.get("health", {}).get("bodyStatus") == "ok",
        "agent-host health smoke test failed",
    )
    require(
        agent.get("goldenAnonymous", {}).get("status") == 200,
        "anonymous golden-board smoke test failed",
    )
    require(
        agent.get("chat", {}).get("status") == 200
        and bool(agent.get("chat", {}).get("answerPresent")),
        "Foundry-backed chat smoke test failed",
    )
    require(
        agent.get("worklist", {}).get("status") == 200
        and bool(agent.get("worklist", {}).get("recommendationPresent")),
        "operational worklist smoke test failed",
    )

    expected_obo = bool(expected.get("oboEnabled"))
    require(
        str(agent.get("oboEnabled", "")).lower() == str(expected_obo).lower(),
        "live OBO_ENABLED does not match compiled parameters",
    )
    require(
        agent.get("oboClientId") == expected.get("oboClientId"),
        "live OBO client ID does not match compiled parameters",
    )
    if expected_obo:
        require(
            bool(agent.get("groupRoleMapConfigured"))
            and agent.get("groupRoleCount") == expected.get("groupRoleCount"),
            "OBO group-role map is absent or incomplete",
        )
        require(
            bool(agent.get("oboSecretRef")),
            "OBO client-secret reference is absent",
        )
        require(
            agent.get("invalidBearer", {}).get("status") == 401,
            "invalid bearer was not denied with HTTP 401",
        )
        require(
            dependencies.get("oboSecretEnabled") is True,
            "Key Vault OBO secret is absent or disabled",
        )

    require(
        frontend.get("provisioningState") == "Succeeded"
        and frontend.get("runningStatus") == "Running",
        "frontend Container App is not running",
    )
    require(frontend.get("httpStatus") == 200, "public SIT frontend did not return HTTP 200")
    require(
        frontend.get("agentHostUrl") == expected.get("agentHostUrl"),
        "frontend AGENT_HOST_URL does not target the live agent-host",
    )
    require(
        frontend.get("goldenSourceUrl") == f"{expected.get('agentHostUrl')}/golden",
        "frontend GOLDEN_SOURCE_URL does not target the live agent-host",
    )

    require(bool(dependencies.get("acrImageDigest")), "expected image is absent from ACR")
    require(
        dependencies.get("cosmosState") == "Succeeded",
        "agent-host Cosmos account is not provisioned",
    )
    missing_containers = _REQUIRED_COSMOS_CONTAINERS - set(
        dependencies.get("cosmosContainers", [])
    )
    require(
        not missing_containers,
        f"required Cosmos containers are missing: {sorted(missing_containers)}",
    )
    require(
        dependencies.get("fabricState") == "Active",
        "Fabric capacity is not Active",
    )
    require(
        dependencies.get("foundryState") == "Succeeded",
        "Foundry account is not provisioned",
    )
    require(
        dependencies.get("keyVaultState") == "Succeeded",
        "Key Vault is not provisioned",
    )
    roles = set(dependencies.get("managedIdentityRoles", []))
    missing_roles = _REQUIRED_MANAGED_IDENTITY_ROLES - roles
    require(
        not missing_roles,
        f"required managed-identity roles are missing: {sorted(missing_roles)}",
    )
    require(
        dependencies.get("cosmosDataContributor") is True,
        "agent-host identity lacks Cosmos DB Built-in Data Contributor",
    )
    require(
        bool(agent.get("redisConfigured")) == bool(expected.get("redisEnabled")),
        "Redis runtime configuration does not match compiled parameters",
    )
    if expected.get("redisEnabled"):
        require(
            dependencies.get("redisState") == "Succeeded",
            "Azure Managed Redis is enabled but not provisioned",
        )

    return failures


def _run_az(*arguments: str) -> Any:
    command = [_AZ_EXECUTABLE, *arguments, "--only-show-errors", "--output", "json"]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown Azure CLI error"
        raise RuntimeError(f"Azure CLI command failed ({' '.join(command[:4])} ...): {detail}")
    output = completed.stdout.strip()
    return json.loads(output) if output else None


def _http_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request_headers = {"Accept": "application/json", **(headers or {})}
    if body is not None:
        request_headers["Content-Type"] = "application/json"
    request = Request(url, data=body, headers=request_headers, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            try:
                parsed = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                parsed = None
            return {"status": response.status, "body": parsed}
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            parsed = None
        return {"status": exc.code, "body": parsed}
    except (TimeoutError, URLError) as exc:
        return {"status": 0, "error": str(exc)}


def _env_map(container_app: dict[str, Any]) -> dict[str, dict[str, Any]]:
    containers = container_app.get("properties", {}).get("template", {}).get("containers", [])
    entries = containers[0].get("env", []) if containers else []
    return {entry.get("name", ""): entry for entry in entries if entry.get("name")}


def _image_parts(image: str) -> tuple[str, str, str]:
    registry, repository_and_tag = image.split("/", maxsplit=1)
    repository, tag = repository_and_tag.rsplit(":", maxsplit=1)
    return registry.removesuffix(".azurecr.io"), repository, tag


def wait_for_ready_revision(
    *,
    resource_group: str,
    agent_host_name: str,
    show: Callable[[str, str], dict[str, Any]],
    sleep: Callable[[float], None] = time.sleep,
    max_attempts: int = 10,
    delay_seconds: float = 5.0,
) -> dict[str, Any]:
    """Poll until the just-deployed revision finishes activating.

    A deployment can return success before Container Apps finishes routing
    traffic to the new revision; checking immediately races that propagation
    (observed live: latestRevisionName ahead of latestReadyRevisionName for a
    few seconds after `az deployment group create` returns). Returns the last
    observed result even if it never converges within max_attempts.
    """
    result: dict[str, Any] = {}
    for attempt in range(max_attempts):
        result = show(resource_group, agent_host_name)
        properties = result.get("properties", {})
        if properties.get("latestRevisionName") == properties.get("latestReadyRevisionName"):
            return result
        if attempt < max_attempts - 1:
            sleep(delay_seconds)
    return result


def collect_evidence(
    *,
    resource_group: str,
    deployment_name: str,
    parameters: dict[str, Any],
) -> dict[str, Any]:
    """Collect live evidence without retrieving secret values or data records."""
    expected = expected_from_parameters(parameters)
    resources = _run_az("resource", "list", "--resource-group", resource_group) or []
    inventory = [
        {
            "name": resource.get("name"),
            "type": resource.get("type"),
            "location": resource.get("location"),
            "provisioningState": (resource.get("properties") or {}).get("provisioningState"),
        }
        for resource in resources
    ]
    resource_failures = [
        resource
        for resource in inventory
        if str(resource.get("provisioningState", "")).lower() == "failed"
    ]

    def _show_agent_host(rg: str, name: str) -> dict[str, Any]:
        return _run_az("containerapp", "show", "--resource-group", rg, "--name", name)

    agent = wait_for_ready_revision(
        resource_group=resource_group,
        agent_host_name=expected["agentHostName"],
        show=_show_agent_host,
    )
    agent_properties = agent.get("properties", {})
    agent_env = _env_map(agent)
    fqdn = agent_properties.get("configuration", {}).get("ingress", {}).get("fqdn", "")
    agent_host_url = f"https://{fqdn}"
    expected["agentHostUrl"] = agent_host_url

    live_group_map_raw = _value(agent_env.get("OBO_GROUP_ROLE_MAP", {}), "value", "")
    try:
        live_group_map = json.loads(live_group_map_raw or "{}")
    except json.JSONDecodeError:
        live_group_map = {}

    smoke_headers = {
        "X-User-Oid": "00000000-0000-0000-0000-000000000001",
        "X-Hospital-Scope": "aggregated",
        "X-Active-Role": "HCC.BedManager",
    }
    health = _http_json(f"{agent_host_url}/healthz")
    golden = _http_json(
        f"{agent_host_url}/golden/bed-manager?hospital=usz&window=72",
        headers=smoke_headers,
    )
    invalid_bearer = {"status": None}
    if expected["oboEnabled"]:
        invalid_bearer = _http_json(
            f"{agent_host_url}/golden/bed-manager?hospital=usz&window=72",
            headers={**smoke_headers, "Authorization": "Bearer not-a-real-jwt"},
        )
    chat = _http_json(
        f"{agent_host_url}/agents/bmca-agent/chat",
        method="POST",
        headers={"X-User-Oid": smoke_headers["X-User-Oid"]},
        payload={
            "prompt": "Summarize the current synthetic bed-capacity signal in one sentence.",
            "conversationId": f"sit-deploy-{deployment_name}",
        },
        timeout=180,
    )
    worklist = _http_json(
        f"{agent_host_url}/agents/dca/worklist",
        headers={
            "X-User-Oid": smoke_headers["X-User-Oid"],
            "X-Active-Role": "HCC.DischargeCoordinator",
            "X-Hospital-Id": "H-USZ",
        },
    )

    frontend = _run_az(
        "containerapp", "show", "--resource-group", resource_group, "--name", expected["frontendName"]
    )
    frontend_properties = frontend.get("properties", {})
    frontend_env = _env_map(frontend)
    frontend_http = _http_json(f"https://{expected['frontendHostname']}")

    registry_name, repository, tag = _image_parts(expected["agentHostImage"])
    image = _run_az(
        "acr", "repository", "show", "--name", registry_name, "--image", f"{repository}:{tag}"
    )
    cosmos = _run_az(
        "cosmosdb", "show", "--resource-group", resource_group, "--name", expected["cosmosName"]
    )
    containers = _run_az(
        "cosmosdb",
        "sql",
        "container",
        "list",
        "--resource-group",
        resource_group,
        "--account-name",
        expected["cosmosName"],
        "--database-name",
        "agenthost",
    )
    fabric = _run_az(
        "resource",
        "show",
        "--resource-group",
        resource_group,
        "--resource-type",
        "Microsoft.Fabric/capacities",
        "--name",
        expected["fabricCapacityName"],
    )
    foundry = _run_az(
        "cognitiveservices",
        "account",
        "show",
        "--resource-group",
        resource_group,
        "--name",
        expected["foundryAccountName"],
    )
    deployment = _run_az(
        "deployment", "group", "show", "--resource-group", resource_group, "--name", deployment_name
    )
    outputs = deployment.get("properties", {}).get("outputs", {})
    key_vault_name = outputs.get("keyVaultName", {}).get("value", "")
    if not key_vault_name:
        raise RuntimeError("deployment output keyVaultName is absent")
    key_vault = _run_az(
        "keyvault", "show", "--resource-group", resource_group, "--name", key_vault_name
    )
    obo_secret_enabled: bool | None = None
    if expected["oboEnabled"]:
        secret = _run_az(
            "resource",
            "show",
            "--ids",
            f"{key_vault['id']}/secrets/{expected['oboSecretName']}",
            "--api-version",
            "2023-07-01",
        )
        obo_secret_enabled = secret.get("properties", {}).get("attributes", {}).get("enabled")

    identities = agent.get("identity", {}).get("userAssignedIdentities", {})
    principal_ids = [identity.get("principalId") for identity in identities.values()]
    principal_id = next((value for value in principal_ids if value), "")
    if not principal_id:
        raise RuntimeError("agent-host user-assigned identity principal ID is absent")
    role_assignments = _run_az(
        "role", "assignment", "list", "--assignee-object-id", principal_id, "--all"
    )
    cosmos_role_assignments = _run_az(
        "cosmosdb",
        "sql",
        "role",
        "assignment",
        "list",
        "--resource-group",
        resource_group,
        "--account-name",
        expected["cosmosName"],
    )

    dependencies: dict[str, Any] = {
        "acrImageDigest": image.get("digest"),
        "cosmosState": cosmos.get("provisioningState")
        or cosmos.get("properties", {}).get("provisioningState"),
        "cosmosContainers": sorted(container.get("name", "") for container in containers),
        "fabricState": fabric.get("properties", {}).get("state"),
        "foundryState": foundry.get("properties", {}).get("provisioningState"),
        "keyVaultName": key_vault_name,
        "keyVaultState": key_vault.get("properties", {}).get("provisioningState"),
        "oboSecretEnabled": obo_secret_enabled,
        "managedIdentityPrincipalId": principal_id,
        "managedIdentityRoles": sorted(
            assignment.get("roleDefinitionName", "") for assignment in role_assignments
        ),
        "cosmosDataContributor": any(
            assignment.get("principalId") == principal_id
            and str(assignment.get("roleDefinitionId", "")).endswith(
                f"/{_COSMOS_DATA_CONTRIBUTOR_ID}"
            )
            for assignment in cosmos_role_assignments
        ),
        "redisMode": "azure-managed" if expected["redisEnabled"] else "in-memory-sit-exception",
    }
    if expected["redisEnabled"]:
        redis = _run_az(
            "resource",
            "show",
            "--resource-group",
            resource_group,
            "--resource-type",
            "Microsoft.Cache/redisEnterprise",
            "--name",
            f"redis-{expected['solutionShortName']}-{expected['environmentName']}",
        )
        dependencies["redisState"] = redis.get("properties", {}).get("provisioningState")

    agent_container = agent_properties.get("template", {}).get("containers", [{}])[0]
    evidence = {
        "metadata": {
            "collectedAt": datetime.now(timezone.utc).isoformat(),
            "resourceGroup": resource_group,
            "deploymentName": deployment_name,
        },
        "expected": expected,
        "resourceInventory": inventory,
        "resourceFailures": resource_failures,
        "agentHost": {
            "provisioningState": agent_properties.get("provisioningState"),
            "runningStatus": agent_properties.get("runningStatus"),
            "latestRevisionName": agent_properties.get("latestRevisionName"),
            "latestReadyRevisionName": agent_properties.get("latestReadyRevisionName"),
            "image": agent_container.get("image"),
            "oboEnabled": _value(agent_env.get("OBO_ENABLED", {}), "value", ""),
            "oboClientId": _value(agent_env.get("OBO_CLIENT_ID", {}), "value", ""),
            "groupRoleMapConfigured": bool(live_group_map),
            "groupRoleCount": len(live_group_map) if isinstance(live_group_map, dict) else 0,
            "oboSecretRef": _value(agent_env.get("OBO_CLIENT_SECRET", {}), "secretRef", ""),
            "redisConfigured": bool(_value(agent_env.get("REDIS_HOST", {}), "value", "")),
            "health": {
                "status": health.get("status"),
                "bodyStatus": (health.get("body") or {}).get("status"),
            },
            "goldenAnonymous": {"status": golden.get("status")},
            "invalidBearer": {"status": invalid_bearer.get("status")},
            "chat": {
                "status": chat.get("status"),
                "answerPresent": bool((chat.get("body") or {}).get("answer")),
                "citationCount": len((chat.get("body") or {}).get("citations", [])),
            },
            "worklist": {
                "status": worklist.get("status"),
                "recommendationPresent": bool((worklist.get("body") or {}).get("recommendation")),
                "liveCitationCount": len(
                    ((worklist.get("body") or {}).get("recommendation") or {}).get(
                        "liveGroundingCitations", []
                    )
                ),
            },
        },
        "frontend": {
            "provisioningState": frontend_properties.get("provisioningState"),
            "runningStatus": frontend_properties.get("runningStatus"),
            "httpStatus": frontend_http.get("status"),
            "agentHostUrl": _value(frontend_env.get("AGENT_HOST_URL", {}), "value", ""),
            "goldenSourceUrl": _value(frontend_env.get("GOLDEN_SOURCE_URL", {}), "value", ""),
        },
        "dependencies": dependencies,
    }
    evidence["failures"] = validate_evidence(evidence)
    evidence["status"] = "pass" if not evidence["failures"] else "fail"
    return evidence


def _write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource-group", required=True)
    parser.add_argument("--deployment-name", required=True)
    parser.add_argument("--parameters-json", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)

    parameters = json.loads(args.parameters_json.read_text(encoding="utf-8-sig"))
    try:
        report = collect_evidence(
            resource_group=args.resource_group,
            deployment_name=args.deployment_name,
            parameters=parameters,
        )
    except Exception as exc:
        report = {
            "metadata": {
                "collectedAt": datetime.now(timezone.utc).isoformat(),
                "resourceGroup": args.resource_group,
                "deploymentName": args.deployment_name,
            },
            "status": "error",
            "failures": [str(exc)],
        }
    _write_report(args.output, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())