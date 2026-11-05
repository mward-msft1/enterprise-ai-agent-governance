"""Validate the reference APIM policy without deploying API Management."""

from __future__ import annotations

from pathlib import Path

from eagov.config import REPO_ROOT
from eagov.errors import ConfigurationError

POLICY_PATH = REPO_ROOT / "deploy" / "apim-policy.xml"


def load_policy(path: Path | None = None) -> str:
    return (path or POLICY_PATH).read_text(encoding="utf-8")


def validate_policy(policy_xml: str) -> dict:
    required = [
        "validate-jwt",
        "https://login.microsoftonline.com/",
        "rate-limit-by-key",
        "set-header",
        "X-Correlation-Id",
    ]
    missing = [token for token in required if token not in policy_xml]
    if "client_secret" in policy_xml.lower() or "REPLACE_WITH_SECRET" in policy_xml:
        raise ConfigurationError("APIM policy must not contain a client secret")
    return {"valid": not missing, "missing": missing}
