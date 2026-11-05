"""Authorized test-tenant entry point.

This file does not call Microsoft when configuration still contains
REPLACE_WITH_* placeholders. Replace those values only in a secret store,
never in this repository, then construct a GraphClient with a real token
provider and pass execute=True on that provider.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eagov.config import load_config
from eagov.errors import ConfigurationError


def main() -> int:
    config = load_config(mode="tenant")
    try:
        config.require_tenant_ready()
    except ConfigurationError as exc:
        print("TENANT_VALIDATION_REQUIRED")
        print(exc)
        print("No Graph, Purview, Agent 365, Defender, or Sentinel call was made.")
        return 2
    print(
        "Configuration has no placeholders. Wire ClientCredentialsTokenProvider "
        "or DelegatedTokenProvider with execute=True in an authorized test tenant "
        "before constructing GovernanceWorkflow. This script still does not place "
        "a live call automatically."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
