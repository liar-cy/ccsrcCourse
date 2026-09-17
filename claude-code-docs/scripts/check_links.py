#!/usr/bin/env python3
"""Validate every local Markdown and image link in the repo.

The site runs docsify with `relativePath: true`, which means each context
resolves links differently. Getting it wrong produces links that work on the
published site but 404 on GitHub, or the reverse. The rules:

  docs/*.md        cross-links are same-directory relative  -> 04-上下文工程.md
  _sidebar.md      root-absolute                            -> /docs/04-上下文工程.md
  _home.md         root-absolute                            -> /docs/04-上下文工程.md
  README*.md       GitHub-relative                          -> ./docs/04-上下文工程.md

Run from the repo root. Exits non-zero on any violation.
"""

from __future__ import annotations

import glob
import os
import re
import sys
import urllib.parse

MD_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
IMG_LINK = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
FENCE = re.compile(r"^(```|~~~).*?^\1", re.MULTILINE | re.DOTALL)
CODE_SPAN = re.compile(r"(`+)(?:(?!\1).)*?\1", re.DOTALL)

ROOT_PAGES = ("_sidebar.md", "_home.md")
README_PAGES = ("README.md", "README_EN.md")


def blank_code(text: str) -> str:
    """Replace code blocks and spans with spaces of equal length.

    Link syntax inside code is illustrative, not a link — the contributing
    guide documents the link conventions by showing them. Blanking rather
    than deleting keeps every offset intact so reported line numbers stay
    correct.
    """
    for pattern in (FENCE, CODE_SPAN):
        text = pattern.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    return text


def is_external(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "#"))


def resolve(source: str, target: str) -> str:
    """Map a link to the repo-relative path it should point at on disk."""
    path = urllib.parse.unquote(target.split("#", 1)[0])
    if not path:
        return ""
    if path.startswith("/"):
        return path.lstrip("/")
    return os.path.normpath(os.path.join(os.path.dirname(source), path))


def check_style(source: str, target: str) -> str | None:
    """Return a message when a link works but uses the wrong convention."""
    if source.startswith("docs/") and target.startswith("docs/"):
        return "chapter cross-links must be same-directory relative, not 'docs/...'"
    if source in ROOT_PAGES and not target.startswith("/"):
        return "sidebar/home links must be root-absolute, starting with '/'"
    if source in README_PAGES and target.startswith("/"):
        return "README links are read on GitHub, use './docs/...' not '/docs/...'"
    return None


def main() -> int:
    sources = sorted(glob.glob("docs/*.md")) + [
        p for p in (*ROOT_PAGES, *README_PAGES, "CONTRIBUTING.md", "CONTRIBUTING_EN.md")
        if os.path.exists(p)
    ]

    broken: list[str] = []
    style: list[str] = []
    checked = 0

    for source in sources:
        text = blank_code(open(source, encoding="utf-8").read())
        for pattern in (MD_LINK, IMG_LINK):
            for match in pattern.finditer(text):
                target = match.group(1).strip()
                if is_external(target) or not target:
                    continue
                checked += 1
                path = resolve(source, target)
                if path and not os.path.exists(path):
                    line = text[: match.start()].count("\n") + 1
                    broken.append(f"{source}:{line}  ->  {target}")
                    continue
                problem = check_style(source, target)
                if problem:
                    line = text[: match.start()].count("\n") + 1
                    style.append(f"{source}:{line}  ->  {target}\n    {problem}")

    if broken:
        print(f"✗ {len(broken)} broken link(s):\n")
        print("\n".join(broken))
    if style:
        print(f"\n✗ {len(style)} link(s) using the wrong convention:\n")
        print("\n".join(style))
    if broken or style:
        print(f"\nchecked {checked} local links across {len(sources)} files")
        return 1

    print(f"✓ {checked} local links across {len(sources)} files, all resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
