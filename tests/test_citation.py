# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""M6: CITATION.cff is structurally valid CFF 1.2.0 (keys and types), carries the manuscript
title and a release-candidate version, and has no release date (no release exists)."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {"abstract", "authors", "cff-version", "commit", "contact", "date-released", "doi",
           "identifiers", "keywords", "license", "license-url", "message", "preferred-citation",
           "references", "repository", "repository-artifact", "repository-code", "title", "type",
           "url", "version"}


def _top_level() -> dict[str, list[str]]:
    keys: dict[str, list[str]] = {}
    current = None
    for line in (ROOT / "CITATION.cff").read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([a-z-]+):\s*(.*)$", line)
        if m:
            current = m.group(1)
            keys[current] = [m.group(2)] if m.group(2) else []
        else:
            assert current and line.startswith(" "), line
            keys[current].append(line.strip())
    return keys


def _scalar(v: list[str]) -> str:
    assert len(v) == 1
    return v[0].strip().strip('"')


def test_citation_structure():
    k = _top_level()
    assert set(k) <= ALLOWED, set(k) - ALLOWED
    for req in ("cff-version", "message", "title", "authors"):
        assert req in k, req
    assert _scalar(k["cff-version"]) == "1.2.0"
    assert _scalar(k["type"]) in {"software", "dataset"}
    assert k["authors"] and k["authors"][0].startswith("- ")
    assert any(a.startswith("- family-names:") for a in k["authors"])
    assert all(x.startswith("- ") for x in k["keywords"])


def test_citation_release_candidate_without_release_date():
    k = _top_level()
    assert "date-released" not in k
    assert re.fullmatch(r"\d+\.\d+\.\d+-rc\d+", _scalar(k["version"]))


def test_citation_title_matches_manuscript():
    ms = (ROOT / "research/paper/manuscript.md").read_text()
    title = re.search(r'^title: "(.*)"$', ms, re.M).group(1)
    assert _scalar(_top_level()["title"]) == title
