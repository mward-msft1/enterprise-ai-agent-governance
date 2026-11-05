"""Check dependency manifests without installing tenant packages."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    runtime = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    tenant = (ROOT / "requirements-tenant.txt").read_text(encoding="utf-8")
    if "microsoft-opentelemetry" not in tenant or "agent-framework" not in tenant:
        print("tenant manifest is missing expected packages")
        return 1
    for name in ("azure-identity", "microsoft-opentelemetry", "agent-framework"):
        if name in runtime and not name.startswith("#"):
            # runtime file is comments plus no package lines; a package line would be a problem
            for line in runtime.splitlines():
                if line.strip().startswith(name):
                    print("tenant package must not be a required offline dependency")
                    return 1
    print("dependency manifest check passed")
    print("tenant packages were not installed and have no reviewed vulnerability scan in this environment")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
