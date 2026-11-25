# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""M5 consistency checks (master prompt 11.6, M5): the demo shows the same verified numbers
as the manuscript and the experiment reports.

1. Re-running the export in memory reproduces the committed demo/public/data/results.json
   byte for byte (and the sandbox fixture likewise).
2. Every display string in results.json occurs verbatim in the manuscript, or is a
   documented exception: a string whose declared source is an experiment report (an
   interval or table value the manuscript does not print), which must then occur
   verbatim in that report.
3. Every number written in the page's prose fields (status, verdicts, notes, assumptions,
   limitations) occurs in the manuscript, a report, the supplement or the registry.

These read committed files only; the fixture check runs the engine for about two seconds.
"""

import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = "research/paper/manuscript.md"
EXCEPTION_SOURCES = {f"research/experiments/EXP-00{i}/report.md" for i in (1, 2, 3)}


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _committed() -> dict:
    return json.loads((ROOT / "demo/public/data/results.json").read_text())


def _text(rel: str) -> str:
    return (ROOT / rel).read_text()


def test_export_reproduces_committed_results_json():
    exp = _load("export_demo_data")
    fresh = exp.serialise(exp.build())
    assert fresh == (ROOT / "demo/public/data/results.json").read_text()


def test_sandbox_fixture_reproduces():
    fx = _load("export_sandbox_fixture")
    assert fx.serialise(fx.build()) == (ROOT / "demo/src/fixtures/engine_fixture.json").read_text()


def _display_items(node, path="results"):
    """Yield (path, string, declared source) for every display-type string."""
    if isinstance(node, dict):
        default = node.get("display_source", MANUSCRIPT)
        for k, v in node.items():
            if k.startswith("display") and k != "display_source" and isinstance(v, str):
                yield f"{path}.{k}", v, default
            elif k == "interval_display" and isinstance(v, str):
                yield f"{path}.{k}", v, node.get("interval_source") or default
            else:
                yield from _display_items(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _display_items(v, f"{path}[{i}]")


def test_every_display_string_is_in_the_manuscript_or_a_documented_exception():
    r = _committed()
    ms = _text(MANUSCRIPT)
    reports = {p: _text(p) for p in EXCEPTION_SOURCES}
    items = list(_display_items(r))
    assert len(items) > 100
    in_ms = exceptions = 0
    for path, s, src in items:
        if src == MANUSCRIPT:
            assert s in ms, (path, s)
            in_ms += 1
        else:
            assert src in EXCEPTION_SOURCES, (path, src)
            assert s in reports[src], (path, s, src)
            exceptions += 1
    assert in_ms > 0 and exceptions > 0
    # Exceptions inside the template estimates must say why the manuscript does not print them.
    for e in r["experiments"]:
        for est in e["estimates"]:
            if est["display_source"] != MANUSCRIPT or (est["interval_source"] not in (None, MANUSCRIPT)):
                assert est.get("note"), (e["id"], est["label"])


def test_every_estimate_with_an_interval_shows_it():
    for e in _committed()["experiments"]:
        for est in e["estimates"]:
            if est["ci_low"] is not None:
                assert est["interval_display"], (e["id"], est["label"])
                assert est["ci_low"] <= est["estimate"] <= est["ci_high"], (e["id"], est["label"])


def test_numbers_in_prose_fields_are_traceable():
    r = _committed()
    corpus = "\n".join(_text(p) for p in [MANUSCRIPT, "research/paper/supplementary.md",
                                           "research/experiment_registry.csv", *sorted(EXCEPTION_SOURCES)])
    corpus_nocomma = corpus.replace(",", "")
    prose = [r["status_label"], r["question"], *r["limitations"],
             r["streak_vs_recall"]["note"], r["heldout_calibration"]["note"]]
    for e in r["experiments"]:
        prose += [e["title"], e["status"], e["verdict"], *e["notes"], *[x["label"] for x in e["estimates"]]]
    prose += [a["value"] for a in r["assumptions"]]
    prose += [s["name"] for s in r["sandbox_scenarios"]]
    for text in prose:
        for tok in re.findall(r"\d[\d,]*(?:\.\d+)?", text):
            tok = tok.rstrip(",")
            assert tok in corpus or tok.replace(",", "") in corpus_nocomma, (tok, text)


def test_every_registered_experiment_is_exported_with_claims():
    import csv
    r = _committed()
    ids = {e["id"] for e in r["experiments"]}
    with (ROOT / "research/experiment_registry.csv").open() as f:
        for row in csv.DictReader(f):
            assert row["exp_id"] in ids
    with (ROOT / "research/claims_register.csv").open() as f:
        claim_ids = {row["claim_id"] for row in csv.DictReader(f)}
    for e in r["experiments"]:
        assert e["claim_ids"] and set(e["claim_ids"]) <= claim_ids, e["id"]


def test_results_json_has_no_timestamp_or_absolute_path():
    text = (ROOT / "demo/public/data/results.json").read_text()
    assert "/Users/" not in text
    assert not re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", text)


def test_public_texts_use_only_verified_decimal_numbers():
    """README, CITATION, articles and the demo README: every decimal number occurs in the
    manuscript, a report or the supplement (same verified results, M5)."""
    corpus = "\n".join(_text(p) for p in [MANUSCRIPT, "research/paper/supplementary.md", *sorted(EXCEPTION_SOURCES)])
    pattern = re.compile(r"(?<![\d.])[-+]?\d+\.\d+(?![\d.])")
    for rel in ("README.md", "CITATION.cff", "articles/medium.md", "articles/linkedin.md", "demo/README.md"):
        found = pattern.findall(_text(rel))
        for tok in found:
            assert tok.lstrip("+") in corpus, (rel, tok)
    assert pattern.findall(_text("articles/medium.md"))


def test_public_texts_keep_owner_placeholders_and_no_stale_status():
    for rel in ("README.md", "articles/medium.md", "articles/linkedin.md"):
        t = _text(rel)
        assert "placeholder" in t, rel
        assert "has not reviewed" not in t and "No confirmatory experiment has been run" not in t, rel


def test_public_texts_use_only_verified_counts_and_percentages():
    """M6 extension: thousands-separated counts (for example 70,000) and percentages in the
    README, CITATION, articles and demo README occur verbatim in the manuscript, a report or
    the supplement."""
    corpus = "\n".join(_text(p) for p in [MANUSCRIPT, "research/paper/supplementary.md", *sorted(EXCEPTION_SOURCES)])
    pattern = re.compile(r"(?<![\d.,])\d{1,3}(?:,\d{3})+(?![\d,])|(?<![\d.])\d+(?:\.\d+)?%")
    n = 0
    for rel in ("README.md", "CITATION.cff", "articles/medium.md", "articles/linkedin.md", "demo/README.md"):
        for tok in pattern.findall(_text(rel)):
            n += 1
            assert tok in corpus, (rel, tok)
    assert n > 0
