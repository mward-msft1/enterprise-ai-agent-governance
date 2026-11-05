"""Shared data models for the governance workflow."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class AgentIdentity:
    agent_id: str
    blueprint_id: str
    application_id: str
    display_name: str
    tenant_id: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class AuthenticatedUser:
    user_id: str
    user_principal_name: str
    permission_type: str
    scopes: list[str]
    token_source: str
    synthetic: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PolicyDecision:
    stage: str
    allowed: bool
    execution_mode: str
    protection_scope_state: str
    policy_actions: list[dict[str, Any]] = field(default_factory=list)
    processing_errors: list[dict[str, Any]] = field(default_factory=list)
    reason: str = ""
    synthetic: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ToolInvocation:
    name: str
    arguments: dict[str, Any]
    allowed: bool
    result: dict[str, Any]
    transport: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowResult:
    correlation_id: str
    mode: str
    status: str
    stages: list[str]
    identity: dict[str, Any]
    user: dict[str, Any]
    prompt_decision: dict[str, Any]
    response_decision: dict[str, Any] | None
    framework: dict[str, Any] | None
    tool: dict[str, Any] | None
    audit: dict[str, Any]
    telemetry: dict[str, Any]
    investigation: dict[str, Any]
    synthetic: bool
    production_ready: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
