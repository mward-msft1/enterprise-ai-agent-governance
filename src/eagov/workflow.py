"""End-to-end custom-agent governance workflow.

Agent identity
→ user authentication
→ Purview protection scope computation
→ prompt policy evaluation
→ Microsoft Agent Framework execution
→ authorized tool/MCP interaction
→ response policy evaluation
→ audit recording
→ Microsoft OpenTelemetry export
→ Defender/Sentinel investigation bundle
"""

from __future__ import annotations

import uuid
from typing import Any

from eagov.agent365.discovery import list_packages
from eagov.agent365.inventory import normalize_inventory
from eagov.auth.graph_auth import SyntheticTokenProvider
from eagov.config import CustomerConfig, ExecutionMode
from eagov.defender.hunting import build_investigation_bundle
from eagov.errors import ConfigurationError, ToolAuthorizationError
from eagov.framework.agent_runner import AgentFrameworkRunner
from eagov.graph.client import GraphClient, GraphResponse, RecordingTransport
from eagov.identity.agent_identity import resolve_agent_identity
from eagov.identity.entra import validate_entra_configuration
from eagov.models import AuthenticatedUser, PolicyDecision, WorkflowResult
from eagov.purview.content_activities import record_content_activity
from eagov.purview.process_content import evaluate_content
from eagov.purview.protection_scopes import compute_protection_scopes
from eagov.telemetry.otel_export import TelemetryExporter
from eagov.tools.mcp_gateway import McpGateway, handle_json_rpc

BLOCK_MARKER = "SYNTHETIC_BLOCK_TOKEN"
RESPONSE_BLOCK_MARKER = "SYNTHETIC_RESPONSE_BLOCK"


class GovernanceWorkflow:
    def __init__(self, config: CustomerConfig, client: GraphClient | None = None):
        self.config = config
        self.client = client or self._default_client()
        self.telemetry = TelemetryExporter(config)

    def _default_client(self) -> GraphClient:
        if self.config.mode == ExecutionMode.OFFLINE:
            transport = RecordingTransport(
                scripted=[
                    GraphResponse(
                        status=200,
                        body={
                            "value": [
                                {
                                    "id": "synthetic-package",
                                    "displayName": "Synthetic Reference Agent",
                                    "type": "agent",
                                    "supportedHosts": ["Copilot"],
                                }
                            ]
                        },
                        headers={},
                    ),
                    GraphResponse(
                        status=200,
                        body={
                            "value": [
                                {
                                    "activities": "uploadText",
                                    "executionMode": "evaluateInline",
                                    "locations": [
                                        {"value": self.config.get("agent_identity", {}).get("application_id")}
                                    ],
                                    "policyActions": [],
                                }
                            ]
                        },
                        headers={"ETag": "synthetic-etag"},
                    ),
                    GraphResponse(status=200, body=self._synthetic_policy("prompt"), headers={}),
                    GraphResponse(status=200, body=self._synthetic_policy("response"), headers={}),
                    GraphResponse(
                        status=201,
                        body={"id": "synthetic-content-activity"},
                        headers={},
                    ),
                    GraphResponse(
                        status=201,
                        body={"id": "synthetic-content-activity-response"},
                        headers={},
                    ),
                ]
            )
            return GraphClient(SyntheticTokenProvider(), transport=transport)
        raise ConfigurationError(
            "Tenant mode requires an authorized GraphClient. "
            "Construct GovernanceWorkflow(config, client=...) after token acquisition."
        )

    def _synthetic_policy(self, stage: str) -> dict[str, Any]:
        return {
            "protectionScopeState": "notModified",
            "policyActions": [],
            "processingErrors": [],
            "stage": stage,
        }

    def run(
        self,
        prompt: str,
        user_id: str = "synthetic-user",
        user_principal_name: str = "synthetic.user@example.invalid",
        tool_name: str = "knowledge_lookup",
        tool_arguments: dict[str, Any] | None = None,
    ) -> WorkflowResult:
        correlation_id = str(uuid.uuid4())
        stages: list[str] = []
        app = self.config.get("application", {})
        app_name = app.get("name", "enterprise-ai-agent-governance")
        app_version = app.get("version", "0.1.0")

        identity = resolve_agent_identity(self.config)
        stages.append("agent_identity")
        self.telemetry.span("agent.identity", identity.as_dict())

        entra = validate_entra_configuration(self.config)
        user = AuthenticatedUser(
            user_id=user_id,
            user_principal_name=user_principal_name,
            permission_type="delegated" if self.config.mode == ExecutionMode.OFFLINE else "tenant-supplied",
            scopes=self.config.get("granted_permissions", {}).get("delegated", []),
            token_source="synthetic" if self.config.mode == ExecutionMode.OFFLINE else "caller-supplied",
            synthetic=self.config.mode == ExecutionMode.OFFLINE,
        )
        stages.append("user_authentication")
        self.telemetry.span("user.authentication", {"permission_type": user.permission_type})

        inventory_raw = list_packages(self.client)
        inventory = normalize_inventory(
            inventory_raw["packages"],
            synthetic=self.config.mode == ExecutionMode.OFFLINE,
        )
        stages.append("agent365_inventory")

        scopes = compute_protection_scopes(
            self.client,
            user,
            identity,
            app_name,
            app_version,
            correlation_id,
        )
        stages.append("protection_scopes")
        self.telemetry.span(
            "purview.protection_scopes",
            {"inline_activities": scopes["inline_activities"]},
        )

        prompt_decision = self._evaluate(
            "prompt",
            "uploadText",
            prompt,
            user,
            identity,
            correlation_id,
            0,
            app_name,
            app_version,
            scopes.get("etag"),
        )
        stages.append("prompt_policy")
        self.telemetry.span("purview.prompt", {"allowed": prompt_decision.allowed})

        framework_result = None
        tool_result = None
        response_decision = None
        if prompt_decision.allowed:
            framework_result = AgentFrameworkRunner(self.config).execute(prompt, [tool_name])
            stages.append("agent_framework")
            self.telemetry.span("agent.framework", {"provider": framework_result["provider"]})
            tool_result = self._invoke_tool(tool_name, tool_arguments or {"topic": "governance"})
            stages.append("tool_mcp")
            self.telemetry.span("tool.mcp", {"tool": tool_name, "allowed": tool_result["allowed"]})
            response_text = framework_result["text"]
            if RESPONSE_BLOCK_MARKER in prompt:
                response_text = RESPONSE_BLOCK_MARKER + " " + response_text
            response_decision = self._evaluate(
                "response",
                "downloadText",
                response_text,
                user,
                identity,
                correlation_id,
                1,
                app_name,
                app_version,
                scopes.get("etag"),
            )
            stages.append("response_policy")
            self.telemetry.span("purview.response", {"allowed": response_decision.allowed})
        else:
            response_decision = None

        status = "allowed"
        if not prompt_decision.allowed:
            status = "denied_prompt"
        elif response_decision and not response_decision.allowed:
            status = "denied_response"
        elif tool_result and not tool_result["allowed"]:
            status = "denied_tool"

        audit_decision = response_decision or prompt_decision
        audit = record_content_activity(
            self.client,
            user,
            identity,
            correlation_id,
            "uploadText" if not prompt_decision.allowed else "downloadText",
            app_name,
            app_version,
            audit_decision,
        )
        stages.append("audit")
        audit["workflow_status"] = status
        telemetry = self.telemetry.export(correlation_id)
        stages.append("otel_export")
        investigation = build_investigation_bundle(correlation_id)
        stages.append("defender_sentinel")

        return WorkflowResult(
            correlation_id=correlation_id,
            mode=self.config.mode.value,
            status=status,
            stages=stages,
            identity=identity.as_dict(),
            user=user.as_dict(),
            prompt_decision=prompt_decision.as_dict(),
            response_decision=response_decision.as_dict() if response_decision else None,
            framework=framework_result,
            tool=tool_result,
            audit={
                "content_activity": audit,
                "entra": entra,
                "inventory": inventory,
                "scopes": {
                    "inline_activities": scopes["inline_activities"],
                    "etag": scopes.get("etag"),
                },
            },
            telemetry=telemetry,
            investigation=investigation,
            synthetic=self.config.mode == ExecutionMode.OFFLINE,
            production_ready=False,
        )

    def _evaluate(
        self,
        stage: str,
        activity: str,
        text: str,
        user: AuthenticatedUser,
        identity,
        correlation_id: str,
        sequence: int,
        app_name: str,
        app_version: str,
        etag: str | None,
    ) -> PolicyDecision:
        if self.config.mode == ExecutionMode.OFFLINE and self._should_synthetic_block(stage, text):
            # Consume the scripted allow response so later calls stay aligned.
            self.client.post("/synthetic/discard", {})
            return PolicyDecision(
                stage=stage,
                allowed=False,
                execution_mode="synthetic-inline",
                protection_scope_state="notModified",
                policy_actions=[
                    {
                        "@odata.type": "#microsoft.graph.restrictAccessAction",
                        "action": "restrictAccess",
                        "restrictionAction": "block",
                    }
                ],
                reason="synthetic block marker",
                synthetic=True,
            )
        return evaluate_content(
            self.client,
            user,
            identity,
            text,
            activity,
            stage,
            correlation_id,
            sequence,
            app_name,
            app_version,
            etag,
            synthetic=self.config.mode == ExecutionMode.OFFLINE,
        )

    def _should_synthetic_block(self, stage: str, text: str) -> bool:
        if stage == "prompt" and BLOCK_MARKER in text:
            return True
        if stage == "response" and RESPONSE_BLOCK_MARKER in text:
            return True
        return False

    def _invoke_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        allowlist = self.config.get("tools", {}).get("allowlist", [])
        gateway = McpGateway(allowlist)
        initialized = handle_json_rpc(
            gateway, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        )
        listed = handle_json_rpc(gateway, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        called = handle_json_rpc(
            gateway,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments},
            },
        )
        allowed = "error" not in called
        return {
            "allowed": allowed,
            "initialize": initialized.get("result", {}).get("serverInfo"),
            "listed_tools": [tool["name"] for tool in listed.get("result", {}).get("tools", [])],
            "call": called,
        }
