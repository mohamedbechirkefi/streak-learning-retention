# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Metric validation on known cases and on a smoke result file (exploratory, M3).

Known cases: hand-computable values of the metric and statistics functions. Smoke file:
for every learner-arm, invariants that must hold by the definitions of protocol section 5;
for A0, retention recomputed independently from the closed form of the initial state.

Usage: .venv/bin/python scripts/validate_smoke.py results/exploratory/SMOKE-M3-EXP-001/results.json
Exit 0 if every check passes; prints one line per check family with counts.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np

from streak.memory import recall
from streak.metrics import runs_of_true
from streak.params import ModelParams
from streak.population import generate_learners
from streak.runner import load_result
from streak.stats import classify, holm_adjust, stratified_bootstrap_means


def known_cases() -> list[tuple[str, bool]]:
    out = []
    out.append(("recall exponential at h = 0.5", abs(float(recall(10.0, 10.0)) - 0.5) < 1e-12))
    out.append(("recall power at h = 0.5", abs(float(recall(10.0, 10.0, "power")) - 0.5) < 1e-12))
    out.append(("recall exponential 2 half-lives = 0.25", abs(float(recall(20.0, 10.0)) - 0.25) < 1e-12))
    out.append(("recall power at 3h = 0.3162", abs(float(recall(30.0, 10.0, "power")) - 1 / math.sqrt(10)) < 1e-12))
    out.append(("streak runs [1,1,0,1,1,1,0,1] = (3, 1)", runs_of_true(np.array([1, 1, 0, 1, 1, 1, 0, 1], bool)) == (3, 1)))
    out.append(("streak runs all active = (5, 5)", runs_of_true(np.ones(5, bool)) == (5, 5)))
    out.append(("holm [0.01, 0.04, 0.03] = [0.03, 0.06, 0.06]",
                np.allclose(holm_adjust([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])))
    out.append(("classify relevant negative", classify((-0.05, -0.03), (-0.045, -0.035), 0.02) == "relevant negative"))
    out.append(("classify equivalent", classify((-0.015, 0.012), (-0.01, 0.01), 0.02) == "practically equivalent under the model"))
    out.append(("classify inconclusive", classify((-0.03, 0.01), (-0.025, 0.005), 0.02) == "inconclusive"))
    b = stratified_bootstrap_means(np.full(10, 0.3), np.repeat([1, 2], 5), 50, 1)
    out.append(("bootstrap of a constant is the constant", np.allclose(b, 0.3)))
    return out


def smoke_checks(path: Path) -> dict[str, list[int]]:
    doc = load_result(path)
    res: dict[str, list[int]] = {}

    def check(name: str, ok: bool) -> None:
        res.setdefault(name, [0, 0])[0 if ok else 1] += 1

    params = {c["cell_id"]: ModelParams.from_dict(c["params"]) for c in doc["cells"]}
    by_key = {}
    for r in doc["records"]:
        check("record status ok", r["status"] == "ok")
        if r["status"] != "ok":
            continue
        p, m = params[r["cell_id"]], r["metrics"]
        by_key[(r["cell_id"], r["master_seed"], r["learner_index"], r["arm"])] = m
        check("minutes = slots x 0.5", abs(m["minutes_spent"] - m["slots_spent"] * p.slot_minutes) < 1e-9)
        check("R1 >= R7 >= R30 >= R90", m["R1"] >= m["R7"] >= m["R30"] >= m["R90"])
        check("0 <= weakest decile <= R30 <= 1", 0 <= m["weakest_decile_R30"] <= m["R30"] <= 1)
        check("R90 <= AUC-R <= 1", m["R90"] <= m["AUC_R"] <= 1)
        check("active + missed available + unavailable = T",
              m["active_days"] + m["missed_available_days"] + m["missed_unavailable_days"] == p.horizon_days)
        check("final streak <= longest streak <= active days", m["final_streak"] <= m["longest_streak"] <= m["active_days"])
        check("residual flag = residual > 5% of M", m["residual_flag"] == (m["residual_slots"] > 0.05 * p.budget_slots))
        if r["arm"] == "A0":
            check("A0 zero practice", m["reviews"] == 0 and m["slots_spent"] == 0 and m["active_days"] == 0)
        else:
            check("spent + residual = M", m["slots_spent"] + m["residual_slots"] == p.budget_slots)
            check("reviews = slots spent (1 slot per review)", m["reviews"] == m["slots_spent"])
    # A0 closed form, recomputed independently of simulate_arm
    for cell, p in params.items():
        for seed in doc["config"]["master_seeds"]:
            for lr in generate_learners(seed, doc["config"]["learners_per_seed"], p):
                m = by_key.get((cell, seed, lr.learner_index, "A0"))
                if m is None:
                    continue
                h = lr.initial_half_lives(p)
                for d in p.retention_delays:
                    exp = float(np.mean(np.exp2(-(p.horizon_days + d) / h)))
                    check(f"A0 R{d} equals closed form", abs(m[f"R{d}"] - exp) < 1e-12)
                # A2 and A3 share timing: identical activity
                a2 = by_key.get((cell, seed, lr.learner_index, "A2"))
                a3 = by_key.get((cell, seed, lr.learner_index, "A3"))
                if a2 and a3:
                    check("A2 and A3 identical activity", all(a2[k] == a3[k] for k in
                          ("active_days", "longest_streak", "final_streak", "slots_spent", "residual_slots")))
    return res


def main() -> int:
    ok = True
    for name, passed in known_cases():
        print(f"known case: {name}: {'PASS' if passed else 'FAIL'}")
        ok &= passed
    if len(sys.argv) > 1:
        for name, (n_ok, n_bad) in smoke_checks(Path(sys.argv[1])).items():
            print(f"smoke check: {name}: {n_ok} pass, {n_bad} fail")
            ok &= n_bad == 0
    print("ALL PASS" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
