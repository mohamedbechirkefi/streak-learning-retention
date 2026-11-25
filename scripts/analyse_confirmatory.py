# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Generate the frozen analysis of one confirmatory experiment from its raw result file.

1. ``streak.report.build_report``: tables, figures and generated report (generic analysis).
2. ``streak.frozen_analysis``: the experiment-specific rules of the frozen protocols
   (EXP-001 verdict; EXP-002 floor rule, categories, grid hypothesis, heat map; EXP-003
   interaction, H-inv, main effects and figure).
Outputs go to research/experiments/<EXP>/generated/ (analysis.json, metrics.csv,
contrasts.csv, frozen_analysis.json, figures/). Written before any confirmatory output.

Usage: .venv/bin/python scripts/analyse_confirmatory.py EXP-001 [results.json] [out_dir]
"""

import json
import sys
from pathlib import Path

from streak import frozen_analysis as fa
from streak.report import build_report
from streak.runner import load_result

ROOT = Path(__file__).resolve().parents[1]


def _shown(path: Path) -> str:
    """Repository-relative path when inside the repository (no local home path in outputs, M6)."""
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def main() -> int:
    exp = sys.argv[1]
    res = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "results" / "confirmatory" / exp / "results.json"
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else ROOT / "research" / "experiments" / exp / "generated"
    written = build_report(res, out, pdf=False, max_cell_figures=1 if exp != "EXP-003" else 4)
    analysis = json.loads((out / "analysis.json").read_text())
    doc = load_result(res)
    sesoi = doc["config"]["analysis"]["sesoi"]
    label = doc["label"]
    extra: dict = {"experiment_id": doc["experiment_id"], "label": label, "config_hash": doc["config_hash"],
                   "result_path": _shown(res), "n_records": doc["n_records"], "n_failed": doc["n_failed"],
                   "failure_rate": analysis["failure_rate"],
                   "analysis_halted_over_1pct_failures": analysis["failure_rate"] > 0.01}
    if doc["experiment_id"].endswith("EXP-001") or exp == "EXP-001":
        c = analysis["cells"][0]
        extra["primary"] = c["primary"]
        extra["verdict"] = fa.exp001_verdict(c["primary"], sesoi)
        extra["verdict_excluding_residual_flagged"] = (
            fa.exp001_verdict(c["primary_excluding_residual_flagged"], sesoi)
            if c["primary_excluding_residual_flagged"] else None)
    elif exp == "EXP-002":
        grid = fa.exp002_grid(analysis, sesoi)
        extra["grid"] = grid
        (out / "figures" / "FIG-02-heatmap.svg").write_text(
            fa.heatmap_svg(grid, f"EXP-002 ({label}): A2 - A1 in R30 across h0, a and q"))
    elif exp == "EXP-003":
        eff = fa.exp003_effects(doc, analysis)
        extra["effects"] = eff
        (out / "figures" / "FIG-03-effects.svg").write_text(
            fa.effects_svg(eff, f"EXP-003 ({label}): A2 - A1, interaction and main effects by model variant"))
    (out / "frozen_analysis.json").write_text(json.dumps(extra, indent=2) + "\n")
    for k, v in written.items():
        print(f"{k}: {v}")
    print(f"frozen_analysis: {out / 'frozen_analysis.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
