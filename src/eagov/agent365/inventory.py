"""Normalize catalog packages into a governance inventory."""

from __future__ import annotations

from typing import Any


def normalize_inventory(packages: list[dict[str, Any]], synthetic: bool) -> list[dict[str, Any]]:
    inventory = []
    for package in packages:
        inventory.append(
            {
                "id": package.get("id"),
                "display_name": package.get("displayName") or package.get("name"),
                "type": package.get("type") or package.get("@odata.type"),
                "supported_hosts": package.get("supportedHosts") or [],
                "classification": "SYNTHETIC" if synthetic else "TENANT_UNVALIDATED",
                "not_customer_evidence": synthetic,
            }
        )
    return inventory
