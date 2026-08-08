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

# The corpus-refresh job (data-platform/scripts/po-agent/corpus/refresh_job.py)
# has a narrower, different contract than the runtime app above - it only
# uploads into the search index, it never calls get_tools(). A first version
# of this guardrail checked the *union* of env vars across every resource in
# the Bicep module, which passed even when the job itself was missing these
# two names (the runtime app's copy satisfied the union) - the job then
# failed at runtime with a real KeyError. Checked per-resource now (see
# test_env_contract.py) so this class of gap fails the guardrail again.
REQUIRED_REFRESH_JOB_ENV_VARS: set[str] = {
    "AZURE_SEARCH_ENDPOINT",
    "AZURE_SEARCH_INDEX",
}
