import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


class LinkTests(unittest.TestCase):
    def test_relative_markdown_links_resolve(self):
        missing = []
        for path in ROOT.rglob("*.md"):
            if any(part.startswith(".") for part in path.parts):
                continue
            text = path.read_text(encoding="utf-8")
            for match in LINK.findall(text):
                target = match.split("#", 1)[0].strip()
                if not target or target.startswith(("http://", "https://", "mailto:")):
                    continue
                if target.startswith("<"):
                    continue
                resolved = (path.parent / target).resolve()
                if not resolved.exists():
                    missing.append(f"{path.relative_to(ROOT)} -> {target}")
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
