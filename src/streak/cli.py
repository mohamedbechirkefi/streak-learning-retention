# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Command-line interface: smoke, run, report, test.

    python -m streak.cli smoke  [--config experiments/smoke-exp001.json] [--out DIR] [--pdf]
    python -m streak.cli run    --config PATH [--out DIR]
    python -m streak.cli report --results PATH [--out DIR] [--pdf]
    python -m streak.cli test   [pytest args...]

``run`` refuses a confirmatory config while the experiment's protocol is not frozen
(gate G-FREEZE). ``smoke`` only accepts exploratory configs.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

from .manifest import repo_root
from .report import build_report
from .runner import GateError, execute, load_config

DEFAULT_SMOKE = "experiments/smoke-exp001.json"


def _default_out(cfg: dict, root: Path) -> Path:
    if cfg["label"] == "exploratory":
        return root / "results" / "exploratory" / cfg["experiment_id"]
    return root / "results" / "raw" / cfg["experiment_id"]


def _run(cfg_path: str, out: str | None, pdf: bool, want_label: str | None, argv: list[str]) -> int:
    root = repo_root()
    path = Path(cfg_path)
    if not path.is_absolute():
        path = root / path
    cfg = load_config(path)
    if want_label and cfg["label"] != want_label:
        print(f"error: smoke accepts only {want_label} configs; {path} is {cfg['label']}", file=sys.stderr)
        return 2
    out_dir = Path(out) if out else _default_out(cfg, root)
    command = "python -m streak.cli " + " ".join(shlex.quote(a) for a in argv)
    try:
        man = execute(cfg, out_dir, command, root)
    except GateError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 3
    n = sum(r["n_learner_arms"] for r in man["runs"])
    fails = sum(r["n_failed"] for r in man["runs"])
    print(f"[{cfg['label']}] {cfg['experiment_id']}: {n} learner-arms, {fails} failed, "
          f"{man['runtime_s']:.2f} s, peak memory {man['peak_memory_bytes']} bytes")
    print(f"results:  {out_dir / 'results.json'}")
    print(f"manifest: {out_dir / 'run_manifest.json'}")
    if want_label == "exploratory":  # smoke also builds its report
        written = build_report(out_dir / "results.json", out_dir / "report", pdf=pdf)
        print(f"report:   {written['report_md']}")
        if "report_pdf" in written:
            print(f"pdf:      {written['report_pdf']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(prog="streak", description="STREAK simulation study CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("smoke", help="exploratory smoke run on smoke seeds, with report")
    s.add_argument("--config", default=DEFAULT_SMOKE)
    s.add_argument("--out")
    s.add_argument("--pdf", action="store_true")
    r = sub.add_parser("run", help="run a config (confirmatory configs need a frozen protocol)")
    r.add_argument("--config", required=True)
    r.add_argument("--out")
    p = sub.add_parser("report", help="build tables, figures and report from a result file")
    p.add_argument("--results", required=True)
    p.add_argument("--out")
    p.add_argument("--pdf", action="store_true")
    p.add_argument("--max-cell-figures", type=int, default=1)
    t = sub.add_parser("test", help="run the test suite (pytest)")
    t.add_argument("pytest_args", nargs=argparse.REMAINDER)
    args = ap.parse_args(argv)

    if args.cmd == "smoke":
        return _run(args.config, args.out, args.pdf, "exploratory", argv)
    if args.cmd == "run":
        return _run(args.config, args.out, False, None, argv)
    if args.cmd == "report":
        res = Path(args.results)
        out = Path(args.out) if args.out else res.parent / "report"
        written = build_report(res, out, pdf=args.pdf, max_cell_figures=args.max_cell_figures)
        for k, v in written.items():
            print(f"{k}: {v}")
        return 0
    if args.cmd == "test":
        return subprocess.call([sys.executable, "-m", "pytest", *args.pytest_args], cwd=repo_root())
    return 2


if __name__ == "__main__":
    sys.exit(main())
