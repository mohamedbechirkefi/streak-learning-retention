# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""M6: every relative link in the tracked Markdown files resolves (scripts/check_links.py)."""

import importlib.util
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("check_links", ROOT / "scripts" / "check_links.py")
check_links = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_links)


def test_all_relative_links_resolve():
    n, problems = check_links.check(ROOT)
    assert n > 50
    assert problems == []


def test_checker_detects_broken_file_and_anchor(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "b.md").write_text("# Title\n\n## Second part\n")
    (tmp_path / "a.md").write_text(
        "[ok](b.md) [ok anchor](b.md#second-part) [web](https://example.org)\n"
        "[missing](nope.md) [bad anchor](b.md#third) `[in code](gone.md)`\n"
        "```\n[fenced](gone.md)\n```\n")
    subprocess.run(["git", "add", "a.md", "b.md"], cwd=tmp_path, check=True)
    n, problems = check_links.check(tmp_path)
    assert n == 4
    assert len(problems) == 2
    assert any("nope.md (missing file)" in p for p in problems)
    assert any("b.md#third (missing anchor)" in p for p in problems)
