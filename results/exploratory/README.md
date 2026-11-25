<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# results/exploratory/

**Exploratory only.** Smoke runs on development seeds 9001 to 9005, made before the protocol freeze to measure runtime, seed spread and degenerate cases (M2 brief). They are not findings, are never pooled with confirmatory results and must not be cited as results of EXP-001 to EXP-003. Journal entries: J-0004 to J-0007 (J-0002 and J-0003 record earlier, discarded attempts) in `research/experiment_journal.jsonl`.

Each folder holds `run_manifest.json` and `report/` (`report.md`, `analysis.json`, `metrics.csv`, `contrasts.csv`, `figures/*.svg`). `SMOKE-EXP-001/` also holds its raw `results.json` and `report/report.pdf`.

Regenerate (raw files of the larger runs go to the git-ignored `results/raw/exploratory/`):

    uv run python -m streak.cli smoke --pdf
    uv run python -m streak.cli run --config experiments/smoke-exp001-n200.json --out results/raw/exploratory/SMOKE-EXP-001-N200
    uv run python -m streak.cli report --results results/raw/exploratory/SMOKE-EXP-001-N200/results.json --out results/exploratory/SMOKE-EXP-001-N200/report
    (same pair of commands for smoke-exp002.json / SMOKE-EXP-002 and smoke-exp003.json / SMOKE-EXP-003)

Result files are byte-identical on rerun with the same code and platform (tested); manifests differ in timestamps, runtime and memory.

## M4 sensitivity checks (2026-11-25, D-019, J-0018)

`SMOKE-M4-SENS-K050`, `-K100`, `-K200`, `-K400` and `-SLOWH0` are exploratory sensitivity runs made in M4, after the confirmatory analysis, on smoke seeds 9001 to 9005 (100 learners each). They never replace or change a frozen verdict. `M4-SENSITIVITY/` holds their summary and the analysis of committed EXP-001 data. Regenerate:

    for n in k050 k100 k200 k400 slow-h0: .venv/bin/python -m streak.cli run --config experiments/m4-sens-$n.json --out results/raw/exploratory/<ID>
    .venv/bin/python -m streak.cli report --results results/raw/exploratory/<ID>/results.json --out results/exploratory/<ID>/report
    .venv/bin/python scripts/m4_exploratory.py
