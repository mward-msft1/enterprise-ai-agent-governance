"""Reject committed secrets. Placeholders and synthetic tokens are allowed."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    re.compile(r"AccountKey=[A-Za-z0-9+/=]{20,}"),
    re.compile(r"-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"InstrumentationKey=[0-9a-fA-F-]{36}"),
]
ALLOW_PARTS = {".git", ".venv", "__pycache__"}


def main() -> int:
    failures = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ALLOW_PARTS.intersection(path.parts):
            continue
        if path.suffix.lower() in {".png", ".zip"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in PATTERNS:
            if pattern.search(text):
                failures.append(f"{path.relative_to(ROOT)} matched {pattern.pattern}")
    if failures:
        print("\n".join(failures))
        return 1
    print("secret scan passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
