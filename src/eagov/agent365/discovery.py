"""Discover Agent 365 / Copilot catalog packages.

Verified against Microsoft Learn on 2026-11-05:
GET https://graph.microsoft.com/v1.0/copilot/admin/catalog/packages
Least privileged: CopilotPackages.Read.All
Supported for delegated and application permissions.
Requires a Microsoft Agent 365 license. Global cloud only in the published matrix.
"""

from __future__ import annotations

from typing import Any

from eagov.graph.client import GraphClient

PACKAGES_PATH = "/copilot/admin/catalog/packages"


def list_packages(client: GraphClient, top: int = 50) -> dict[str, Any]:
    response = client.get(f"{PACKAGES_PATH}?$top={top}")
    packages = response.body.get("value", [])
    return {
        "status": response.status,
        "path": PACKAGES_PATH,
        "permission": "CopilotPackages.Read.All",
        "count": len(packages),
        "packages": packages,
        "license_requirement": "Microsoft Agent 365",
        "production_note": (
            "Package Management API availability depends on license and cloud. "
            "This adapter was not executed against a tenant in the authoring environment."
        ),
    }
