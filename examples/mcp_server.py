"""Local MCP-style JSON-RPC server for the allowlisted reference tools."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eagov.tools.mcp_gateway import McpGateway, handle_json_rpc


def main() -> None:
    gateway = McpGateway(["knowledge_lookup", "policy_status"])
    for line in sys.stdin:
        if not line.strip():
            continue
        message = json.loads(line)
        response = handle_json_rpc(gateway, message)
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
