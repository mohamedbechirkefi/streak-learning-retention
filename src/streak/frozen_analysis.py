# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Frozen-protocol analyses that the generic report generator does not compute.

Written and tested before any confirmatory output existed (M3, 2026-11-25). Each
function implements a rule stated in a frozen protocol (version 1.0):

- EXP-001 section 4: verdict on the primary contrast.
- EXP-002 sections 4, 5, 12 and 13, with P§14.6: floor rule, outcome categories, the
  grid-level descriptive hypothesis, its disconfirmation, Holm across cells and the
  agreement of the q = 1.0 cells.
- EXP-003 sections 4, 5 and 9: the timing x selection interaction, H-inv per forgetting
  form, and main effects. The protocol names main effects without a formula; the
  conventional equal-weight marginal definition is used and labelled as such.

Inputs are a validated result document and the ``analyse`` output of ``streak.report``.
Every number is computed from the per-learner records; nothing is typed by hand.
"""

from __future__ import annotations

from html import escape

import numpy as np

from .stats import paired_summary

FLOOR_R30 = 0.02  # EXP-002 section 12: both A1 and A2 mean R30 below this -> uninformative (floor)
EXP002_EQUIVALENT_DISCONFIRM = 9  # EXP-002 section 4: 9 or more equivalent cells disconfirm robustness


def _r30_table(doc: dict) -> dict:
    out: dict = {}
    for r in doc["records"]:
        if r["status"] == "ok":
            out.setdefault((r["cell_id"], r["arm"]), {})[(r["master_seed"], r["learner_index"])] = r["metrics"]["R30"]
    return out


def _summary(diff: np.ndarray, seeds: np.ndarray, label: str, an: dict) -> dict:
    return paired_summary(diff, seeds, label, "R30", an["bootstrap_resamples"], an["bootstrap_seed"],
                          an["sesoi"]).to_dict()


def linear_contrast(doc: dict, cell: str, weights: dict[str, float], label: str) -> dict | None:
    """Per-learner linear combination sum_w w * R30(arm), summarised with the frozen bootstrap.
    Only learners present in every arm of the combination are used (pairing kept)."""
    tab = _r30_table(doc)
    rows = [tab.get((cell, arm), {}) for arm in weights]
    keys = sorted(set.intersection(*[set(r) for r in rows])) if rows else []
    if len(keys) < 2:
        return None
    diff = np.array([sum(w * tab[(cell, arm)][k] for arm, w in weights.items()) for k in keys])
    seeds = np.array([k[0] for k in keys])
    return _summary(diff, seeds, label, doc["config"]["analysis"])


# --------------------------------------------------------------------------- EXP-001

def exp001_verdict(primary: dict, sesoi: float) -> str:
    """EXP-001 protocol section 4 wording for the primary contrast A2 - A1."""
    lo95, hi95 = primary["ci95"]
    lo90, hi90 = primary["ci90"]
    if -sesoi < lo90 and hi90 < sesoi:
        return ("practically equivalent under the model (90% interval inside the SESOI bounds); "
                "contradicts the expected direction")
    if hi95 < -sesoi:
        return "supports the expected direction with practical relevance (95% interval entirely below -SESOI)"
    if lo95 > 0:
        return ("contradicts the expected direction (95% interval entirely above 0)"
                + ("; the interval also lies entirely above +SESOI" if lo95 > sesoi else ""))
    if hi95 < 0:
        return "statistically detectable but below the SESOI (negative; 95% interval excludes 0 but crosses -SESOI)"
    return "inconclusive (95% interval includes 0 and equivalence is not shown)"


# --------------------------------------------------------------------------- EXP-002

def exp002_grid(analysis: dict, sesoi: float) -> dict:
    """Per-cell floor flag and outcome category, counts, the grid-level hypothesis and its
    disconfirmation, and the q = 1.0 sign agreement."""
    cells = []
    for c in analysis["cells"]:
        p = c["primary"]
        means = {a["arm"]: (a["metrics"]["R30"]["mean"] if a["metrics"].get("R30") else None) for a in c["arms"]}
        floor = (means.get("A1") is not None and means.get("A2") is not None
                 and means["A1"] < FLOOR_R30 and means["A2"] < FLOOR_R30)
        params = dict(kv.split("=") for kv in c["cell_id"].split("|"))
        cells.append({
            "cell_id": c["cell_id"], "h0": float(params["h0"]), "a": float(params["a"]), "q": float(params["q"]),
            "mean_R30_A1": means.get("A1"), "mean_R30_A2": means.get("A2"),
            "mean_diff": p["mean_diff"] if p else None,
            "ci95": p["ci95"] if p else None, "ci90": p["ci90"] if p else None,
            "p_boot": p["p_boot"] if p else None, "p_holm_across_cells": p.get("p_holm") if p else None,
            "classification": p["classification"] if p else None,
            "relevant_holm_across_cells": p.get("relevant_holm_across_cells") if p else None,
            "uninformative_floor": bool(floor),
            "category": "uninformative (floor)" if floor else (p["classification"] if p else "missing"),
            "ci95_entirely_above_0": bool(p and p["ci95"][0] > 0),
        })
    informative = [c for c in cells if not c["uninformative_floor"] and c["mean_diff"] is not None]
    counts: dict[str, int] = {}
    for c in cells:
        counts[c["category"]] = counts.get(c["category"], 0) + 1
    n_equiv = sum(c["category"] == "practically equivalent under the model" for c in cells)
    above = [c["cell_id"] for c in informative if c["ci95_entirely_above_0"]]
    sign_neg = sum(c["mean_diff"] < 0 for c in informative)
    q1 = [c for c in informative if c["q"] == 1.0]
    others = [c for c in informative if c["q"] != 1.0]
    def sign(v): return int(np.sign(v))
    return {
        "cells": cells,
        "n_cells": len(cells),
        "n_uninformative_floor": sum(c["uninformative_floor"] for c in cells),
        "category_counts": counts,
        "n_relevant_holm_across_cells": sum(bool(c["relevant_holm_across_cells"]) for c in cells),
        "grid_hypothesis_all_negative": {
            "statement": "the sign of E[delta_c] is negative in all 27 cells (descriptive, not tested)",
            "n_negative_mean": sign_neg, "n_informative": len(informative),
            "holds": len(informative) == len(cells) and sign_neg == len(cells),
        },
        "robustness_disconfirmed": {
            "cells_ci95_entirely_above_0": above,
            "n_practically_equivalent": n_equiv,
            "rule": "any cell with 95% interval entirely above 0, or 9 or more practically equivalent cells",
            "disconfirmed": bool(above) or n_equiv >= EXP002_EQUIVALENT_DISCONFIRM,
        },
        "q1_sign_agreement": {
            "q1_signs": {c["cell_id"]: sign(c["mean_diff"]) for c in q1},
            "other_signs_count": {str(s): sum(sign(c["mean_diff"]) == s for c in others) for s in (-1, 0, 1)},
            "all_same_sign_as_majority_of_others": (
                None if not q1 or not others else
                all(sign(c["mean_diff"]) == int(np.sign(sum(sign(o["mean_diff"]) for o in others))) for c in q1)),
        },
    }


def heatmap_svg(grid: dict, title: str) -> str:
    """EXP-002 heat map: one panel per h0, rows q, columns a; colour = mean A2 - A1 difference
    (diverging, symmetric around 0); text = mean and 95% interval; marker = category."""
    cells = grid["cells"]
    h0s = sorted({c["h0"] for c in cells})
    a_s = sorted({c["a"] for c in cells})
    qs = sorted({c["q"] for c in cells}, reverse=True)
    vmax = max(abs(c["mean_diff"]) for c in cells if c["mean_diff"] is not None) or 1e-9
    cw, ch, gap, top, left = 96, 46, 30, 70, 60
    pw = len(a_s) * cw
    W = left + len(h0s) * (pw + gap) + 20
    H = top + len(qs) * ch + 110
    mark = {"relevant negative": "R-", "relevant positive": "R+", "practically equivalent under the model": "EQ",
            "detectable but below the SESOI": "D", "inconclusive": "I", "uninformative (floor)": "F"}

    def colour(v: float) -> str:
        t = max(-1.0, min(1.0, v / vmax))
        if t >= 0:  # orange for A2 above A1
            r, g, b = 255, int(255 - 120 * t), int(255 - 200 * t)
        else:       # blue for A2 below A1
            r, g, b = int(255 + 200 * t), int(255 + 120 * t), 255
        return f"#{r:02x}{g:02x}{b:02x}"

    body = [f'<text x="{left}" y="22" font-size="14" fill="#1f2328">{escape(title)}</text>']
    for pi, h0 in enumerate(h0s):
        x0 = left + pi * (pw + gap)
        body.append(f'<text x="{x0 + pw / 2}" y="{top - 26}" text-anchor="middle" fill="#1f2328">h0 = {h0:g} days</text>')
        for ai, a in enumerate(a_s):
            body.append(f'<text x="{x0 + ai * cw + cw / 2}" y="{top - 8}" text-anchor="middle" font-size="11" fill="#6b7280">a = {a:g}</text>')
        for qi, q in enumerate(qs):
            if pi == 0:
                body.append(f'<text x="{left - 6}" y="{top + qi * ch + ch / 2 + 4}" text-anchor="end" font-size="11" fill="#6b7280">q = {q:g}</text>')
            for ai, a in enumerate(a_s):
                c = next(c for c in cells if c["h0"] == h0 and c["a"] == a and c["q"] == q)
                x, y = x0 + ai * cw, top + qi * ch
                body.append(f'<rect x="{x}" y="{y}" width="{cw - 2}" height="{ch - 2}" fill="{colour(c["mean_diff"])}" stroke="#d1d5db"/>')
                body.append(f'<text x="{x + cw / 2}" y="{y + 17}" text-anchor="middle" font-size="11" fill="#111827">'
                            f'{c["mean_diff"]:+.4f} {mark.get(c["category"], "?")}</text>')
                body.append(f'<text x="{x + cw / 2}" y="{y + 32}" text-anchor="middle" font-size="9" fill="#374151">'
                            f'[{c["ci95"][0]:+.4f}, {c["ci95"][1]:+.4f}]</text>')
    ly = top + len(qs) * ch + 28
    body.append(f'<text x="{left}" y="{ly}" font-size="11" fill="#1f2328">Cell text: mean paired R30 difference A2 - A1 (proportion) and its 95% '
                'stratified bootstrap interval (per cell, unadjusted).</text>')
    body.append(f'<text x="{left}" y="{ly + 16}" font-size="11" fill="#1f2328">Codes: R- relevant negative, R+ relevant positive, EQ practically '
                'equivalent, D detectable below SESOI, I inconclusive, F floor.</text>')
    body.append(f'<text x="{left}" y="{ly + 32}" font-size="11" fill="#1f2328">Colour: orange A2 above A1, blue A2 below A1, '
                f'scaled to the largest absolute mean ({vmax:.4f}). n = 500 learners per cell.</text>')
    desc = "; ".join(f'{c["cell_id"]}: {c["mean_diff"]:+.4f} [{c["ci95"][0]:+.4f}, {c["ci95"][1]:+.4f}] {c["category"]}' for c in cells)
    return ('<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-labelledby="t d" font-family="Helvetica, Arial, sans-serif" font-size="12">'
            f'<title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>'
            f'<rect width="{W}" height="{H}" fill="#ffffff"/>' + "".join(body) + "</svg>\n")


# --------------------------------------------------------------------------- EXP-003

#: EXP-003 section 4: policy cells as (timing, selection).
POLICY = {"A1": ("fixed", "round_robin"), "F-EASY": ("fixed", "easiest"), "F-DUE": ("fixed", "due_threshold"),
          "D-RR": ("daily", "round_robin"), "A2": ("daily", "easiest"), "A3": ("daily", "due_threshold")}


def exp003_effects(doc: dict, analysis: dict) -> dict:
    """Per model variant: the interaction of section 9, H-inv (flat-gain variants) and main
    effects (conventional definition, labelled)."""
    sesoi = doc["config"]["analysis"]["sesoi"]
    out = []
    for c in analysis["cells"]:
        cell = c["cell_id"]
        form, gain = cell.split("-")
        inter = linear_contrast(doc, cell, {"A2": 1, "D-RR": -1, "F-EASY": -1, "A1": 1},
                                "interaction [(A2 - D-RR) - (F-EASY - A1)]")
        main_t = linear_contrast(doc, cell, {"D-RR": 1 / 3, "A2": 1 / 3, "A3": 1 / 3,
                                             "A1": -1 / 3, "F-EASY": -1 / 3, "F-DUE": -1 / 3},
                                 "main effect of timing: mean(daily) - mean(3 per week)")
        main_easy = linear_contrast(doc, cell, {"A2": 0.5, "F-EASY": 0.5, "D-RR": -0.5, "A1": -0.5},
                                    "main effect of selection: easiest first - round-robin (mean over timing)")
        main_due = linear_contrast(doc, cell, {"A3": 0.5, "F-DUE": 0.5, "D-RR": -0.5, "A1": -0.5},
                                   "main effect of selection: threshold - round-robin (mean over timing)")
        entry = {"variant": cell, "form": form, "gain_rule": gain,
                 "primary_A2_minus_A1": c["primary"],
                 "interaction": inter,
                 "main_effects_conventional_definition": [main_t, main_easy, main_due]}
        if gain == "flat":
            p = c["primary"]
            lo95 = p["ci95"][0]
            lo90, hi90 = p["ci90"]
            equiv = -sesoi < lo90 and hi90 < sesoi
            entry["H_inv"] = {
                "rule": ("EXP-001 interpretation reported as dependent on the difficulty-dependent gain if, under flat "
                         "gain, the 90% interval lies inside +-SESOI or the 95% interval lies entirely above 0"),
                "ci90_inside_sesoi": bool(equiv), "ci95_entirely_above_0": bool(lo95 > 0),
                "triggered": bool(equiv or lo95 > 0),
                "H0_rejected_unadjusted": bool(p["ci95"][0] > 0 or p["ci95"][1] < 0),
            }
        out.append(entry)
    return {"variants": out}


def effects_svg(effects: dict, title: str) -> str:
    """EXP-003 figure: per variant, mean and 95% interval of A2 - A1, the interaction and the
    selection and timing effects within each level (from the generator's secondary contrasts
    is not needed here: only the combinations computed above)."""
    rows = []
    for v in effects["variants"]:
        items = [("A2 - A1", v["primary_A2_minus_A1"]), ("interaction", v["interaction"])]
        items += [(lab, s) for lab, s in zip(["timing (main)", "easiest - RR (main)", "threshold - RR (main)"],
                                             v["main_effects_conventional_definition"])]
        rows += [(v["variant"], lab, s) for lab, s in items if s]
    lo = min(min(s["ci95"][0] for _, _, s in rows), 0.0)
    hi = max(max(s["ci95"][1] for _, _, s in rows), 0.0)
    pad = 0.05 * (hi - lo) + 1e-4
    lo, hi = lo - pad, hi + pad
    W, rh, top, left, right = 720, 18, 50, 300, 30
    H = top + len(rows) * rh + 70
    def x(v): return left + (W - left - right) * (v - lo) / (hi - lo)
    body = [f'<text x="20" y="22" font-size="14" fill="#1f2328">{escape(title)}</text>',
            f'<line x1="{x(0):.1f}" y1="{top - 6}" x2="{x(0):.1f}" y2="{top + len(rows) * rh}" stroke="#1f2328" stroke-dasharray="4 3"/>']
    for i, (var, lab, s) in enumerate(rows):
        y = top + i * rh + rh / 2
        body.append(f'<text x="{left - 8}" y="{y + 4:.1f}" text-anchor="end" font-size="11" fill="#1f2328">{escape(var)}: {escape(lab)}</text>')
        body.append(f'<line x1="{x(s["ci95"][0]):.1f}" y1="{y:.1f}" x2="{x(s["ci95"][1]):.1f}" y2="{y:.1f}" stroke="#1d4ed8" stroke-width="2"/>')
        body.append(f'<circle cx="{x(s["mean_diff"]):.1f}" cy="{y:.1f}" r="3" fill="#1d4ed8"/>')
    for t in np.linspace(lo, hi, 5):
        body.append(f'<text x="{x(t):.1f}" y="{top + len(rows) * rh + 16}" text-anchor="middle" font-size="10" fill="#6b7280">{t:.3f}</text>')
    body.append(f'<text x="{(left + W - right) / 2}" y="{top + len(rows) * rh + 36}" text-anchor="middle" font-size="11" fill="#1f2328">'
                'paired R30 difference (proportion); dot = mean, bar = 95% stratified bootstrap interval, n = 500</text>')
    desc = "; ".join(f'{var} {lab}: {s["mean_diff"]:+.4f} [{s["ci95"][0]:+.4f}, {s["ci95"][1]:+.4f}]' for var, lab, s in rows)
    return ('<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-labelledby="t d" font-family="Helvetica, Arial, sans-serif" font-size="12">'
            f'<title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>'
            f'<rect width="{W}" height="{H}" fill="#ffffff"/>' + "".join(body) + "</svg>\n")
