# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Fit the median initial half-life h0 on the fit split only (protocol section 14.2).

Exploratory calibration; never touches the held-out split or any simulation.
Writes results/exploratory/CAL-H0/fit.json (aggregate numbers only, committed).

Usage: .venv/bin/python scripts/fit_h0.py
"""

import json
import math
import sys
import time
from pathlib import Path

from streak import duolingo as dl
from streak.manifest import git_info, sha256_file
from streak.params import ModelParams

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed" / "first_repeat.npz"
OUT = ROOT / "results" / "exploratory" / "CAL-H0"


def main() -> int:
    p = ModelParams()
    sigma = math.sqrt(p.sigma_item ** 2 + p.sigma_learner ** 2)
    fit_split = dl.subset(dl.load_processed(PROC), 0)
    t0 = time.perf_counter()
    fit = dl.fit_h0(fit_split.delta_days, fit_split.n, fit_split.k, sigma, "exponential")
    rev, dirty = git_info(ROOT)
    h0 = round(fit["h0_days"], 2)
    out = {"id": "CAL-H0", "label": "exploratory", "protocol_section": "14.2", "split": "fit",
           "processed_sha256": sha256_file(PROC), "git_revision": rev, "git_dirty": dirty,
           "runtime_s": round(time.perf_counter() - t0, 3), "fit": fit,
           "h0_fitted_rounded_days": h0,
           "exp002_h0_axis_days": [round(0.5 * h0, 2), h0, round(2 * h0, 2)]}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "fit.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 1 if fit["on_grid_edge"] else 0


if __name__ == "__main__":
    sys.exit(main())
