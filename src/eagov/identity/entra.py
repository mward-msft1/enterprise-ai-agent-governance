"""Validate identity configuration against the permissions matrix."""

from __future__ import annotations

import json
from pathlib import Path

from eagov.auth.graph_auth import validate_permission_grant
from eagov.config import REPO_ROOT, CustomerConfig, ExecutionMode
from eagov.errors import ConfigurationError

MATRIX_PATH = REPO_ROOT / "config" / "permissions-matrix.json"


def load_matrix(path: Path | None = None) -> dict:
    matrix_path = path or MATRIX_PATH
    return json.loads(matrix_path.read_text(encoding="utf-8"))


def validate_entra_configuration(config: CustomerConfig, matrix: dict | None = None) -> dict:
    matrix = matrix or load_matrix()
    granted = config.get("granted_permissions", {})
    delegated = granted.get("delegated", [])
    application = granted.get("application", [])
    if config.mode == ExecutionMode.TENANT and (not delegated and not application):
        raise ConfigurationError(
            "Tenant mode requires granted_permissions.delegated or application"
        )
    rows = []
    for item in matrix["permissions"]:
        rows.append(
            validate_permission_grant(
                {
                    "permission": item["name"],
                        "delegated": [item["name"]] if item["delegated"]["supported"] else [],
                        "application": [item["name"]] if item["application"]["supported"] else [],
                        "delegated_supported": item["delegated"]["supported"],
                        "application_supported": item["application"]["supported"],
                        "personal_account_supported": item.get("personal_account_supported", False),
                },
                delegated,
                application,
            )
        )
    user_path_ready = all(
        row["delegated_satisfied"]
        for row in rows
        if row["permission"]
        in {
            "ProtectionScopes.Compute.User",
            "Content.Process.User",
            "ContentActivity.Write",
        }
    )
    return {
        "permission_type_distinction": "delegated_and_application",
        "rows": rows,
        "user_workflow_delegated_ready": user_path_ready,
        "notes": matrix.get("notes", []),
    }
