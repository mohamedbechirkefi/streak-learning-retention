# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Control-only floor check after the h0 fit (protocol section 14.3).

Runs arms A0 and A1 only (never A2 or A3: the primary contrast is not computed)
on smoke seeds 9001 to 9005 with 200 learners each, at the given h0 and the other
default parameters. Criterion: mean R30 of A1 in [0.2, 0.8]. K ladder: 100; if below,
50; if above, 200 then 400. Exploratory. Writes results/exploratory/FLOOR-CHECK/floor_check.json.

Usage: .venv/bin/python scripts/floor_check.py H0_DAYS
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

from streak import ENGINE_VERSION
from streak.manifest import git_info
from streak.metrics import learner_arm_metrics
from streak.params import ModelParams, get_arm
from streak.population import generate_learners
from streak.simulate import simulate_arm

ROOT = Path(__file__).resolve().parents[1]
SEEDS = (9001, 9002, 9003, 9004, 9005)
N = 200
LO, HI = 0.2, 0.8


def check(h0: float, k: int) -> dict:
    p = ModelParams(h0=h0, n_items=k)
    r30 = {"A0": [], "A1": []}
    for seed in SEEDS:
        for lr in generate_learners(seed, N, p):
            h_init, av = lr.initial_half_lives(p), lr.availability(p)
            for arm in ("A0", "A1"):
                res = simulate_arm(h_init, av, lr.outcome_u, get_arm(arm), p)
                r30[arm].append(learner_arm_metrics(res, p)["R30"])
    m = {a: float(np.mean(v)) for a, v in r30.items()}
    return {"n_items": k, "h0": h0, "n_learners": len(r30["A1"]), "mean_R30": m,
            "meets_criterion": LO <= m["A1"] <= HI}


def main() -> int:
    h0 = float(sys.argv[1])
    t0 = time.perf_counter()
    steps = [check(h0, 100)]
    ladder = [50] if steps[0]["mean_R30"]["A1"] < LO else [200, 400]
    if not steps[0]["meets_criterion"]:
        for k in ladder:
            steps.append(check(h0, k))
            if steps[-1]["meets_criterion"]:
                break
    adopted = next((s["n_items"] for s in steps if s["meets_criterion"]), None)
    rev, dirty = git_info(ROOT)
    out = {"id": "FLOOR-CHECK", "label": "exploratory", "protocol_section": "14.3", "arms": ["A0", "A1"],
           "seeds": list(SEEDS), "learners_per_seed": N, "criterion": f"A1 mean R30 in [{LO}, {HI}]",
           "engine_version": ENGINE_VERSION, "git_revision": rev, "git_dirty": dirty,
           "runtime_s": round(time.perf_counter() - t0, 2), "steps": steps, "adopted_n_items": adopted}
    d = ROOT / "results" / "exploratory" / "FLOOR-CHECK"
    d.mkdir(parents=True, exist_ok=True)
    (d / "floor_check.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0 if adopted is not None else 1


if __name__ == "__main__":
    sys.exit(main())
