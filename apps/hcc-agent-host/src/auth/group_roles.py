"""Sprint 43 WS-6 follow-up -- group-claim role mapping.

Assigning a principal to an app role (``POST .../appRoleAssignedTo``) requires
a Microsoft Entra directory role (Application Administrator, Cloud Application
Administrator, etc.) with no owner-of-resource exception (see
docs/superpowers/specs/2026-08-09-obo-context-aware-role-agent-decision-loop-design.md
§1.3). Setting ``groupMembershipClaims`` on the app registration is, by
contrast, an owner-level, self-service app-registration property (same class
as ``appRoles``) and puts a ``groups`` claim on the OBO token driven entirely
by the signed-in user's EXISTING security-group memberships -- no new
assignment write needed.

This module maps those group object IDs to the HCC.* role names the decision
loop already understands, so ``_require_active_role_held`` and friends keep
working unchanged (see :func:`auth.token_validator.validate_claims`, which
unions group-derived roles into ``ValidatedCaller.roles``). The mapping is
tenant-specific (like ``OBO_TENANT_ID``/``OBO_CLIENT_ID`` elsewhere in this
app) so it is sourced from config, never hard-coded (copilot-instructions
§3/§4).
"""

from __future__ import annotations

import json
import os


def group_role_map() -> dict[str, str]:
    """Parse ``OBO_GROUP_ROLE_MAP`` (a JSON object of group-object-id -> role name).

    Deny-by-default on any malformed config: an unset or invalid value yields
    an empty map rather than raising, so a misconfigured/absent mapping simply
    means no group-derived roles are added (falls back to any direct ``roles``
    claim) instead of taking the process down.
    """
    raw = os.getenv("OBO_GROUP_ROLE_MAP", "")
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except ValueError:
        return {}
    if not isinstance(parsed, dict):
        return {}
    return {str(k): str(v) for k, v in parsed.items()}
