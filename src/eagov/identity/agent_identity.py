"""Resolve the Entra-backed agent identity used by the workflow."""

from __future__ import annotations

from eagov.config import CustomerConfig, ExecutionMode
from eagov.errors import ConfigurationError
from eagov.models import AgentIdentity


def resolve_agent_identity(config: CustomerConfig) -> AgentIdentity:
    identity = config.get("agent_identity", {})
    tenant = config.get("tenant", {})
    if config.mode == ExecutionMode.TENANT:
        config.require_tenant_ready()
    required = {
        "agent_id": identity.get("agent_id"),
        "blueprint_id": identity.get("blueprint_id"),
        "application_id": identity.get("application_id"),
        "display_name": identity.get("display_name"),
        "tenant_id": tenant.get("tenant_id"),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise ConfigurationError("Agent identity is missing: " + ", ".join(missing))
    if required["agent_id"] == required["application_id"]:
        raise ConfigurationError(
            "Agent instance ID and application ID must be distinct objects"
        )
    return AgentIdentity(
        agent_id=required["agent_id"],
        blueprint_id=required["blueprint_id"],
        application_id=required["application_id"],
        display_name=required["display_name"],
        tenant_id=required["tenant_id"],
    )
