# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""M4 evidence audit (master prompt 11.5). Read-only checks; no simulation.

1. Checksums: every confirmatory results.json against its sha256_manifest.json.
2. Recomputation: from the raw per-learner records, recompute sample counts (records,
   failures, learners per arm and cell) and the mean paired difference of every primary
   contrast, and compare with the committed generated tables (tolerance 1e-12).
3. Number trace: every decimal number (two or more decimals) in the manuscript, the
   supplementary file, the experiment reports and the claims register must equal, at its
   printed precision, some value in a committed source (generated tables, frozen analyses,
   held-out test, run manifests, M4 exploratory summary, protocols). Unmatched numbers are
   listed for manual review; the audit record explains each one.

    .venv/bin/python scripts/m4_evidence_audit.py

Writes research/publication/evidence_audit.json and prints a summary.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPS = ["EXP-001", "EXP-002", "EXP-003"]
DOCS = [
    "research/paper/manuscript.md",
    "research/paper/supplementary.md",
    "research/paper/supplementary_tables.md",
    "research/publication/review_pass_2.md",
    "research/experiments/EXP-001/report.md",
    "research/experiments/EXP-002/report.md",
    "research/experiments/EXP-003/report.md",
    "research/claims_register.csv",
]
SOURCES_GLOBS = [
    "research/experiments/EXP-00*/generated/*.json",
    "research/experiments/EXP-00*/generated/*.csv",
    "research/experiments/EXP-00*/run_manifest.json",
    "results/confirmatory/*/provenance.json",
    "results/confirmatory/HELDOUT-14.4/heldout.json",
    "results/exploratory/CAL-H0/fit.json",
    "results/exploratory/FLOOR-CHECK/floor_check.json",
    "results/exploratory/M4-SENSITIVITY/summary.json",
    "results/exploratory/SMOKE-M3-EXP-001/report/contrasts.csv",
    "results/exploratory/SMOKE-EXP-001-N200/report/contrasts.csv",
    "results/exploratory/SMOKE-EXP-001/report/contrasts.csv",
    "results/exploratory/SMOKE-EXP-002/report/contrasts.csv",
    "results/exploratory/SMOKE-EXP-003/report/contrasts.csv",
]
TEXT_SOURCES = ["research/protocol.md", "research/experiments/EXP-00*/protocol.md",
                "research/experiment_journal.jsonl", "data/manifest.json"]
NUM = re.compile(r"(?<![\w.])[-+]?\d+\.\d{2,}(?![\w.])")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def collect_numbers(obj, out: list[float]) -> None:
    if isinstance(obj, bool) or obj is None:
        return
    if isinstance(obj, (int, float)):
        out.append(float(obj))
    elif isinstance(obj, dict):
        for v in obj.values():
            collect_numbers(v, out)
    elif isinstance(obj, list):
        for v in obj:
            collect_numbers(v, out)
    elif isinstance(obj, str):
        for m in re.findall(r"[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?", obj):
            try:
                out.append(float(m))
            except ValueError:
                pass


def source_values() -> list[float]:
    vals: list[float] = []
    for g in SOURCES_GLOBS:
        for p in sorted(ROOT.glob(g)):
            if p.suffix == ".json":
                collect_numbers(json.loads(p.read_text()), vals)
            else:
                with p.open() as f:
                    for row in csv.reader(f):
                        collect_numbers(row, vals)
    for g in TEXT_SOURCES:
        for p in sorted(ROOT.glob(g)):
            collect_numbers(p.read_text(), vals)
    return vals


def matches(token: str, values: list[float], index: set[str]) -> bool:
    t = token.lstrip("+")
    dec = len(t.split(".")[1])
    if t in index:
        return True
    x = float(t)
    tol = 0.5 * 10 ** (-dec) + 1e-12
    for v in values:
        if abs(v - x) <= tol:
            return True
    return False


def recompute(exp: str) -> dict:
    path = ROOT / "results" / "confirmatory" / exp / "results.json"
    shaman = json.loads((ROOT / "results" / "confirmatory" / exp / "sha256_manifest.json").read_text())
    key = f"results/confirmatory/{exp}/results.json"
    out = {"result_path": key, "sha256_expected": shaman[key]["sha256"]}
    if not path.exists():
        out["status"] = "raw file absent (git-ignored); not recomputed"
        return out
    out["sha256_actual"] = sha(path)
    doc = json.loads(path.read_text())
    recs = doc["records"]
    out["n_records"] = len(recs)
    out["n_failed"] = sum(r["status"] != "ok" for r in recs)
    by: dict[tuple, dict] = {}
    for r in recs:
        by.setdefault((r["cell_id"], r["master_seed"], r["learner_index"]), {})[r["arm"]] = r["metrics"]["R30"]
    cells = sorted({k[0] for k in by})
    primary = {}
    for c in cells:
        diffs = [v["A2"] - v["A1"] for k, v in by.items() if k[0] == c]
        primary[c] = (len(diffs), sum(diffs) / len(diffs))
    with (ROOT / "research" / "experiments" / exp / "generated" / "contrasts.csv").open() as f:
        rows = [r for r in csv.DictReader(f) if r["kind"] == "primary" and r["contrast"] == "A2 - A1"]
    worst = 0.0
    n_mismatch = 0
    for r in rows:
        n, m = primary[r["cell_id"]]
        worst = max(worst, abs(m - float(r["mean_diff"])))
        n_mismatch += int(n != int(r["n"]))
    out.update({"cells": len(cells), "primary_rows_compared": len(rows),
                "max_abs_diff_mean": worst, "n_count_mismatches": n_mismatch,
                "learners_per_cell": sorted({primary[c][0] for c in cells})})
    out["status"] = "ok" if (out["sha256_actual"] == out["sha256_expected"] and worst < 1e-12
                             and n_mismatch == 0 and len(rows) == len(cells)) else "MISMATCH"
    return out


def main() -> int:
    values = source_values()
    index = {f"{v:.{d}f}" for v in values for d in (2, 3, 4)}
    trace = {}
    for d in DOCS:
        p = ROOT / d
        if not p.exists():
            trace[d] = {"status": "missing"}
            continue
        text = re.sub(r"(doi:|doi\.org/)\S+", "", p.read_text())  # identifiers, not numbers
        toks = NUM.findall(text)
        unmatched = sorted({t for t in toks if not matches(t, values, index)})
        by_prec = {}
        for t in toks:
            k = "4+ decimals" if len(t.split(".")[1]) >= 4 else f"{len(t.split('.')[1])} decimals"
            by_prec[k] = by_prec.get(k, 0) + 1
        trace[d] = {"numbers_checked": len(toks), "by_precision": by_prec, "unmatched": unmatched}
    rec = {e: recompute(e) for e in EXPS}
    doc = {"generator": "scripts/m4_evidence_audit.py", "recomputation": rec, "number_trace": trace,
           "n_source_values": len(values)}
    out = ROOT / "research" / "publication" / "evidence_audit.json"
    out.write_text(json.dumps(doc, indent=2) + "\n")
    print(json.dumps(rec, indent=1))
    for d, t in trace.items():
        print(d, t.get("numbers_checked"), t.get("by_precision"), "unmatched:", t.get("unmatched"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
