# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Build research/publication/artifact_manifest.json (master prompt 11.5).

Maps every result, table, figure and claim used in the manuscript and the reports to its
experiment id, run ids, metric definition, result path, generator script, config or protocol
hash and code revision. File checksums are computed here, so the manifest fails visibly
(missing file) rather than silently.

    .venv/bin/python scripts/m4_build_artifact_manifest.py
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "publication" / "artifact_manifest.json"
R30 = "R30: mean true recall probability over all K items at t = T + 30 days, analytic (protocol section 5); contrasts are mean within-learner paired differences with stratified percentile bootstrap intervals (protocol section 6)"


def sha(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def manifest(exp: str) -> dict:
    return json.loads((ROOT / "research" / "experiments" / exp / "run_manifest.json").read_text())


def run_ids(exp: str) -> list[str]:
    return [r["run_id"] for r in manifest(exp)["runs"]]


def conf(exp: str, protocol_hash: str) -> dict:
    m = manifest(exp)
    return {"experiment_id": exp, "label": "confirmatory", "run_ids": run_ids(exp),
            "result_path": f"results/confirmatory/{exp}/results.json", "result_sha256": m["result_sha256"],
            "generated_dir": f"research/experiments/{exp}/generated/",
            "generator_script": f"scripts/run_confirmatory.py {exp}; scripts/analyse_confirmatory.py {exp}",
            "config_path": f"research/experiments/{exp}/config.json", "config_hash": m["config_hash"],
            "protocol_hash": protocol_hash, "code_revision": m["git_revision"], "git_dirty": m["git_dirty"]}


def expl(sid: str, cfg: str) -> dict:
    m = json.loads((ROOT / "results" / "exploratory" / sid / "run_manifest.json").read_text())
    return {"experiment_id": sid, "label": "exploratory", "run_ids": [r["run_id"] for r in m["runs"]],
            "result_path": f"results/raw/exploratory/{sid}/results.json (git-ignored)",
            "result_sha256": m["result_sha256"], "generated_dir": f"results/exploratory/{sid}/report/",
            "generator_script": f"python -m streak.cli run --config {cfg}; python -m streak.cli report; scripts/m4_exploratory.py",
            "config_path": cfg, "config_hash": m["config_hash"], "protocol_hash": None,
            "code_revision": m["git_revision"], "git_dirty": m["git_dirty"]}


def main() -> int:
    freeze = json.loads((ROOT / "research" / "freeze.json").read_text())
    p_hash = freeze["protocol_sha256"]
    reg = {r["exp_id"]: r["protocol_hash"] for r in csv.DictReader((ROOT / "research" / "experiment_registry.csv").open())}
    held = json.loads((ROOT / "results" / "confirmatory" / "HELDOUT-14.4" / "heldout.json").read_text())
    results = {
        "RES-EXP-001-PRIMARY": {**conf("EXP-001", reg["EXP-001"]), "metric": R30 + "; contrast A2 - A1", "source_files": ["generated/frozen_analysis.json", "generated/contrasts.csv"]},
        "RES-EXP-001-ACTIVITY": {**conf("EXP-001", reg["EXP-001"]), "metric": "active days, longest streak, minutes, item coverage, practice success rate (protocol section 5)", "source_files": ["generated/metrics.csv"]},
        "RES-EXP-001-A3A1": {**conf("EXP-001", reg["EXP-001"]), "metric": R30 + "; contrast A3 - A1 (secondary)", "source_files": ["generated/contrasts.csv"]},
        "RES-EXP-001-A2A3": {**conf("EXP-001", reg["EXP-001"]), "metric": R30 + "; contrast A2 - A3 (secondary); within-arm Spearman(active days, R30)", "source_files": ["generated/contrasts.csv", "generated/report.md"]},
        "RES-EXP-002-GRID": {**conf("EXP-002", reg["EXP-002"]), "metric": R30 + "; A2 - A1 per cell; Holm across cells", "source_files": ["generated/frozen_analysis.json", "generated/contrasts.csv"]},
        "RES-EXP-002-A3A1": {**conf("EXP-002", reg["EXP-002"]), "metric": R30 + "; A3 - A1 per cell (secondary)", "source_files": ["generated/contrasts.csv"]},
        "RES-EXP-003-HINV": {**conf("EXP-003", reg["EXP-003"]), "metric": R30 + "; A2 - A1 per model variant; H-inv rule (EXP-003 protocol section 4)", "source_files": ["generated/frozen_analysis.json"]},
        "RES-EXP-003-DECOMP": {**conf("EXP-003", reg["EXP-003"]), "metric": R30 + "; selection and timing contrasts, interaction, equal-weight main effects", "source_files": ["generated/frozen_analysis.json", "generated/contrasts.csv"]},
        "RES-EXP-003-TIMING": {**conf("EXP-003", reg["EXP-003"]), "metric": R30 + "; timing contrasts D-RR - A1, A2 - F-EASY, A3 - F-DUE", "source_files": ["generated/contrasts.csv"]},
        "RES-HELDOUT-14.4": {"experiment_id": "HELDOUT-14.4", "label": "confirmatory (preregistered descriptive test)", "run_ids": ["HELDOUT-14.4"],
                             "result_path": "results/confirmatory/HELDOUT-14.4/heldout.json", "result_sha256": sha("results/confirmatory/HELDOUT-14.4/heldout.json"),
                             "generator_script": "scripts/heldout_test.py", "config_hash": None, "protocol_hash": p_hash + " (section 14.4)",
                             "code_revision": held["git_revision"], "git_dirty": held["git_dirty"],
                             "metric": "mean binomial log-likelihood per held-out trial; calibration by delay bin (protocol section 14.4)"},
        "RES-CAL-H0": {"experiment_id": "CAL-H0", "label": "exploratory calibration (method preregistered)", "run_ids": ["CAL-H0"],
                       "result_path": "results/exploratory/CAL-H0/fit.json", "result_sha256": sha("results/exploratory/CAL-H0/fit.json"),
                       "generator_script": "scripts/fit_h0.py", "protocol_hash": p_hash + " (section 14.2)", "code_revision": "08b4400ef729f9db73ebb77b118afbe74a621380",
                       "metric": "maximum marginal binomial likelihood of h0 (days)"},
        "RES-FLOOR-CHECK": {"experiment_id": "FLOOR-CHECK", "label": "exploratory (control arms only)", "run_ids": ["FLOOR-CHECK"],
                            "result_path": "results/exploratory/FLOOR-CHECK/floor_check.json", "result_sha256": sha("results/exploratory/FLOOR-CHECK/floor_check.json"),
                            "generator_script": "scripts/floor_check.py 67.59", "protocol_hash": p_hash + " (section 14.3)", "metric": "mean R30 of A0 and A1"},
        "RES-SMOKE-EXP-001-N200": {"experiment_id": "SMOKE-EXP-001-N200", "label": "exploratory (pre-freeze, draft parameters)",
                                   "result_path": "results/exploratory/SMOKE-EXP-001-N200/report/contrasts.csv",
                                   "result_sha256": sha("results/exploratory/SMOKE-EXP-001-N200/report/contrasts.csv"),
                                   "generator_script": "python -m streak.cli run --config experiments/smoke-exp001-n200.json; python -m streak.cli report",
                                   "config_path": "experiments/smoke-exp001-n200.json", "code_revision": "dfa9dd4", "metric": R30 + "; A2 - A1"},
        "RES-M4-SENS-K": {"label": "exploratory", "parts": [expl(f"SMOKE-M4-SENS-K{k:03d}", f"experiments/m4-sens-k{k:03d}.json") for k in (50, 100, 200, 400)],
                          "summary": "results/exploratory/M4-SENSITIVITY/summary.csv", "metric": R30 + "; A2 - A1, A3 - A1; A2 item coverage"},
        "RES-M4-SENS-SLOWH0": {**expl("SMOKE-M4-SENS-SLOWH0", "experiments/m4-sens-slow-h0.json"),
                               "summary": "results/exploratory/M4-SENSITIVITY/summary.json", "metric": R30 + "; A2 - A1; share of A1's gain over A0 recovered by A2 = (R30_A2 - R30_A0) / (R30_A1 - R30_A0)"},
        "RES-M4-EXP001-ASSOC": {"label": "exploratory analysis of committed confirmatory data", "result_path": "results/exploratory/M4-SENSITIVITY/summary.json (part_a_committed_exp001)",
                                "input": "results/confirmatory/EXP-001/results.json", "generator_script": "scripts/m4_exploratory.py",
                                "metric": "Spearman correlation across learners between A2 item coverage (or A0 R30) and the paired difference A2 - A1 in R30"},
        "RES-EXEC": {"label": "execution record", "sources": ["results/confirmatory/EXP-00N/run_manifest.json", "research/publication/evidence_audit.json"],
                     "metric": "learner-arm counts and status"},
    }
    figures = {
        "MS-FIG-1": {"file": "research/paper/figures/EXP-001_FIG-01a-arm-r30.svg", "copy_of": "research/experiments/EXP-001/generated/figures/FIG-01a-arm-r30.svg", "result": "RES-EXP-001-PRIMARY"},
        "MS-FIG-2": {"file": "research/paper/figures/EXP-001_FIG-01b-primary-diff.svg", "copy_of": "research/experiments/EXP-001/generated/figures/FIG-01b-primary-diff.svg", "result": "RES-EXP-001-PRIMARY"},
        "MS-FIG-3": {"file": "research/paper/figures/EXP-002_FIG-02-heatmap.svg", "copy_of": "research/experiments/EXP-002/generated/figures/FIG-02-heatmap.svg", "result": "RES-EXP-002-GRID"},
        "MS-FIG-4": {"file": "research/paper/figures/EXP-003_FIG-03-effects.svg", "copy_of": "research/experiments/EXP-003/generated/figures/FIG-03-effects.svg", "result": "RES-EXP-003-DECOMP"},
    }
    for f in figures.values():
        f["sha256"] = sha(f["file"])
        f["copy_sha256_matches"] = f["sha256"] == sha(f["copy_of"])
        f["generator_script"] = "scripts/analyse_confirmatory.py (streak.report.build_report)"
    tables = {
        "MS-TAB-1": {"section": "5.1", "result": ["RES-EXP-001-PRIMARY", "RES-EXP-001-ACTIVITY"], "source": "research/experiments/EXP-001/generated/metrics.csv"},
        "MS-TAB-2": {"section": "5.3", "result": ["RES-EXP-003-HINV", "RES-EXP-003-DECOMP"], "source": "research/experiments/EXP-003/generated/frozen_analysis.json"},
        "MS-TAB-3": {"section": "5.6", "result": ["RES-M4-SENS-K", "RES-M4-SENS-SLOWH0"], "source": "results/exploratory/M4-SENSITIVITY/summary.csv"},
        "SUPP-TABLES": {"section": "S2", "file": "research/paper/supplementary_tables.md", "generator_script": "scripts/m4_supplement_tables.py",
                        "source": "research/experiments/EXP-00N/generated/contrasts.csv"},
    }
    with (ROOT / "research" / "claims_register.csv").open() as f:
        claims = {r["claim_id"]: {"result_id": r["result_id"], "config_hash": r["config_hash"], "figure_or_table": r["figure_or_table"],
                                  "manuscript_section": r["manuscript_section"], "evidence": r["evidence_path_or_source"], "type": r["type"]}
                  for r in csv.DictReader(f)}
    missing = [c for c, v in claims.items() if v["result_id"] not in results and v["result_id"] != "n/a"]
    doc = {"schema_version": "1.0", "updated": "2026-11-25", "generator": "scripts/m4_build_artifact_manifest.py",
           "note": "Maps every quantitative figure, table and claim to experiment id, run ids, metric definition, result path, generator script, config or protocol hash and code revision (master prompt 11.5). Number-level trace: research/publication/evidence_audit.json.",
           "protocol_sha256": p_hash, "results": results, "figures": figures, "tables": tables, "claims": claims,
           "claims_without_result_entry": missing}
    OUT.write_text(json.dumps(doc, indent=2) + "\n")
    print(f"results {len(results)}, figures {len(figures)}, tables {len(tables)}, claims {len(claims)}, missing {missing}")
    print("figure copies match:", all(f["copy_sha256_matches"] for f in figures.values()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
