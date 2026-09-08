"""Repository-local documentation integrity checks."""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


class DocumentationTests(unittest.TestCase):
    def test_relative_markdown_links_resolve(self) -> None:
        broken: list[str] = []
        for markdown in ROOT.rglob("*.md"):
            if ".tmp" in markdown.parts or ".git" in markdown.parts:
                continue
            content = markdown.read_text(encoding="utf-8")
            for target in LINK_PATTERN.findall(content):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path_text = unquote(target.split("#", maxsplit=1)[0])
                if not (markdown.parent / path_text).resolve().exists():
                    broken.append(f"{markdown.relative_to(ROOT)} -> {target}")
        self.assertEqual(broken, [], "broken local documentation links")


if __name__ == "__main__":
    unittest.main()
