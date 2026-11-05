"""Typed errors for configuration and policy enforcement."""


class GovernanceError(Exception):
    """Base error for the reference implementation."""


class ConfigurationError(GovernanceError):
    """Raised when tenant configuration is incomplete or still templated."""


class PolicyDenied(GovernanceError):
    """Raised when Purview or the local policy engine denies content."""

    def __init__(self, stage: str, decision: dict):
        self.stage = stage
        self.decision = decision
        super().__init__(f"Policy denied at {stage}")


class ToolAuthorizationError(GovernanceError):
    """Raised when a tool or MCP call is outside the allowlist."""


class TenantNotValidated(GovernanceError):
    """Raised when a live Microsoft call is attempted without authorization."""
