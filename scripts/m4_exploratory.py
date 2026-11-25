# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""M4 exploratory confounder and sensitivity summary (decision D-019, journal J-0018).

EXPLORATORY. Nothing here changes or replaces a frozen verdict.

Part A reads committed confirmatory outputs only (no simulation): the per-learner
association between A2's item coverage and the primary paired difference in EXP-001,
and the mean R30 of each arm split by A2's coverage tercile.

Part B summarises the M4 exploratory sensitivity runs on smoke seeds 9001 to 9005
(configs experiments/m4-sens-*.json; raw results under the git-ignored
results/raw/exploratory/; generated reports under results/exploratory/SMOKE-M4-SENS-*/).

    .venv/bin/python scripts/m4_exploratory.py

Writes results/exploratory/M4-SENSITIVITY/summary.json and summary.csv.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np

from streak.stats import spearman

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "exploratory" / "M4-SENSITIVITY"
SENS = {"SMOKE-M4-SENS-K050": "experiments/m4-sens-k050.json",
        "SMOKE-M4-SENS-K100": "experiments/m4-sens-k100.json",
        "SMOKE-M4-SENS-K200": "experiments/m4-sens-k200.json",
        "SMOKE-M4-SENS-K400": "experiments/m4-sens-k400.json",
        "SMOKE-M4-SENS-SLOWH0": "experiments/m4-sens-slow-h0.json"}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _by_learner(records: list[dict], cell: str) -> dict[tuple, dict]:
    out: dict[tuple, dict] = {}
    for r in records:
        if r["cell_id"] != cell or r["status"] != "ok":
            continue
        out.setdefault((r["master_seed"], r["learner_index"]), {})[r["arm"]] = r["metrics"]
    return out


def part_a() -> dict:
    path = ROOT / "results" / "confirmatory" / "EXP-001" / "results.json"
    doc = json.loads(path.read_text())
    learners = _by_learner(doc["records"], "default")
    keys = sorted(learners)
    cov = np.array([learners[k]["A2"]["item_coverage"] for k in keys])
    delta = np.array([learners[k]["A2"]["R30"] - learners[k]["A1"]["R30"] for k in keys])
    r30 = {arm: np.array([learners[k][arm]["R30"] for k in keys]) for arm in ("A0", "A1", "A2", "A3")}
    terciles = np.quantile(cov, [1 / 3, 2 / 3])
    groups = np.digitize(cov, terciles, right=True)
    tercile_rows = []
    for g in range(3):
        m = groups == g
        tercile_rows.append({
            "tercile": g + 1,
            "n": int(m.sum()),
            "A2_coverage_mean": float(cov[m].mean()),
            "A2_coverage_min": float(cov[m].min()),
            "A2_coverage_max": float(cov[m].max()),
            "delta_A2_A1_mean": float(delta[m].mean()),
            **{f"R30_{arm}_mean": float(v[m].mean()) for arm, v in r30.items()},
        })
    return {
        "source": str(path.relative_to(ROOT)),
        "source_sha256": _sha(path),
        "n_learners": len(keys),
        "A2_coverage_mean": float(cov.mean()),
        "A2_coverage_min": float(cov.min()),
        "A2_coverage_max": float(cov.max()),
        "A2_share_of_A1_gain": float((r30["A2"].mean() - r30["A0"].mean()) / (r30["A1"].mean() - r30["A0"].mean())),
        "spearman_A2coverage_delta": spearman(cov, delta),
        "spearman_A2coverage_R30A2": spearman(cov, r30["A2"]),
        "spearman_R30A0_delta": spearman(r30["A0"], delta),
        "coverage_terciles": tercile_rows,
    }


def _contrast(rows: list[dict], cell: str, contrast: str) -> dict:
    for r in rows:
        if r["cell_id"] == cell and r["contrast"] == contrast and r["kind"] in ("primary", "secondary"):
            return {"mean": float(r["mean_diff"]), "ci95": [float(r["ci95_low"]), float(r["ci95_high"])],
                    "ci90": [float(r["ci90_low"]), float(r["ci90_high"])], "class": r["classification"],
                    "n": int(r["n"])}
    raise KeyError((cell, contrast))


def _metric(rows: list[dict], cell: str, arm: str, metric: str) -> float:
    for r in rows:
        if r["cell_id"] == cell and r["arm"] == arm and r["metric"] == metric:
            return float(r["mean"])
    raise KeyError((cell, arm, metric))


def part_b() -> list[dict]:
    out = []
    for sid, cfg_path in SENS.items():
        rep = ROOT / "results" / "exploratory" / sid / "report"
        man = json.loads((ROOT / "results" / "exploratory" / sid / "run_manifest.json").read_text())
        with (rep / "contrasts.csv").open() as f:
            con = list(csv.DictReader(f))
        with (rep / "metrics.csv").open() as f:
            met = list(csv.DictReader(f))
        cfg = json.loads((ROOT / cfg_path).read_text())
        base = cfg.get("base_params", {})
        for cell in sorted({r["cell_id"] for r in con}):
            row = {
                "exploratory_id": sid,
                "cell_id": cell,
                "K": base.get("n_items"),
                "h0": float(cell.split("=")[1]) if cell.startswith("h0=") else base.get("h0"),
                "config": cfg_path,
                "config_hash": man.get("config_hash"),
                "result_sha256": man.get("result_sha256"),
                "git_revision": man.get("git_revision"),
                "git_dirty": man.get("git_dirty"),
                "seeds": cfg.get("master_seeds"),
            }
            for arm in ("A0", "A1", "A2", "A3"):
                row[f"R30_{arm}"] = _metric(met, cell, arm, "R30")
            row["A2_item_coverage"] = _metric(met, cell, "A2", "item_coverage")
            row["A2_share_of_A1_gain"] = (row["R30_A2"] - row["R30_A0"]) / (row["R30_A1"] - row["R30_A0"])
            row["A2_minus_A1"] = _contrast(con, cell, "A2 - A1")
            row["A3_minus_A1"] = _contrast(con, cell, "A3 - A1")
            row["A2_minus_A0"] = _contrast(con, cell, "A2 - A0")
            out.append(row)
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rev = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    doc = {
        "label": "exploratory",
        "notice": "M4 exploratory analysis (D-019, J-0018). Smoke seeds only for new simulations. "
                  "Never replaces or changes a frozen confirmatory verdict.",
        "generator": "scripts/m4_exploratory.py",
        "git_revision_at_generation": rev,
        "part_a_committed_exp001": part_a(),
        "part_b_sensitivity_runs": part_b(),
    }
    (OUT / "summary.json").write_text(json.dumps(doc, indent=2) + "\n")
    with (OUT / "summary.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["exploratory_id", "cell_id", "K", "h0", "R30_A0", "R30_A1", "R30_A2", "R30_A3",
                    "A2_item_coverage", "A2_share_of_A1_gain", "A2_minus_A1", "A2_minus_A1_ci95_low", "A2_minus_A1_ci95_high",
                    "A2_minus_A1_class", "A3_minus_A1", "A3_minus_A1_ci95_low", "A3_minus_A1_ci95_high",
                    "A3_minus_A1_class", "A2_minus_A0", "A2_minus_A0_class"])
        for r in doc["part_b_sensitivity_runs"]:
            w.writerow([r["exploratory_id"], r["cell_id"], r["K"], r["h0"],
                        *(f"{r[f'R30_{a}']:.4f}" for a in ("A0", "A1", "A2", "A3")),
                        f"{r['A2_item_coverage']:.4f}", f"{r['A2_share_of_A1_gain']:.3f}",
                        f"{r['A2_minus_A1']['mean']:.4f}", f"{r['A2_minus_A1']['ci95'][0]:.4f}",
                        f"{r['A2_minus_A1']['ci95'][1]:.4f}", r["A2_minus_A1"]["class"],
                        f"{r['A3_minus_A1']['mean']:.4f}", f"{r['A3_minus_A1']['ci95'][0]:.4f}",
                        f"{r['A3_minus_A1']['ci95'][1]:.4f}", r["A3_minus_A1"]["class"],
                        f"{r['A2_minus_A0']['mean']:.4f}", r["A2_minus_A0"]["class"]])
    print(json.dumps(doc["part_a_committed_exp001"], indent=1))
    print((OUT / "summary.csv").read_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
