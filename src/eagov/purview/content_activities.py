"""Record a Purview content activity without resending raw prompt text.

Verified against Microsoft Learn on 2026-11-05:
POST /users/{userId}/dataSecurityAndGovernance/activities/contentActivities
Permission: ContentActivity.Write for both delegated and application.
Success: 201 Created.
The audit body carries metadata, not the evaluated text.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from eagov.graph.client import GraphClient
from eagov.models import AgentIdentity, AuthenticatedUser, PolicyDecision

ACTIVITY_PATH = "/users/{user_id}/dataSecurityAndGovernance/activities/contentActivities"


def build_content_activity(
    identity: AgentIdentity,
    correlation_id: str,
    activity: str,
    app_name: str,
    app_version: str,
    decision: PolicyDecision,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "scopeIdentifier": None,
        "contentMetadata": {
            "contentEntries": [
                {
                    "@odata.type": "microsoft.graph.processConversationMetadata",
                    "identifier": correlation_id,
                    "name": f"{app_name} audit {decision.stage}",
                    "correlationId": correlation_id,
                    "sequenceNumber": 0 if activity == "uploadText" else 1,
                    "isTruncated": False,
                    "createdDateTime": now,
                    "modifiedDateTime": now,
                }
            ],
            "activityMetadata": {"activity": activity},
            "protectedAppMetadata": {
                "name": app_name,
                "version": app_version,
                "applicationLocation": {
                    "@odata.type": "microsoft.graph.policyLocationApplication",
                    "value": identity.application_id,
                },
            },
            "integratedAppMetadata": {"name": app_name, "version": app_version},
        },
        "additionalMetadata": {
            "decision": decision.reason,
            "allowed": decision.allowed,
            "stage": decision.stage,
            "classification": "SYNTHETIC" if decision.synthetic else "TENANT_PENDING_VALIDATION",
        },
    }


def record_content_activity(
    client: GraphClient,
    user: AuthenticatedUser,
    identity: AgentIdentity,
    correlation_id: str,
    activity: str,
    app_name: str,
    app_version: str,
    decision: PolicyDecision,
) -> dict[str, Any]:
    body = build_content_activity(
        identity, correlation_id, activity, app_name, app_version, decision
    )
    response = client.post(ACTIVITY_PATH.format(user_id=user.user_id), body)
    return {
        "status": response.status,
        "id": response.body.get("id"),
        "path": ACTIVITY_PATH.format(user_id=user.user_id),
        "permission": "ContentActivity.Write",
        "raw_content_included": False,
        "body": body,
    }
