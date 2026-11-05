"""Evaluate prompts and responses with processContent.

Verified against Microsoft Learn on 2026-11-05:
POST /users/{userId}/dataSecurityAndGovernance/processContent
Least privileged: Content.Process.User
Higher: Content.Process.All
Successful bodies include protectionScopeState, policyActions, and processingErrors.
A restrictAccess action with restrictionAction=block must stop the workflow.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from eagov.graph.client import GraphClient
from eagov.models import AgentIdentity, AuthenticatedUser, PolicyDecision

PROCESS_PATH = "/users/{user_id}/dataSecurityAndGovernance/processContent"


def build_process_content_request(
    identity: AgentIdentity,
    user: AuthenticatedUser,
    text: str,
    activity: str,
    correlation_id: str,
    sequence_number: int,
    app_name: str,
    app_version: str,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "contentToProcess": {
            "contentEntries": [
                {
                    "@odata.type": "microsoft.graph.processConversationMetadata",
                    "identifier": correlation_id,
                    "content": {
                        "@odata.type": "microsoft.graph.textContent",
                        "data": text,
                    },
                    "agents": [
                        {
                            "@odata.type": "microsoft.graph.aiAgentInfo",
                            "blueprintId": identity.blueprint_id,
                            "identifier": identity.agent_id,
                            "name": identity.display_name,
                            "version": app_version,
                        }
                    ],
                    "name": f"{app_name} {activity}",
                    "correlationId": correlation_id,
                    "sequenceNumber": sequence_number,
                    "isTruncated": False,
                    "createdDateTime": now,
                    "modifiedDateTime": now,
                }
            ],
            "activityMetadata": {"activity": activity},
            "deviceMetadata": {
                "deviceType": "Unmanaged",
                "operatingSystemSpecifications": {
                    "operatingSystemPlatform": "reference-implementation",
                    "operatingSystemVersion": "0.1.0",
                },
            },
            "protectedAppMetadata": {
                "name": app_name,
                "version": app_version,
                "applicationLocation": {
                    "@odata.type": "microsoft.graph.policyLocationApplication",
                    "value": identity.application_id,
                },
            },
            "integratedAppMetadata": {"name": app_name, "version": app_version},
        }
    }


def interpret_process_content(stage: str, body: dict[str, Any], synthetic: bool) -> PolicyDecision:
    actions = list(body.get("policyActions") or [])
    errors = list(body.get("processingErrors") or [])
    blocked = any(
        action.get("restrictionAction") == "block"
        or action.get("action") == "restrictAccess"
        and action.get("restrictionAction") == "block"
        for action in actions
    )
    # Explicit block wins. Other restrictAccess values are treated as deny-by-default
    # until the customer maps them during tenant validation.
    if not blocked:
        blocked = any(action.get("action") == "restrictAccess" for action in actions)
    if errors:
        return PolicyDecision(
            stage=stage,
            allowed=False,
            execution_mode="error",
            protection_scope_state=str(body.get("protectionScopeState") or "unknown"),
            policy_actions=actions,
            processing_errors=errors,
            reason="processContent returned processingErrors",
            synthetic=synthetic,
        )
    return PolicyDecision(
        stage=stage,
        allowed=not blocked,
        execution_mode="evaluateInline",
        protection_scope_state=str(body.get("protectionScopeState") or "notModified"),
        policy_actions=actions,
        processing_errors=errors,
        reason="block" if blocked else "allow",
        synthetic=synthetic,
    )


def evaluate_content(
    client: GraphClient,
    user: AuthenticatedUser,
    identity: AgentIdentity,
    text: str,
    activity: str,
    stage: str,
    correlation_id: str,
    sequence_number: int,
    app_name: str,
    app_version: str,
    etag: str | None,
    synthetic: bool,
) -> PolicyDecision:
    body = build_process_content_request(
        identity,
        user,
        text,
        activity,
        correlation_id,
        sequence_number,
        app_name,
        app_version,
    )
    headers = {"Client-Request-Id": correlation_id}
    if etag:
        headers["If-None-Match"] = etag
    response = client.post(
        PROCESS_PATH.format(user_id=user.user_id),
        body,
        extra_headers=headers,
    )
    if response.status == 204:
        return PolicyDecision(
            stage=stage,
            allowed=True,
            execution_mode="noContent",
            protection_scope_state="notModified",
            reason="204 No Content",
            synthetic=synthetic,
        )
    return interpret_process_content(stage, response.body, synthetic)
