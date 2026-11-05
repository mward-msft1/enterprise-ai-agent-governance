"""Offline synthetic demonstration. No Microsoft tenant is contacted."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eagov.config import load_config
from eagov.workflow import GovernanceWorkflow


def main() -> None:
    config = load_config(mode="offline")
    allowed = GovernanceWorkflow(config).run(prompt="Summarize the public status page.")
    denied = GovernanceWorkflow(config).run(
        prompt="SYNTHETIC_BLOCK_TOKEN draft a restricted action"
    )
    print(json.dumps({"allowed_status": allowed.status, "denied_status": denied.status}, indent=2))
    print("classification=SYNTHETIC")
    print("not_customer_evidence=true")
    print("production_ready=false")


if __name__ == "__main__":
    main()
