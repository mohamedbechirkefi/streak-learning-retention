# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Fail-closed checks on the M4 publication evidence (master prompt 7 and 11.5).

These read committed files only; they never run a simulation.
"""

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _sha(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def test_every_claim_has_a_result_entry_and_mapping():
    manifest = json.loads((ROOT / "research/publication/artifact_manifest.json").read_text())
    with (ROOT / "research/claims_register.csv").open() as f:
        claims = list(csv.DictReader(f))
    assert claims
    for c in claims:
        for col in ("result_id", "config_hash", "figure_or_table", "manuscript_section", "limitations"):
            assert c[col].strip(), (c["claim_id"], col)
        if c["result_id"] != "n/a":
            assert c["result_id"] in manifest["results"], c["claim_id"]
        else:
            assert c["type"].startswith("external"), c["claim_id"]
    assert manifest["claims_without_result_entry"] == []


def test_manuscript_figures_are_copies_of_generated_figures():
    manifest = json.loads((ROOT / "research/publication/artifact_manifest.json").read_text())
    for fig in manifest["figures"].values():
        assert _sha(fig["file"]) == _sha(fig["copy_of"]) == fig["sha256"]
        assert fig["file"].split("/")[-1] in (ROOT / "research/paper/manuscript.md").read_text()


def test_number_trace_has_no_unmatched_numbers():
    audit = json.loads((ROOT / "research/publication/evidence_audit.json").read_text())
    for doc, rec in audit["number_trace"].items():
        assert rec.get("unmatched") == [], doc
    for exp, rec in audit["recomputation"].items():
        assert rec["status"] in ("ok", "raw file absent (git-ignored); not recomputed"), exp


def test_exploratory_summary_uses_smoke_seeds_only():
    summary = json.loads((ROOT / "results/exploratory/M4-SENSITIVITY/summary.json").read_text())
    assert summary["label"] == "exploratory"
    for row in summary["part_b_sensitivity_runs"]:
        assert row["seeds"] == [9001, 9002, 9003, 9004, 9005]
        assert row["git_dirty"] is False


def test_manuscript_keeps_preprint_status():
    text = (ROOT / "research/paper/manuscript.md").read_text()
    assert "preprint draft, not peer reviewed" in text
