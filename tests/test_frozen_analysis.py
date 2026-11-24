# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Tests of the frozen-protocol analyses (streak.frozen_analysis) and the M3 scripts,
written before any confirmatory output existed."""

import copy
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from streak import frozen_analysis as fa
from streak.report import analyse
from streak.runner import execute

ROOT = Path(__file__).resolve().parents[1]
AN = {"bootstrap_resamples": 200, "bootstrap_seed": 1, "sesoi": 0.02}


def fake_doc(cell: str, r30: dict[str, list[float]], seeds=(1, 1, 2, 2)) -> dict:
    recs = []
    for arm, vals in r30.items():
        for i, v in enumerate(vals):
            recs.append({"cell_id": cell, "arm": arm, "master_seed": seeds[i], "learner_index": i,
                         "status": "ok", "metrics": {"R30": v}})
    return {"records": recs, "config": {"analysis": AN}}


def test_interaction_is_difference_of_differences():
    vals = {"A2": [0.5, 0.6, 0.7, 0.8], "D-RR": [0.4, 0.4, 0.4, 0.4],
            "F-EASY": [0.3, 0.3, 0.3, 0.3], "A1": [0.25, 0.25, 0.25, 0.25]}
    s = fa.linear_contrast(fake_doc("exponential-flat", vals), "exponential-flat",
                           {"A2": 1, "D-RR": -1, "F-EASY": -1, "A1": 1}, "i")
    expected = np.mean([(a - 0.4) - (0.3 - 0.25) for a in vals["A2"]])
    assert s["mean_diff"] == pytest.approx(expected)
    assert s["n"] == 4


def test_linear_contrast_keeps_pairing():
    d = fake_doc("c", {"A2": [0.5, 0.6, 0.7, 0.8], "A1": [0.4, 0.4, 0.4, 0.4]})
    d["records"] = [r for r in d["records"] if not (r["arm"] == "A1" and r["learner_index"] == 0)]
    s = fa.linear_contrast(d, "c", {"A2": 1, "A1": -1}, "x")
    assert s["n"] == 3 and s["mean_diff"] == pytest.approx(np.mean([0.2, 0.3, 0.4]))


@pytest.mark.parametrize("ci95,ci90,start", [
    ((-0.05, -0.03), (-0.045, -0.035), "supports the expected direction"),
    ((0.01, 0.03), (0.012, 0.028), "contradicts the expected direction (95% interval entirely above 0)"),
    ((-0.01, 0.005), (-0.008, 0.004), "practically equivalent"),
    ((-0.025, -0.001), (-0.022, -0.003), "statistically detectable but below the SESOI"),
    ((-0.03, 0.01), (-0.025, 0.005), "inconclusive"),
])
def test_exp001_verdict(ci95, ci90, start):
    assert fa.exp001_verdict({"ci95": ci95, "ci90": ci90}, 0.02).startswith(start)


def _cell(cid, a1, a2, ci95, ci90, cls, prel=False):
    return {"cell_id": cid, "arms": [{"arm": "A1", "metrics": {"R30": {"mean": a1}}},
                                     {"arm": "A2", "metrics": {"R30": {"mean": a2}}}],
            "primary": {"mean_diff": a2 - a1, "ci95": list(ci95), "ci90": list(ci90), "p_boot": 0.0,
                        "p_holm": 0.0, "classification": cls, "relevant_holm_across_cells": prel}}


def test_exp002_floor_and_disconfirmation():
    cells = [_cell("h0=1|a=1|q=1", 0.01, 0.015, (0.001, 0.009), (0.002, 0.008), "practically equivalent under the model"),
             _cell("h0=1|a=2|q=0.7", 0.5, 0.45, (-0.06, -0.04), (-0.058, -0.042), "relevant negative", True),
             _cell("h0=2|a=2|q=0.7", 0.5, 0.53, (0.02, 0.04), (0.022, 0.038), "relevant positive", True)]
    g = fa.exp002_grid({"cells": cells}, 0.02)
    assert g["n_uninformative_floor"] == 1
    assert g["cells"][0]["category"] == "uninformative (floor)"
    assert g["robustness_disconfirmed"]["cells_ci95_entirely_above_0"] == ["h0=2|a=2|q=0.7"]
    assert g["robustness_disconfirmed"]["disconfirmed"] is True
    assert g["grid_hypothesis_all_negative"]["holds"] is False
    assert g["n_relevant_holm_across_cells"] == 2


def test_exp002_heatmap_renders_full_grid():
    cells = []
    for h0 in (1, 2, 3):
        for a in (1, 2, 3):
            for q in (0.7, 0.85, 1.0):
                cells.append(_cell(f"h0={h0}|a={a}|q={q}", 0.5, 0.48, (-0.03, -0.01), (-0.028, -0.012),
                                   "detectable but below the SESOI"))
    g = fa.exp002_grid({"cells": cells}, 0.02)
    assert g["grid_hypothesis_all_negative"]["holds"] is True
    assert g["q1_sign_agreement"]["all_same_sign_as_majority_of_others"] is True
    svg = fa.heatmap_svg(g, "t")
    assert svg.count("<rect") == 28 and "SPDX" in svg


def test_exp003_effects_and_h_inv(tiny_config, tmp_path):
    cfg = copy.deepcopy(tiny_config)
    cfg["arms"] = ["A1", "F-EASY", "F-DUE", "D-RR", "A2", "A3"]
    cfg["model_variants"] = [{"form": "exponential", "gain_rule": "difficulty"},
                             {"form": "exponential", "gain_rule": "flat"}]
    cfg["analysis"]["secondary_contrasts"] = [["F-EASY", "A1"], ["A2", "A3"]]
    execute(cfg, tmp_path, "test")
    doc = json.loads((tmp_path / "results.json").read_text())
    eff = fa.exp003_effects(doc, analyse(doc))
    assert [v["variant"] for v in eff["variants"]] == ["exp-diff", "exp-flat"]
    assert "H_inv" in eff["variants"][1] and "H_inv" not in eff["variants"][0]
    v = eff["variants"][0]
    assert v["interaction"]["n"] == 6 and len(v["main_effects_conventional_definition"]) == 3
    assert "<svg" in fa.effects_svg(eff, "t")


def test_validate_smoke_script(tiny_config, tmp_path):
    execute(tiny_config, tmp_path, "test")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_smoke.py"), str(tmp_path / "results.json")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "ALL PASS" in r.stdout and "A0 R30 equals closed form" in r.stdout


def test_analyse_script_on_exploratory_result(tiny_config, tmp_path):
    execute(tiny_config, tmp_path / "run", "test")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "analyse_confirmatory.py"), "EXP-001",
                        str(tmp_path / "run" / "results.json"), str(tmp_path / "out")], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    fx = json.loads((tmp_path / "out" / "frozen_analysis.json").read_text())
    assert fx["label"] == "exploratory" and "verdict" in fx
