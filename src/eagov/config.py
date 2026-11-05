"""Customer configuration loading. Tenant values stay as REPLACE_WITH_* placeholders."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from eagov.errors import ConfigurationError

PLACEHOLDER_PREFIX = "REPLACE_WITH_"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TEMPLATE = REPO_ROOT / "config" / "customer.template.json"


class ExecutionMode(str, Enum):
    OFFLINE = "offline"
    TENANT = "tenant"


@dataclass
class CustomerConfig:
    mode: ExecutionMode
    values: dict[str, Any]
    source: str
    placeholders: list[str] = field(default_factory=list)

    def require_tenant_ready(self) -> None:
        if self.mode != ExecutionMode.TENANT:
            raise ConfigurationError("Tenant operations require mode=tenant")
        if self.placeholders:
            joined = ", ".join(self.placeholders)
            raise ConfigurationError(
                "Refusing tenant calls while placeholders remain: " + joined
            )

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)


def find_placeholders(payload: Any, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            found.extend(find_placeholders(value, path))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            found.extend(find_placeholders(value, f"{prefix}[{index}]"))
    elif isinstance(payload, str) and payload.startswith(PLACEHOLDER_PREFIX):
        found.append(prefix or payload)
    return found


def load_config(path: str | Path | None = None, mode: str | None = None) -> CustomerConfig:
    config_path = Path(path) if path else DEFAULT_TEMPLATE
    if not config_path.is_file():
        raise ConfigurationError(f"Configuration file not found: {config_path}")
    values = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(values, dict):
        raise ConfigurationError("Configuration root must be a JSON object")
    selected = mode or os.environ.get("EAGOV_MODE") or values.get("mode") or "offline"
    try:
        execution_mode = ExecutionMode(selected)
    except ValueError as exc:
        raise ConfigurationError(
            "mode must be 'offline' or 'tenant'"
        ) from exc
    placeholders = find_placeholders(values)
    return CustomerConfig(
        mode=execution_mode,
        values=values,
        source=str(config_path),
        placeholders=placeholders,
    )
