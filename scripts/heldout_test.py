# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Preregistered second test on the held-out Duolingo user split (protocol section 14.4).

Evaluated once, after the freeze. Fits h0 on the fit split for the exponential and the
power-law form and reports, on the held-out split, the mean binomial log-likelihood per
trial of each form and of a constant-recall baseline, plus the calibration table by delay
bin (``streak.duolingo.heldout_evaluation``). Writes aggregates only to
results/confirmatory/HELDOUT-14.4/heldout.json, with the reading fixed in section 14.4.

Usage: .venv/bin/python scripts/heldout_test.py
"""

import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from streak import duolingo as dl
from streak.manifest import environment, git_info, sha256_file
from streak.params import ModelParams

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed" / "first_repeat.npz"
OUT = ROOT / "results" / "confirmatory" / "HELDOUT-14.4"


def main() -> int:
    p = ModelParams()
    sigma = math.sqrt(p.sigma_item ** 2 + p.sigma_learner ** 2)
    proc = dl.load_processed(PROC)
    started = datetime.now(timezone.utc)
    t0 = time.perf_counter()
    ev = dl.heldout_evaluation(dl.subset(proc, 0), dl.subset(proc, 1), sigma)
    rev, dirty = git_info(ROOT)
    ll_exp, ll_pow, ll_c = ev["exponential"]["ll_per_trial"], ev["power"]["ll_per_trial"], ev["constant"]["ll_per_trial"]
    out = {"id": "HELDOUT-14.4", "label": "confirmatory (preregistered descriptive second test, P§14.4)",
           "processed_sha256": sha256_file(PROC), "data_manifest_sha256": sha256_file(ROOT / "data" / "manifest.json"),
           "git_revision": rev, "git_dirty": dirty, "environment": environment(),
           "started_utc": started.isoformat(timespec="seconds"),
           "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "runtime_s": round(time.perf_counter() - t0, 3), "evaluation": ev,
           "reading": {
               "exponential_beats_constant": ll_exp > ll_c,
               "better_supported_form": "exponential" if ll_exp > ll_pow else ("power" if ll_pow > ll_exp else "tie"),
               "rule": ("P§14.4: exponential describes held-out first-repeat data better than the constant baseline "
                        "if its log-likelihood per trial is higher; the form with the higher held-out log-likelihood "
                        "is reported as better supported. Descriptive; does not test H1.")}}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "heldout.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("runtime_s", "reading")}, indent=2))
    print(f"ll/trial: exponential {ll_exp:.6f}, power {ll_pow:.6f}, constant {ll_c:.6f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
