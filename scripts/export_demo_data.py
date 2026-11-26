# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Export the published results for the M5 demo page (master prompt 11.6, M5).

Writes ``demo/public/data/results.json`` in the shared template schema
(``lab-demo-results`` 1.0.0) plus STREAK-specific top-level keys used by the
page's charts. Inputs are committed files only: generated analysis outputs,
committed confirmatory and exploratory summaries, the frozen configs, the
experiment registry, the claims register, the artifact manifest, the manuscript
and the experiment reports. No simulation is run, nothing is recomputed from raw
records, and no timestamp is written, so the output is a pure function of the
committed inputs.

Every ``display`` and ``interval_display`` string is formatted from the committed
value and must appear verbatim in its declared source text (the manuscript by
default, otherwise the named experiment report). The export fails closed if a
string is missing from its source.

Usage: .venv/bin/python scripts/export_demo_data.py [--check]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "demo/public/data/results.json"
MANUSCRIPT = "research/paper/manuscript.md"
REPORT = {e: f"research/experiments/{e}/report.md" for e in ("EXP-001", "EXP-002", "EXP-003")}


class ExportError(RuntimeError):
    """Raised when a committed input is missing or a display string has no verbatim source."""


class Reader:
    """Reads committed inputs and records each one's SHA-256 for the ``sources`` list."""

    def __init__(self) -> None:
        self.sources: dict[str, str] = {}

    def _bytes(self, rel: str) -> bytes:
        path = ROOT / rel
        if not path.is_file():
            raise ExportError(f"missing committed input: {rel}")
        data = path.read_bytes()
        self.sources[rel] = hashlib.sha256(data).hexdigest()
        return data

    def text(self, rel: str) -> str:
        return self._bytes(rel).decode("utf-8")

    def json(self, rel: str):
        return json.loads(self._bytes(rel))

    def csv(self, rel: str) -> list[dict[str, str]]:
        return list(csv.DictReader(self.text(rel).splitlines()))


def f4(x: float) -> str:
    return f"{x:.4f}"


def s4(x: float) -> str:
    """Four decimals with an explicit sign, as the reports print secondary contrasts."""
    return f"{x:+.4f}"


def bracket(lo: float, hi: float, fmt=f4) -> str:
    return f"[{fmt(lo)}, {fmt(hi)}]"


def ci_words(lo: float, hi: float) -> str:
    return f"95% CI {f4(lo)} to {f4(hi)}"


class Texts:
    """Holds source texts and checks that display strings occur in them verbatim."""

    def __init__(self, reader: Reader, paths: list[str]) -> None:
        self.text = {p: reader.text(p) for p in paths}

    def require(self, s: str, source: str) -> None:
        if source not in self.text:
            raise ExportError(f"unknown display source {source}")
        if s not in self.text[source]:
            raise ExportError(f"display string {s!r} does not occur verbatim in {source}")


def estimate(texts: Texts, label: str, value: float, ci: list[float] | None, display: str,
             interval_display: str | None, *, unit: str = "R30 proportion",
             source: str = MANUSCRIPT, interval_source: str | None = None, note: str = "") -> dict:
    """One template estimate. ``source`` holds the display string verbatim; ``interval_source``
    (default: same as ``source``) holds the interval string verbatim."""
    texts.require(display, source)
    isrc = interval_source or source
    if interval_display is not None:
        texts.require(interval_display, isrc)
    e = {
        "label": label,
        "estimate": value,
        "ci_low": ci[0] if ci else None,
        "ci_high": ci[1] if ci else None,
        "ci_level": 0.95 if ci else None,
        "unit": unit,
        "display": display,
        "interval_display": interval_display,
        "display_source": source,
        "interval_source": isrc if interval_display is not None else None,
    }
    if note:
        e["note"] = note
    return e


def contrast_row(rows: list[dict[str, str]], cell: str, contrast: str, kind_prefix: str = "") -> dict:
    hits = [r for r in rows if r["cell_id"] == cell and r["contrast"] == contrast
            and r["metric"] == "R30" and "excluded" not in r["kind"] and r["kind"].startswith(kind_prefix)]
    if len(hits) != 1:
        raise ExportError(f"expected one contrast row for {cell} {contrast}, found {len(hits)}")
    return hits[0]


def metric_row(rows: list[dict[str, str]], cell: str, arm: str, metric: str) -> dict:
    hits = [r for r in rows if r["cell_id"] == cell and r["arm"] == arm and r["metric"] == metric]
    if len(hits) != 1:
        raise ExportError(f"expected one metric row for {cell} {arm} {metric}, found {len(hits)}")
    return hits[0]


def claims_for(claims: list[dict[str, str]], manifest: dict, prefixes: tuple[str, ...]) -> list[str]:
    ids = [c["claim_id"] for c in claims if c["result_id"].startswith(prefixes)]
    if not ids:
        raise ExportError(f"no claim maps to result ids starting with {prefixes}")
    for c in claims:
        if c["claim_id"] in ids and c["result_id"] not in manifest["results"]:
            raise ExportError(f"{c['claim_id']}: result id {c['result_id']} not in the artifact manifest")
    return ids


def registry_status(registry: list[dict[str, str]], exp_id: str) -> str:
    row = next((r for r in registry if r["exp_id"] == exp_id), None)
    if row is None:
        raise ExportError(f"{exp_id} not in the experiment registry")
    m = re.match(r"(complete \(confirmatory[^)]*\))", row["status"])
    if not m:
        raise ExportError(f"{exp_id}: registry status is not complete: {row['status']!r}")
    return m.group(1)


def manuscript_limitations(ms: str) -> list[str]:
    sec = ms.split("# 7. Limitations and threats to validity", 1)
    if len(sec) != 2:
        raise ExportError("manuscript section 7 not found")
    body = sec[1].split("\n# ", 1)[0]
    items = [re.sub(r"\*\*(.+?)\*\*", r"\1", line[2:]).strip()
             for line in body.splitlines() if line.startswith("- ")]
    if len(items) < 5:
        raise ExportError("manuscript section 7 has fewer bullets than expected")
    return items


ARM_NAMES = {"A0": "A0 NoPractice", "A1": "A1 Fixed", "A2": "A2 Streak", "A3": "A3 Spaced"}
VARIANT_NAMES = {
    "exp-diff": "exponential, difficulty gain",
    "exp-flat": "exponential, flat gain",
    "pow-diff": "power law, difficulty gain",
    "pow-flat": "power law, flat gain",
}


def build() -> dict:
    rd = Reader()
    texts = Texts(rd, [MANUSCRIPT, *REPORT.values()])
    ms = texts.text[MANUSCRIPT]
    claims = rd.csv("research/claims_register.csv")
    manifest = rd.json("research/publication/artifact_manifest.json")
    registry = rd.csv("research/experiment_registry.csv")

    # ---------------- EXP-001 ----------------
    fa1 = rd.json("research/experiments/EXP-001/generated/frozen_analysis.json")
    c1 = rd.csv("research/experiments/EXP-001/generated/contrasts.csv")
    m1 = rd.csv("research/experiments/EXP-001/generated/metrics.csv")
    rm1 = rd.json("results/confirmatory/EXP-001/run_manifest.json")
    cfg1 = rd.json("research/experiments/EXP-001/config.json")
    if fa1["n_failed"] != 0 or rm1["config_hash"] != fa1["config_hash"]:
        raise ExportError("EXP-001: failed records or config hash mismatch")
    pr = fa1["primary"]
    est1 = [estimate(texts, "A2 Streak - A1 Fixed, R30 (primary)", pr["mean_diff"], pr["ci95"],
                     f4(pr["mean_diff"]), ci_words(*pr["ci95"]))]
    for contrast, label, disp, interval, isrc in (
        ("A3 - A1", "A3 Spaced - A1 Fixed, R30", s4, ci_words, None),
        ("A2 - A0", "A2 Streak - A0 NoPractice, R30", f4, ci_words, None),
        ("A2 - A3", "A2 Streak - A3 Spaced, R30 (identical activity)", f4, bracket, REPORT["EXP-001"]),
    ):
        r = contrast_row(c1, "default", contrast, "secondary")
        lo, hi = float(r["ci95_low"]), float(r["ci95_high"])
        est1.append(estimate(texts, label, float(r["mean_diff"]), [lo, hi], disp(float(r["mean_diff"])),
                             interval(lo, hi), interval_source=isrc,
                             note="Interval printed in the EXP-001 report (section 8.3); the manuscript prints the estimate only." if isrc else ""))
    arms = []
    for arm in ("A0", "A1", "A2", "A3"):
        r30 = metric_row(m1, "default", arm, "R30")
        lo, hi = float(r30["ci95_low"]), float(r30["ci95_high"])
        est1.append(estimate(texts, f"R30, {ARM_NAMES[arm]}", float(r30["mean"]), [lo, hi],
                             f4(float(r30["mean"])), bracket(lo, hi)))
        curve = []
        for delay in (1, 7, 30, 90):
            row = metric_row(m1, "default", arm, f"R{delay}")
            v = float(row["mean"])
            texts.require(f4(v), REPORT["EXP-001"])
            curve.append({
                "delay_days": delay, "mean": v,
                "ci_low": float(row["ci95_low"]) if row["ci95_low"] else None,
                "ci_high": float(row["ci95_high"]) if row["ci95_high"] else None,
                "display": f4(v), "display_source": REPORT["EXP-001"],
            })
        act = float(metric_row(m1, "default", arm, "active_days")["mean"])
        streak = float(metric_row(m1, "default", arm, "longest_streak")["mean"])
        cov = float(metric_row(m1, "default", arm, "item_coverage")["mean"])
        minutes = float(metric_row(m1, "default", arm, "minutes_spent")["mean"])
        for s in (f"{act:.2f}", f"{streak:.2f}", f"{cov:.3f}"):
            texts.require(s, MANUSCRIPT)
        texts.require(f"{minutes:.1f}", REPORT["EXP-001"])
        arms.append({
            "arm": arm, "name": ARM_NAMES[arm], "n": int(r30["n"]),
            "r30": {"mean": float(r30["mean"]), "ci_low": lo, "ci_high": hi,
                    "display": f4(float(r30["mean"])), "interval_display": bracket(lo, hi),
                    "display_source": MANUSCRIPT},
            "active_days": {"mean": act, "display": f"{act:.2f}", "display_source": MANUSCRIPT},
            "longest_streak": {"mean": streak, "display": f"{streak:.2f}", "display_source": MANUSCRIPT},
            "item_coverage": {"mean": cov, "display": f"{cov:.3f}", "display_source": MANUSCRIPT},
            "minutes": {"mean": minutes, "display": f"{minutes:.1f}", "display_source": REPORT["EXP-001"]},
            "retention_curve": curve,
        })
    exp1 = {
        "id": "EXP-001",
        "title": "Streak-driven versus fixed practice at matched minutes",
        "status": registry_status(registry, "EXP-001"),
        "verdict": fa1["verdict"],
        "estimates": est1,
        "claim_ids": claims_for(claims, manifest, ("RES-EXP-001",)),
        "report_path": REPORT["EXP-001"],
        "notes": [
            "Primary experiment, preregistered and frozen (protocol 1.0). n = 1,000 synthetic learners per policy, master seeds 1 to 5.",
            "Intervals are 95% stratified percentile bootstrap intervals over learners within master seed (10,000 resamples). SESOI 0.02.",
        ],
        "label": "measured (confirmatory simulation)",
        "code_revision": rm1["git_revision"],
    }

    # ---------------- EXP-002 ----------------
    fa2 = rd.json("research/experiments/EXP-002/generated/frozen_analysis.json")
    rm2 = rd.json("results/confirmatory/EXP-002/run_manifest.json")
    if fa2["n_failed"] != 0 or rm2["config_hash"] != fa2["config_hash"]:
        raise ExportError("EXP-002: failed records or config hash mismatch")
    g = fa2["grid"]
    cells = []
    for c in g["cells"]:
        h0 = c["h0"]
        h0s = f"{h0:g}"
        # The whole table row (cell, arm means, estimate, interval) must occur in the report.
        row = (f"| {h0s} | {c['a']:g} | {float(c['q'])!r} | {c['mean_R30_A1']:.2f} | {c['mean_R30_A2']:.2f} "
               f"| {f4(c['mean_diff'])} | {bracket(*c['ci95'])} |")
        texts.require(row, REPORT["EXP-002"])
        cells.append({
            "cell_id": c["cell_id"], "h0_days": h0, "a": c["a"], "q": c["q"],
            "estimate": c["mean_diff"], "ci_low": c["ci95"][0], "ci_high": c["ci95"][1],
            "display": f4(c["mean_diff"]), "interval_display": bracket(*c["ci95"]),
            "display_source": REPORT["EXP-002"],
            "classification": c["classification"],
            "relevant_holm_across_cells": c["relevant_holm_across_cells"],
        })
    lo_cell = min(cells, key=lambda c: c["estimate"])
    hi_cell = max(cells, key=lambda c: c["estimate"])
    n_neg = g["grid_hypothesis_all_negative"]["n_negative_mean"]
    n_rel = g["n_relevant_holm_across_cells"]
    disc = g["robustness_disconfirmed"]
    if g["n_cells"] != 27 or disc["disconfirmed"]:
        raise ExportError("EXP-002 grid summary differs from the reported state")
    verdict2 = (f"Grid hypothesis holds: A2 - A1 negative in {n_neg} of {g['n_cells']} cells, relevant negative after "
                f"Holm adjustment across cells in {n_rel} of {g['n_cells']}; robustness not disconfirmed "
                f"({len(disc['cells_ci95_entirely_above_0'])} cells with a 95% interval above 0, "
                f"{disc['n_practically_equivalent']} practically equivalent).")
    c2 = rd.csv("research/experiments/EXP-002/generated/contrasts.csv")
    a3 = [float(r["mean_diff"]) for r in c2 if r["contrast"] == "A3 - A1" and r["kind"] == "secondary"
          and r["cell_id"].startswith("h0=33.8|")]
    if len(a3) != 9:
        raise ExportError("EXP-002: expected 9 A3 - A1 cells at h0 = 33.8")
    a3_range = f"{f4(min(a3))} to {f4(max(a3))}"
    texts.require(a3_range, MANUSCRIPT)
    exp2 = {
        "id": "EXP-002",
        "title": "When does the gap appear: robustness across forgetting parameters and availability",
        "status": registry_status(registry, "EXP-002"),
        "verdict": verdict2,
        "estimates": [
            estimate(texts, f"A2 - A1, largest gap (h0 = {lo_cell['h0_days']:g} days, a = {lo_cell['a']:g}, q = {lo_cell['q']:g})",
                     lo_cell["estimate"], [lo_cell["ci_low"], lo_cell["ci_high"]], lo_cell["display"],
                     lo_cell["interval_display"], interval_source=REPORT["EXP-002"],
                     note="Interval printed in the EXP-002 report (table 8.1); the manuscript prints the estimate only."),
            estimate(texts, f"A2 - A1, smallest gap (h0 = {hi_cell['h0_days']:g} days, a = {hi_cell['a']:g}, q = {hi_cell['q']:g})",
                     hi_cell["estimate"], [hi_cell["ci_low"], hi_cell["ci_high"]], hi_cell["display"],
                     hi_cell["interval_display"], interval_source=REPORT["EXP-002"],
                     note="Interval printed in the EXP-002 report (table 8.1); the manuscript prints the estimate only."),
        ],
        "claim_ids": claims_for(claims, manifest, ("RES-EXP-002",)),
        "report_path": REPORT["EXP-002"],
        "notes": [
            "27 cells: h0 in {33.8, 67.59, 135.18} days, gain coefficient a in {1.5, 2.5, 4}, availability q in {0.7, 0.85, 1.0}; 500 learners per cell. All 27 cells are drawn in the cell chart.",
            f"Unexpected secondary result: at h0 = 33.8 days the threshold comparator A3 retained less than A1 in all 9 cells ({a3_range}), relevant in 8.",
            "The cells share learners (common random numbers), so they are not independent confirmations.",
        ],
        "label": "measured (confirmatory simulation)",
        "code_revision": rm2["git_revision"],
    }

    # ---------------- EXP-003 ----------------
    fa3 = rd.json("research/experiments/EXP-003/generated/frozen_analysis.json")
    rm3 = rd.json("results/confirmatory/EXP-003/run_manifest.json")
    if fa3["n_failed"] != 0 or rm3["config_hash"] != fa3["config_hash"]:
        raise ExportError("EXP-003: failed records or config hash mismatch")
    est3, effects = [], []
    flat_ok = []
    for v in fa3["effects"]["variants"]:
        name = VARIANT_NAMES[v["variant"]]
        p = v["primary_A2_minus_A1"]
        est3.append(estimate(texts, f"A2 - A1, {name}", p["mean_diff"], p["ci95"], f4(p["mean_diff"]),
                             bracket(*p["ci95"])))
        if v["gain_rule"] == "flat":
            flat_ok.append(p["classification"] == "relevant negative")
        rows = [("A2 - A1", p, MANUSCRIPT)]
        me = {m["contrast"]: m for m in v["main_effects_conventional_definition"]}
        rows += [
            ("Easiest first - round-robin (main effect)",
             me["main effect of selection: easiest first - round-robin (mean over timing)"], MANUSCRIPT),
            ("Threshold - round-robin (main effect)",
             me["main effect of selection: threshold - round-robin (mean over timing)"], REPORT["EXP-003"]),
            ("Daily - 3 per week (timing main effect)", me["main effect of timing: mean(daily) - mean(3 per week)"], MANUSCRIPT),
            ("Timing x selection interaction", v["interaction"], MANUSCRIPT),
        ]
        eff = []
        for label, e, src in rows:
            # The report prints signed values with signed bracketed intervals in table 8.4.
            if label == "A2 - A1":
                disp, idisp, isrc = f4(e["mean_diff"]), bracket(*e["ci95"]), MANUSCRIPT
            else:
                disp = f4(e["mean_diff"]) if src == MANUSCRIPT else s4(e["mean_diff"])
                idisp = bracket(*e["ci95"], fmt=s4 if e["ci95"][0] >= 0 or e["ci95"][1] > 0 else f4)
                isrc = REPORT["EXP-003"]
                texts.require(f"{s4(e['mean_diff']) if e['mean_diff'] > 0 else f4(e['mean_diff'])} {idisp}",
                              REPORT["EXP-003"])
            texts.require(disp, src)
            texts.require(idisp, isrc)
            eff.append({"effect": label, "estimate": e["mean_diff"], "ci_low": e["ci95"][0], "ci_high": e["ci95"][1],
                        "display": disp, "interval_display": idisp, "display_source": src,
                        "interval_source": isrc, "classification": e["classification"]})
        effects.append({"variant": v["variant"], "name": name, "effects": eff})
    if len(flat_ok) != 2:
        raise ExportError("EXP-003: expected two flat-gain variants")
    verdict3 = ("H-inv not triggered: under the flat gain rule A2 - A1 stayed relevant negative for both forgetting forms."
                if all(flat_ok) else "H-inv triggered: the main interpretation is invalidated under flat gain.")
    exp3 = {
        "id": "EXP-003",
        "title": "Timing versus item selection, and model-form sensitivity",
        "status": registry_status(registry, "EXP-003"),
        "verdict": verdict3,
        "estimates": est3,
        "claim_ids": claims_for(claims, manifest, ("RES-EXP-003",)),
        "report_path": REPORT["EXP-003"],
        "notes": [
            "2 x 3 design (timing: daily or 3 per week; selection: round-robin, easiest first or threshold) under 4 model variants; 500 learners per variant.",
            "Main effects use the conventional equal-weight marginal definition, which the protocol names without a formula (an AI reading). Effect intervals are printed in the EXP-003 report (table 8.4); the manuscript prints the estimates only.",
        ],
        "label": "measured (confirmatory simulation)",
        "code_revision": rm3["git_revision"],
    }

    # ---------------- Held-out test (P section 14.4) ----------------
    ho = rd.json("results/confirmatory/HELDOUT-14.4/heldout.json")
    ev = ho["evaluation"]
    if ho["reading"]["exponential_beats_constant"] is not False:
        raise ExportError("held-out reading differs from the reported negative result")
    est_ho = [
        estimate(texts, "Constant-recall baseline, log-likelihood per held-out trial", ev["constant"]["ll_per_trial"],
                 None, f4(ev["constant"]["ll_per_trial"]), None, unit="nats per trial"),
        estimate(texts, "Power-law form, log-likelihood per held-out trial", ev["power"]["ll_per_trial"],
                 None, f4(ev["power"]["ll_per_trial"]), None, unit="nats per trial"),
        estimate(texts, "Exponential form (the model's default), log-likelihood per held-out trial",
                 ev["exponential"]["ll_per_trial"], None, f4(ev["exponential"]["ll_per_trial"]), None,
                 unit="nats per trial"),
    ]
    calib = []
    for be, bp in zip(ev["exponential"]["calibration"], ev["power"]["calibration"]):
        if be["bin"] != bp["bin"] or be["trials"] != bp["trials"]:
            raise ExportError("held-out calibration bins differ between forms")
        lo, hi = be["bin"]
        closing = "]" if hi == 90 else ")"
        label = f"[{lo:g}, {hi:g}{closing}"
        row = f"| {label} | {be['trials']:,} | {be['observed']:.3f} | {be['predicted']:.3f} | {bp['predicted']:.3f} |"
        texts.require(row, REPORT["EXP-001"])
        calib.append({"bin": label, "bin_low_days": lo, "bin_high_days": hi, "trials": be["trials"],
                      "observed": be["observed"], "predicted_exponential": be["predicted"],
                      "predicted_power": bp["predicted"],
                      "display_observed": f"{be['observed']:.3f}",
                      "display_exponential": f"{be['predicted']:.3f}",
                      "display_power": f"{bp['predicted']:.3f}", "display_source": REPORT["EXP-001"]})
    heldout = {
        "id": "HELDOUT-14.4",
        "title": "Held-out test of the forgetting model on real Duolingo traces (not a registered experiment)",
        "status": "complete (preregistered descriptive test, protocol section 14.4, run once after the freeze)",
        "verdict": "Negative result for the model's forgetting assumption: the exponential form does not describe the held-out first-repeat data better than a constant-recall baseline; the power-law form is better supported than the exponential form.",
        "estimates": est_ho,
        "claim_ids": claims_for(claims, manifest, ("RES-HELDOUT",)),
        "report_path": "research/experiments/EXP-001/report.md (section 8.4)",
        "notes": [
            f"Held-out user split: {ev['n_test_rows']:,} first-repeat rows, {ev['n_test_trials']:,} trials. Higher (less negative) log-likelihood is better.",
            "No interval was computed for these log-likelihoods; the naive likelihood treats trials as independent.",
        ],
        "label": "measured (real public data, descriptive test)",
        "code_revision": ho["git_revision"],
    }

    # ---------------- Floor regime (exploratory, pre-freeze) ----------------
    fl = rd.csv("results/exploratory/SMOKE-EXP-001-N200/report/contrasts.csv")
    fr = contrast_row(fl, "default", "A2 - A1", "primary")
    flo, fhi = float(fr["ci95_low"]), float(fr["ci95_high"])
    floor = {
        "id": "SMOKE-EXP-001-N200",
        "title": "Contradictory evidence: the floor regime at the draft parameters (exploratory, not a registered experiment)",
        "status": "exploratory, seen before the freeze (draft parameters h0 = 1 day, K = 100, an earlier A3 rule; smoke seeds)",
        "verdict": "No frozen rule applies (exploratory). The sign is the opposite of the confirmatory result: in a regime where nearly every item is forgotten by the test, daily easy practice beat sparse round-robin.",
        "estimates": [estimate(texts, "A2 - A1, R30, draft parameters", float(fr["mean_diff"]), [flo, fhi],
                               s4(float(fr["mean_diff"])), ci_words(flo, fhi))],
        "claim_ids": claims_for(claims, manifest, ("RES-SMOKE-EXP-001-N200",)),
        "report_path": "results/exploratory/SMOKE-EXP-001-N200/report/report.md",
        "notes": [
            "These values were seen before the freeze; the decision to leave the floor regime was taken with them visible. The rules that set the frozen parameters used the control arms only (manuscript section 5.5).",
        ],
        "label": "exploratory (pre-freeze smoke run)",
        "code_revision": "dfa9dd4",
    }

    # ---------------- M4 sensitivity (exploratory) ----------------
    sens = rd.json("results/exploratory/M4-SENSITIVITY/summary.json")
    est_s = []
    runs = sens["part_b_sensitivity_runs"]
    ordered = sorted([r for r in runs if "SLOWH0" not in r["exploratory_id"]], key=lambda r: r["K"]) + \
        sorted([r for r in runs if "SLOWH0" in r["exploratory_id"]], key=lambda r: r["h0"])
    for r in ordered:
        d = r["A2_minus_A1"]
        label = (f"A2 - A1, K = {r['K']} items" if "SLOWH0" not in r["exploratory_id"]
                 else f"A2 - A1, h0 = {r['h0']:g} days")
        est_s.append(estimate(texts, label, d["mean"], d["ci95"], f4(d["mean"]), bracket(*d["ci95"])))
    sens_entry = {
        "id": "M4-SENSITIVITY",
        "title": "Sensitivity to the number of items and to slower forgetting (exploratory, not a registered experiment)",
        "status": "exploratory, after the confirmatory analysis (smoke seeds 9001 to 9005, 500 learners per row)",
        "verdict": "No frozen rule applies (exploratory); no confirmatory verdict changes.",
        "estimates": est_s,
        "claim_ids": claims_for(claims, manifest, ("RES-M4-",)),
        "report_path": "research/paper/manuscript.md (section 5.6)",
        "notes": [
            "The gap varies with K in a non-monotone way and shrinks in absolute size under much slower forgetting, while A2 recovers about the same share of A1's gain over no practice (0.186 to 0.188).",
        ],
        "label": "exploratory (smoke seeds)",
        "code_revision": sens["git_revision_at_generation"],
    }

    # ---------------- Assumptions (model inputs, not results) ----------------
    bp = cfg1["base_params"]
    cal = rd.json("results/exploratory/CAL-H0/fit.json")
    lr = cal["fit"]["lr95_naive_days"]
    h0_text = (f"{bp['h0']:g} days, fitted on the Duolingo fit split (naive 95% likelihood-ratio interval "
               f"{lr[0]:.2f} to {lr[1]:.2f} days)")
    texts.require(f"{lr[0]:.2f} to {lr[1]:.2f} days", MANUSCRIPT)
    minutes = bp["budget_slots"] * bp["slot_minutes"]
    assumptions = [
        {"name": "Items per learner, K", "value": f"{bp['n_items']} (set by a control-only ceiling rule before the freeze)", "source": "research/experiments/EXP-001/config.json; manuscript section 4.3"},
        {"name": "Practice horizon, T", "value": f"days 1 to {bp['horizon_days']}", "source": "research/experiments/EXP-001/config.json"},
        {"name": "Practice budget, M", "value": f"{bp['budget_slots']} slots of {bp['slot_minutes']:g} minutes ({minutes:g} minutes) per learner, at most {bp['daily_cap_slots']} slots per day", "source": "research/experiments/EXP-001/config.json"},
        {"name": "Median initial half-life, h0", "value": h0_text, "source": "results/exploratory/CAL-H0/fit.json; manuscript section 4.2"},
        {"name": "Forgetting curve", "value": "p = 2^(-delay/h) (exponential, default); power-law form in EXP-003", "source": "manuscript section 3.1"},
        {"name": "Gain on a successful review", "value": f"h <- h(1 + {bp['g_min']:g} + {bp['a']:g}(1 - p)) (difficulty-dependent, default); flat gain h <- 1.85h in EXP-003", "source": "manuscript section 3.1"},
        {"name": "Failed review", "value": f"h <- max({bp['h_min']:g}, {bp['b']:g}h)", "source": "manuscript section 3.1"},
        {"name": "Heterogeneity", "value": f"item log-SD {bp['sigma_item']:g}, learner log-SD {bp['sigma_learner']:g}", "source": "research/experiments/EXP-001/config.json"},
        {"name": "Daily availability, q", "value": f"{bp['q']:g}, drawn once per learner and shared by all policies", "source": "research/experiments/EXP-001/config.json"},
        {"name": "Scheduler belief", "value": "population-median parameters and the default model, updated with observed outcomes; never the true state", "source": "manuscript section 3.3"},
        {"name": "Threshold of A3", "value": "items with estimated recall at or below 0.9 first", "source": "manuscript section 3.3"},
        {"name": "Smallest effect size of interest", "value": f"{cfg1['analysis']['sesoi']:g} in R30", "source": "research/experiments/EXP-001/config.json; protocol 1.0"},
    ]

    # ---------------- Sandbox scenarios (assumption values for the browser port) ----------------
    cfg2 = rd.json("research/experiments/EXP-002/config.json")
    cfg3 = rd.json("research/experiments/EXP-003/config.json")
    keys = ("n_items", "horizon_days", "budget_slots", "slot_minutes", "daily_cap_slots", "fixed_weekdays",
            "h0", "sigma_item", "sigma_learner", "g_min", "a", "b", "h_min", "q", "form", "gain_rule")
    base = {k: bp[k] for k in keys}
    for c in (cfg2, cfg3):
        if {k: c["base_params"][k] for k in keys if k in c["base_params"]} != {k: base[k] for k in keys if k in c["base_params"]}:
            raise ExportError("EXP-002 or EXP-003 base parameters differ from EXP-001")
    grid = cfg2.get("grid") or cfg2.get("parameter_grid")
    if not grid:
        raise ExportError("EXP-002 config has no grid")
    h0_axis = grid["h0"]
    scenarios = [
        {"id": "default", "name": "Frozen default parameters (as EXP-001)", "params": dict(base),
         "source": "research/experiments/EXP-001/config.json"},
        {"id": "fast", "name": f"Faster forgetting, h0 = {min(h0_axis):g} days (EXP-002 axis)",
         "params": {**base, "h0": min(h0_axis)}, "source": "research/experiments/EXP-002/config.json"},
        {"id": "slow", "name": f"Slower forgetting, h0 = {max(h0_axis):g} days (EXP-002 axis)",
         "params": {**base, "h0": max(h0_axis)}, "source": "research/experiments/EXP-002/config.json"},
        {"id": "always", "name": "Always available, q = 1 (EXP-002 axis)", "params": {**base, "q": max(grid["q"])},
         "source": "research/experiments/EXP-002/config.json"},
        {"id": "flat", "name": "Flat gain rule (EXP-003 variant)", "params": {**base, "gain_rule": "flat"},
         "source": "research/experiments/EXP-003/config.json"},
        {"id": "power", "name": "Power-law forgetting (EXP-003 variant)", "params": {**base, "form": "power"},
         "source": "research/experiments/EXP-003/config.json"},
        {"id": "k50", "name": "Fewer items, K = 50 (M4 exploratory setting)", "params": {**base, "n_items": 50},
         "source": "experiments/m4-sens-k050.json"},
        {"id": "floor", "name": "Near-total forgetting, h0 = 1 day and K = 100 (pre-freeze draft regime)",
         "params": {**base, "h0": 1.0, "n_items": 100},
         "source": "src/streak/params.py draft defaults; manuscript section 5.5 (the published floor values used an earlier A3 rule)"},
    ]
    k50 = rd.json("experiments/m4-sens-k050.json")
    if k50["base_params"]["n_items"] != 50:
        raise ExportError("m4-sens-k050.json does not set K = 50")
    for v in cfg3["model_variants"]:
        if v["form"] not in ("exponential", "power") or v["gain_rule"] not in ("difficulty", "flat"):
            raise ExportError("unexpected EXP-003 model variant")

    revs = sorted({exp1["code_revision"][:7] + " (EXP-001, EXP-002, held-out test)"
                   if exp1["code_revision"] == exp2["code_revision"] == heldout["code_revision"] else "",
                   exp3["code_revision"][:7] + " (EXP-003)"} - {""}, reverse=True)
    if exp1["code_revision"] != exp2["code_revision"]:
        raise ExportError("EXP-001 and EXP-002 revisions differ; update the code_revision text")

    status_label = ("Simulation of synthetic learners. Independent research manuscript 1.0, preprint draft, "
                    "not peer reviewed. Protocol 1.0 frozen on 2026-11-24; all three registered experiments "
                    "complete. The title and the funding, competing-interest and AI-assistance statements were "
                    "approved by the owner on 2026-11-25; the owner's full-text review of the manuscript is "
                    "pending (M6). The repository is public; no release exists yet.")
    out = {
        "schema": "lab-demo-results",
        "schema_version": "1.0.0",
        "project": "STREAK",
        "question": "When can activity streaks diverge from knowledge retention in a learning model?",
        "status_label": status_label,
        "code_revision": "; ".join(revs),
        "sources": [],
        "experiments": [exp1, exp2, exp3, heldout, floor, sens_entry],
        "assumptions": assumptions,
        "limitations": manuscript_limitations(ms),
        "streak_vs_recall": {
            "experiment_id": "EXP-001",
            "note": "Mean per policy over 1,000 synthetic learners at the frozen default parameters. R30 intervals are 95% stratified bootstrap intervals. Active days and longest streak are descriptive means; no interval was computed for them. Retention at delays 1, 7 and 90 days has no interval in the committed outputs.",
            "arms": arms,
        },
        "exp002_grid": {
            "experiment_id": "EXP-002",
            "contrast": "A2 - A1 in R30",
            "sesoi": cfg2["analysis"]["sesoi"],
            "cells": cells,
        },
        "exp003_effects": {
            "experiment_id": "EXP-003",
            "sesoi": cfg3["analysis"]["sesoi"],
            "variants": effects,
        },
        "heldout_calibration": {
            "experiment_id": "HELDOUT-14.4",
            "note": "Observed recall on held-out Duolingo first repeats by delay bin, against the recall predicted by each fitted forgetting form. In-session accuracy of users of one product, not free recall.",
            "bins": calib,
        },
        "sandbox_scenarios": scenarios,
    }
    out["sources"] = [{"path": p, "sha256": h} for p, h in sorted(rd.sources.items())]
    return out


def serialise(d: dict) -> str:
    return json.dumps(d, indent=1, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="compare with the committed file instead of writing")
    args = ap.parse_args(argv)
    text = serialise(build())
    if args.check:
        same = OUT.is_file() and OUT.read_text() == text
        print("results.json up to date" if same else "results.json differs from a fresh export")
        return 0 if same else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(text.encode())} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
