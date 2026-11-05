"""Model execution through Microsoft Agent Framework when the package is installed.

Official Python surface reviewed on 2026-11-05:
    from agent_framework import Agent
    from agent_framework.openai import OpenAIChatClient

Azure OpenAI is configured with an OpenAI-compatible base URL and deployment.
This module does not call a model unless tenant mode is selected, placeholders
are gone, and the package imports. Offline mode uses a deterministic stub so
the governance workflow remains executable without credentials.
"""

from __future__ import annotations

from typing import Any

from eagov.config import CustomerConfig, ExecutionMode
from eagov.errors import ConfigurationError, TenantNotValidated


class AgentFrameworkRunner:
    def __init__(self, config: CustomerConfig):
        self.config = config

    def execute(self, prompt: str, tool_names: list[str]) -> dict[str, Any]:
        if self.config.mode == ExecutionMode.OFFLINE:
            return self._synthetic(prompt, tool_names)
        return self._tenant(prompt, tool_names)

    def _synthetic(self, prompt: str, tool_names: list[str]) -> dict[str, Any]:
        requested = tool_names[0] if tool_names else None
        return {
            "provider": "synthetic-agent-framework-stub",
            "model": "SYNTHETIC_MODEL",
            "text": (
                "Synthetic response for correlation testing. "
                "No model was called. Prompt length="
                f"{len(prompt)}."
            ),
            "requested_tool": requested,
            "package_imported": False,
            "synthetic": True,
            "production_ready": False,
        }

    def _tenant(self, prompt: str, tool_names: list[str]) -> dict[str, Any]:
        self.config.require_tenant_ready()
        azure = self.config.get("azure_openai", {})
        endpoint = str(azure.get("endpoint", "")).rstrip("/")
        deployment = azure.get("deployment")
        if not endpoint or not deployment:
            raise ConfigurationError("azure_openai.endpoint and deployment are required")
        try:
            from agent_framework import Agent
            from agent_framework.openai import OpenAIChatClient
        except ImportError as exc:
            raise TenantNotValidated(
                "agent-framework and agent-framework-openai are not installed. "
                "Install them in the authorized test tenant environment before "
                "claiming model integration. Offline mode remains available."
            ) from exc
        client = OpenAIChatClient(
            model=deployment,
            base_url=f"{endpoint}/openai/v1/",
            api_key=azure.get("api_key"),
        )
        agent = Agent(
            client=client,
            instructions=(
                "You are an enterprise agent. Use only tools the governance "
                "gateway has already authorized. Do not invent citations."
            ),
            name=self.config.get("agent_identity", {}).get("display_name", "agent"),
        )
        # The live call is intentionally not wrapped as success until a tenant
        # test records evidence. Callers that reach here have opted into network.
        result = agent.run(prompt)
        text = getattr(result, "text", None) or str(result)
        return {
            "provider": "microsoft-agent-framework",
            "model": deployment,
            "text": text,
            "requested_tool": tool_names[0] if tool_names else None,
            "package_imported": True,
            "synthetic": False,
            "production_ready": False,
            "validation_required": True,
        }
