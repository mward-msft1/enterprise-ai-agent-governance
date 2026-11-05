"""Entra token acquisition examples for delegated and application permissions.

Live token calls are not made unless ``execute`` is True and configuration
has passed placeholder checks. Offline mode uses a synthetic token that is
explicitly labeled and cannot be presented to Microsoft Graph.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from eagov.errors import ConfigurationError, TenantNotValidated

GRAPH_SCOPE = "https://graph.microsoft.com/.default"
TOKEN_PATH = "/oauth2/v2.0/token"
AUTHORIZE_PATH = "/oauth2/v2.0/authorize"


@dataclass
class TokenResult:
    access_token: str
    token_type: str
    permission_type: str
    synthetic: bool
    expires_in: int = 0
    scope: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "token_type": self.token_type,
            "permission_type": self.permission_type,
            "synthetic": self.synthetic,
            "expires_in": self.expires_in,
            "scope": self.scope,
            "access_token_present": bool(self.access_token),
        }


class SyntheticTokenProvider:
    def __init__(self, permission_type: str = "delegated", scopes: list[str] | None = None):
        self.permission_type = permission_type
        self.scopes = scopes or []

    def __call__(self) -> str:
        return "SYNTHETIC_TOKEN_NOT_VALID_FOR_MICROSOFT_GRAPH"

    def describe(self) -> TokenResult:
        return TokenResult(
            access_token=self(),
            token_type="Bearer",
            permission_type=self.permission_type,
            synthetic=True,
            expires_in=300,
            scope=" ".join(self.scopes),
        )


class ClientCredentialsTokenProvider:
    """Application-permission token via the OAuth 2.0 client credentials grant."""

    def __init__(self, tenant_id: str, client_id: str, client_secret: str, execute: bool = False):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.execute = execute
        self.last_request: dict[str, Any] | None = None

    def token_endpoint(self) -> str:
        return f"https://login.microsoftonline.com/{self.tenant_id}{TOKEN_PATH}"

    def build_request(self) -> dict[str, Any]:
        form = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": GRAPH_SCOPE,
            "grant_type": "client_credentials",
        }
        request = {
            "method": "POST",
            "url": self.token_endpoint(),
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "body_fields": ["client_id", "scope", "grant_type"],
            "secret_included": True,
        }
        self.last_request = request
        return {"request": request, "form": form}

    def __call__(self) -> str:
        built = self.build_request()
        if not self.execute:
            raise TenantNotValidated(
                "Client-credentials token acquisition was not executed. "
                "Set execute=True only in an authorized test tenant."
            )
        data = urlencode(built["form"]).encode("utf-8")
        http = Request(
            built["request"]["url"],
            data=data,
            headers=built["request"]["headers"],
            method="POST",
        )
        with urlopen(http, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        token = payload.get("access_token")
        if not token:
            raise ConfigurationError("Token response did not include access_token")
        return token


class DelegatedTokenProvider:
    """Authorization-code request builder for delegated Graph permissions.

    The interactive sign-in must be completed by a person in the test tenant.
    This class never embeds a refresh token or authorization code in source.
    """

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        redirect_uri: str,
        scopes: list[str],
        authorization_code: str | None = None,
        client_secret: str | None = None,
        execute: bool = False,
    ):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self.authorization_code = authorization_code
        self.client_secret = client_secret
        self.execute = execute

    def authorize_url(self, state: str) -> str:
        query = urlencode(
            {
                "client_id": self.client_id,
                "response_type": "code",
                "redirect_uri": self.redirect_uri,
                "response_mode": "query",
                "scope": " ".join(self.scopes),
                "state": state,
            }
        )
        return (
            f"https://login.microsoftonline.com/{self.tenant_id}{AUTHORIZE_PATH}?{query}"
        )

    def __call__(self) -> str:
        if not self.authorization_code or not self.execute:
            raise TenantNotValidated(
                "Delegated token exchange requires an authorization code "
                "collected in an authorized test tenant and execute=True."
            )
        form = {
            "client_id": self.client_id,
            "scope": " ".join(self.scopes),
            "code": self.authorization_code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        if self.client_secret:
            form["client_secret"] = self.client_secret
        data = urlencode(form).encode("utf-8")
        url = f"https://login.microsoftonline.com/{self.tenant_id}{TOKEN_PATH}"
        http = Request(
            url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urlopen(http, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        token = payload.get("access_token")
        if not token:
            raise ConfigurationError("Delegated token response missing access_token")
        return token


def validate_permission_grant(
    required: dict[str, Any],
    granted_delegated: list[str],
    granted_application: list[str],
) -> dict[str, Any]:
    """Compare a permissions-matrix row with granted Entra permissions."""

    delegated_needed = set(required.get("delegated", []))
    application_needed = set(required.get("application", []))
    missing_delegated = sorted(delegated_needed - set(granted_delegated))
    missing_application = sorted(application_needed - set(granted_application))
    return {
        "permission": required.get("permission"),
        "delegated_satisfied": not missing_delegated,
        "application_satisfied": not missing_application,
        "missing_delegated": missing_delegated,
        "missing_application": missing_application,
        "delegated_supported": required.get("delegated_supported", True),
        "application_supported": required.get("application_supported", True),
        "personal_account_supported": required.get("personal_account_supported", False),
    }
