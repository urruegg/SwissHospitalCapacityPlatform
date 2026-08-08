"""Sprint 42 ST-4 guardrail: single source of truth for the env vars
`get_tools()` (app.py) reads. A CI test parses the Bicep module and asserts
every name here is declared as a container env var, so the class of drift
that shipped in Sprint 41 (SEARCH_ENDPOINT vs AZURE_SEARCH_ENDPOINT) fails
the build instead of shipping silently.
"""
from __future__ import annotations

REQUIRED_ENV_VARS: set[str] = {
    "AZURE_SUBSCRIPTION_ID",
    "AZURE_SEARCH_ENDPOINT",
    "AZURE_SEARCH_INDEX",
    "FABRIC_DATA_AGENT_ENDPOINT",
    "FABRIC_WORKSPACE_ID",
    "FABRIC_DATA_AGENT_ID",
    "FOUNDRY_PROJECT_ENDPOINT",
    "FOUNDRY_PROJECT_NAME",
}
