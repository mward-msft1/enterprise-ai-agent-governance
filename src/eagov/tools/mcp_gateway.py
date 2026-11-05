"""Allowlisted MCP JSON-RPC tool gateway.

Implements the subset of MCP-style JSON-RPC used by the reference workflow:
initialize, tools/list, and tools/call. Unknown tools are denied before any
handler runs. This is an original local gateway, not a copy of an external server.
"""

from __future__ import annotations

from typing import Any, Callable

from eagov.errors import ToolAuthorizationError
from eagov.models import ToolInvocation

ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]


def _knowledge_lookup(arguments: dict[str, Any]) -> dict[str, Any]:
    topic = str(arguments.get("topic") or "governance")
    return {
        "topic": topic,
        "summary": f"Synthetic knowledge card for {topic}. Not a live data source.",
        "classification": "SYNTHETIC",
    }


def _policy_status(_: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "reference-only",
        "classification": "SYNTHETIC",
    }


class McpGateway:
    def __init__(self, allowlist: list[str]):
        self.allowlist = list(allowlist)
        self.handlers: dict[str, ToolHandler] = {
            "knowledge_lookup": _knowledge_lookup,
            "policy_status": _policy_status,
        }

    def invoke(self, name: str, arguments: dict[str, Any] | None = None) -> ToolInvocation:
        arguments = arguments or {}
        if name not in self.allowlist:
            raise ToolAuthorizationError(f"Tool '{name}' is not on the allowlist")
        handler = self.handlers.get(name)
        if handler is None:
            raise ToolAuthorizationError(f"Tool '{name}' is allowlisted but has no handler")
        return ToolInvocation(
            name=name,
            arguments=arguments,
            allowed=True,
            result=handler(arguments),
            transport="in-process-mcp",
        )


def handle_json_rpc(gateway: McpGateway, message: dict[str, Any]) -> dict[str, Any]:
    method = message.get("method")
    request_id = message.get("id")
    if message.get("jsonrpc") != "2.0":
        return _error(request_id, -32600, "Invalid Request")
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2025-06-18",
                "serverInfo": {"name": "eagov-reference-mcp", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        }
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {"name": name, "description": "Allowlisted reference tool"}
                    for name in gateway.allowlist
                    if name in gateway.handlers
                ]
            },
        }
    if method == "tools/call":
        params = message.get("params") or {}
        try:
            invocation = gateway.invoke(params.get("name", ""), params.get("arguments") or {})
        except ToolAuthorizationError as exc:
            return _error(request_id, -32001, str(exc))
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"content": [invocation.result], "isError": False},
        }
    return _error(request_id, -32601, "Method not found")


def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}
