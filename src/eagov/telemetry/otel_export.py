"""Microsoft OpenTelemetry export boundary.

Offline mode records spans in memory. Tenant mode attempts to configure
microsoft-opentelemetry only after placeholders are removed. If the package
is absent, the call is reported as not exported rather than faked as success.

Reviewed 2026-11-05:
- pip package: microsoft-opentelemetry
- entry point: use_microsoft_opentelemetry(enable_a365=True, a365_token_resolver=...)
- delegated permission: Agent365.Observability.OtelWrite
- Agent 365 exporter does not use an Application Insights connection string
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from eagov.config import CustomerConfig, ExecutionMode


class TelemetryExporter:
    def __init__(self, config: CustomerConfig):
        self.config = config
        self.spans: list[dict[str, Any]] = []

    def span(self, name: str, attributes: dict[str, Any]) -> None:
        self.spans.append(
            {
                "name": name,
                "attributes": attributes,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "classification": "SYNTHETIC"
                if self.config.mode == ExecutionMode.OFFLINE
                else "TENANT_LOCAL_BUFFER",
            }
        )

    def export(self, correlation_id: str) -> dict[str, Any]:
        if self.config.mode == ExecutionMode.OFFLINE:
            return {
                "exported": True,
                "destination": "in-memory",
                "span_count": len(self.spans),
                "span_names": [span["name"] for span in self.spans],
                "correlation_id": correlation_id,
                "synthetic": True,
                "agent365_exported": False,
                "app_insights_exported": False,
                "production_ready": False,
            }
        self.config.require_tenant_ready()
        a365_ready = False
        app_insights_ready = bool(
            self.config.get("application_insights", {}).get("connection_string")
        )
        detail = "microsoft-opentelemetry is not installed"
        try:
            from microsoft.opentelemetry import use_microsoft_opentelemetry
        except ImportError:
            use_microsoft_opentelemetry = None
        if use_microsoft_opentelemetry is not None:
            detail = (
                "Package imported. Live Agent 365 export was not invoked by the "
                "unit-tested path because a token resolver must be supplied by "
                "the authorized tenant run."
            )
            a365_ready = False
        return {
            "exported": False,
            "destination": "not-exported",
            "span_count": len(self.spans),
            "span_names": [span["name"] for span in self.spans],
            "correlation_id": correlation_id,
            "synthetic": False,
            "agent365_exported": a365_ready,
            "app_insights_exported": False,
            "app_insights_configured": app_insights_ready,
            "detail": detail,
            "permission": "Agent365.Observability.OtelWrite",
            "production_ready": False,
        }
