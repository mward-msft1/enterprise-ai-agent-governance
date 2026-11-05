"""Boundary between Microsoft Agent 365 SDK and this reference app.

Microsoft Learn (reviewed 2026-11-05) states that the Agent 365 SDK does not
build agents. It extends an agent with identity, notifications, and governed
tooling. Observability is provided by Microsoft OpenTelemetry Distro, not by
treating the Agent 365 SDK as a model runtime.
"""

from __future__ import annotations


def sdk_capability_map() -> dict:
    return {
        "builds_agents": False,
        "capabilities": {
            "identity": "Entra agent identity blueprint and agent instance",
            "tooling": "Governed Microsoft 365 tooling through the Agent 365 SDK",
            "notifications": "Agent 365 notification extensions",
            "observability": "Microsoft OpenTelemetry Distro, separate from the SDK",
        },
        "python_otel_package": "microsoft-opentelemetry",
        "otel_entrypoint": "microsoft.opentelemetry.use_microsoft_opentelemetry",
        "otel_permission_delegated": "Agent365.Observability.OtelWrite",
        "s2s_route": (
            "A registered agent instance can export on the service-to-service "
            "route without the delegated Observability permission. Blueprint "
            "agents created with a365 setup all need an app-only resolver unless "
            "the delegated permission and admin consent are granted."
        ),
        "tenant_validated": False,
    }
