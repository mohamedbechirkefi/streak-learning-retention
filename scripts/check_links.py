# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Check that every relative link in the tracked Markdown files resolves (M6).

A link is `[text](target)` or `![alt](target)`. External targets (http, https, mailto) are
skipped. A relative target must name an existing file or folder, relative to the Markdown
file; a `#fragment` must match a heading of the target Markdown file (GitHub-style slug).

Usage: .venv/bin/python scripts/check_links.py     exit 0 and "LINK-CHECK PASS" if all resolve
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
FENCE = re.compile(r"^(```|~~~)")
CODE_SPAN = re.compile(r"`[^`]*`")


def tracked_markdown(root: Path = ROOT) -> list[Path]:
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=root, capture_output=True, text=True, check=True)
    return [root / p for p in out.stdout.split() if p]


def slug(heading: str) -> str:
    s = heading.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def anchors(md: Path) -> set[str]:
    seen: dict[str, int] = {}
    out = set()
    fenced = False
    for line in md.read_text(encoding="utf-8").splitlines():
        if FENCE.match(line):
            fenced = not fenced
        if fenced:
            continue
        m = re.match(r"^#{1,6}\s+(.*?)\s*#*\s*$", line)
        if m:
            base = slug(m.group(1))
            n = seen.get(base, 0)
            out.add(base if n == 0 else f"{base}-{n}")
            seen[base] = n + 1
    return out


def links(md: Path) -> list[tuple[int, str]]:
    found = []
    fenced = False
    for i, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        for m in LINK.finditer(CODE_SPAN.sub("", line)):
            found.append((i, m.group(1)))
    return found


def check(root: Path = ROOT) -> tuple[int, list[str]]:
    n, problems = 0, []
    for md in tracked_markdown(root):
        for line, target in links(md):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            n += 1
            path, _, frag = target.partition("#")
            dest = md if not path else (md.parent / unquote(path)).resolve()
            where = f"{md.relative_to(root)}:{line}: {target}"
            if not dest.exists():
                problems.append(f"{where} (missing file)")
            elif frag and dest.suffix == ".md" and frag.lower() not in anchors(dest):
                problems.append(f"{where} (missing anchor)")
    return n, problems


def main() -> int:
    n, problems = check()
    for p in problems:
        print(f"BROKEN {p}")
    print(f"relative links checked: {n}; broken: {len(problems)}")
    print("LINK-CHECK PASS" if not problems else "LINK-CHECK FAIL")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
