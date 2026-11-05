"""Agent identity and Entra permission validation."""

from eagov.identity.agent_identity import resolve_agent_identity
from eagov.identity.entra import validate_entra_configuration

__all__ = ["resolve_agent_identity", "validate_entra_configuration"]
