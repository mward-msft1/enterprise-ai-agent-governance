"""Command-line entry point for the reference workflow."""

from __future__ import annotations

import argparse
import json
import sys

from eagov import NOT_PRODUCTION_READY
from eagov.config import load_config
from eagov.workflow import GovernanceWorkflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the enterprise AI agent governance reference workflow."
    )
    parser.add_argument("--mode", choices=["offline", "tenant"], default="offline")
    parser.add_argument("--config", default=None)
    parser.add_argument("--prompt", default="Summarize the public status page.")
    parser.add_argument("--tool", default="knowledge_lookup")
    parser.add_argument("--user-id", default="synthetic-user")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.mode == "tenant":
        print(NOT_PRODUCTION_READY, file=sys.stderr)
        print(
            "Tenant mode does not run from the CLI without an authorized GraphClient. "
            "Use examples/tenant_demo.py inside an authorized test tenant.",
            file=sys.stderr,
        )
        return 2
    config = load_config(args.config, mode=args.mode)
    result = GovernanceWorkflow(config).run(
        prompt=args.prompt,
        user_id=args.user_id,
        tool_name=args.tool,
    )
    print(
        f"status={result.status} synthetic={str(result.synthetic).lower()} production_ready=false",
        file=sys.stderr,
    )
    print(json.dumps(result.as_dict(), indent=2))
    return 0 if result.status == "allowed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
