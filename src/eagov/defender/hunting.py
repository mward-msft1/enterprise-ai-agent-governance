"""Build a Defender/Sentinel investigation package from the detection library."""

from __future__ import annotations

import json
from pathlib import Path

from eagov.config import REPO_ROOT

CATALOG_PATH = REPO_ROOT / "detections" / "catalog.json"


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def load_hunting_query(relative_path: str) -> str:
    path = REPO_ROOT / relative_path
    return path.read_text(encoding="utf-8")


def build_investigation_bundle(correlation_id: str) -> dict:
    catalog = load_catalog()
    queries = []
    for detection in catalog["detections"]:
        queries.append(
            {
                "detection_id": detection["id"],
                "priority": detection["priority"],
                "surface": detection["surface"],
                "query_file": detection["query_file"],
                "correlation_filter": f'CorrelationId == "{correlation_id}"'
                if detection["surface"] == "sentinel-custom"
                else "Use ReportId or AlertId from the hunting result; do not interpolate the user prompt.",
            }
        )
    return {
        "correlation_id": correlation_id,
        "executed_against_tenant": False,
        "production_ready": False,
        "queries": queries,
        "note": (
            "This bundle lists queries to run in Defender advanced hunting or "
            "Sentinel. The authoring environment did not execute them."
        ),
    }
