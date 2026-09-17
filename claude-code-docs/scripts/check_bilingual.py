#!/usr/bin/env python3
"""Check that every chapter exists in both Chinese and English.

Chapters are paired by their numeric prefix: docs/04-上下文工程.md is the
Chinese side of docs/04-Context-Engineering.md. A chapter that exists in only
one language is a gap; a pair whose lengths diverge sharply usually means one
side received an update the other did not.

Run from the repo root. Exits non-zero when a chapter is missing a language.
"""

from __future__ import annotations

import glob
import os
import re
import sys

NUMBER = re.compile(r"^(\d{2})-")
# A chapter is the English side when its body is mostly ASCII.
CJK = re.compile(r"[一-鿿]")

# Ratio beyond which the two sides are flagged as possibly out of sync.
DIVERGENCE = 1.6


def language_of(path: str) -> str:
    text = open(path, encoding="utf-8").read()
    cjk = len(CJK.findall(text))
    return "zh" if cjk > len(text) * 0.05 else "en"


def main() -> int:
    chapters: dict[str, dict[str, str]] = {}
    for path in sorted(glob.glob("docs/*.md")):
        match = NUMBER.match(os.path.basename(path))
        if not match:
            continue
        chapters.setdefault(match.group(1), {})[language_of(path)] = path

    missing: list[str] = []
    diverged: list[str] = []

    for number, pair in sorted(chapters.items()):
        if len(pair) < 2:
            have = next(iter(pair))
            missing.append(f"chapter {number}: only {have} exists ({pair[have]})")
            continue
        zh_size = os.path.getsize(pair["zh"])
        en_size = os.path.getsize(pair["en"])
        # Chinese is denser per byte-normalized concept, so compare loosely.
        ratio = max(zh_size, en_size) / max(1, min(zh_size, en_size))
        if ratio > DIVERGENCE:
            diverged.append(
                f"chapter {number}: {ratio:.2f}x size gap "
                f"(zh {zh_size:,}B / en {en_size:,}B) — check they still agree"
            )

    if missing:
        print(f"✗ {len(missing)} chapter(s) missing a language:\n")
        print("\n".join(missing))
    if diverged:
        print(f"\n⚠ {len(diverged)} chapter pair(s) may be out of sync:\n")
        print("\n".join(diverged))
    if not missing and not diverged:
        print(f"✓ {len(chapters)} chapters, both languages present and comparable")

    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
