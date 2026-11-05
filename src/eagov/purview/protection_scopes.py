"""Compute Purview protection scopes.

Verified against Microsoft Learn on 2026-11-05:
POST /users/{userId}/dataSecurityAndGovernance/protectionScopes/compute
Least privileged: ProtectionScopes.Compute.User
Higher: ProtectionScopes.Compute.All
Delegated and application permissions are both documented.
The /me route requires a delegated permission.
"""

from __future__ import annotations

from typing import Any

from eagov.graph.client import GraphClient
from eagov.models import AgentIdentity, AuthenticatedUser

USER_COMPUTE_PATH = "/users/{user_id}/dataSecurityAndGovernance/protectionScopes/compute"
ACTIVITIES = "uploadText,downloadText"


def build_protection_scope_request(
    identity: AgentIdentity,
    integrated_app_name: str,
    integrated_app_version: str,
) -> dict[str, Any]:
    return {
        "activities": ACTIVITIES,
        "integratedAppMetadata": {
            "name": integrated_app_name,
            "version": integrated_app_version,
        },
        "locations": [
            {
                "@odata.type": "microsoft.graph.policyLocationApplication",
                "value": identity.application_id,
            }
        ],
    }


def inline_activities(scopes: list[dict[str, Any]]) -> list[str]:
    required: list[str] = []
    for scope in scopes:
        if scope.get("executionMode") == "evaluateInline":
            activities = str(scope.get("activities", ""))
            required.extend([item.strip() for item in activities.split(",") if item.strip()])
    return sorted(set(required))


def compute_protection_scopes(
    client: GraphClient,
    user: AuthenticatedUser,
    identity: AgentIdentity,
    app_name: str,
    app_version: str,
    client_request_id: str,
) -> dict[str, Any]:
    body = build_protection_scope_request(identity, app_name, app_version)
    path = USER_COMPUTE_PATH.format(user_id=user.user_id)
    response = client.post(
        path,
        body,
        extra_headers={"Client-Request-Id": client_request_id},
    )
    scopes = response.body.get("value", [])
    etag = response.headers.get("ETag") or response.headers.get("Etag")
    return {
        "status": response.status,
        "scopes": scopes,
        "etag": etag,
        "inline_activities": inline_activities(scopes),
        "path": path,
        "permission": "ProtectionScopes.Compute.User",
    }
