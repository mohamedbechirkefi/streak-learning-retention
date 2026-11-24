# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Report generator: validated result file -> analysis.json, CSV tables, SVG figures,
a Markdown report and (optionally) a PDF through pandoc -> Typst.

Every number in the outputs is computed here from the result file; nothing is
typed by hand. Figures are plain SVG written without a plotting dependency.
"""

from __future__ import annotations

import csv
import io
import json
import os
import subprocess
from html import escape
from pathlib import Path

import numpy as np

from .manifest import repo_root, sha256_file
from .runner import load_result
from .stats import holm_adjust, paired_summary, percentile_interval, spearman, stratified_bootstrap_means

SUMMARY_METRICS = ["R1", "R7", "R30", "R90", "AUC_R", "weakest_decile_R30", "minutes_spent",
                   "residual_slots", "reviews", "active_days", "longest_streak", "final_streak",
                   "missed_unavailable_days", "missed_available_days", "practice_success_rate",
                   "item_coverage"]
DEFAULT_PANDOC = "/Users/bechir/research/labs/.tools/pandoc"
DEFAULT_TYPST_PYTHON = "/Users/bechir/research/labs/.tools/py/bin/python"


# --------------------------------------------------------------------------- analysis

def _table(doc: dict) -> dict[tuple[str, str], dict[tuple[int, int], dict]]:
    """{(cell, arm): {(seed, learner): metrics}} for successful records."""
    out: dict = {}
    for r in doc["records"]:
        if r["status"] == "ok":
            out.setdefault((r["cell_id"], r["arm"]), {})[(r["master_seed"], r["learner_index"])] = r["metrics"]
    return out


def analyse(doc: dict) -> dict:
    cfg = doc["config"]
    an = cfg["analysis"]
    B, bseed, sesoi = an["bootstrap_resamples"], an["bootstrap_seed"], an["sesoi"]
    tab = _table(doc)
    cells = [c["cell_id"] for c in doc["cells"]]
    out = {"experiment_id": doc["experiment_id"], "label": doc["label"],
           "simulation_notice": doc["simulation_notice"], "config_hash": doc["config_hash"],
           "n_records": doc["n_records"], "n_failed": doc["n_failed"],
           "failure_rate": doc["n_failed"] / max(1, doc["n_records"]), "cells": []}
    for cell in cells:
        arms_out = []
        for arm in cfg["arms"]:
            rows = tab.get((cell, arm), {})
            keys = sorted(rows)
            seeds = np.array([k[0] for k in keys])
            entry = {"arm": arm, "n": len(keys), "metrics": {}}
            for m in SUMMARY_METRICS:
                vals = np.array([rows[k][m] for k in keys if rows[k].get(m) is not None], dtype=float)
                if vals.size == 0:
                    entry["metrics"][m] = None
                    continue
                e = {"mean": float(vals.mean()), "sd": float(vals.std(ddof=1)) if vals.size > 1 else 0.0,
                     "min": float(vals.min()), "max": float(vals.max())}
                if m == "R30" and vals.size == len(keys):
                    boot = stratified_bootstrap_means(vals, seeds, B, bseed)
                    e["ci95"] = list(percentile_interval(boot, 0.95))
                    e["per_seed_mean"] = {str(s): float(vals[seeds == s].mean()) for s in np.unique(seeds)}
                entry["metrics"][m] = e
            entry["residual_flagged"] = int(sum(rows[k]["residual_flag"] for k in keys))
            if keys:
                entry["spearman_active_days_R30"] = spearman(
                    np.array([rows[k]["active_days"] for k in keys]), np.array([rows[k]["R30"] for k in keys]))
            arms_out.append(entry)

        def contrast(pair, exclude_flagged=False, metric="R30"):
            t, c = pair
            rt, rc = tab.get((cell, t), {}), tab.get((cell, c), {})
            keys = sorted(set(rt) & set(rc))
            if exclude_flagged:
                flagged = {k for arm in cfg["arms"] for k, v in tab.get((cell, arm), {}).items()
                           if v["residual_flag"]}
                keys = [k for k in keys if k not in flagged]
            if len(keys) < 2:
                return None
            diff = np.array([rt[k][metric] - rc[k][metric] for k in keys])
            seeds = np.array([k[0] for k in keys])
            return paired_summary(diff, seeds, f"{t} - {c}", metric, B, bseed, sesoi).to_dict()

        primary = contrast(an["primary_contrast"])
        primary_excl = contrast(an["primary_contrast"], exclude_flagged=True)
        secondary = [contrast(p) for p in an["secondary_contrasts"]]
        valid = [s for s in secondary if s is not None]
        if valid:
            for s, adj in zip(valid, holm_adjust([s["p_boot"] for s in valid])):
                s["p_holm"] = adj
        out["cells"].append({"cell_id": cell, "arms": arms_out, "primary": primary,
                             "primary_excluding_residual_flagged": primary_excl,
                             "secondary": secondary})
    return out


# --------------------------------------------------------------------------- SVG figures

_W, _H, _ML, _MR, _MT, _MB = 640, 360, 84, 20, 40, 60
_INK, _MUTED, _ACCENT = "#1f2328", "#6b7280", "#1d4ed8"


def _svg(title: str, desc: str, body: list[str]) -> str:
    return ('<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{_W}" height="{_H}" viewBox="0 0 {_W} {_H}" '
            f'role="img" aria-labelledby="t d" font-family="Helvetica, Arial, sans-serif" font-size="12">'
            f'<title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>'
            f'<rect width="{_W}" height="{_H}" fill="#ffffff"/>'
            f'<text x="{_ML}" y="22" font-size="14" fill="{_INK}">{escape(title)}</text>'
            + "".join(body) + "</svg>\n")


def _yaxis(lo: float, hi: float, label: str) -> tuple[list[str], callable]:
    if hi <= lo:
        hi = lo + 1e-9
    def y(v): return _MT + (_H - _MT - _MB) * (1 - (v - lo) / (hi - lo))
    parts = [f'<line x1="{_ML}" y1="{_MT}" x2="{_ML}" y2="{_H - _MB}" stroke="{_MUTED}"/>']
    for tick in np.linspace(lo, hi, 5):
        parts.append(f'<line x1="{_ML - 4}" y1="{y(tick):.1f}" x2="{_W - _MR}" y2="{y(tick):.1f}" stroke="#e5e7eb"/>')
        parts.append(f'<text x="{_ML - 8}" y="{y(tick) + 4:.1f}" text-anchor="end" fill="{_MUTED}">{tick:.3g}</text>')
    parts.append(f'<text transform="translate(16 {(_MT + _H - _MB) / 2}) rotate(-90)" text-anchor="middle" fill="{_INK}">{escape(label)}</text>')
    return parts, y


def fig_arm_means(cell: dict, label: str) -> str:
    arms = [a for a in cell["arms"] if a["metrics"].get("R30")]
    lows = [a["metrics"]["R30"]["ci95"][0] for a in arms]
    highs = [a["metrics"]["R30"]["ci95"][1] for a in arms]
    lo, hi = min(lows), max(highs)
    pad = 0.1 * (hi - lo) + 1e-3
    body, y = _yaxis(max(0.0, lo - pad), min(1.0, hi + pad), "R30 (mean expected recall, proportion)")
    step = (_W - _ML - _MR) / (len(arms) + 1)
    for i, a in enumerate(arms, 1):
        m = a["metrics"]["R30"]
        x = _ML + i * step
        body.append(f'<line x1="{x:.1f}" y1="{y(m["ci95"][0]):.1f}" x2="{x:.1f}" y2="{y(m["ci95"][1]):.1f}" stroke="{_ACCENT}" stroke-width="2"/>')
        body.append(f'<circle cx="{x:.1f}" cy="{y(m["mean"]):.1f}" r="4" fill="{_ACCENT}"/>')
        body.append(f'<text x="{x:.1f}" y="{_H - _MB + 18}" text-anchor="middle" fill="{_INK}">{escape(a["arm"])}</text>')
        body.append(f'<text x="{x:.1f}" y="{_H - _MB + 33}" text-anchor="middle" fill="{_MUTED}">n={a["n"]}</text>')
    desc = (f"{label}. Mean R30 per arm with 95% stratified bootstrap interval; " +
            "; ".join(f'{a["arm"]} {a["metrics"]["R30"]["mean"]:.4f}' for a in arms))
    return _svg(f"R30 by arm ({label})", desc, body)


def fig_diff_hist(diffs: np.ndarray, contrast: str, label: str, bins: int = 30) -> str:
    counts, edges = np.histogram(diffs, bins=bins)
    body, y = _yaxis(0, float(counts.max()), "learners (count)")
    x0, x1 = float(edges[0]), float(edges[-1])
    if x1 <= x0:
        x1 = x0 + 1e-9
    def x(v): return _ML + (_W - _ML - _MR) * (v - x0) / (x1 - x0)
    for c, a, b in zip(counts, edges[:-1], edges[1:]):
        body.append(f'<rect x="{x(a):.1f}" y="{y(c):.1f}" width="{max(0.5, x(b) - x(a) - 1):.1f}" height="{y(0) - y(c):.1f}" fill="{_ACCENT}" fill-opacity="0.75"/>')
    if x0 <= 0 <= x1:
        body.append(f'<line x1="{x(0):.1f}" y1="{_MT}" x2="{x(0):.1f}" y2="{_H - _MB}" stroke="{_INK}" stroke-dasharray="4 3"/>')
    for v in np.linspace(x0, x1, 5):
        body.append(f'<text x="{x(v):.1f}" y="{_H - _MB + 18}" text-anchor="middle" fill="{_MUTED}">{v:.3g}</text>')
    body.append(f'<text x="{(_ML + _W - _MR) / 2}" y="{_H - 14}" text-anchor="middle" fill="{_INK}">paired difference in R30, {escape(contrast)} (proportion)</text>')
    desc = (f"{label}. Histogram of per-learner paired differences in R30 ({contrast}), n={diffs.size}, "
            f"mean {diffs.mean():.4f}, dashed line at zero.")
    return _svg(f"Paired R30 difference {contrast} ({label})", desc, body)


def fig_cells(cells: list[dict], label: str) -> str:
    rows = [c for c in cells if c["primary"]]
    lo = min(c["primary"]["ci95"][0] for c in rows)
    hi = max(c["primary"]["ci95"][1] for c in rows)
    lo, hi = min(lo, 0.0), max(hi, 0.0)
    pad = 0.05 * (hi - lo) + 1e-4
    body, y = _yaxis(lo - pad, hi + pad, "mean paired R30 difference")
    body.append(f'<line x1="{_ML}" y1="{y(0):.1f}" x2="{_W - _MR}" y2="{y(0):.1f}" stroke="{_INK}" stroke-dasharray="4 3"/>')
    step = (_W - _ML - _MR) / (len(rows) + 1)
    for i, c in enumerate(rows, 1):
        p = c["primary"]
        xx = _ML + i * step
        body.append(f'<line x1="{xx:.1f}" y1="{y(p["ci95"][0]):.1f}" x2="{xx:.1f}" y2="{y(p["ci95"][1]):.1f}" stroke="{_ACCENT}"/>')
        body.append(f'<circle cx="{xx:.1f}" cy="{y(p["mean_diff"]):.1f}" r="3" fill="{_ACCENT}"/>')
        body.append(f'<text x="{xx:.1f}" y="{_H - _MB + 16}" text-anchor="middle" font-size="9" fill="{_MUTED}">{i}</text>')
    contrast = rows[0]["primary"]["contrast"]
    body.append(f'<text x="{(_ML + _W - _MR) / 2}" y="{_H - 22}" text-anchor="middle" fill="{_INK}">cell number (order of the cell sections in the report)</text>')
    desc = f"{label}. Mean paired R30 difference {contrast} with 95% bootstrap interval in each of {len(rows)} cells."
    return _svg(f"{contrast} by cell ({label})", desc, body)


# --------------------------------------------------------------------------- tables and Markdown

def _f(v, nd=4):
    if v is None:
        return "n/a"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def _p(v):
    """p-values: a bootstrap p of 0 only means smaller than the resolution of the bootstrap."""
    if v is None:
        return "n/a"
    return "< 0.0001" if v < 1e-4 else f"{v:.4f}"


def arm_rows(analysis: dict) -> list[dict]:
    rows = []
    for cell in analysis["cells"]:
        for a in cell["arms"]:
            for m in SUMMARY_METRICS:
                e = a["metrics"].get(m)
                if e is None:
                    continue
                rows.append({"cell_id": cell["cell_id"], "arm": a["arm"], "metric": m, "n": a["n"],
                             "mean": e["mean"], "sd": e["sd"], "min": e["min"], "max": e["max"],
                             "ci95_low": e.get("ci95", [None, None])[0], "ci95_high": e.get("ci95", [None, None])[1]})
    return rows


def contrast_rows(analysis: dict) -> list[dict]:
    rows = []
    for cell in analysis["cells"]:
        items = [("primary", cell["primary"]), ("primary, residual-flagged excluded", cell["primary_excluding_residual_flagged"])]
        items += [("secondary", s) for s in cell["secondary"]]
        for kind, s in items:
            if s is None:
                continue
            rows.append({"cell_id": cell["cell_id"], "kind": kind, "contrast": s["contrast"], "metric": s["metric"],
                         "n": s["n"], "mean_diff": s["mean_diff"], "sd_diff": s["sd_diff"], "d_z": s["d_z"],
                         "ci95_low": s["ci95"][0], "ci95_high": s["ci95"][1], "ci90_low": s["ci90"][0],
                         "ci90_high": s["ci90"][1], "p_boot": s["p_boot"], "p_holm": s.get("p_holm"),
                         "classification": s["classification"]})
    return rows


def _csv(rows: list[dict]) -> str:
    if not rows:
        return ""
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0]), lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({k: ("" if v is None else v) for k, v in r.items()})
    return buf.getvalue()


def markdown(analysis: dict, doc: dict, result_path: str, result_sha: str, figs: list[tuple[str, str, str]]) -> str:
    lab = analysis["label"].upper()
    lines = [
        "<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->",
        f"# {analysis['experiment_id']}: generated results report ({lab})", "",
        f"**Label: {lab}.** {doc['simulation_notice']}",
    ]
    if analysis["label"] == "exploratory":
        lines.append("This report is exploratory. It uses development seeds only and is not a finding; "
                     "nothing in it may be cited as a result of a registered experiment.")
    lines += ["", "Generated by `streak.report` from the result file. Do not edit by hand.", "",
              f"- Result file: `{result_path}`",
              f"- Result SHA-256: `{result_sha[:32]}` `{result_sha[32:]}`",
              f"- Config hash: `{analysis['config_hash'][:32]}` `{analysis['config_hash'][32:]}`",
              f"- Protocol version {doc['protocol_version']}; engine version {doc['engine_version']}",
              f"- Records (learner-arms): {analysis['n_records']}; failed: {analysis['n_failed']} "
              f"({analysis['failure_rate']:.2%})",
              f"- Master seeds: {', '.join(map(str, doc['config']['master_seeds']))}; "
              f"learners per seed: {doc['config']['learners_per_seed']}", ""]
    for cell in analysis["cells"]:
        lines += [f"## Cell `{cell['cell_id']}`", "", "### Retention by arm (means over learners, proportions)", "",
                  "| Arm | n | R30 | R30 95% CI | R1 | R7 | R90 | AUC-R | Weakest decile R30 |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for a in cell["arms"]:
            mm = a["metrics"]
            g = lambda k, nd=4: _f(mm[k]["mean"], nd) if mm.get(k) else "n/a"
            ci = mm["R30"].get("ci95") if mm.get("R30") else None
            lines.append(f"| {a['arm']} | {a['n']} | {g('R30')} | {('[' + _f(ci[0]) + ', ' + _f(ci[1]) + ']') if ci else 'n/a'} | "
                         f"{g('R1')} | {g('R7')} | {g('R90')} | {g('AUC_R')} | {g('weakest_decile_R30')} |")
        lines += ["", "### Activity by arm (means over learners)", "",
                  "| Arm | Minutes | Residual slots | Active days | Longest streak | Success rate | Coverage | Spearman (active days, R30) | Residual-flagged |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for a in cell["arms"]:
            mm = a["metrics"]
            g = lambda k, nd=4: _f(mm[k]["mean"], nd) if mm.get(k) else "n/a"
            lines.append(f"| {a['arm']} | {g('minutes_spent', 1)} | {g('residual_slots', 2)} | {g('active_days', 2)} | "
                         f"{g('longest_streak', 2)} | {g('practice_success_rate', 3)} | {g('item_coverage', 3)} | "
                         f"{_f(a.get('spearman_active_days_R30'), 3)} | {a['residual_flagged']} |")
        items = [("primary", cell["primary"]), ("primary, flagged excluded", cell["primary_excluding_residual_flagged"])]
        items += [("secondary", s) for s in cell["secondary"]]
        items = [(k, s) for k, s in items if s is not None]
        lines += ["", "### Paired contrasts on R30: effects", "",
                  "| Kind | Contrast | n | Mean diff | SD diff | d_z | 95% CI | 90% CI |", "|---|---|---|---|---|---|---|---|"]
        for kind, s in items:
            lines.append(f"| {kind} | {s['contrast']} | {s['n']} | {_f(s['mean_diff'])} | {_f(s['sd_diff'])} | {_f(s['d_z'], 2)} | "
                         f"[{_f(s['ci95'][0])}, {_f(s['ci95'][1])}] | [{_f(s['ci90'][0])}, {_f(s['ci90'][1])}] |")
        lines += ["", "### Paired contrasts on R30: tests and classes", "",
                  "| Kind | Contrast | p (bootstrap) | p (Holm) | Class (protocol section 4) |", "|---|---|---|---|---|"]
        for kind, s in items:
            lines.append(f"| {kind} | {s['contrast']} | {_p(s['p_boot'])} | {_p(s.get('p_holm'))} | {s['classification']} |")
        if cell["primary"]:
            ps = cell["primary"]["per_seed_mean"]
            lines += ["", "Per-master-seed mean of the primary paired difference: " +
                      ", ".join(f"seed {k}: {_f(v)}" for k, v in ps.items()) + "."]
        lines.append("")
    if figs:
        lines += ["## Figures", ""]
        for fid, rel, caption in figs:
            lines += [f"![{fid}. {caption}]({rel})", ""]
    lines += ["## Notes", "",
              "- Intervals are stratified percentile bootstrap intervals over learners within master seeds "
              f"({doc['config']['analysis']['bootstrap_resamples']} resamples, seed {doc['config']['analysis']['bootstrap_seed']}).",
              "- Classes follow research/protocol.md section 4 with SESOI "
              f"{doc['config']['analysis']['sesoi']}. Non-significance is never equivalence.",
              "- Holm adjustment is applied to bootstrap p-values of the secondary contrasts within each cell.", ""]
    return "\n".join(lines)


def build_report(result_path: Path, out_dir: Path, *, pdf: bool = False, max_cell_figures: int = 1) -> dict:
    """Generate all report outputs. Returns a dict of written paths."""
    doc = load_result(result_path)
    analysis = analyse(doc)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "figures").mkdir(exist_ok=True)
    written = {}
    (out_dir / "analysis.json").write_text(json.dumps(analysis, indent=2) + "\n")
    (out_dir / "metrics.csv").write_text(_csv(arm_rows(analysis)))
    (out_dir / "contrasts.csv").write_text(_csv(contrast_rows(analysis)))
    written.update(analysis=out_dir / "analysis.json", metrics=out_dir / "metrics.csv",
                   contrasts=out_dir / "contrasts.csv")
    label = f"{doc['label']}, {doc['experiment_id']}"
    figs = []
    tab = _table(doc)
    for i, cell in enumerate(analysis["cells"][:max_cell_figures]):
        name = f"FIG-{i + 1:02d}a-arm-r30.svg"
        (out_dir / "figures" / name).write_text(fig_arm_means(cell, label))
        figs.append((f"FIG-{i + 1:02d}a", f"figures/{name}",
                     f"Mean R30 per arm with 95% stratified bootstrap interval, cell {cell['cell_id']}; "
                     "unit: proportion of items expected to be recalled 30 days after practice ends."))
        if cell["primary"]:
            t, c = doc["config"]["analysis"]["primary_contrast"]
            rt, rc = tab[(cell["cell_id"], t)], tab[(cell["cell_id"], c)]
            keys = sorted(set(rt) & set(rc))
            diffs = np.array([rt[k]["R30"] - rc[k]["R30"] for k in keys])
            name = f"FIG-{i + 1:02d}b-primary-diff.svg"
            (out_dir / "figures" / name).write_text(fig_diff_hist(diffs, f"{t} - {c}", label))
            figs.append((f"FIG-{i + 1:02d}b", f"figures/{name}",
                         f"Distribution of per-learner paired R30 differences {t} - {c}, n = {diffs.size}, cell {cell['cell_id']}."))
    if len(analysis["cells"]) > 1:
        (out_dir / "figures" / "FIG-99-cells.svg").write_text(fig_cells(analysis["cells"], label))
        figs.append(("FIG-99", "figures/FIG-99-cells.svg",
                     "Mean paired R30 difference of the primary contrast with 95% bootstrap interval in every cell; cells are "
                     "numbered 1 to " + str(len(analysis["cells"])) + " in the order of the cell sections of this report: "
                     + "; ".join(f"{i} = {c['cell_id']}" for i, c in enumerate(analysis["cells"], 1)) + "."))
    try:
        shown = str(Path(result_path).resolve().relative_to(repo_root().resolve()))
    except ValueError:
        shown = Path(result_path).name
    md = markdown(analysis, doc, shown, sha256_file(result_path), figs)
    (out_dir / "report.md").write_text(md)
    written["report_md"] = out_dir / "report.md"
    if pdf:
        written["report_pdf"] = build_pdf(out_dir / "report.md")
    return written


def build_pdf(md_path: Path) -> Path:
    """pandoc Markdown -> Typst (mainfont Libertinus Serif, decision D-002), then the typst
    Python package compiles it. Tool locations can be overridden with STREAK_PANDOC and
    STREAK_TYPST_PYTHON."""
    pandoc = os.environ.get("STREAK_PANDOC", DEFAULT_PANDOC)
    typst_py = os.environ.get("STREAK_TYPST_PYTHON", DEFAULT_TYPST_PYTHON)
    typ = md_path.with_suffix(".typ")
    pdf = md_path.with_suffix(".pdf")
    subprocess.run([pandoc, str(md_path.name), "-s", "-t", "typst", "-V", 'mainfont=Libertinus Serif',
                    "-V", "papersize=a4", "-V", "fontsize=10pt", "-o", typ.name], cwd=md_path.parent, check=True)
    subprocess.run([typst_py, "-I", "-c", "import sys, typst; typst.compile(sys.argv[1], output=sys.argv[2])",
                    typ.name, pdf.name], cwd=md_path.parent, check=True)
    typ.unlink()
    return pdf
