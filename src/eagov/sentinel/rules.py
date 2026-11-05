"""Load Sentinel analytics-rule ARM templates."""

from __future__ import annotations

import json
from pathlib import Path

from eagov.config import REPO_ROOT

ARM_PATH = REPO_ROOT / "detections" / "arm" / "analytics-rules.json"


def load_arm_template(path: Path | None = None) -> dict:
    return json.loads((path or ARM_PATH).read_text(encoding="utf-8"))


def scheduled_rule_ids(template: dict | None = None) -> list[str]:
    template = template or load_arm_template()
    return [
        resource.get("properties", {}).get("displayName", "")
        for resource in template.get("resources", [])
    ]
