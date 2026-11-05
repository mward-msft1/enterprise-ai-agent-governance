"""Agent 365 discovery and SDK boundary adapters."""

from eagov.agent365.discovery import list_packages
from eagov.agent365.inventory import normalize_inventory
from eagov.agent365.sdk_adapter import sdk_capability_map

__all__ = ["list_packages", "normalize_inventory", "sdk_capability_map"]
