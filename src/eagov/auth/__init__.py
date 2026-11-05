"""Microsoft Graph authentication examples."""

from eagov.auth.graph_auth import (
    ClientCredentialsTokenProvider,
    DelegatedTokenProvider,
    SyntheticTokenProvider,
    validate_permission_grant,
)

__all__ = [
    "ClientCredentialsTokenProvider",
    "DelegatedTokenProvider",
    "SyntheticTokenProvider",
    "validate_permission_grant",
]
